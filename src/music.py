from spotdl import Spotdl
from spotdl.types.song import Song
from typing import Generator
import os

# https://github.com/spotDL/spotify-downloader/blob/a3163302c3032e8310dfee4dae5fe2490f0910a4/spotdl/utils/config.py#L296-L297
s = Spotdl(
    client_id="5f573c9620494bae87890c0f08a60293",
    client_secret="212476d9b0f3472eaa762d90b19b0ba8",
)


class Music:
    def __init__(self):
        self.music_dir = os.path.abspath("music")

    def search(self, query: str) -> list:
        """Search for songs and return the list of results."""
        songs: list[Song] = s.search([query])
        return songs

    def download(self, songs: list) -> Generator[str, None, None]:
        """Download songs one by one, yielding the file path for each."""
        for song in songs:
            file_path = s.download(song)
            yield file_path


music = Music()
