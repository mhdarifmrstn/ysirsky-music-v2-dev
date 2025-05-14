from extra import extract_song_name
import os
import subprocess
import uuid


class Music:
    def __init__(self):
        self.bin_path = os.path.abspath(".venv") + "/bin"
        self.music_dir = os.path.abspath("music")

    def download(self, query: str):
        file_name = uuid.uuid4().hex
        path_without_ext = os.path.join(self.music_dir, file_name)
        ext = "{output-ext}"

        command = [
            self.bin_path + "/spotdl",
            f'"{query}"',
            "--output",
            f"{path_without_ext}." + ext,
            "--log-level=DEBUG",  # for testing purposes
        ]
        print(f"Executing command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)

        print(f"Command output: {result.stdout}")

        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        else:
            file_path = os.path.join(path_without_ext + ".mp3")
            print(f"File path: {file_path}")

            return file_path


music = Music()
