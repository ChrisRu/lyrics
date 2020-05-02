import os
import time
import re
from SwSpotify import spotify
from lib.spinner import SpinnerThread
from lib.highlight import highlight_text, highlight_title
from lib.fetch import get_page_lyrics, get_page_title, open_genius_page, search_genius_for_lyrics


def clear_terminal():
    if os.name == "nt":
        os.system("cls")
    else:
        print(chr(27) + "[2J")
        print(chr(27) + "[3J")


def print_text(text, indent="  "):
    text = text.replace("\n", "\n" + indent)
    print(indent + text)


def fetch_and_render(song_name, search_as_lyrics=False, indent="  "):
    try:
        spinner_thread = SpinnerThread(indent)

        if search_as_lyrics:
            clear_terminal()
            print()
            print_text(highlight_title("Searching..."))
            print()
            spinner_thread.start()

            song_name = search_genius_for_lyrics(song_name)

            spinner_thread.stop()

        clear_terminal()
        print()
        print_text(highlight_title(song_name))
        print()
        spinner_thread = SpinnerThread(indent)
        spinner_thread.start()

        page = open_genius_page(song_name)
        title = get_page_title(page)
        text = get_page_lyrics(page)

        if (title is None or text is None):
            raise ValueError(
                "Genius has some troubles with this request for unknown reasons")

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
