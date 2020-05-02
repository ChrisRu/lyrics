#!/usr/bin/env python3
import unicodedata
import os
import argparse
import time
import re
from SwSpotify import spotify
from lib.spinner import SpinnerThread
from lib.highlight import highlight_text, highlight_title
from lib.fetch import get_page_lyrics, get_page_title, open_genius_page, search_genius_for_lyrics


indent = "  "
watch_timeout = 3


def transform_song_name(song_name):
    song_name = song_name.lower()
    song_name = u"".join([c for c in unicodedata.normalize(
        "NFKD", song_name) if not unicodedata.combining(c)])
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


def clear_terminal():
    if os.name == 'nt':
        os.system('cls')
    else:
        print(chr(27) + '[2J')
        print(chr(27) + "[3J")


def print_text(text):
    text = text.replace("\n", "\n" + indent)
    print(indent + text)


def fetch_and_render(song_name, pretty_song_name=None):
    clear_terminal()

    print()
    print_text(highlight_title(
        pretty_song_name if pretty_song_name is not None else song_name))
    print()

    spinner_thread = SpinnerThread(indent)
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

        errors = {
            "HTTP Error 404: Not Found": "No lyrics for this song on Genius",
            "read of closed file": "No lyrics for this song on Genius",
        }

        message = str(e)

        print()
        print_text("Could not get lyrics:")
        print_text(errors[message] if message in errors else message)
        print()


def get_cli_args():
    parser = argparse.ArgumentParser(
        description="Get the lyrics from a Spotify song in the terminal")
    parser.version = '1.2.0'
    parser.add_argument('song_name', nargs='?', type=str,
                        help='song name to get the lyrics for')
    parser.add_argument("-w", "--watch", "-c", "--continuous", action="store_true",
                        help='watches for song changes and automatically fetches the new song lyrics')
    parser.add_argument('-v', '--version', action='version')
    return parser.parse_args()


try:
    args = get_cli_args()

    if args.song_name:
        song_name = search_genius_for_lyrics(args.song_name)
        fetch_and_render(song_name)
    else:
        previous_song_name = ''
        while True:
            current_song_name = " - ".join(spotify.current()[::-1])
            if previous_song_name != current_song_name:
                previous_song_name = current_song_name
                fetch_and_render(transform_song_name(
                    current_song_name), current_song_name)
            if not args.watch:
                break
            time.sleep(watch_timeout)
except KeyboardInterrupt:
    pass
except ValueError:
    print()
    print_text("No song found with those lyrics")
    print()
except Exception as exception:
    print()
    print_text(str(exception))
    print()
