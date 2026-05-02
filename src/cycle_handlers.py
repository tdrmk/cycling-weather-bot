from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

import forecast
import labels as l
from weather_handlers import resolve_location, _next_weekday, _WEEKDAYS

PERIODS = {
    "morning": (range(8, 12),  "Morning (8AM–12PM)"),
    "noon":    (range(12, 16), "Noon (12PM–4PM)"),
    "evening": (range(16, 20), "Evening (4PM–8PM)"),
    "night":   (range(20, 24), "Night (8PM–12AM)"),
}

_PERIOD_NAMES = set(PERIODS)


def _parse_cycle_args(args, saved_locs, today):
    tokens = [t.lower() for t in args]

    # Extract period (first matching token wins)
    period = None
    rest = []
    for t in tokens:
        if period is None and t in _PERIOD_NAMES:
            period = t
        else:
            rest.append(t)
    tokens = rest

    # Extract day (token by token, handles "next <weekday>")
    target_date = today
    rest = []
    i = 0
    while i < len(tokens):
        if tokens[i] == "next" and i + 1 < len(tokens) and tokens[i + 1] in _WEEKDAYS:
            target_date = _next_weekday(_WEEKDAYS.index(tokens[i + 1]), today) + timedelta(7)
            i += 2
        elif tokens[i] == "today":
            target_date = today
            i += 1
        elif tokens[i] == "tomorrow":
            target_date = today + timedelta(1)
            i += 1
        elif tokens[i] in _WEEKDAYS:
            target_date = _next_weekday(_WEEKDAYS.index(tokens[i]), today)
            i += 1
        else:
            rest.append(tokens[i])
            i += 1
    tokens = rest

    # Remaining tokens = city name
    city_str = " ".join(tokens) or None
    city_arg = None
    if city_str:
        match = next((loc for loc in saved_locs if loc.city_name.lower() == city_str), None)
        if not match:
            return None, None, None, (
                f'Unknown argument "{city_str}". '
                f'Usage: /cycle [city] [day] [morning|noon|evening|night]'
            )
        city_arg = match.city_name

    return city_arg, target_date, period, None


# --- Verdict ---

def _cycle_verdict(row, is_dark=False):
    # WMO-only: surface ice / thunderstorm
    if row.wmo_code in {56, 57, 66, 67}:
        return "Don't ride", "ice on road"
    if row.wmo_code in {95, 96, 99}:
        return "Don't ride", "thunderstorm"

    # Don't ride — quantitative
    if row.aqi is not None and row.aqi >= 201:
        return "Don't ride", "AQI hazardous"
    if row.feels < 2:
        return "Don't ride", "too cold"
    if row.feels > 35:
        return "Don't ride", "too hot"
    if row.wind >= 35:
        return "Don't ride", "wind too strong"
    if row.gusts >= 40:
        return "Don't ride", "gusts dangerous"
    if row.rain_mm >= 10:
        return "Don't ride", "too much rain"
    if row.visibility < 1000:
        return "Don't ride", "dangerous fog"

    # Tough
    reasons = []
    if row.wind >= 20:                                reasons.append(("Tough", "strong wind"))
    if row.gusts >= 30:                               reasons.append(("Tough", "strong gusts"))
    if row.rain_mm >= 3:                              reasons.append(("Tough", "heavy rain"))
    if getattr(row, 'rain_prob', 0) >= 75 and row.rain_mm >= 1: reasons.append(("Tough", "rain"))
    if row.aqi is not None and 151 <= row.aqi < 201:  reasons.append(("Tough", "AQI unhealthy"))
    if row.wmo_code in {75, 77}:                      reasons.append(("Tough", "heavy snow"))
    if row.feels < 7:                                 reasons.append(("Tough", "very cold"))
    if row.feels > 30:                                reasons.append(("Tough", "heat risk"))
    if 1000 <= row.visibility < 2000:                 reasons.append(("Tough", "fog"))

    # Manageable
    if row.wind >= 13:                                reasons.append(("Manageable", "wind"))
    if row.gusts >= 20:                               reasons.append(("Manageable", "gusty"))
    if row.rain_mm >= 1:                              reasons.append(("Manageable", "rain"))
    if getattr(row, 'rain_prob', 0) >= 60:               reasons.append(("Manageable", "rain likely"))
    if row.aqi is not None and 101 <= row.aqi < 151:  reasons.append(("Manageable", "poor air"))
    if row.wmo_code in {71, 73}:                      reasons.append(("Manageable", "snow"))
    if row.feels < 10:                                reasons.append(("Manageable", "cold"))
    if row.feels > 25:                                reasons.append(("Manageable", "warm"))
    if 2000 <= row.visibility < 5000:                 reasons.append(("Manageable", "low visibility"))

    _PHYSICAL = {"wind", "gusty", "rain"}
    if not reasons:
        verdict, reason = "Good", ""
    else:
        manageable_reasons = [r for v, r in reasons if v == "Manageable"]
        physical_manageable = [r for r in manageable_reasons if r in _PHYSICAL]
        combo_upgrade = len(manageable_reasons) >= 2 and len(physical_manageable) >= 1
        has_tough = any(v == "Tough" for v, _ in reasons)
        verdict = "Tough" if (has_tough or combo_upgrade) else "Manageable"
        if has_tough:
            top = list(dict.fromkeys(r for v, r in reasons if v == "Tough"))[:2]
        else:
            top = list(dict.fromkeys(manageable_reasons))[:2]
        reason = " + ".join(top)

    # Night downgrade — applied after base verdict
    if is_dark and verdict in ("Good", "Manageable"):
        if row.rain_mm > 0 or row.visibility < 5000:
            if verdict == "Good":
                verdict, reason = "Manageable", "low light"
            else:
                reason = (reason + " + low light").lstrip(" + ")
                verdict = "Tough"

    return verdict, reason


# --- Field helpers ---

def _temp_note(feels):
    if feels < 2:   return " — too cold, don't ride"
    if feels < 7:   return " — very cold, full winter kit"
    if feels < 10:  return " — cold, layer up"
    if feels <= 25: return ""
    if feels <= 30: return " — warm, stay hydrated"
    if feels <= 35: return " — hot, shorten your ride"
    return " — too hot, don't ride"


def _rain_note(mm, prob):
    if prob is None:
        if mm >= 5: return " — bring a jacket"
        if mm >= 2: return " — light jacket recommended"
        return ""
    if mm >= 5 and prob >= 60:  return " — bring a jacket"
    if prob >= 60 and mm < 2:   return " — possible light shower"
    if mm >= 2 or prob >= 40:   return " — light jacket recommended"
    return ""


def _uv_line(uv):
    if uv < 3:  return None
    emoji = l.uv_emoji(uv)
    if uv < 6:  return f"{emoji} UV {uv:.1f} — Moderate — sunscreen recommended"
    if uv < 8:  return f"{emoji} UV {uv:.1f} — High — sunscreen essential"
    if uv < 11: return f"{emoji} UV {uv:.1f} — Very High — full protection, cover up"
    return f"{emoji} UV {uv:.1f} — Extreme — reapply mid-ride"


def _visibility_line(vis):
    if vis >= 5000: return None
    km = f"{vis / 1000:.1f}".rstrip("0").rstrip(".")
    emoji = l.visibility_emoji(vis)
    if vis >= 2000: return f"{emoji} {km}km — Mist — use lights"
    if vis >= 1000: return f"{emoji} {km}km — Fog — stay off busy roads"
    return f"{emoji} {km}km — Dense fog — don't ride"


def _is_dark(dt, sunrise, sunset):
    t = dt.time()
    return t < sunrise or t >= sunset


# --- Formatter ---

_VERDICT_EMOJI = {
    "Good":       "🚴",
    "Manageable": "🚴",
    "Tough":      "🚴",
    "Don't ride": "⛔",
}


def _format_hour_fields(row, rain_prob, dark):
    label, cond_emoji = l.wmo(row.wmo_code, is_night=dark)
    cardinal = l.wind_cardinal(row.wind_direction)
    beaufort = l.beaufort_label(row.wind)
    wind_line = f"{l.wind_emoji(row.wind)} {row.wind:.0f}mph {cardinal} — {beaufort}"
    if row.gusts >= row.wind + 10:
        wind_line += f" — gusty, expect sideways push (gusts {row.gusts:.0f}mph)"
    if rain_prob is not None:
        rain_line = f"{l.rain_emoji(row.rain_mm)} {rain_prob}% / {row.rain_mm:.1f}mm{_rain_note(row.rain_mm, rain_prob)}"
    else:
        rain_line = f"{l.rain_emoji(row.rain_mm)} {row.rain_mm:.1f}mm{_rain_note(row.rain_mm, None)}"
    lines = [
        f"{cond_emoji} {label}",
        f"{l.temp_emoji(row.feels)} {row.temp:.1f}°C / feels {row.feels:.1f}°C{_temp_note(row.feels)}",
        wind_line,
        rain_line,
    ]
    uv = _uv_line(row.uv)
    if uv:
        lines.append(uv)
    vis = _visibility_line(row.visibility)
    if vis:
        lines.append(vis)
    if row.aqi is not None:
        lines.append(f"{l.aqi_emoji(row.aqi)} AQI {row.aqi} — {l.aqi_label(row.aqi)}")
    return lines


def format_cycle(loc_name, hrly, period, today):
    period_hours, period_label = PERIODS[period]
    rows = {dt: row for dt, row in hrly.rows.items() if dt.hour in period_hours}

    if hrly.date == today:
        date_label = f"Today ({hrly.date.strftime('%a %b %-d')})"
    elif hrly.date == today + timedelta(1):
        date_label = f"Tomorrow ({hrly.date.strftime('%a %b %-d')})"
    else:
        date_label = hrly.date.strftime("%a %b %-d")

    lines = [f"📍 *{loc_name}*", date_label, period_label, ""]

    for dt, row in sorted(rows.items()):
        dark = _is_dark(dt, hrly.sunrise, hrly.sunset)
        verdict, reason = _cycle_verdict(row, is_dark=dark)

        hour_str = dt.strftime("%-I%p")
        header = f"{hour_str} — {_VERDICT_EMOJI[verdict]} {verdict}"
        if reason:
            header += f" — {reason}"
        lines.append(header)
        lines.extend(_format_hour_fields(row, row.rain_prob, dark))
        lines.append("")

    return "\n".join(lines).rstrip()


def format_cycle_day_compact(loc_name, hrly, today):
    if hrly.date == today:
        date_label = f"Today ({hrly.date.strftime('%a %b %-d')})"
    elif hrly.date == today + timedelta(1):
        date_label = f"Tomorrow ({hrly.date.strftime('%a %b %-d')})"
    else:
        date_label = hrly.date.strftime("%a %b %-d")

    lines = [f"📍 *{loc_name}*", date_label, ""]

    for _, (period_hours, period_label) in PERIODS.items():
        rows = {dt: row for dt, row in hrly.rows.items() if dt.hour in period_hours}
        if not rows:
            continue
        lines.append(f"*{period_label}*")
        for dt, row in sorted(rows.items()):
            dark = _is_dark(dt, hrly.sunrise, hrly.sunset)
            verdict, reason = _cycle_verdict(row, is_dark=dark)
            hour_str = dt.strftime("%-I%p")
            line = f"{hour_str} — {_VERDICT_EMOJI[verdict]} {verdict}"
            if reason:
                line += f" — {reason}"
            lines.append(line)
        lines.append("")

    return "\n".join(lines).rstrip()


def format_cycle_day_extended(loc_name, hrly, today):
    return "\n\n".join(
        format_cycle(loc_name, hrly, period, today) for period in PERIODS
    )


def format_cycle_now(loc_name, row):
    dark = not row.is_day
    verdict, reason = _cycle_verdict(row, is_dark=dark)
    hour_str = row.dt.strftime("%-I:%M %p %Z")
    header = f"{hour_str} — {_VERDICT_EMOJI[verdict]} {verdict}"
    if reason:
        header += f" — {reason}"
    lines = [f"📍 *{loc_name}*", header]
    lines.extend(_format_hour_fields(row, None, dark))
    return "\n".join(lines)


# --- Handler ---

async def cycle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    saved_locs = context.user_data.get("locations", [])
    if not saved_locs:
        await update.message.reply_text("No locations set. Add one with /add <city>")
        return

    # First pass: extract city only (city extraction is date-independent)
    city_arg, _, _, err = _parse_cycle_args(context.args, saved_locs, date.today())
    if err:
        await update.message.reply_text(err)
        return

    loc, err = resolve_location(context, city_arg)
    if err:
        await update.message.reply_text(err)
        return

    today_loc = datetime.now(ZoneInfo(loc.timezone)).date()
    city_arg, target_date, period, err = _parse_cycle_args(context.args, saved_locs, today_loc)
    if err:
        await update.message.reply_text(err)
        return

    hrly = await forecast.get_hourly(loc, target_date)

    if period is None:
        text = format_cycle_day_compact(loc.city_name, hrly, today_loc)
        button = InlineKeyboardButton(
            "Show extended ▼",
            callback_data=f"cycle:extended:{loc.id}:{target_date.isoformat()}",
        )
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[button]]))
        return

    # Check if period is already past for today
    if target_date == today_loc:
        now_h = datetime.now(ZoneInfo(loc.timezone)).hour
        period_hours, _ = PERIODS[period]
        if max(period_hours) < now_h:
            period_names = list(PERIODS)
            idx = period_names.index(period)
            suggestions = period_names[idx + 1:]
            if suggestions:
                tip = " or ".join(f"/cycle {p}" for p in suggestions[:2])
            else:
                tip = "/cycle morning tomorrow"
            await update.message.reply_text(f"That period has already passed. Try {tip}.")
            return

    text = format_cycle(loc.city_name, hrly, period, today_loc)
    await update.message.reply_text(text, parse_mode="Markdown")


async def cyclenow_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city_arg = " ".join(context.args).strip() or None
    loc, err = resolve_location(context, city_arg)
    if err:
        await update.message.reply_text(err)
        return
    result = await forecast.get_now(loc)
    text = format_cycle_now(loc.city_name, result)
    await update.message.reply_text(text, parse_mode="Markdown")


async def cycle_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, view, loc_id, date_str = query.data.split(":", 3)
    loc_id = int(loc_id)
    locs = context.user_data.get("locations", [])
    loc = next((l for l in locs if l.id == loc_id), None)
    if not loc:
        await query.edit_message_text("Location no longer saved.")
        return
    today_loc = datetime.now(ZoneInfo(loc.timezone)).date()
    target_date = date.fromisoformat(date_str)
    hrly = await forecast.get_hourly(loc, target_date)
    if view == "extended":
        text = format_cycle_day_extended(loc.city_name, hrly, today_loc)
        button = InlineKeyboardButton(
            "Show compact ▲",
            callback_data=f"cycle:compact:{loc.id}:{date_str}",
        )
    else:
        text = format_cycle_day_compact(loc.city_name, hrly, today_loc)
        button = InlineKeyboardButton(
            "Show extended ▼",
            callback_data=f"cycle:extended:{loc.id}:{date_str}",
        )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[button]]))


cycle_handlers = [
    CommandHandler("cycle", cycle_cmd),
    CommandHandler("cyclenow", cyclenow_cmd),
    CallbackQueryHandler(cycle_toggle, pattern=r"^cycle:"),
]

commands = [
    ("cycle", "Cycling breakdown with verdict"),
    ("cyclenow", "Cycling verdict for right now"),
]
