# Lyrics

Get the lyrics to songs right in your terminal.

![lyrics example](example.png)

## CLI

- `lyrics` to display the lyrics of the currently playing song on Spotify
- `lyrics "The Beatles - Blackbird"` for getting lyrics for a specific song
- `lyrics "Can't you see im trying"` for finding the song based on it's lyrics
- `lyrics --watch` to stay open and update the lyrics when you get to the next song
  - Alternatively `-w`, `--continuous`, or `-c`
- `lyrics --version` to get the current version
  - Alternatively `-v`
- `lyrics --help` to show what commands are available
  - Alternatively `-h`

## Support

This script should support Linux, MacOS and Windows. Color highlighting is unfortunately not supported on Windows (you're welcome to add this in a pull request 😀 ).

## Installation

### Requirements

Requires Python 3 with pip installed.

### Dependencies

Install the packages from the requirement.txt document with pip:

`$ pip install -r ./requirements.txt --user`

### Execute from anywhere

Then you can add a link to your bin so the lyrics can be executed from anywhere in the terminal:

`$ ln -s ./lyrics/__main__.py /usr/local/bin/lyrics`.

(The `/usr/local/bin` path will have to be in your `$PATH` variable)
