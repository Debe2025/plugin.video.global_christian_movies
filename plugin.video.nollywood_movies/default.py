# -*- coding: utf-8 -*-
# default.py - Nollywood Movies Addon (DYNAMIC 2025 VERSION)

import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib.parse
import re
import requests
from resources.lib.tmdb import search_tmdb

ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

# Top official Nollywood channels (2025) — these never change
CHANNELS = {
    'irokotv': 'UCHbSUtIxfTd4TXzfDw37F9Q',        # iROKOtv OFFICIAL
    'ruthkadiri': 'UC1lormcUqR3gYb8M6n7wE7Q',     # Ruth Kadiri 247
    'ibakatv': 'UC0fX5X-3cK3cK3cK3cK3cK3c',        # IBAKATV (placeholder - find real)
    'nollywoodmovies': 'UC0fX5X-3cK3cK3cK3cK3cK3c'  # NollywoodMoviesTV
}

# Dynamic search queries per category (you can tweak these)
SEARCH_QUERIES = {
    'latest':  'Nollywood full movie 2025 OR 2024 site:youtube.com',
    'action':  'Nollywood action OR thriller full movie',
    'romance': 'Nollywood romance OR love full movie',
    'comedy':  'Nollywood comedy OR funny full movie',
    'drama':   'Nollywood drama OR family full movie'
}

def build_url(query):
    return f"{BASE_URL}?{urllib.parse.urlencode(query)}"

def youtube_search(query, max_results=50):
    api_key = ADDON.getSetting('youtube_api_key').strip()
    if not api_key:
        xbmcgui.Dialog().ok("Nollywood Movies", "YouTube API Key required!\nGo to Add-on Settings → API Keys")
        return []

    url = "https://www.googleapis.com/youtube/v3/search"
    videos = []
    next_page = ""

    try:
        while len(videos) < max_results:
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'videoEmbeddable': 'true',
                'videoDuration': 'long',           # Prefer full movies (>20 mins)
                'order': 'date',                   # Newest first
                'maxResults': min(50, max_results - len(videos)),
                'key': api_key,
                'pageToken': next_page or ''
            }
            response = requests.get(url, params=params, timeout=20)
            data = response.json()

            if 'error' in data:
                xbmc.log(f"YouTube API Error: {data['error']['message']}", xbmc.LOGERROR)
                xbmcgui.Dialog().ok("YouTube Error", data['error']['message'])
                break

            for item in data.get('items', []):
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                thumb = item['snippet']['thumbnails']['high']['url']
                channel = item['snippet']['channelTitle']

                # Filter out shorts/trailers/music
                if any(bad in title.lower() for bad in ['trailer', 'short', 'music', 'song', 'official video']):
                    continue

                year = extract_year(title) or extract_year(item['snippet'].get('description', ''))

                videos.append({
                    'title': title,
                    'video_id': video_id,
                    'year': year or '2025',
                    'thumb': thumb,
                    'channel': channel
                })

            next_page = data.get('nextPageToken')
            if not next_page or len(videos) >= max_results:
                break

    except Exception as e:
        xbmc.log(f"YouTube search failed: {str(e)}", xbmc.LOGERROR)

    return videos

def extract_year(text):
    match = re.search(r'\b(19\d{2}|20\d{2})\b', text or '')
    return match.group(0) if match else None

def list_category(category):
    query = SEARCH_QUERIES.get(category, SEARCH_QUERIES['latest'])
    videos = youtube_search(query, max_results=50)

    if not videos:
        xbmcgui.Dialog().ok("No Results", f"No movies found in '{category.title()}'\nTry Search instead.")
        return

    listing = []
    for v in videos:
        meta = search_tmdb(v['title'], v['year']) or {}
        title = f"{v['title']} ({v['year']})"
        plot = meta.get('plot') or f"{v['channel']} • Nollywood Full Movie"
        thumb = v['thumb'] or meta.get('thumb', ADDON.getAddonInfo('icon'))
        fanart = meta.get('fanart', ADDON.getAddonInfo('fanart'))

        li = xbmcgui.ListItem(title)
        li.setInfo('video', {
            'title': title,
            'plot': plot,
            'year': int(v['year']) if v['year'].isdigit() else 2025,
            'rating': float(meta.get('rating', 7.0)),
            'mediatype': 'movie',
            'genre': 'Nollywood'
        })
        li.setArt({'thumb': thumb, 'icon': thumb, 'fanart': fanart})
        li.setProperty('IsPlayable', 'true')

        url = build_url({'mode': 'play', 'video_id': v['video_id']})
        listing.append((url, li, False))

    xbmcplugin.addDirectoryItems(HANDLE, listing, len(listing))
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_DATEADDED)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(HANDLE)

def play_video(video_id):
    play_item = xbmcgui.ListItem(path=f"https://www.youtube.com/watch?v={video_id}")
    xbmcplugin.setResolvedUrl(HANDLE, True, play_item)

def search_movies():
    kb = xbmc.Keyboard('', "Search Nollywood Movies")
    kb.doModal()
    if not kb.isConfirmed() or not kb.getText().strip():
        return

    query = f"{kb.getText().strip()} Nollywood full movie"
    videos = youtube_search(query, max_results=30)

    if not videos:
        xbmcgui.Dialog().ok("No Results", "No movies found. Try: Lionheart, Mount Zion, Ruth Kadiri")
        return

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
    items = [
        ("Latest Movies",    {'mode': 'list', 'category': 'latest'}),
        ("Action",           {'mode': 'list', 'category': 'action'}),
        ("Romance",          {'mode': 'list', 'category': 'romance'}),
        ("Comedy",           {'mode': 'list', 'category': 'comedy'}),
        ("Drama",            {'mode': 'list', 'category': 'drama'}),
        ("Search",           {'mode': 'search'})
    ]

    for label, params in items:
        url = build_url(params)
        li = xbmcgui.ListItem(label)
        li.setArt({'icon': ADDON.getAddonInfo('icon'), 'fanart': ADDON.getAddonInfo('fanart')})
        xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=True)

    xbmcplugin.endOfDirectory(HANDLE)

def router():
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
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