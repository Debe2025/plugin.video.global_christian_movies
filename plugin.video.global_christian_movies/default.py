# -*- coding: utf-8 -*-
# default.py - Global Christian Movies + Documentaries v1.0.0 (2025)

import sys, xbmc, xbmcgui, xbmcplugin, xbmcaddon, urllib.parse, re, requests
from resources.lib.tmdb import search_tmdb

ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

COUNTRIES = {
    'all':          'Christian full movie OR gospel film OR faith-based movie OR Jesus film 2025',
    'nigeria':      '"Mount Zion" OR "Mike Bamiloye" OR "Flaming Sword" full movie OR documentary',
    'ghana':        'Ghana Christian movie OR documentary OR testimony',
    'kenya':        'Kenya Christian movie OR gospel film OR testimony',
    'south_africa': 'South Africa Christian movie OR Afrikaans gospel OR documentary',
    'usa':          '"Pure Flix" OR "Kendrick Brothers" OR "The Chosen" OR Christian documentary USA',
    'uk':           'UK Christian movie OR British gospel film OR documentary',
    'india':        'Hindi OR Tamil OR Malayalam Christian movie OR Jesus film India OR documentary',
    'brazil':       'Filme cristão completo OR gospel brasileiro OR documentário cristão',
    'philippines':  'Filipino Christian movie OR Tagalog gospel OR documentary',
    'korea':        'Korean Christian movie OR 기독교 영화 OR documentary',
    'china':        'Chinese Christian movie OR 基督教电影 OR Jesus film China OR house church testimony'  # NEW!
}

def build_url(q): return f"{BASE_URL}?{urllib.parse.urlencode(q)}"

def youtube_search(query, max_results=50):
    key = ADDON.getSetting('youtube_api_key').strip()
    if not key:
        xbmcgui.Dialog().ok("Global Christian Movies", "YouTube API Key required!")
        return []
    videos = []
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        next_page = ""
        while len(videos) < max_results:
            data = requests.get(url, params={
                'part': 'snippet', 'q': query, 'type': 'video',
                'videoEmbeddable': 'true', 'videoDuration': 'long',
                'order': 'date', 'maxResults': 50, 'key': key,
                'pageToken': next_page or ''
            }, timeout=20).json()

            for item in data.get('items', []):
                if any(b in item['snippet']['title'].lower() for b in ['trailer','short','teaser','song','music']): continue
                vid = item['id']['videoId']
                title = item['snippet']['title']
                thumb = item['snippet']['thumbnails']['high']['url']
                year = re.search(r'\b(20\d{2})\b', title + item['snippet'].get('description',''))
                videos.append({'title': title, 'video_id': vid, 'thumb': thumb, 'year': year.group(0) if year else '2025'})
            next_page = data.get('nextPageToken')
            if not next_page: break
    except: pass
    return videos

def list_country(country):
    videos = youtube_search(COUNTRIES.get(country, COUNTRIES['all']))
    if not videos:
        xbmcgui.Dialog().ok("No Results", f"No content found for {country.replace('_',' ').title()}")
        return
    for v in videos:
        li = xbmcgui.ListItem(f"{v['title']} ({v['year']})")
        li.setInfo('video', {'title': v['title'], 'year': int(v['year']), 'mediatype': 'movie', 'genre': 'Christian'})
        li.setArt({'thumb': v['thumb']})
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(HANDLE, build_url({'mode': 'play', 'video_id': v['video_id']}), li, False)
    xbmcplugin.endOfDirectory(HANDLE)

def play_video(vid):
    url = f"plugin://plugin.video.youtube/play/?video_id={vid}" if xbmc.getCondVisibility('System.HasAddon(plugin.video.youtube)') else f"https://www.youtube.com/watch?v={vid}"
    xbmcplugin.setResolvedUrl(HANDLE, True, xbmcgui.ListItem(path=url))

def search():
    kb = xbmc.Keyboard('', "Search Global Christian Movies & Documentaries")
    kb.doModal()
    if kb.isConfirmed() and kb.getText():
        videos = youtube_search(f"{kb.getText()} Christian movie OR documentary OR testimony OR gospel")
        for v in videos:
            li = xbmcgui.ListItem(v['title'])
            li.setArt({'thumb': v['thumb']})
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(HANDLE, build_url({'mode': 'play', 'video_id': v['video_id']}), li, False)
        xbmcplugin.endOfDirectory(HANDLE)

def main_menu():
    order = ['all','nigeria','ghana','kenya','south_africa','usa','uk','india','brazil','philippines','korea','china']
    for code in order:
        name = code.replace('_', ' ').title()
        name = 'China (Mainland & House Church)' if code == 'china' else name
        name = 'All Countries' if code == 'all' else name
        li = xbmcgui.ListItem(name)
        li.setArt({'icon': ADDON.getAddonInfo('icon')})
        xbmcplugin.addDirectoryItem(HANDLE, build_url({'mode': 'country', 'country': code}), li, True)
    # Search
    li = xbmcgui.ListItem("Search All Countries")
    xbmcplugin.addDirectoryItem(HANDLE, build_url({'mode': 'search'}), li, True)
    xbmcplugin.endOfDirectory(HANDLE)

def router():
    p = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
    m = p.get('mode')
    if m == 'country': list_country(p.get('country'))
    elif m == 'play': play_video(p['video_id'])
    elif m == 'search': search()
    else: main_menu()

if __name__ == '__main__': router()