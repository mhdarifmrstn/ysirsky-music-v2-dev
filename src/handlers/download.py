from telegram import Update
from telegram.ext import ContextTypes
from extra import send_audio_info, CustomAudio
from music import music
from state import state


async def download_handler(update: Update, context: ContextTypes):
    user_id = update.message.from_user.id
    user_state = state.get_state(user_id)

    if user_state:
        if user_state.task == "file_name":
            new_file_name = update.message.text
            user_state.file_name = new_file_name

        elif user_state.task == "title":
            new_title = update.message.text
            user_state.title = new_title

        elif user_state.task == "performer":
            new_performer = update.message.text
            user_state.performer = new_performer

        state.set_task(user_id, None)
        state.set_state(user_id, user_state)

        all_msg_ids = [update.message.id] + user_state.msgs_to_delete
        await update._bot.delete_messages(user_id, all_msg_ids)

        await send_audio_info(
            update,
            CustomAudio(
                user_state.audio_path,
                user_state.thumb_buf,
                user_state.file_name,
                user_state.title,
                user_state.performer,
            ),
        )

        return

    query = update.message.text

    if not query:
        return

    waiting_message = await update.message.reply_text("Downloading...")
    songs = music.search(query)

    if len(songs) > 1:
        await waiting_message.edit_text(
            f"Berhasil mendapatkan {len(songs)} lagu, sedang mendownload.."
        )

    for _, file_path in music.download(songs):
        if not file_path:
            await update.message.reply_text("Error downloading the file.")

        await update.message.reply_audio(
            audio=open(file_path, "rb"), caption="@YsirskyMusic_Bot"
        )

    if len(songs) > 1:
        await update.message.reply_text("Done")
