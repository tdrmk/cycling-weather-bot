import os
from pathlib import Path
from warnings import filterwarnings
from dotenv import load_dotenv
from telegram.warnings import PTBUserWarning

# PTB warns when a ConversationHandler contains a CallbackQueryHandler with the default
# per_message=False setting. This is intentional — our conversations mix MessageHandler
# and CallbackQueryHandler, so per_message=False is correct. Muting the noise.
filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

from telegram.ext import Application, PicklePersistence
from location_handlers import location_handlers, commands as location_commands
from weather_handlers import weather_handlers, commands as weather_commands
from cycle_handlers import cycle_handlers, commands as cycle_commands
from bot_handlers import bot_handlers

load_dotenv()

TOKEN = os.getenv("TOKEN")


async def post_init(app):
    await app.bot.set_my_commands(location_commands + weather_commands + cycle_commands)


if __name__ == "__main__":
    Path("data").mkdir(exist_ok=True)
    persistence = PicklePersistence(filepath="data/bot_data")
    app = Application.builder().token(TOKEN).persistence(persistence).post_init(post_init).build()
    for h in bot_handlers:
        app.add_handler(h)
    for h in location_handlers:
        app.add_handler(h)
    for h in weather_handlers:
        app.add_handler(h)
    for h in cycle_handlers:
        app.add_handler(h)
    print("Bot running")
    app.run_polling()
