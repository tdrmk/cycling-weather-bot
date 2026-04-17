from datetime import timedelta
from zoneinfo import ZoneInfo

import labels as l


def _is_night(dt, sunrise, sunset):
    t = dt.time()
    return t < sunrise or t >= sunset


def _compact_hourly_row(hour_str, row, condition_emoji):
    prob = min(int(row.rain_prob), 99)
    mm = "HVY" if row.rain_mm >= 100 else f"{int(row.rain_mm)}"
    return f"`{hour_str:>4} {row.temp:>2.0f}/{row.feels:>2.0f} {condition_emoji} {prob:>2}/{mm:<2} {row.wind:>2.0f} {row.uv:>2.0f}`"


def _compact_week_row(d, row, condition_emoji):
    prob = min(int(row.rain_prob), 99)
    mm = "HV" if row.rain_mm >= 100 else f"{int(row.rain_mm):>2}"
    return f"`{d.strftime('%a %-d'):<6} {condition_emoji} {row.temp_high:>2.0f}/{row.temp_low:>2.0f} {prob:>2}/{mm} {row.wind:>2.0f} {row.uv:>2.0f}`"


def _date_label(target_date, today):
    if target_date == today:
        return f"Today ({target_date.strftime('%a %b %-d')})"
    elif target_date == today + timedelta(days=1):
        return f"Tomorrow ({target_date.strftime('%a %b %-d')})"
    return target_date.strftime("%a %b %-d")


def format_now(loc, forecast):
    dt, row = next(iter(forecast.rows.items()))
    night = _is_night(dt, forecast.sunrise, forecast.sunset)
    label, condition_emoji = l.wmo(row.wmo_code, night)
    tz_abbr = dt.replace(tzinfo=ZoneInfo(loc.timezone)).strftime("%Z")
    lines = [
        f"📍 *{loc.city_name}*",
        dt.strftime("%-I %p") + f" {tz_abbr}",
        f"{condition_emoji} {label} ({row.cloud}% clouds)",
        f"🌡 {row.temp:.0f}°C  (feels {row.feels:.0f}°C)",
        f"💧 Humidity {row.humidity}%",
        f"☀️ UV {row.uv:.0f} ({l.uv_label(row.uv)})",
        f"🌧 Rain {row.rain_prob}% / {row.rain_mm:.0f}mm",
        f"💨 {row.wind:.0f}mph {l.wind_cardinal(row.wind_direction)} {l.beaufort_label(row.wind)} (gusts {row.gusts:.0f}mph)",
        f"👁 {row.visibility / 1000:.0f}km",
    ]
    if row.aqi is not None:
        lines.append(f"😷 AQI {row.aqi} ({l.aqi_label(row.aqi)})")
    return "\n".join(lines)


def format_hourly_compact(loc_name, forecast, today):
    sunrise_str = forecast.sunrise.strftime("%-I:%M %p")
    sunset_str = forecast.sunset.strftime("%-I:%M %p")

    rows = []
    for dt, row in forecast.rows.items():
        night = _is_night(dt, forecast.sunrise, forecast.sunset)
        _, condition_emoji = l.wmo(row.wmo_code, night)
        rows.append(_compact_hourly_row(dt.strftime("%-I%p"), row, condition_emoji))

    return "\n".join([
        f"📍 *{loc_name}*",
        _date_label(forecast.date, today),
        f"🌅 {sunrise_str}   🌇 {sunset_str}",
        "",
        "`        °C    %/mm mph UV`",
    ] + rows)


def format_hourly_extended(loc_name, forecast, today):
    sunrise_str = forecast.sunrise.strftime("%-I:%M %p")
    sunset_str = forecast.sunset.strftime("%-I:%M %p")

    blocks = []
    for dt, row in forecast.rows.items():
        night = _is_night(dt, forecast.sunrise, forecast.sunset)
        label, condition_emoji = l.wmo(row.wmo_code, night)
        hour_str = dt.strftime("%-I%p")
        block = [
            f"*{hour_str}*",
            f"🌡 {row.temp:.0f}°C (feels {row.feels:.0f}°C)  💧 {row.humidity}%",
            f"{condition_emoji} {label} ({row.cloud}% clouds)  👁 {row.visibility / 1000:.0f}km",
            f"🌧 Rain {row.rain_prob}% / {row.rain_mm:.0f}mm",
            f"💨 {row.wind:.0f}mph {l.wind_cardinal(row.wind_direction)} {l.beaufort_label(row.wind)} (gusts {row.gusts:.0f}mph)",
            f"☀️ UV {row.uv:.0f} ({l.uv_label(row.uv)})",
        ]
        if row.aqi is not None:
            block.append(f"😷 AQI {row.aqi} ({l.aqi_label(row.aqi)})")
        blocks.append("\n".join(block))

    return "\n".join([
        f"📍 *{loc_name}*",
        _date_label(forecast.date, today),
        f"🌅 {sunrise_str}   🌇 {sunset_str}",
        "",
    ] + [b + "\n" for b in blocks]).rstrip()


def format_week_compact(loc_name, week):
    dates = list(week.rows.keys())
    date_range = f"{dates[0].strftime('%b %-d')}–{dates[-1].strftime('%b %-d')}"
    first = week.rows[dates[0]]
    sunrise_str = first.sunrise.strftime("%-I:%M %p")
    sunset_str = first.sunset.strftime("%-I:%M %p")

    rows = []
    for d, row in week.rows.items():
        _, condition_emoji = l.wmo(row.wmo_code)
        rows.append(_compact_week_row(d, row, condition_emoji))

    return "\n".join([
        f"📍 *{loc_name}*",
        date_range,
        f"🌅 {sunrise_str}   🌇 {sunset_str}",
        "",
        "`             °C %/mm mph UV`",
    ] + rows)


def format_week_extended(loc_name, week):
    dates = list(week.rows.keys())
    date_range = f"{dates[0].strftime('%b %-d')}–{dates[-1].strftime('%b %-d')}"

    blocks = []
    for d, row in week.rows.items():
        label, condition_emoji = l.wmo(row.wmo_code)
        sunrise_str = row.sunrise.strftime("%-I:%M %p")
        sunset_str = row.sunset.strftime("%-I:%M %p")
        block = [
            f"*{d.strftime('%a %b %-d')}*",
            f"{condition_emoji} {label}",
            f"🌡 {row.temp_high:.0f}°C / {row.temp_low:.0f}°C (feels {row.feels_high:.0f}°C / {row.feels_low:.0f}°C)",
            f"🌧 Rain {row.rain_prob}% / {row.rain_mm:.0f}mm",
            f"💨 {row.wind:.0f}mph {l.wind_cardinal(row.wind_direction)} (gusts {row.wind_gusts:.0f}mph)",
            f"☀️ UV {row.uv:.0f} ({l.uv_label(row.uv)})",
        ]
        if row.aqi is not None:
            block.append(f"😷 AQI {row.aqi} ({l.aqi_label(row.aqi)})")
        block.append(f"🌅 {sunrise_str}   🌇 {sunset_str}")
        blocks.append("\n".join(block))

    return "\n".join([
        f"📍 *{loc_name}*",
        date_range,
        "",
    ] + [b + "\n" for b in blocks]).rstrip()
