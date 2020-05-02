from urllib.parse import quote
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import re
import json


def search_genius_for_lyrics(lyrics):
    lyrics = re.sub("\s+", "+", lyrics)
    lyrics = quote(lyrics, safe="+")

    page_url = f"https://genius.com/api/search/multi?q={lyrics}"
    request = Request(page_url, headers={"User-agent": "Mozilla/5.0"})
    response = urlopen(request)

    data = json.load(response)

    name_matches = []
    lyric_matches = []
    other_matches = []
    for hit in data['response']['sections'][0]['hits']:
        if 'path' not in hit['result']:
            continue

        path = hit['result']['path'][1:]
        if hit['index'] == 'lyric':
            lyric_matches.append(path)
        elif hit['index'] == 'song':
            name_matches.append(path)
        else:
            other_matches.append(path)

    if len(name_matches) > 0:
        return name_matches[0]

    if len(lyric_matches) > 0:
        return lyric_matches[0]

    if len(other_matches) > 0:
        return other_matches[0]

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
