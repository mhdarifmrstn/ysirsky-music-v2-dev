from telegram import Update
from telegram.ext import ContextTypes
from state import state
import time


async def uptime_handler(update: Update, context: ContextTypes):
    uptime_total = abs(time.time() - state.start_time)
    uptime_hours = int(uptime_total // 3600)
    uptime_total -= uptime_hours * 3600
    uptime_minutes = int((uptime_total // 60) % 60)
    uptime_total -= uptime_minutes * 60
    uptime_seconds = round(uptime_total % 60)

    if uptime_hours != 0 and uptime_minutes != 0:
        uptime_message = f"{uptime_hours}h {uptime_minutes}m {uptime_seconds}s"
    elif uptime_hours == 0 and uptime_minutes != 0:
        uptime_message = f"{uptime_minutes}m {uptime_seconds}s"
    else:
        uptime_message = f"{uptime_seconds}s"

    await update.message.reply_text(uptime_message)
