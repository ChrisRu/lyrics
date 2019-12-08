#!/usr/bin/env python3
import re
import unicodedata
import sys
import time
import os
import threading
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

    def stop(self):
        self._stopevent.set()

    def _spin(self):
        while not self._stopevent.isSet():
            for t in '|/-\\':
                sys.stdout.write(indent + t + indent)
                sys.stdout.flush()
                time.sleep(self._speed)
                sys.stdout.write('\b' * (len(indent) * 2 + 1))
        sys.stdout.flush()


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

    return song_name


def open_genius_page(song_name):
    song_name = transform_song_name(song_name)

    page_url = f"https://genius.com/{song_name}-lyrics"
    request = Request(page_url, headers={"User-agent": "Mozilla/5.0"})
    page = urlopen(request)

    return BeautifulSoup(page, "html.parser")


def get_page_lyrics(page):
    full_text = page.select("div.lyrics")[0].text

    text = full_text.replace("More on Genius", "").strip()
    text = re.sub("\n\n(\n+)", "\n\n", text)
    return text


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


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

    try:
        spinner_thread = SpinnerThread()
        spinner_thread.start()

        page = open_genius_page(song_name)
        text = get_page_lyrics(page)

        spinner_thread.stop()

        clear_terminal()

        print()
        print_text(highlight_title(song_name))
        print()
        print_text(highlight_text(text))
        print()
    except Exception as e:
        e = str(e)
        if e in errors:
            print_text(f"{errors[e]}")
        else:
            print_text("Could not get lyrics:")
            print_text(e)
        print("\n")


try:
    song_name = ""

    if len(sys.argv) > 1:
        if sys.argv[1] in ("--help", "-h"):
            print(
                (
                    "\n"
                    "USAGE:"
                    "\n\tlyrics [options...] <songname>"
                    "\n"
                    "\n\t<songname> is optional, if not included lyrics will try to"
                    "\n\tget the current song playing on spotify"
                    "\n\n"
                    "FLAGS:"
                    "\n\t-w, --watch\twatches for song changes and automatically"
                    "\n\t           \tfetches the new song lyrics"
                    "\n"
                    "\n\t-h, --help\tshows this help screen"
                    "\n"
                )
            )
        elif sys.argv[1] in ("--watch", "-w"):
            while True:
                new_song_name = get_current_song_name()
                if song_name != new_song_name:
                    song_name = new_song_name
                    fetch_and_render(song_name)
                time.sleep(watch_timeout)
        else:
            song_name = " ".join(map(str, sys.argv[1:]))
            fetch_and_render(song_name)
    else:
        song_name = get_current_song_name()
        fetch_and_render(song_name)

except KeyboardInterrupt:
    sys.exit()
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
