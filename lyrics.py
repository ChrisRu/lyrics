#!/usr/bin/env python3
import re
import unicodedata
import sys
import time
import os
import threading
import argparse
import json
from urllib.parse import quote
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from SwSpotify import spotify, SpotifyPaused, SpotifyNotRunning, SpotifyClosed


indent = "  "
watch_timeout = 3


class style:
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


class color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"


class SpinnerThread(threading.Thread):
    def __init__(self, speed=0.15):
        super().__init__(target=self._spin)
        self.daemon = True
        self._stopevent = threading.Event()
        self._speed = speed
        self._written = False

    def stop(self):
        self._stopevent.set()
        if self._written:
            self._clear_spin()

    def _print_spin(self, char):
        message = indent + char + indent
        print(message, end='', file=sys.stdout, flush=True)
        self._written = True

    def _clear_spin(self):
        message = '\b' * (len(indent) * 2 + 1)
        print(message, end='', file=sys.stdout, flush=True)
        self._written = False

    def _spin(self):
        while not self._stopevent.isSet():
            for t in '|/-\\':
                self._print_spin(t)
                time.sleep(self._speed)

                if self._written and not self._stopevent.isSet():
                    self._clear_spin()

                if self._stopevent.isSet():
                    break


def remove_accents(input):
    nkfd_form = unicodedata.normalize("NFKD", input)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


def get_current_song_name():
    return " - ".join(spotify.current()[::-1])


def transform_song_name(song_name):
    song_name = song_name.lower()
    song_name = remove_accents(song_name)
    song_name = song_name.replace(" - ", "-", 1)
    song_name = re.sub("(\s+)-(.+)", "", song_name)
    song_name = re.sub("\(feat.+\)", "", song_name).strip()
    song_name = song_name.replace(" . ", "-")
    song_name = song_name.replace(". ", "-")
    song_name = song_name.replace(" / ", "-")
    song_name = song_name.replace("/", "-")
    song_name = song_name.replace("^", "-")
    song_name = song_name.replace(" & ", " and ")
    song_name = song_name.replace(" ", "-")
    song_name = re.sub("[^a-z0-9-]", "", song_name)
    song_name = song_name.title()

    return song_name + "-lyrics"


def search_genius_for_lyrics(lyrics):
    lyrics = re.sub("\s+", "+", lyrics)
    lyrics = quote(lyrics, safe="+")

    page_url = f"https://genius.com/api/search/multi?q={lyrics}"
    request = Request(page_url, headers={"User-agent": "Mozilla/5.0"})
    response = urlopen(request)

    data = json.load(response)

    hits = data['response']['sections'][0]['hits']

    for hit in hits:
        if hit['type'] == 'song':
            return hit['result']['path'][1:]

    raise ValueError("No song found")


def open_genius_page(song_location):
    page_url = f"https://genius.com/{song_location}"
    request = Request(page_url, headers={"User-agent": "Mozilla/5.0"})
    response = urlopen(request)

    return BeautifulSoup(response, "html.parser")


def get_page_title(page):
    song_name = page.select(
        ".header_with_cover_art-primary_info-title")[0].text
    song_artist = page.select(
        ".header_with_cover_art-primary_info-primary_artist")[0].text

    return f"{song_artist} - {song_name}"


def get_page_lyrics(page):
    full_text = page.select("div.lyrics")[0].text

    text = full_text.replace("More on Genius", "").strip()
    text = re.sub("\n\n(\n+)", "\n\n", text)

    return text


def clear_terminal():
    if os.name == 'nt':
        os.system('cls')
    else:
        print(chr(27) + '[2J')
        print(chr(27) + "[3J")


def highlight_title(title):
    if os.name == 'nt':
        return title

    return f"{color.CYAN}{style.BOLD}{style.UNDERLINE}{title}{style.END}"


def highlight_text(text):
    if os.name != 'nt':
        text = text.replace("[", f"{style.BOLD}{color.BLUE}[")
        text = text.replace("]", f"]{style.END}")
        text = text.replace("(", f"{color.PURPLE}(")
        text = text.replace(")", f"){style.END}")

    return text


errors = {
    "No song found": "No song found",
    "HTTP Error 404: Not Found": "No lyrics for this song on Genius",
    "read of closed file": "No lyrics for this song on Genius",
}


def print_text(text):
    text = text.replace("\n", "\n" + indent)
    print(indent + text)


def fetch_and_render(song_name):
    clear_terminal()

    print()
    print_text(highlight_title(song_name))
    print()

    spinner_thread = SpinnerThread()
    try:
        spinner_thread.start()

        page = open_genius_page(song_name)
        title = get_page_title(page)
        text = get_page_lyrics(page)

        spinner_thread.stop()

        clear_terminal()

        print()
        print_text(highlight_title(title))
        print()
        print_text(highlight_text(text))
        print()
    except Exception as e:
        spinner_thread.stop()

        message = str(e)
        print()
        if message in errors:
            print_text(f"{errors[message]}")
        else:
            print_text("Could not get lyrics:")
            print_text(message)
        print("")


def get_cli_args():
    parser = argparse.ArgumentParser(
        description="Get the lyrics from a Spotify song in the terminal")
    parser.version = '1.0.3'
    parser.add_argument('song_name', nargs='?', type=str,
                        help='song name to get the lyrics for')
    parser.add_argument("-w", "--watch", action="store_true",
                        help='watches for song changes and automatically fetches the new song lyrics')
    parser.add_argument('-v', '--version', action='version')
    return parser.parse_args()


try:
    args = get_cli_args()

    if args.song_name:
        song_name = search_genius_for_lyrics(args.song_name)
        fetch_and_render(song_name)
    elif args.watch:
        song_name = ''
        while True:
            new_song_name = get_current_song_name()
            if song_name != new_song_name:
                song_name = new_song_name
                fetch_and_render(transform_song_name(song_name))
            time.sleep(watch_timeout)
    else:
        song_name = get_current_song_name()
        fetch_and_render(transform_song_name(song_name))
except KeyboardInterrupt:
    pass
except ValueError:
    print()
    print_text("No song found with those lyrics")
    print()
except SpotifyPaused:
    print()
    print_text("Spotify doesn't appear to be playing at the moment")
    print()
except SpotifyClosed:
    print()
    print_text("Spotify appears to be closed at the moment")
    print()
except SpotifyNotRunning:
    print()
    print_text("Spotify appears not to be running")
    print()
