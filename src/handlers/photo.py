from telegram import Update
from telegram.ext import ContextTypes
from extra import download_tg_photo, send_audio_info, CustomAudio
from state import state


async def photo_handler(update: Update, context: ContextTypes):
    try:
        user_id = update.message.from_user.id
        user_state = state.get_state(user_id)

        if not user_state:
            return

        if not user_state.task == "photo":
            return

        photo = update.message.photo[-1]
        photo_path = await download_tg_photo(photo)

        with open(photo_path, "rb") as f:
            photo_buf = f.read()

        user_state.thumb_buf = photo_buf
        state.set_task(user_id, None)
        state.set_state(user_id, user_state)

        await update.message.delete()
        await update._bot.delete_messages(user_id, user_state.msgs_to_delete)

        await send_audio_info(
            update,
            CustomAudio(
                user_state.audio_path,
                photo_buf,
                user_state.file_name,
                user_state.title,
                user_state.performer,
            ),
        )

    except Exception as error:
        print(f"Error in photo_handler: {error}")
        await update.message.reply_text("cb kirim ulang.. klo gabisa berarti error")
