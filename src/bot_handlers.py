from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

_COMMANDS = """
/now — current conditions
/today — hourly forecast for today
/forecast [day] — hourly forecast for any day
/week — 7-day summary
/cycle [day] [period] — cycling-specific breakdown with verdict"""


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    user = update.effective_user
    locs = context.user_data.get("locations", [])
    if not locs:
        await update.message.reply_text(
            f"Welcome, {name}! 🚴\n\n"
            "I send you a daily cycling weather forecast and let you check conditions on demand.\n"
            f"\nCommands:{_COMMANDS}\n\n"
            "Add your first location with /add [city] to get started."
        )
    else:
        await update.message.reply_text(
            f"Welcome back, {name}! 🚴\n"
            f"{_COMMANDS}"
        )


bot_handlers = [CommandHandler("start", start_cmd)]
