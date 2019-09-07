#!/usr/bin/env python3
import urllib.request
from bs4 import BeautifulSoup
import re
import warnings
import dbus
import unicodedata
import os
import sys

warnings.filterwarnings("ignore", category=DeprecationWarning)


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', str(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


def get_current_song_name():
    session_bus = dbus.SessionBus()
    spotify_bus = session_bus.get_object(
        "org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
    spotify_properties = dbus.Interface(
        spotify_bus, "org.freedesktop.DBus.Properties")
    metadata = spotify_properties.Get(
        "org.mpris.MediaPlayer2.Player", "Metadata")

    artist = metadata['xesam:artist'][0]
    song = metadata['xesam:title']
    song = re.sub('(\s+)-(.+)', '', song)
    song = re.sub('\(feat.+\)', '', song).strip()

    return remove_accents(artist + ' - ' + song)


def transform_song_name(song_name):
    song_name = song_name.lower()
    song_name = song_name.replace(' - ', '-')
    song_name = song_name.replace('. ', '-')
    song_name = song_name.replace('/', '-')
    song_name = song_name.replace(' & ', ' and ')
    song_name = song_name.replace(' ', '-')
    song_name = re.sub("[^a-z0-9-]", '', song_name)
    return song_name


class AppURLOpener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"

    def http_error_default(self, url, fp, errorcode, errormessage, headers):
        if errorcode == 403:
            raise ValueError("403")
        return super(AppURLOpener, self).http_error_default(url, fp, errorcode, errormessage, headers)


def open_genius(song_name):
    song_name = transform_song_name(song_name)
    page_url = 'https://genius.com/' + song_name + "-lyrics"

    page = AppURLOpener().open(page_url)
    return (BeautifulSoup(page, 'html.parser'), page_url)


def get_page_lyrics(soup):
    full_text = soup.select('div.song_body-lyrics')[0].text

    text = full_text.replace('More on Genius', '').strip()
    text = re.sub("\n\n(\n+)", "\n\n", text)
    return text


try:
    args = sys.argv[1:]
    if len(args) == 0:
        song_name = get_current_song_name()
    else:
        song_name = ' '.join(map(str, sys.argv[1:]))

    print("\n\t" + song_name + "\n")

    (soup, url) = open_genius(song_name)

    text = get_page_lyrics(soup)

    os.system('clear')
    print(text)
except Exception as e:
    print("Could not get lyrics:")
    print('No lyrics for this song on Genius' if str(
        e) == 'read of closed file' else e)
