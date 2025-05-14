from telegram import (
    Audio,
    PhotoSize,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from typing import Sequence
from dataclasses import dataclass
from state import state
from mutagen import File
from mutagen.mp4 import MP4, MP4Cover
from tinytag import TinyTag
import re
import io
import os
import subprocess
import tempfile


def format_object(obj: object, properties: Sequence[str]) -> str:
    result_lines = []
    for prop in properties:
        value = getattr(obj, prop, None)
        line = f"{prop}: {'' if value is None else value}"
        result_lines.append(line)
    return "\n".join(result_lines)


def extract_song_name(text: str) -> str | None:
    match = re.search(r'Downloaded\s+"([^"]+)"', text)
    if match:
        return match.group(1)

    match = re.search(r"at\s+'([^']+\.mp3)'", text, flags=re.DOTALL)
    if match:
        raw_path = match.group(1)

        # Remove the "downloader.py:506" logging artifact
        print(f"Raw path: {raw_path}")
        cleaned_path = re.sub(r"\w+\.py:\d+", "", raw_path)

        # Remove newlines and tabs
        print(f"Cleaned path: {cleaned_path}")
        cleaned_path = cleaned_path.replace("\n", " ").replace("\t", " ")

        # Collapse multiple spaces into a single space
        print(f"Collapsed path: {cleaned_path}")
        cleaned_path = re.sub(r" {2,}", " ", cleaned_path)

        # Trim leading/trailing spaces
        print(f"Trimmed path: {cleaned_path}")
        cleaned_path = cleaned_path.strip()

        # Extract file name from full path
        file_name = os.path.basename(cleaned_path)
        file_name = os.path.splitext(file_name)[0]

        return file_name

    return None


async def download_tg_audio(audio: Audio) -> str:
    # audio.file_name from telegram already contains extension
    file_path = os.path.join(os.path.abspath("music"), f"{audio.file_name}")
    audio_file = await audio.get_file()
    await audio_file.download_to_drive(file_path)

    return file_path


async def download_tg_photo(photo: PhotoSize) -> str:
    file_path = tempfile.mktemp(suffix=".jpg")
    photo_file = await photo.get_file()
    await photo_file.download_to_drive(file_path)

    return file_path


def extract_cover_image(file_path: str) -> bytes | None:
    try:
        tag = TinyTag.get(filename=file_path, image=True)
        image_data = tag.images.any

        if image_data:
            return image_data.data
        else:
            return None

    except Exception as e:
        print(f"An error occurred with tinytag: {e}")
        return None


@dataclass
class CustomAudio:
    path: str
    thumb_buf: io.BytesIO | None = None
    file_name: str | None = None
    title: str | None = None
    performer: str | None = None


async def send_audio_info(update: Update, audio: CustomAudio):
    message = update.message if update.message else update.callback_query.message
    audio_info = format_object(audio, ["file_name", "title", "performer"])

    keyboard = [
        [
            InlineKeyboardButton("file_name", callback_data="file_name"),
            InlineKeyboardButton("title", callback_data="title"),
        ],
        [
            InlineKeyboardButton("performer", callback_data="performer"),
            InlineKeyboardButton("photo", callback_data="photo"),
        ],
        [InlineKeyboardButton("finish", callback_data="finish")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if audio.thumb_buf:
        await message.reply_photo(
            photo=audio.thumb_buf,
            caption=f"Audio info:\n\n{audio_info}",
            reply_markup=reply_markup,
        )
    else:
        await message.reply_text(
            f"Audio info:\n\n{audio_info}", reply_markup=reply_markup
        )


# def finalize_audio_with_ffmpeg(user_id: int) -> tuple[str | None, str | None]:
#     user_state = state.get_state(user_id)
#     if not user_state:
#         print(f"No state found for user_id {user_id}")
#         return None, None

#     input_path = user_state.audio_path
#     output_path = tempfile.mktemp(suffix=os.path.splitext(input_path)[1])

#     print(f"Input path: {input_path}")
#     print(f"Output path: {output_path}")

#     # Prepare metadata
#     metadata_args = []
#     if user_state.title:
#         metadata_args += ["-metadata", f"title={user_state.title}"]
#     if user_state.performer:
#         metadata_args += ["-metadata", f"artist={user_state.performer}"]

#     # Cover art image handling
#     cover_args = []
#     cover_path = None
#     if user_state.thumb_buf:
#         cover_path = tempfile.mktemp(suffix=".jpg")
#         with open(cover_path, "wb") as f:
#             f.write(user_state.thumb_buf)

#         cover_args = [
#             "-i",
#             cover_path,  # Add image as second input
#             "-map",
#             "0:a",  # Use audio stream from input 0
#             "-map",
#             "1:v",  # Use video (image) stream from input 1
#             "-c",
#             "copy",  # No re-encoding
#             "-id3v2_version",
#             "3",  # Needed for image embedding in ID3
#             "-metadata:s:v",
#             'title="Album cover"',
#             "-metadata:s:v",
#             'comment="Cover (front)"',
#         ]

#     else:
#         cover_args = []

#     # FFmpeg command
#     cmd = ["ffmpeg", "-y", "-i", input_path, *cover_args, *metadata_args, output_path]

#     try:
#         subprocess.run(cmd, check=True)
#         print(f"Metadata and cover art embedded successfully to: {output_path}")
#         return output_path, cover_path

#     except subprocess.CalledProcessError as e:
#         print(f"FFmpeg error: {e}")
#         return None, None


def finalize_audio_with_ffmpeg(user_id: int) -> tuple[str | None, str | None]:
    user_state = state.get_state(user_id)
    if not user_state:
        print(f"No state found for user_id {user_id}")
        return None, None

    input_path = user_state.audio_path
    output_ext = os.path.splitext(input_path)[1].lower()
    output_path = tempfile.mktemp(suffix=output_ext)

    print(f"Input path: {input_path}")
    print(f"Output path: {output_path}")

    # Prepare metadata
    metadata_args = []
    if user_state.title:
        metadata_args += ["-metadata", f"title={user_state.title}"]
    if user_state.performer:
        metadata_args += ["-metadata", f"artist={user_state.performer}"]

    # Cover art image handling
    cover_args = []
    cover_path = None
    if user_state.thumb_buf:
        cover_path = tempfile.mktemp(suffix=".jpg")
        with open(cover_path, "wb") as f:
            f.write(user_state.thumb_buf)

        if output_ext == ".mp3":
            # MP3 with ID3 image
            cover_args = [
                "-i",
                cover_path,
                "-map",
                "0:a",
                "-map",
                "1:v",
                "-c",
                "copy",
                "-id3v2_version",
                "3",
                "-metadata:s:v",
                "title=Album cover",
                "-metadata:s:v",
                "comment=Cover (front)",
            ]
        elif output_ext == ".m4a":
            # M4A (MP4 container) with image
            cover_args = [
                "-i",
                cover_path,
                "-map",
                "0:a",
                "-map",
                "1:v",
                "-c:a",
                "copy",
                "-c:v",
                "mjpeg",  # or "libx264" if jpeg fails
                "-disposition:v",
                "attached_pic",
            ]

    # FFmpeg command
    cmd = ["ffmpeg", "-y", "-i", input_path, *cover_args, *metadata_args, output_path]

    try:
        subprocess.run(cmd, check=True)
        print(f"Metadata and cover art embedded successfully to: {output_path}")
        return output_path, cover_path

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        return None, None
