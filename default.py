# default.py
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
    'latest': 'PLEXAMPLE123',  # Replace with real playlist ID
    'action': 'PLACTION456',
    'romance': 'PLROMANCE789',
    'comedy': 'PLCOMEDY000',
    'drama': 'PLDRAMA111'
}

def build_url(query):
    return f"{BASE_URL}?{urllib.parse.urlencode(query)}"

def get_youtube_videos(playlist_id):
    # Placeholder: Use YouTube API or yt-dlp in real addon
    return [
        {'title': 'Living in Bondage', 'video_id': 'dQw4w9WgXcQ', 'year': '2019'},
        {'title': 'The Wedding Party', 'video_id': 'abc123', 'year': '2016'},
    ]

def list_movies(category):
    videos = get_youtube_videos(PLAYLISTS.get(category, PLAYLISTS['latest']))
    listing = []

    for video in videos:
        meta = search_tmdb(video['title'], video['year']) or {}
        title = f"{video['title']} ({video['year']})"
        plot = meta.get('plot', 'No description available.')
        thumb = meta.get('thumb') or f"{ADDON.getAddonInfo('path')}/icon.png"

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
