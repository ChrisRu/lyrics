#!/usr/bin/env python3
import argparse
import time
from SwSpotify import spotify
from lib.render import print_text, write_title, fetch_and_render, clear_terminal


name = "lyrics"
description = "Get the lyrics from a Spotify song in the terminal"
__version__ = "1.2.4"


watch_timeout = 3


def get_cli_args():
    parser = argparse.ArgumentParser(prog=name, description=description)
    parser.version = __version__
    parser.add_argument("song_lyrics", nargs="*", type=str,
                        help="song name, or part of the lyrics of a song to find the lyrics for")
    parser.add_argument("-w", "--watch", "-c", "--continuous", action="store_true",
                        help="watches for song changes and automatically fetches the new song lyrics")
    parser.add_argument("-v", "--version", action="version")
    return parser.parse_args()


def execute():
    try:
        write_title("lyrics")
        args = get_cli_args()

        if len(args.song_lyrics) > 0:
            fetch_and_render(" ".join(args.song_lyrics), True)
        elif args.watch:
            previous_song_name = None
            current_song_name = None
            while True:
                try:
                    current_song_name = " - ".join(spotify.current()[::-1])
                except Exception:
                    previous_song_name = None
                    current_song_name = None

                    write_title("lyrics")
                    clear_terminal()
                    print_text("\nNothing is playing at the moment.\n")
                if current_song_name is not None and previous_song_name != current_song_name:
                    previous_song_name = current_song_name
                    write_title(f"lyrics | {current_song_name}")
                    fetch_and_render(current_song_name, False)
                time.sleep(watch_timeout)
        else:
            song_name = " - ".join(spotify.current()[::-1])
            fetch_and_render(song_name, False)
    except KeyboardInterrupt:
        pass
    except ValueError:
        print_text("\nNo song found with those lyrics\n")
    except Exception as exception:
        print_text(f"\n{exception}\n")


if __name__ == "__main__":
    execute()
