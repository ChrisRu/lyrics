import unicodedata
import re
import requests
from requests.utils import requote_uri
from bs4 import BeautifulSoup
import lxml
import cchardet

session = requests.Session()
headers = {"User-agent": "Mozilla/5.0"}


def search_genius_for_lyrics(lyrics):
    lyrics = re.sub(r"\s+", "+", lyrics)
    lyrics = requote_uri(lyrics, safe="+")

    page_url = f"https://genius.com/api/search/multi?q={lyrics}"
    response = session.get(page_url, headers=headers).json()

    name_matches = []
    lyric_matches = []
    other_matches = []
    for hit in response["response"]["sections"][0]["hits"]:
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
    song_name = re.sub(r"(\s+)-(.+)", "", song_name)
    song_name = re.sub(r"\(feat.+\)", "", song_name).strip()
    song_name = song_name.replace(" . ", "-")
    song_name = song_name.replace(". ", "-")
    song_name = song_name.replace(" / ", "-")
    song_name = song_name.replace("/", "-")
    song_name = song_name.replace("^", "-")
    song_name = song_name.replace(" & ", " and ")
    song_name = song_name.replace(" ", "-")
    song_name = re.sub(r"[^a-z0-9-]", "", song_name)
    song_name = re.sub(r"-lyrics$", "", song_name)
    song_name = song_name.title()

    return song_name + "-lyrics"


def open_genius_page(song_name):
    song_location = transform_song_name_to_location(song_name)
    page_url = f"https://genius.com/{song_location}"
    response = session.get(page_url, headers=headers)

    return BeautifulSoup(response.text, "lxml")


def get_page_title(page):
    song_name_elements = page.select(
        "#application h1[class*=SongHeader__Title]")
    song_artist_elements = page.select(
        "#application a[class*=SongHeader__Artist]")

    if (len(song_name_elements) == 0):
        song_name_elements = page.select(
            "h1.header_with_cover_art-primary_info-title")
    if (len(song_artist_elements) == 0):
        song_artist_elements = page.select(
            "h2 a.header_with_cover_art-primary_info-primary_artist")

    if (len(song_name_elements) == 0 or len(song_artist_elements) == 0):
        return None

    song_artist = song_artist_elements[0].text
    song_name = song_name_elements[0].text
    return f"{song_artist} - {song_name}"


def get_page_lyrics(page):
    full_text_elements = page.select(
        "#application div[class*=Lyrics__Container]")
    if (len(full_text_elements) > 0):
        text = '\n'.join([str(f) for f in full_text_elements])
        text = text.replace('<br/>', '\n')
        text = BeautifulSoup(text, "lxml").text
        text = text.replace("More on Genius", "").strip()
        return text

    full_text_elements = page.select("div.lyrics")
    if (len(full_text_elements) > 0):
        text = full_text_elements[0].text
        text = text.replace("More on Genius", "").strip()
        text = re.sub(r"\n\n(\n+)", "\n\n", text)
        return text

    return None
