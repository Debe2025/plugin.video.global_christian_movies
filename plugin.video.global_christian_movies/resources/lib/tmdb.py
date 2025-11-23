# resources/lib/tmdb.py
import xbmc
import xbmcaddon
import requests

ADDON = xbmcaddon.Addon()

def search_tmdb(title, year=None):
    """
    OPTIONAL TMDB lookup — if no key → just return empty dict (no crash, no dialog)
    """
    api_key = ADDON.getSetting('tmdb_api_key').strip()
    if not api_key:
        return {}  # ← silently skip TMDB, no popup!

    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        'api_key': api_key,
        'query': title,
        'language': 'en-US',
        'include_adult': False
    }
    if year and year.isdigit():
        params['year'] = year

    try:
        data = requests.get(url, params=params, timeout=10).json()
        if data.get('results'):
            m = data['results'][0]
            poster = f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}" if m.get('poster_path') else ''
            backdrop = f"https://image.tmdb.org/t/p/w1280{m.get('backdrop_path')}" if m.get('backdrop_path') else ''
            return {
                'plot': m.get('overview', ''),
                'thumb': poster,
                'fanart': backdrop,
                'rating': m.get('vote_average', 0)
            }
    except:
        pass  # fail silently

    return {}