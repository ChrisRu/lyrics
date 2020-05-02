#!/usr/bin/env python3
import argparse
import time
from SwSpotify import spotify
from lib.render import print_text, fetch_and_render


indent = "  "
watch_timeout = 3


def get_cli_args():
    parser = argparse.ArgumentParser(
        description="Get the lyrics from a Spotify song in the terminal")
    parser.version = "1.2.0"
    parser.add_argument("song_lyrics", nargs="?", type=str,
                        help="song name, or part of the lyrics of a song to find the lyrics for")
    parser.add_argument("-w", "--watch", "-c", "--continuous", action="store_true",
                        help="watches for song changes and automatically fetches the new song lyrics")
    parser.add_argument("-v", "--version", action="version")
    return parser.parse_args()


try:
    args = get_cli_args()

    if args.song_lyrics:
        fetch_and_render(args.song_lyrics, True, indent)
    else:
        previous_song_name = ""
        while True:
            current_song_name = " - ".join(spotify.current()[::-1])
            if previous_song_name != current_song_name:
                previous_song_name = current_song_name
                fetch_and_render(current_song_name, False, indent)
            if not args.watch:
                break
            time.sleep(watch_timeout)
except KeyboardInterrupt:
    pass
except ValueError:
    print()
    print_text("No song found with those lyrics", indent)
    print()
except Exception as exception:
    print()
    print_text(str(exception), indent)
    print()
