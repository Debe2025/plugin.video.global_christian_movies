# resources/lib/tmdb.py
import xbmc
import xbmcaddon
import xbmcgui
import requests

ADDON = xbmcaddon.Addon()
TMDB_API_KEY = ADDON.getSetting('tmdb_api_key')

def search_tmdb(title, year=None):
    if not TMDB_API_KEY:
        xbmcgui.Dialog().ok("Error", "TMDB API Key not set in addon settings.")
        return None

    url = f"https://api.themoviedb.org/3/search/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'query': title,
        'include_adult': ADDON.getSettingBool('show_adult')
    }
    if year:
        params['year'] = year

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data['results']:
            movie = data['results'][0]
            return {
                'title': movie['title'],
                'plot': movie.get('overview', ''),
                'thumb': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else '',
                'fanart': f"https://image.tmdb.org/t/p/w1280{movie['backdrop_path']}" if movie.get('backdrop_path') else '',
                'year': movie['release_date'][:4] if movie.get('release_date') else '',
                'rating': str(movie.get('vote_average', 0))
            }
    except Exception as e:
        xbmc.log(f"TMDB Error: {e}", xbmc.LOGERROR)
    return None
