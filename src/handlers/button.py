from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from state import state
from extra import finalize_audio_with_ffmpeg, send_audio_info, CustomAudio


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    cancel_button = [
        [InlineKeyboardButton("cancel", callback_data="cancel")],
    ]
    reply_markup = InlineKeyboardMarkup(cancel_button)

    if data == "file_name":
        state.set_task(user_id, "file_name")
        await update.callback_query.message.delete()
        reply_msg = await update.callback_query.message.reply_text(
            "Kirim nama file yang baru", reply_markup=reply_markup
        )
        state.set_msgs_to_delete(user_id, [reply_msg.message_id])

    elif data == "title":
        state.set_task(user_id, "title")
        await update.callback_query.message.delete()
        reply_msg = await update.callback_query.message.reply_text(
            "Kirim judul yang baru", reply_markup=reply_markup
        )
        state.set_msgs_to_delete(user_id, [reply_msg.message_id])

    elif data == "performer":
        state.set_task(user_id, "performer")
        await update.callback_query.message.delete()
        reply_msg = await update.callback_query.message.reply_text(
            "Kirim nama artist yang baru", reply_markup=reply_markup
        )
        state.set_msgs_to_delete(user_id, [reply_msg.message_id])

    elif data == "photo":
        state.set_task(user_id, "photo")
        await update.callback_query.message.delete()
        reply_msg = await update.callback_query.message.reply_text(
            "Kirim cover art yang baru", reply_markup=reply_markup
        )
        state.set_msgs_to_delete(user_id, [reply_msg.message_id])

    elif data == "finish":
        await update.callback_query.message.delete()
        # probably will caused bugs, since we reply after deleting the update.callback_query.message
        # but we will just leave it for now, and see if it works
        audio_path, cover_path = finalize_audio_with_ffmpeg(user_id)
        if not audio_path:
            print(f"Error finalizing audio for user_id {user_id}")
            return

        user_state = state.get_state(user_id)

        if not user_state:
            print(f"No state found for user_id {user_id}")
            return

        print(f"Cover path: {cover_path}")

        await update.callback_query.message.reply_audio(
            audio=open(audio_path, "rb"),
            caption="@YsirskyMusic_Bot",
            performer=user_state.performer,
            title=user_state.title,
            thumbnail=cover_path,
            # the thumbnail is not working, so we just leave it for now
            # okay, the ffmpeg one is working, but only thumbnail telegram not working
            # prolly can fix by just send audio, with the thumb parameter,
            # and also we should sent all params
        )
        state.clear_state(user_id)

    elif data == "cancel":
        user_state = state.get_state(user_id)
        if user_state:
            user_state.task = None
            state.set_state(user_id, user_state)
            all_msg_ids = [update.callback_query.message.message_id]

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

    else:
        pass

    # https://github.com/python-telegram-bot/python-telegram-bot/blob/c34e19edfdaaf7e592fbbef6c0fc3b470c519f0e/examples/inlinekeyboard.py#L43
    await query.answer()
