from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import forecast
import formatters

_PT = ZoneInfo("America/Los_Angeles")


async def send_daily_forecast(context: ContextTypes.DEFAULT_TYPE):
    for user_id, user_data in list(context.application.user_data.items()):
        locs = user_data.get("locations", [])
        if not locs:
            continue
        loc = locs[0]
        today_loc = datetime.now(ZoneInfo(loc.timezone)).date()
        tomorrow = today_loc + timedelta(1)
        try:
            hourly = await forecast.get_hourly(loc, tomorrow)
        except Exception as e:
            print(f"[scheduler] forecast fetch failed for user {user_id}: {e}")
            continue
        text = formatters.format_hourly_compact(loc.city_name, hourly, today_loc)
        button = InlineKeyboardButton(
            "Show extended ▼",
            callback_data=f"forecast:extended:{loc.id}:{tomorrow.isoformat()}",
        )
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[button]]),
            )
            print(f"[scheduler] sent daily forecast to user {user_id} for {loc.city_name}")
        except Exception as e:
            print(f"[scheduler] send failed for user {user_id}: {e}")


def register_jobs(app):
    app.job_queue.run_daily(send_daily_forecast, time=time(20, 0, tzinfo=_PT))
