from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
)
from handlers.start import start_handler
from handlers.uptime import uptime_handler
from handlers.audio import audio_handler
from handlers.photo import photo_handler
from handlers.download import download_handler
from handlers.button import button_handler
from dotenv import load_dotenv
from os import getenv
import nest_asyncio

# currently our spotdl downloader resulting an error
# RuntimeError: This event loop is already running
# so we try to solve it by doing this
# https://stackoverflow.com/a/56434301
nest_asyncio.apply()

load_dotenv()

token = getenv("BOT_TOKEN")
app = ApplicationBuilder().token(token).build()

app.add_handler(CommandHandler("start", start_handler))
app.add_handler(CommandHandler("uptime", uptime_handler))
app.add_handler(MessageHandler(filters.AUDIO, audio_handler))
app.add_handler(MessageHandler(filters.TEXT, download_handler))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.add_handler(CallbackQueryHandler(button_handler))


async def set_commands(app):
    await app.bot.set_my_commands(
        [
            ("start", "untuk mulai botnya"),
            ("uptime", "lihat udah brp lama bot nya jalan"),
        ]
    )


app.post_init = set_commands

app.run_polling()
