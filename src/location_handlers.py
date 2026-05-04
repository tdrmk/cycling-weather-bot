from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler,
    MessageHandler, filters,
)
import forecast

WAITING_CITY = 0


async def locations_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    locs = context.user_data.get("locations", [])
    if locs:
        lines = ["*Your locations:*"]
        for l in locs:
            detail = ", ".join(filter(None, [l.state, l.country]))
            suffix = f" — {detail}" if detail else ""
            lines.append(f"• *{l.city_name}*{suffix}")
        text = "\n".join(lines)
    else:
        text = "*Locations*\nNo locations set yet."
    buttons = [[InlineKeyboardButton("＋ Add", callback_data="loc:add")]]
    if locs:
        buttons.append([InlineKeyboardButton("－ Remove", callback_data="loc:remove")])
    markup = InlineKeyboardMarkup(buttons)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    return ConversationHandler.END


async def loc_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Send a city name to add:\n\n_(use /locations to cancel)_",
        parse_mode="Markdown",
    )
    return WAITING_CITY


async def loc_receive_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
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
            callback_data=f"loc:pick:{r.id}",
        )]
        for r in results
    ]
    await update.message.reply_text(
        "Found multiple matches, pick one:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    return ConversationHandler.END


async def add_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled. Use /locations to try again.")
    return ConversationHandler.END


async def loc_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    loc_id = int(query.data.split(":")[2])
    results = context.chat_data.pop("add_results", [])
    loc = next(r for r in results if r.id == loc_id)
    locs = context.user_data.get("locations", [])
    if any(l.id == loc.id for l in locs):
        await query.edit_message_text(f"{loc.city_name} is already in your locations.")
    else:
        context.user_data.setdefault("locations", []).append(loc)
        await query.edit_message_text(f"Added {', '.join(filter(None, [loc.city_name, loc.state, loc.country]))} ✅")


async def loc_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    locs = context.user_data.get("locations", [])
    buttons = [
        [InlineKeyboardButton(
            ", ".join(filter(None, [l.city_name, l.state, l.country])),
            callback_data=f"loc:delete:{l.id}",
        )]
        for l in locs
    ]
    buttons.append([InlineKeyboardButton("« Back", callback_data="loc:back")])
    await query.edit_message_text(
        "Which location to remove?",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def loc_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    loc_id = int(query.data.split(":")[2])
    locs = context.user_data.get("locations", [])
    loc = next((l for l in locs if l.id == loc_id), None)
    if not loc:
        await query.edit_message_text("Already removed.")
        return
    context.user_data["locations"] = [l for l in locs if l.id != loc_id]
    await query.edit_message_text(f"Removed {loc.city_name} ✅")


location_handlers = [
    ConversationHandler(
        entry_points=[CallbackQueryHandler(loc_add, pattern="^loc:add$")],
        states={
            WAITING_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, loc_receive_city)],
        },
        fallbacks=[MessageHandler(filters.COMMAND, add_cancel)],
        conversation_timeout=60,
    ),
    CommandHandler("locations", locations_cmd),
    CallbackQueryHandler(loc_remove, pattern="^loc:remove$"),
    CallbackQueryHandler(loc_delete, pattern="^loc:delete:"),
    CallbackQueryHandler(loc_pick, pattern="^loc:pick:"),
    CallbackQueryHandler(locations_cmd, pattern="^loc:back$"),
]

commands = [
    ("locations", "Manage your locations"),
]
