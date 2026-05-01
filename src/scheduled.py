from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import forecast
import formatters
from utils import retry


async def send_daily_forecast(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    user_id = data["user_id"]
    loc_id = data["loc_id"]

    user_data = context.application.user_data.get(user_id, {})
    locs = user_data.get("locations", [])
    loc = next((l for l in locs if l.id == loc_id), None)
    if not loc:
        context.job.schedule_removal()
        return

    today_loc = datetime.now(ZoneInfo(loc.timezone)).date()
    tomorrow = today_loc + timedelta(1)
    try:
        get_hourly = retry()(forecast.get_hourly)
        hourly = await get_hourly(loc, tomorrow)
    except Exception as e:
        print(f"[scheduler] forecast fetch failed for user {user_id}: {repr(e)}")
        return

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
        print(f"[scheduler] send failed for user {user_id}: {repr(e)}")


def _job_name(user_id, loc_id):
    return f"daily_{user_id}_{loc_id}"


def register_user_job(app, user_id, loc, hour):
    name = _job_name(user_id, loc.id)
    for job in app.job_queue.get_jobs_by_name(name):
        job.schedule_removal()
    app.job_queue.run_daily(
        send_daily_forecast,
        time=time(hour, 0, tzinfo=ZoneInfo(loc.timezone)),
        name=name,
        data={"user_id": user_id, "loc_id": loc.id},
    )


def remove_user_job(app, user_id, loc_id):
    for job in app.job_queue.get_jobs_by_name(_job_name(user_id, loc_id)):
        job.schedule_removal()


def register_jobs(app):
    for user_id, user_data in app.user_data.items():
        schedules = user_data.get("schedules", {})
        locs = user_data.get("locations", [])
        loc_map = {l.id: l for l in locs}
        for loc_id, hour in schedules.items():
            loc = loc_map.get(loc_id)
            if loc:
                register_user_job(app, user_id, loc, hour)
