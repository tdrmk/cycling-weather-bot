import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

import forecast
import formatters

TZ = ZoneInfo("America/Los_Angeles")

_DAY_RE = re.compile(
    r"\b(next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow)\b",
    re.IGNORECASE,
)
_WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


def _loc_name(loc):
    return loc.city_name


def resolve_location(context, city_arg=None):
    locs = context.user_data.get("locations", [])
    if not locs:
        return None, "No locations set. Add one with /add <city>"
    if city_arg:
        match = next((l for l in locs if l.city_name.lower() == city_arg.lower()), None)
        if not match:
            return None, f'"{city_arg}" not in your locations. Use /locations to see what\'s saved.'
        return match, None
    return locs[0], None


def _now_hour():
    return datetime.now(TZ).replace(minute=0, second=0, microsecond=0, tzinfo=None)


def _next_weekday(weekday):
    today = date.today()
    days = (weekday - today.weekday()) % 7
    return today + timedelta(days or 7)


def _parse_forecast_args(args):
    text = " ".join(args)
    m = _DAY_RE.search(text)
    if not m:
        return text.strip() or None, date.today() + timedelta(1)
    day_str = m.group(2).lower()
    is_next = bool(m.group(1))
    city = " ".join(_DAY_RE.sub("", text).split()) or None
    if day_str == "tomorrow":
        target_date = date.today() + timedelta(1)
    else:
        target_date = _next_weekday(_WEEKDAYS.index(day_str))
        if is_next:
            target_date += timedelta(7)
    return city, target_date


async def now_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city_arg = " ".join(context.args).strip() or None
    loc, err = resolve_location(context, city_arg)
    if err:
        await update.message.reply_text(err)
        return
    result = await forecast.get_now(loc)
    text = formatters.format_now(_loc_name(loc), result)
    await update.message.reply_text(text, parse_mode="Markdown")


async def week_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city_arg = " ".join(context.args).strip() or None
    loc, err = resolve_location(context, city_arg)
    if err:
        await update.message.reply_text(err)
        return
    week = await forecast.get_week(loc)
    text = formatters.format_week_compact(_loc_name(loc), week)
    button = InlineKeyboardButton("Show extended ▼", callback_data=f"week:extended:{loc.id}")
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[button]]))


async def week_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, view, loc_id = query.data.split(":", 2)
    loc_id = int(loc_id)
    locs = context.user_data.get("locations", [])
    loc = next((l for l in locs if l.id == loc_id), None)
    if not loc:
        await query.edit_message_text("Location no longer saved.")
        return
    week = await forecast.get_week(loc)
    if view == "extended":
        text = formatters.format_week_extended(_loc_name(loc), week)
        button = InlineKeyboardButton("Show compact ▲", callback_data=f"week:compact:{loc.id}")
    else:
        text = formatters.format_week_compact(_loc_name(loc), week)
        button = InlineKeyboardButton("Show extended ▼", callback_data=f"week:extended:{loc.id}")
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[button]]))


async def today_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city_arg = " ".join(context.args).strip() or None
    loc, err = resolve_location(context, city_arg)
    if err:
        await update.message.reply_text(err)
        return
    hourly = await forecast.get_hourly(loc, date.today())
    now = _now_hour()
    hourly.rows = {dt: row for dt, row in hourly.rows.items() if dt >= now}
    text = formatters.format_hourly_compact(_loc_name(loc), hourly)
    button = InlineKeyboardButton("Show extended ▼", callback_data=f"today:extended:{loc.id}")
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[button]]))


async def today_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, view, loc_id = query.data.split(":", 2)
    loc_id = int(loc_id)
    locs = context.user_data.get("locations", [])
    loc = next((l for l in locs if l.id == loc_id), None)
    if not loc:
        await query.edit_message_text("Location no longer saved.")
        return
    hourly = await forecast.get_hourly(loc, date.today())
    now = _now_hour()
    hourly.rows = {dt: row for dt, row in hourly.rows.items() if dt >= now}
    if view == "extended":
        text = formatters.format_hourly_extended(_loc_name(loc), hourly)
        button = InlineKeyboardButton("Show compact ▲", callback_data=f"today:compact:{loc.id}")
    else:
        text = formatters.format_hourly_compact(_loc_name(loc), hourly)
        button = InlineKeyboardButton("Show extended ▼", callback_data=f"today:extended:{loc.id}")
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[button]]))


async def forecast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city_arg, target_date = _parse_forecast_args(context.args)
    loc, err = resolve_location(context, city_arg)
    if err:
        await update.message.reply_text(err)
        return
    hourly = await forecast.get_hourly(loc, target_date)
    text = formatters.format_hourly_compact(_loc_name(loc), hourly)
    button = InlineKeyboardButton(
        "Show extended ▼",
        callback_data=f"forecast:extended:{loc.id}:{target_date.isoformat()}",
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[button]]))


async def forecast_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, view, loc_id, date_str = query.data.split(":", 3)
    loc_id = int(loc_id)
    locs = context.user_data.get("locations", [])
    loc = next((l for l in locs if l.id == loc_id), None)
    if not loc:
        await query.edit_message_text("Location no longer saved.")
        return
    target_date = date.fromisoformat(date_str)
    hourly = await forecast.get_hourly(loc, target_date)
    if view == "extended":
        text = formatters.format_hourly_extended(_loc_name(loc), hourly)
        button = InlineKeyboardButton(
            "Show compact ▲",
            callback_data=f"forecast:compact:{loc.id}:{date_str}",
        )
    else:
        text = formatters.format_hourly_compact(_loc_name(loc), hourly)
        button = InlineKeyboardButton(
            "Show extended ▼",
            callback_data=f"forecast:extended:{loc.id}:{date_str}",
        )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[button]]))


weather_handlers = [
    CommandHandler("now", now_cmd),
    CommandHandler("week", week_cmd),
    CallbackQueryHandler(week_toggle, pattern="^week:"),
    CommandHandler("today", today_cmd),
    CallbackQueryHandler(today_toggle, pattern="^today:"),
    CommandHandler("forecast", forecast_cmd),
    CallbackQueryHandler(forecast_toggle, pattern="^forecast:"),
]

commands = [
    ("now", "Current conditions"),
    ("today", "Hourly forecast for today"),
    ("forecast", "Hourly forecast for any day"),
    ("week", "7-day summary"),
]
