from datetime import datetime, time as dtime
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from scheduled import register_user_job, remove_user_job


def _schedule_pairs(user_data):
    schedules = user_data.get("schedules", {})
    loc_map = {l.id: l for l in user_data.get("locations", [])}
    return [(loc_map[loc_id], hour) for loc_id, hour in schedules.items() if loc_id in loc_map]


async def schedule_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pairs = _schedule_pairs(context.user_data)
    if pairs:
        text = "*Daily Forecast*\n" + "\n".join(f"• {loc.city_name} — {dtime(hour).strftime('%-I %p')}" for loc, hour in pairs)
    else:
        text = "*Daily Forecast*\nGet tomorrow's weather forecast delivered at a time that works for you."
    buttons = [[InlineKeyboardButton("＋ Add", callback_data="schedule:add")]]
    if pairs:
        buttons.append([InlineKeyboardButton("－ Remove", callback_data="schedule:remove")])
    markup = InlineKeyboardMarkup(buttons)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)


async def sched_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    locs = context.user_data.get("locations", [])
    if not locs:
        await query.edit_message_text(
            "You have no locations. Use /add to add one first.",
            reply_markup=None,
        )
        return
    buttons = [
        [InlineKeyboardButton(
            ", ".join(filter(None, [l.city_name, l.state, l.country])),
            callback_data=f"schedule:add:loc:{l.id}",
        )]
        for l in locs
    ]
    buttons.append([InlineKeyboardButton("« Back", callback_data="schedule:back")])
    await query.edit_message_text(
        "Pick a location to schedule:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def sched_pick_loc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    loc_id = int(query.data.split(":")[3])
    locs = context.user_data.get("locations", [])
    loc = next((l for l in locs if l.id == loc_id), None)
    if not loc:
        await query.edit_message_text("Location not found. Try /schedule again.")
        return
    tz_abbr = datetime.now(ZoneInfo(loc.timezone)).strftime("%Z")
    hours = range(5, 23)
    rows = []
    row = []
    for h in hours:
        row.append(InlineKeyboardButton(dtime(h).strftime("%-I %p"), callback_data=f"schedule:add:time:{loc_id}:{h}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("« Back", callback_data="schedule:add")])
    loc_line = f"{loc.city_name} ({tz_abbr})"
    await query.edit_message_text(
        f"Pick a time for {loc_line}:",
        reply_markup=InlineKeyboardMarkup(rows),
    )


async def sched_pick_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, _, _, loc_id, hour = query.data.split(":")
    loc_id = int(loc_id)
    hour = int(hour)

    locs = context.user_data.get("locations", [])
    loc = next((l for l in locs if l.id == loc_id), None)
    if not loc:
        await query.edit_message_text("Location not found. Try /schedule again.")
        return

    context.user_data.setdefault("schedules", {})[loc_id] = hour

    register_user_job(context.application, query.from_user.id, loc, hour)

    tz = ZoneInfo(loc.timezone)
    time_str = datetime.now(tz).replace(hour=hour, minute=0).strftime("%-I %p %Z")
    await query.edit_message_text(
        f"Scheduled {loc.city_name} at {time_str} ✅",
    )


async def sched_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pairs = _schedule_pairs(context.user_data)
    if not pairs:
        await query.edit_message_text("No active schedules.")
        return
    buttons = [
        [InlineKeyboardButton(
            f"{loc.city_name} — {dtime(hour).strftime("%-I %p")}",
            callback_data=f"schedule:remove:{loc.id}",
        )]
        for loc, hour in pairs
    ]
    buttons.append([InlineKeyboardButton("« Back", callback_data="schedule:back")])
    await query.edit_message_text(
        "Pick a schedule to remove:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def sched_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    loc_id = int(query.data.split(":")[2])

    locs = context.user_data.get("locations", [])
    loc = next((l for l in locs if l.id == loc_id), None)

    context.user_data.get("schedules", {}).pop(loc_id, None)
    remove_user_job(context.application, query.from_user.id, loc_id)

    name = loc.city_name if loc else "schedule"
    await query.edit_message_text(f"{name} schedule removed ✅")


schedule_handlers = [
    CommandHandler("schedule", schedule_cmd),
    CallbackQueryHandler(sched_add, pattern="^schedule:add$"),
    CallbackQueryHandler(sched_pick_loc, pattern="^schedule:add:loc:"),
    CallbackQueryHandler(sched_pick_time, pattern="^schedule:add:time:"),
    CallbackQueryHandler(sched_remove, pattern="^schedule:remove$"),
    CallbackQueryHandler(sched_delete, pattern="^schedule:remove:"),
    CallbackQueryHandler(schedule_cmd, pattern="^schedule:back$"),
]

commands = [
    ("schedule", "Manage daily forecast schedules"),
]
