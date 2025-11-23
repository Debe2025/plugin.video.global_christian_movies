# -*- coding: utf-8 -*-
# default.py - Global Christian Movies v1.0.2
# Multi-Part Auto-Play + Massive Content Boost

import sys, xbmc, xbmcgui, xbmcplugin, xbmcaddon, urllib.parse, re, requests
from resources.lib.tmdb import search_tmdb

ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

COUNTRIES = {
    'all':          'Christian full movie OR "Jesus film" OR gospel movie OR testimony OR deliverance after:2023',
    'nigeria':      'Mount Zion OR "Mike Bamiloye" OR "Christian movie Nigeria" OR testimony Nigeria',
    'ghana':        'Ghana Christian movie OR testimony OR "Apostle" OR revival Ghana',
    'kenya':        'Kenya gospel movie OR Swahili Christian OR testimony Kenya',
    'south_africa': 'South Africa Christian movie OR Afrikaans gospel OR testimony',
    'usa':          '"Pure Flix" OR "Kendrick Brothers" OR "The Chosen" OR "God’s Not Dead" OR "War Room"',
    'uk':           'British Christian movie OR UK gospel OR testimony',
    'india':        'Hindi Christian OR Tamil Jesus OR Malayalam gospel OR Telugu Christian full movie',
    'brazil':       'filme cristão completo OR testemunho Brasil OR evangelho',
    'philippines':  'Tagalog Christian movie OR Filipino gospel OR testimony',
    'korea':        '기독교 영화 OR Korean Christian movie OR testimony Korea',
    'china':        '基督教电影 OR Chinese Christian movie OR house church testimony OR Jesus film Chinese'
}

def build_url(q): return f"{BASE_URL}?{urllib.parse.urlencode(q)}"

def youtube_search(query, max_results=200):
    key = ADDON.getSetting('youtube_api_key').strip()
    if not key:
        xbmcgui.Dialog().ok("Global Christian Movies", "YouTube API Key required!")
        return []

    raw_videos = {}
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        next_page = ""
        while len(raw_videos) < max_results and next_page != False:
            data = requests.get(url, params={
                'part': 'snippet', 'q': query, 'type': 'video',
                'videoEmbeddable': 'true', 'videoDuration': 'long',
                'videoCategoryId': '22', 'order': 'relevance',
                'relevanceLanguage': 'en', 'regionCode': 'US',
                'maxResults': 50, 'key': key, 'pageToken': next_page or ''
            }, timeout=20).json()

            for item in data.get('items', []):
                title = item['snippet']['title']
                vid = item['id']['videoId']
                thumb = item['snippet']['thumbnails']['high']['url']

                clean_title = re.sub(r'\s*(official|hd|4k|trailer|teaser|short|music|lyrics).*', '', title, flags=re.I)
                clean_title = re.sub(r'\s*[\[\(].*?[\]\)]', '', clean_title)

                part_match = re.search(r'(?:part|pt|ep|p)\s*[\:]*\s*(\d+)', clean_title, re.I)
                part_num = int(part_match.group(1)) if part_match else 1

                base_name = re.sub(r'(?:part|pt|ep|p)\s*[\:]*\s*\d+.*$', '', clean_title, flags=re.I).strip()
                if len(base_name) < 12: continue

                if base_name not in raw_videos:
                    raw_videos[base_name] = {'title': base_name, 'parts': {}, 'thumb': thumb}
                raw_videos[base_name]['parts'][part_num] = vid

            next_page = data.get('nextPageToken') or False
    except: pass

    final = []
    for movie in raw_videos.values():
        if 1 in movie['parts']:
            year = re.search(r'\b(20\d{2})\b', movie['title'])
            final.append({
                'title': movie['title'],
                'video_id': movie['parts'][1],
                'all_parts': '|'.join(movie['parts'].get(i, '') for i in sorted(movie['parts'])),
                'thumb': movie['thumb'],
                'year': year.group(0) if year else '2025',
                'total_parts': len(movie['parts'])
            })
    return final

def list_country(country):
    query = COUNTRIES.get(country, COUNTRIES['all'])
    videos = youtube_search(query)
    if not videos:
        xbmcgui.Dialog().ok("No Results", f"No content for {country.title()}")
        return
    for v in videos:
        label = v['title']
        if v['total_parts'] > 1:
            label += f"  [COLOR yellow]({v['total_parts']} Parts)[/COLOR]"
        li = xbmcgui.ListItem(label + f" ({v['year']})")
        li.setInfo('video', {'title': v['title'], 'year': int(v['year']), 'mediatype': 'movie', 'genre': 'Christian'})
        li.setArt({'thumb': v['thumb']})
        li.setProperty('IsPlayable', 'true')
        url = build_url({'mode': 'play', 'video_id': v['video_id'], 'parts': v['all_parts']})
        xbmcplugin.addDirectoryItem(HANDLE, url, li, False)
    xbmcplugin.endOfDirectory(HANDLE)

def play_video(video_id, parts=None):
    if parts and '|' in parts:
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        for vid in parts.split('|'):
            if vid:
                url = f"plugin://plugin.video.youtube/play/?video_id={vid}"
                li = xbmcgui.ListItem(path=url)
                playlist.add(url, li)
        xbmc.Player().play(playlist)
    else:
        url = f"plugin://plugin.video.youtube/play/?video_id={video_id}"
        xbmcplugin.setResolvedUrl(HANDLE, True, xbmcgui.ListItem(path=url))

def search():
    kb = xbmc.Keyboard('', "Global Search")
    kb.doModal()
    if kb.isConfirmed() and kb.getText():
        videos = youtube_search(f"{kb.getText()} Christian OR Jesus OR testimony OR full movie", 200)
        for v in videos:
            label = v['title']
            if v['total_parts'] > 1:
                label += f"  [COLOR yellow]({v['total_parts']} Parts)[/COLOR]"
            li = xbmcgui.ListItem(label)
            li.setArt({'thumb': v['thumb']})
            li.setProperty('IsPlayable', 'true')
            url = build_url({'mode': 'play', 'video_id': v['video_id'], 'parts': v['all_parts']})
            xbmcplugin.addDirectoryItem(HANDLE, url, li, False)
        xbmcplugin.endOfDirectory(HANDLE)

def main_menu():
    order = ['all','nigeria','ghana','kenya','south_africa','usa','uk','india','brazil','philippines','korea','china']
    for code in order:
        name = code.replace('_', ' ').title()
        if code == 'all': name = 'All Countries'
        if code == 'china': name = 'China (House Church)'
        li = xbmcgui.ListItem(name)
        li.setArt({'icon': ADDON.getAddonInfo('icon')})
        xbmcplugin.addDirectoryItem(HANDLE, build_url({'mode': 'country', 'country': code}), li, True)
    li = xbmcgui.ListItem("Search All Countries")
    xbmcplugin.addDirectoryItem(HANDLE, build_url({'mode': 'search'}), li, True)
    xbmcplugin.endOfDirectory(HANDLE)

def router():
    p = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
    m = p.get('mode')
    if m == 'country': list_country(p.get('country'))
    elif m == 'play': play_video(p.get('video_id'), p.get('parts'))
    elif m == 'search': search()
    else: main_menu()

if __name__ == '__main__':
    router()