from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters,
)
import forecast

WAITING_CITY, WAITING_PICK = range(2)


async def _add_city(update, context, city):
    results = await forecast.geocode(city)

    if not results:
        await update.message.reply_text(f'No locations found for "{city}". Try a different name.')
        return ConversationHandler.END

    if len(results) == 1:
        loc = results[0]
        locs = context.user_data.get("locations", [])
        if any(l.id == loc.id for l in locs):
            await update.message.reply_text(f"{loc.city_name} is already in your locations.")
        else:
            context.user_data.setdefault("locations", []).append(loc)
            await update.message.reply_text(f"Added {', '.join(filter(None, [loc.city_name, loc.state, loc.country]))} ✅")
        return ConversationHandler.END

    context.chat_data["add_results"] = results
    buttons = [
        [InlineKeyboardButton(
            ", ".join(filter(None, [r.city_name, r.state, r.country])),
            callback_data=f"add:{r.id}",
        )]
        for r in results
    ]
    await update.message.reply_text(
        "Found multiple matches, pick one:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    return WAITING_PICK


async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = " ".join(context.args).strip()
    if city:
        return await _add_city(update, context, city)
    await update.message.reply_text("Which city?")
    return WAITING_CITY


async def add_receive_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    return await _add_city(update, context, city)


async def add_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    loc_id = int(query.data.split(":")[1])
    results = context.chat_data.pop("add_results", [])
    loc = next(r for r in results if r.id == loc_id)
    locs = context.user_data.get("locations", [])
    if any(l.id == loc.id for l in locs):
        await query.edit_message_text(f"{loc.city_name} is already in your locations.")
    else:
        context.user_data.setdefault("locations", []).append(loc)
        await query.edit_message_text(f"Added {', '.join(filter(None, [loc.city_name, loc.state, loc.country]))} ✅")
    return ConversationHandler.END


async def locations_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    locs = context.user_data.get("locations", [])
    if not locs:
        await update.message.reply_text("You have no locations set. Add one with /add <city>")
        return
    lines = ["*Your locations:*"]
    for l in locs:
        detail = ", ".join(filter(None, [l.state, l.country]))
        suffix = f" — {detail}" if detail else ""
        lines.append(f"• *{l.city_name}*{suffix}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def remove_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    locs = context.user_data.get("locations", [])
    if not locs:
        await update.message.reply_text("You have no locations set. Add one with /add <city>")
        return
    buttons = [
        [InlineKeyboardButton(
            ", ".join(filter(None, [l.city_name, l.state, l.country])),
            callback_data=f"remove:{l.id}",
        )]
        for l in locs
    ]
    await update.message.reply_text(
        "Which location to remove?",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def remove_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    loc_id = int(query.data.split(":", 1)[1])
    locs = context.user_data.get("locations", [])
    loc = next(l for l in locs if l.id == loc_id)
    context.user_data["locations"] = [l for l in locs if l.id != loc_id]
    await query.edit_message_text(f"Removed {loc.city_name} ✅")


location_handlers = [
    ConversationHandler(
        entry_points=[CommandHandler(["add", "addlocation"], add_start)],
        states={
            WAITING_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_receive_city)],
            WAITING_PICK: [CallbackQueryHandler(add_pick, pattern="^add:")],
        },
        fallbacks=[],
        conversation_timeout=60,
    ),
    CommandHandler(["remove", "removelocation"], remove_start),
    CallbackQueryHandler(remove_pick, pattern="^remove:"),
    CommandHandler("locations", locations_cmd),
]

commands = [
    ("add", "Add a location"),
    ("remove", "Remove a location"),
    ("locations", "List your locations"),
]
