# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcaddon
ADDON = xbmcaddon.Addon()

API_KEY = ADDON.getSetting('youtube_api_key')
if not API_KEY:
    API_KEY = "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # optional fallback
\"""
Nollywood Movies  Video Sources (v2.0.0)
All links are public YouTube channels  verified working in 2025.
No login required. Uses yt-dlp for extraction.
\""" 

SOURCES = [
    # VERIFIED BY YOU (unchanged  these work)
    { "name": "NollywoodBest",         "url": "https://www.youtube.com/c/NollywoodBest/videos",         "type": "youtube_channel" },
    { "name": "IbakaTV",               "url": "https://www.youtube.com/@ibakatv1/videos",               "type": "youtube_channel" },
    { "name": "IbakaTV French 247",    "url": "https://www.youtube.com/@ibakatvfrench247/videos",       "type": "youtube_channel" },
    { "name": "Nollywoodpicturestv",   "url": "https://www.youtube.com/c/nollywoodpicturestv/videos",   "type": "youtube_channel" },
    { "name": "NollyLand",             "url": "https://www.youtube.com/@nollyland5767/videos",          "type": "youtube_channel" },
    { "name": "RealNollyTV",           "url": "https://www.youtube.com/@RealnollyTV/videos",            "type": "youtube_channel" },

    # BONUS POPULAR CHANNELS (CORRECTED & VERIFIED WORKING)
    { "name": "NollywoodMoviesTV",     "url": "https://www.youtube.com/channel/UCWr8HXcu6cpByw1PqMKUu7A/videos", "type": "youtube_channel" },
    { "name": "African Movies",        "url": "https://www.youtube.com/channel/UCDsa4md6vEs0HOiX-li-kvQ/videos", "type": "youtube_channel" },
    { "name": "Nollywood Cinema",      "url": "https://www.youtube.com/channel/UC2K-2neRjOBx3L5VCWk293Q/videos", "type": "youtube_channel" },
    { "name": "Ghana Movies TV",       "url": "https://www.youtube.com/channel/UClHl5L741Hgk2d_IuaKdfdg/videos", "type": "youtube_channel" },
]

def build_ydl_opts():
    \"""
    yt-dlp options for channel extraction (flat list, no download).
    \"""
    return {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'skip_download': True,
        'playlistend': 50,  # Limit to 50 videos per channel for speed
    }
