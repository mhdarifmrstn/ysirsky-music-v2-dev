from telegram import Update
from telegram.ext import ContextTypes


async def start_handler(update: Update, context: ContextTypes):
    await update.message.reply_text("Hai, kirim aja file atau nama lagu")
