# default.py
import requests
import re
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib.parse
from resources.lib.tmdb import search_tmdb

ADDON = xbmcaddon.Addon()
_handle = int(sys.argv[1])
BASE_URL = sys.argv[0]

# Sample YouTube Nollywood Playlists (replace with real ones)
PLAYLISTS = {
    'latest': 'PLr5e0TIgT4X8w7hK7j6g9vZ3vZ3vZ3vZ3',  # Example: iROKOtv Nollywood
    'action': 'PLr5e0TIgT4X9aBcDeFgHiJkLmNoPqRsTu',
    'romance': 'PLr5e0TIgT4X8cDeFgHiJkLmNoPqRsTuVw',
    'comedy': 'PLr5e0TIgT4X7dEfGhIjKlMnOpQrStUvWx',
    'drama': 'PLr5e0TIgT4X6eFgHiJkLmNoPqRsTuVxy'
}

def build_url(query):
    return f"{BASE_URL}?{urllib.parse.urlencode(query)}"

def get_youtube_videos(playlist_id):
    """
    Fetch real videos from a YouTube playlist using YouTube Data API v3
    """
    import requests

    YOUTUBE_API_KEY = ADDON.getSetting('youtube_api_key')
    if not YOUTUBE_API_KEY:
        xbmcgui.Dialog().ok("Error", "YouTube API Key not set in addon settings.")
        return []

    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    videos = []
    next_page_token = ""

    try:
        while True:
            params = {
                'part': 'snippet',
                'playlistId': playlist_id,
                'maxResults': 50,
                'key': YOUTUBE_API_KEY,
                'pageToken': next_page_token
            }
            response = requests.get(url, params=params, timeout=15)
            data = response.json()

            if 'error' in data:
                xbmc.log(f"YouTube API Error: {data['error']['message']}", xbmc.LOGERROR)
                xbmcgui.Dialog().ok("YouTube Error", data['error']['message'])
                break

            for item in data.get('items', []):
                snippet = item['snippet']
                if snippet['resourceId']['kind'] != 'youtube#video':
                    continue

                video_id = snippet['resourceId']['videoId']
                title = snippet['title']
                # Extract year from title or description (fallback)
                year = extract_year(title) or extract_year(snippet.get('description', ''))

                videos.append({
                    'title': title,
                    'video_id': video_id,
                    'year': year or 'Unknown',
                    'thumb': snippet['thumbnails']['high']['url']
                })

            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break

    except Exception as e:
        xbmc.log(f"YouTube fetch error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok("Network Error", "Failed to fetch YouTube videos.")

    return videos


def extract_year(text):
    """Extract 4-digit year (19xx or 20xx) from text"""
    match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
    return match.group(0) if match else None


def list_movies(category):
    videos = get_youtube_videos(PLAYLISTS.get(category, PLAYLISTS['latest']))
    listing = []

    for video in videos:
        meta = search_tmdb(video['title'], video['year']) or {}
        title = f"{video['title']} ({video['year']})"
        plot = meta.get('plot', 'No description available.')
        # Use YouTube thumbnail first, fallback to TMDB
        thumb = video.get('thumb') or meta.get('thumb') or f"{ADDON.getAddonInfo('path')}/icon.png"

        li = xbmcgui.ListItem(label=title)
        li.setInfo('video', {
            'title': title,
            'plot': plot,
            'year': int(video['year']),
            'rating': float(meta.get('rating', 0)),
            'mediatype': 'movie'
        })
        li.setArt({'thumb': thumb, 'icon': thumb, 'fanart': meta.get('fanart', '')})
        li.setProperty('IsPlayable', 'true')

        url = build_url({'mode': 'play', 'video_id': video['video_id']})
        listing.append((url, li, False))

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(_handle)

def play_video(video_id):
    play_item = xbmcgui.ListItem(path=f"https://www.youtube.com/watch?v={video_id}")
    xbmcplugin.setResolvedUrl(_handle, True, play_item)

def search_movies():
    kb = xbmc.Keyboard('', ADDON.getLocalizedString(30100))
    kb.doModal()
    if kb.isConfirmed() and kb.getText():
        query = kb.getText()
        # Simulate search (replace with real YouTube search)
        videos = [{'title': query, 'video_id': 'dQw4w9WgXcQ', 'year': '2020'}]
        list_movies_from_list(videos)

def list_movies_from_list(videos):
    listing = []
    for video in videos:
        meta = search_tmdb(video['title'], video.get('year')) or {}
        li = xbmcgui.ListItem(label=video['title'])
        li.setInfo('video', {'title': video['title'], 'plot': meta.get('plot', '')})
        li.setArt({'thumb': meta.get('thumb', ADDON.getAddonInfo('icon'))})
        li.setProperty('IsPlayable', 'true')
        url = build_url({'mode': 'play', 'video_id': video['video_id']})
        listing.append((url, li, False))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)

def main_menu():
    items = [
        ('Latest Nollywood Movies', {'mode': 'list', 'category': 'latest'}),
        ('Action', {'mode': 'list', 'category': 'action'}),
        ('Romance', {'mode': 'list', 'category': 'romance'}),
        ('Comedy', {'mode': 'list', 'category': 'comedy'}),
        ('Drama', {'mode': 'list', 'category': 'drama'}),
        ('Search Movies', {'mode': 'search'}),
    ]

    for label, params in items:
        url = build_url(params)
        li = xbmcgui.ListItem(label)
        li.setArt({'icon': f"{ADDON.getAddonInfo('path')}/icon.png"})
        xbmcplugin.addDirectoryItem(_handle, url, li, True)

    xbmcplugin.endOfDirectory(_handle)

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    mode = params.get('mode')

    if mode == 'list':
        list_movies(params.get('category', 'latest'))
    elif mode == 'play':
        play_video(params['video_id'])
    elif mode == 'search':
        search_movies()
    else:
        main_menu()

if __name__ == '__main__':
    router(sys.argv[2][1:])

