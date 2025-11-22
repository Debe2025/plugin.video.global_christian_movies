# -*- coding: utf-8 -*-
# default.py - Nollywood Movies Addon

import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib.parse
import re
import requests
from resources.lib.tmdb import search_tmdb

# === Global variables ===
ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

# Your real YouTube Nollywood playlists (update these with actual big channels)
PLAYLISTS = {
    'latest':  'PLr5e0TIgT4X8w7hK7j6g9vZ3vZ3vZ3vZ3',   # iROKOtv, NollywoodMoviesTV, etc.
    'action':  'PLr5e0TIgT4X9aBcDeFgHiJkLmNoPqRsTu',
    'romance': 'PLr5e0TIgT4X8cDeFgHiJkLmNoPqRsTuVw',
    'comedy':  'PLr5e0TIgT4X7dEfGhIjKlMnOpQrStUvWx',
    'drama':   'PLr5e0TIgT4X6eFgHiJkLmNoPqRsTuVxy'
}

def build_url(query):
    return f"{BASE_URL}?{urllib.parse.urlencode(query)}"

def get_youtube_videos(playlist_id):
    api_key = ADDON.getSetting('youtube_api_key').strip()
    if not api_key:
        xbmcgui.Dialog().ok("Nollywood Movies", "Please set your YouTube API Key in Add-on Settings → API Keys")
        return []

    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    videos = []
    next_page = ""

    try:
        while True:
            params = {
                'part': 'snippet',
                'playlistId': playlist_id,
                'maxResults': 50,
                'key': api_key,
                'pageToken': next_page
            }
            response = requests.get(url, params=params, timeout=20)
            data = response.json()

            if 'error' in data:
                xbmc.log(f"YouTube API Error: {data['error']['message']}", xbmc.LOGERROR)
                xbmcgui.Dialog().ok("YouTube Error", data['error']['message'])
                break

            for item in data.get('items', []):
                s = item['snippet']
                if s.get('resourceId', {}).get('kind') != 'youtube#video':
                    continue

                video_id = s['resourceId']['videoId']
                title = s['title']
                year = extract_year(title) or extract_year(s.get('description', ''))

                videos.append({
                    'title': title,
                    'video_id': video_id,
                    'year': year or 'Unknown',
                    'thumb': s['thumbnails'].get('high', s['thumbnails']['default'])['url']
                })

            next_page = data.get('nextPageToken')
            if not next_page:
                break

    except Exception as e:
        xbmc.log(f"YouTube fetch failed: {str(e)}", xbmc.LOGERROR)

    return videos

def extract_year(text):
    match = re.search(r'\b(19\d{2}|20\d{2})\b', text or '')
    return match.group(0) if match else None

def list_category(category):
    videos = get_youtube_videos(PLAYLISTS.get(category, PLAYLISTS['latest']))
    listing = []

    for v in videos:
        meta = search_tmdb(v['title'], v['year']) or {}
        title = f"{v['title']} ({v['year']})"
        plot = meta.get('plot', 'Nollywood movie')
        thumb = v['thumb'] or meta.get('thumb') or ADDON.getAddonInfo('icon')
        fanart = meta.get('fanart', '')

        li = xbmcgui.ListItem(title)
        li.setInfo('video', {
            'title': title,
            'plot': plot,
            'year': int(v['year']) if v['year'].isdigit() else 0,
            'rating': float(meta.get('rating', 0)),
            'mediatype': 'movie',
            'genre': 'Nollywood'
        })
        li.setArt({'thumb': thumb, 'icon': thumb, 'fanart': fanart})
        li.setProperty('IsPlayable', 'true')

        url = build_url({'mode': 'play', 'video_id': v['video_id']})
        listing.append((url, li, False))

    xbmcplugin.addDirectoryItems(HANDLE, listing, len(listing))
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.endOfDirectory(HANDLE)

def play_video(video_id):
    play_item = xbmcgui.ListItem(path=f"https://www.youtube.com/watch?v={video_id}")
    xbmcplugin.setResolvedUrl(HANDLE, True, play_item)

def search_movies():
    kb = xbmc.Keyboard('', "Search Nollywood Movies")
    kb.doModal()
    if not kb.isConfirmed() or not kb.getText().strip():
        return

    query = kb.getText().strip()
    # Simple YouTube search fallback (you can expand this later)
    videos = []
    try:
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': f"{query} Nollywood full movie",
            'type': 'video',
            'videoEmbeddable': 'true',
            'maxResults': 20,
            'key': ADDON.getSetting('youtube_api_key')
        }
        data = requests.get(search_url, params=params, timeout=15).json()
        for item in data.get('items', []):
            vid = item['id']['videoId']
            title = item['snippet']['title']
            thumb = item['snippet']['thumbnails']['high']['url']
            videos.append({'title': title, 'video_id': vid, 'thumb': thumb, 'year': 'Unknown'})
    except:
        xbmcgui.Dialog().ok("Search Failed", "Check internet or YouTube API key")

    # Show results
    listing = []
    for v in videos:
        li = xbmcgui.ListItem(v['title'])
        li.setArt({'thumb': v['thumb']})
        li.setProperty('IsPlayable', 'true')
        url = build_url({'mode': 'play', 'video_id': v['video_id']})
        listing.append((url, li, False))

    xbmcplugin.addDirectoryItems(HANDLE, listing, len(listing))
    xbmcplugin.endOfDirectory(HANDLE)

def main_menu():
    menu = [
        ("Latest Movies",     {'mode': 'list', 'category': 'latest'}),
        ("Action",            {'mode': 'list', 'category': 'action'}),
        ("Romance",           {'mode': 'list', 'category': 'romance'}),
        ("Comedy",            {'mode': 'list', 'category': 'comedy'}),
        ("Drama",             {'mode': 'list', 'category': 'drama'}),
        ("Search",            {'mode': 'search'})
    ]

    for label, params in menu:
        url = build_url(params)
        li = xbmcgui.ListItem(label)
        li.setArt({'icon': ADDON.getAddonInfo('icon'), 'fanart': ADDON.getAddonInfo('fanart')})
        xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=('search' not in params.get('mode', '')))

    xbmcplugin.endOfDirectory(HANDLE)

# === Router ===
def router():
    args = urllib.parse.parse_qsl(sys.argv[2][1:])
    params = dict(args)
    mode = params.get('mode')

    if mode == 'list':
        list_category(params.get('category', 'latest'))
    elif mode == 'play':
        play_video(params['video_id'])
    elif mode == 'search':
        search_movies()
    else:
        main_menu()

if __name__ == '__main__':
    router()