# -*- coding: utf-8 -*-
# default.py - Nollywood Movies Addon v1.0.2 (2025) - PLAYBACK FIXED FOREVER

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

# Dynamic search queries per category
SEARCH_QUERIES = {
    'latest':  'Nollywood full movie 2025 OR 2024',
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
        xbmcgui.Dialog().ok("Nollywood Movies", "YouTube API Key required!\nAdd-on Settings → API Keys")
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
                'videoDuration': 'long',
                'order': 'date',
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

                # Filter out junk
                if any(x in title.lower() for x in ['trailer', 'short', 'teaser', 'music', 'song']):
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
            if not next_page:
                break

    except Exception as e:
        xbmc.log(f"YouTube search failed: {str(e)}", xbmc.LOGERROR)

    return videos

def extract_year(text):
    if not text:
        return None
    match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
    return match.group(0) if match else None

def list_category(category):
    query = SEARCH_QUERIES.get(category, SEARCH_QUERIES['latest'])
    videos = youtube_search(query, max_results=50)

    if not videos:
        xbmcgui.Dialog().ok("No Results", f"No movies found in '{category.title()}'\nTry the Search tab.")
        return

    listing = []
    for v in videos:
        meta = search_tmdb(v['title'], v['year']) or {}
        title = f"{v['title']} ({v['year']})"
        plot = meta.get('plot') or f"{v['channel']} • Nollywood Full Movie"

        li = xbmcgui.ListItem(title)
        li.setInfo('video', {
            'title': title,
            'plot': plot,
            'year': int(v['year']) if v['year'].isdigit() else 2025,
            'rating': float(meta.get('rating', 7.0)),
            'mediatype': 'movie',
            'genre': 'Nollywood'
        })
        li.setArt({
            'thumb': v['thumb'],
            'fanart': meta.get('fanart') or v['thumb']
        })
        li.setProperty('IsPlayable', 'true')
        url = build_url({'mode': 'play', 'video_id': v['video_id']})
        listing.append((url, li, False))

    xbmcplugin.addDirectoryItems(HANDLE, listing, len(listing))
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_DATEADDED)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(HANDLE)

def play_video(video_id):
    # PRIORITY 1: Official YouTube addon (best quality, handles everything)
    if xbmc.getCondVisibility('System.HasAddon(plugin.video.youtube)'):
        youtube_url = f"plugin://plugin.video.youtube/play/?video_id={video_id}"
        play_item = xbmcgui.ListItem(path=youtube_url)
        xbmcplugin.setResolvedUrl(HANDLE, True, play_item)
        return

    # PRIORITY 2: yt-dlp module (bundled fallback, resolves to direct stream)
    try:
        from resources.lib.third_party import yt_dlp  # Your bundled yt-dlp
        ydl_opts = {
            'format': 'best[height<=1080]/best',  # Prefer 1080p or lower
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False  # Get full stream URL
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            direct_url = info['url']

        # Attach inputstream.adaptive for DASH/HLS
        play_item = xbmcgui.ListItem(path=direct_url)
        play_item.setProperty('inputstream', 'inputstream.adaptive')
        play_item.setProperty('inputstream.adaptive.manifest_type', 'dash')  # Or 'hls' if needed
        xbmcplugin.setResolvedUrl(HANDLE, True, play_item)
        return

    except ImportError:
        pass  # yt-dlp not available, try next
    except Exception as e:
        xbmc.log(f"yt-dlp playback failed: {str(e)}", xbmc.LOGERROR)

    # PRIORITY 3: Prompt to install official YouTube addon
    xbmcgui.Dialog().ok(
        "Playback Setup Needed", 
        "For best YouTube playback, install the official 'YouTube' addon:\n\n"
        "Add-ons → Download → Video add-ons → YouTube → Install"
    )
    # Fallback to raw URL (may fail, but user can install after)
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
        xbmcgui.Dialog().ok("No Results", "Try: Ruth Kadiri, Mount Zion, Lionheart")
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