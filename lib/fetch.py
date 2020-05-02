import unicodedata
import re
import json
from urllib.parse import quote
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup


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
    for hit in data["response"]["sections"][0]["hits"]:
        if "path" not in hit["result"]:
            continue

        path = hit["result"]["path"][1:]
        if hit["index"] == "lyric":
            lyric_matches.append(path)
        elif hit["index"] == "song":
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


def transform_song_name_to_location(song_name):
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
    song_name = re.sub("-lyrics$", "", song_name)
    song_name = song_name.title()

    return song_name + "-lyrics"


def open_genius_page(song_name):
    song_location = transform_song_name_to_location(song_name)
    page_url = f"https://genius.com/{song_location}"
    request = Request(page_url, headers={
                      "User-agent": "Mozilla/5.0 (compatible)"})
    response = urlopen(request)

    return BeautifulSoup(response, "html.parser")


def get_page_title(page):
    song_name_elements = page.select(
        ".header_with_cover_art-primary_info-title")
    song_artist_elements = page.select(
        ".header_with_cover_art-primary_info-primary_artist")

    if (len(song_name_elements) == 0 or len(song_artist_elements) == 0):
        return None

    song_artist = song_artist_elements[0].text
    song_name = song_name_elements[0].text
    return f"{song_artist} - {song_name}"


def get_page_lyrics(page):
    full_text_elements = page.select("div.lyrics")

    if (len(full_text_elements) == 0):
        return None

    text = full_text_elements[0].text
    text = text.replace("More on Genius", "").strip()
    text = re.sub("\n\n(\n+)", "\n\n", text)

    return text
