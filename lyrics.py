#!/usr/bin/env python3
import re
import unicodedata
import sys
import os
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from SwSpotify import spotify


class style:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'


def remove_accents(input):
    nkfd_form = unicodedata.normalize("NFKD", input)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


def get_current_song_name():
    return " - ".join(spotify.current()[::-1])


def transform_song_name(song_name):
    song_name = song_name.lower()
    song_name = remove_accents(song_name)
    song_name = song_name.replace(" - ", '-', 1)
    song_name = re.sub("(\s+)-(.+)", '', song_name)
    song_name = re.sub("\(feat.+\)", '', song_name).strip()
    song_name = song_name.replace(". ", '-')
    song_name = song_name.replace("/", '-')
    song_name = song_name.replace(" & ", ' and ')
    song_name = song_name.replace(" ", '-')
    song_name = re.sub("[^a-z0-9-]", "", song_name)

    return song_name


def open_genius_page(song_name):
    song_name = transform_song_name(song_name)

    page_url = f"https://genius.com/{song_name}-lyrics"
    request = Request(page_url, headers={"User-agent": 'Mozilla/5.0'})
    page = urlopen(request)

    return BeautifulSoup(page, "html.parser")


def get_page_lyrics(page):
    full_text = page.select("div.lyrics")[0].text

    text = full_text.replace("More on Genius", '').strip()
    text = re.sub("\n\n(\n+)", "\n\n", text)
    return text


def clear_terminal():
    print(chr(27) + "[2J")


def highlight_title(title):
    if os.name != 'nt':
        return f"{color.CYAN}{style.BOLD}{style.UNDERLINE}{title}{style.END}"
    return title


def highlight_text(text):
    if os.name != 'nt':
        text = text.replace("[", f"{style.BOLD}{color.BLUE}[")
        text = text.replace("]", f"]{style.END}")
        text = text.replace("(", f"{color.PURPLE}(")
        text = text.replace(")", f"){style.END}")
    return text


try:
    args = sys.argv[1:]
    if len(args) == 0:
        song_name = get_current_song_name()
    else:
        song_name = " ".join(map(str, sys.argv[1:]))

    clear_terminal()
    print(f"\n\t{highlight_title(song_name)}\n")

    page = open_genius_page(song_name)
    text = get_page_lyrics(page)

    clear_terminal()
    print(highlight_title(song_name))
    print("\n")
    print(highlight_text(text))
except Exception as e:
    print("Could not get lyrics:")
    print("No lyrics for this song on Genius" if str(
        e) == "read of closed file" else e)
