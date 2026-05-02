from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

_COMMANDS = """
/now [city] — current conditions
/today [city] — hourly forecast for today
/forecast [city] [day] — hourly forecast for any day
/week [city] — 7-day summary
/cycle [city] [day] [morning|noon|evening|night] — cycling breakdown with verdict
/cyclenow [city] — cycling verdict for right now
/schedule — manage daily forecast schedule
/add [city] — add a location
/remove — remove a saved location
/locations — list saved locations"""


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    locs = context.user_data.get("locations", [])
    if not locs:
        await update.message.reply_text(
            f"Welcome, {name}! 🚴\n\n"
            "I send you a daily weather forecast and let you check conditions on demand.\n"
            f"\nCommands:{_COMMANDS}\n\n"
            "Add your first location with /add [city], then set up a daily forecast with /schedule."
        )
    else:
        await update.message.reply_text(
            f"Welcome back, {name}! 🚴\n"
            f"{_COMMANDS}"
        )


bot_handlers = [CommandHandler("start", start_cmd)]

commands = [("start", "Show all commands")]
