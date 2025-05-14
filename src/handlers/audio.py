from telegram import Update
from telegram.ext import ContextTypes
from extra import download_tg_audio, extract_cover_image, send_audio_info, CustomAudio
from state import state, UserState


async def audio_handler(update: Update, context: ContextTypes):
    try:
        audio = update.message.audio
        waiting_message = await update.message.reply_text("Downloading...")
        audio_path = await download_tg_audio(audio)
        thumb_buf = extract_cover_image(audio_path)

        await waiting_message.delete()
        await send_audio_info(
            update,
            CustomAudio(
                audio_path, thumb_buf, audio.file_name, audio.title, audio.performer
            ),
        )

        user_id = update.message.from_user.id

        state.set_state(
            user_id,
            UserState(
                user_id=user_id,
                audio=audio,
                audio_path=audio_path,
                thumb_buf=thumb_buf,
                task=None,
                file_name=audio.file_name,
                title=audio.title,
                performer=audio.performer,
            ),
        )

    except Exception as error:
        print(f"Error in audio_handler: {error}")
        await update.message.reply_text("cb kirim ulang.. klo gabisa berarti error")
