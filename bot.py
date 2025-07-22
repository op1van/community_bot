import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
from notion_client import Client as NotionClient

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if not TELEGRAM_TOKEN:
    raise RuntimeError("BOT_TOKEN env var is missing")
if not (NOTION_TOKEN and DATABASE_ID):
    raise RuntimeError("Notion env vars are missing")

notion = NotionClient(auth=NOTION_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Hey there, meet cllb — the music community label that kinda accidentally started itself but stuck around on purpose 🧢"
    )
    keyboard = [[InlineKeyboardButton("nice", callback_data="nice")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "nice":
        await query.message.reply_text(
            "Few questions coming up — but first, read the manifesto. It’s kinda sacred\n\n🕺🏼",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("no chance to skip", callback_data="show_manifesto")]
            ])
        )
    elif data == "show_manifesto":
        manifesto = (
            "<b>cllllllllllllb manifesto</b>\n\n"
            "<b>collaba</b> is a bunch of people who can’t stop making stuff and hyping each other up. "
            "It was born ‘cause we wanted a space where no one had to pretend to “fit in”\n\n"
            "<b>music</b> is not something we drop — it’s something we accidentally turn into a whole thing at 2 am\n\n"
            "<blockquote>WHERE WEIRD IS HOT AND ROUGH EDGES MEAN IT’S ALIVE</blockquote>\n\n"
            "That bizarre voice memo you almost deleted? Yeah, that’s the one! We were looking for that tune! "
            "We’re not afraid of things that make the algorithm upset 🥲\n\n"
            "We move like a plastic bags, chaotic floating on the wind. Somebody drops an idea in chat — 💥. "
            "Someone’s mixing, someone’s drawing, someone’s pitching a blog. You could be a DJ, a coder, a poet, "
            "or just someone with oddly good vibes — it all matters 💯\n\n"
            "<blockquote>"
            "collaba\n"
            "doesn’t chase formats - chases goose bumps\n"
            "doesn’t sign artists - notice them and then build a tiny universe around them\n"
            "doesn’t care how many streams you got - care if someone played it three times in a row ‘cause it hit"
            "</blockquote>\n\n"
            "We’re not promising fame or funding or fame and funding. We’re promising to stick around from "
            "“this is just a draft but…” to a gig in a country you’ve never been to 😎\n\n"
            "No contracts here. No KPIs. But sometimes you get ten people saying “omg” at once. Creativity here is more "
            "“send voice note while eating noodles” 🍜  than “boardroom vibe.”\n\n"
            "If you’re here, you’re already part of the magic. Right now. Not when you’re “ready.”"
        )
        keyboard = [
            [InlineKeyboardButton("100% vibing with your values", callback_data="vibe_yes")],
            [InlineKeyboardButton("not my vibe, sorry folks", callback_data="vibe_no")]
        ]
        await query.message.reply_text(manifesto, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "vibe_yes":
        await query.message.reply_text("Next step coming soon…")
    elif data == "vibe_no":
        await query.message.reply_text("No worries! See you around.")

def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
