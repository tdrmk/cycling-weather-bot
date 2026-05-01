import os
from pathlib import Path
from warnings import filterwarnings
from dotenv import load_dotenv
from telegram.warnings import PTBUserWarning

# PTB warns when a ConversationHandler contains a CallbackQueryHandler with the default
# per_message=False setting. This is intentional — our conversations mix MessageHandler
# and CallbackQueryHandler, so per_message=False is correct. Muting the noise.
filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

from telegram import Update
from telegram.ext import Application, PicklePersistence, TypeHandler
from location_handlers import location_handlers, commands as location_commands
from weather_handlers import weather_handlers, commands as weather_commands
from cycle_handlers import cycle_handlers, commands as cycle_commands
from schedule_handlers import schedule_handlers, commands as schedule_commands
from bot_handlers import bot_handlers
from scheduled import register_jobs

load_dotenv()

TOKEN = os.getenv("TOKEN")


async def post_init(app):
    await app.bot.set_my_commands(location_commands + weather_commands + cycle_commands + schedule_commands)
    register_jobs(app)


async def log_update(update: Update, _context):
    user = update.effective_user
    who = f"{user.full_name!r} (@{user.username!r}, id={user.id})"
    if update.message and update.message.text:
        print(f"[cmd]      {who}: {update.message.text!r}")
    elif update.callback_query:
        print(f"[callback] {who}: {update.callback_query.data!r}")


async def log_error(_update, context):
    print(f"[error] {type(context.error).__name__}: {context.error}")


if __name__ == "__main__":
    Path("data").mkdir(exist_ok=True)
    persistence = PicklePersistence(filepath="data/bot_data")
    app = Application.builder().token(TOKEN).persistence(persistence).post_init(post_init).build()
    # Group -1 runs before all command/callback handlers (which default to group 0).
    # TypeHandler(Update) matches every update type, so this logs everything
    # without interfering with normal handler dispatch.
    app.add_handler(TypeHandler(Update, log_update), group=-1)
    app.add_error_handler(log_error)
    for h in bot_handlers:
        app.add_handler(h)
    for h in location_handlers:
        app.add_handler(h)
    for h in weather_handlers:
        app.add_handler(h)
    for h in cycle_handlers:
        app.add_handler(h)
    for h in schedule_handlers:
        app.add_handler(h)
    print("Bot running")
    app.run_polling()
