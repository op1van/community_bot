import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ========== ENVIRONMENT VARIABLES ==========
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")  # задействуем позже
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")  # задействуем позже

if not TELEGRAM_TOKEN:
    raise RuntimeError("BOT_TOKEN env var is missing")

logging.basicConfig(level=logging.INFO)

# ========== HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "Hey there, meet cllb — the music community-label that kinda accidentally started itself (but stuck around on purpose)"
    keyboard = [[InlineKeyboardButton("NICE", callback_data="nice")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "nice":
        text = "Few questions coming up — but first, read the manifesto. It’s kinda sacred"
        keyboard = [
            [InlineKeyboardButton("The Important Doc", callback_data="read_doc")],
            [InlineKeyboardButton("No Time To Read", callback_data="skip_doc")],
        ]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "skip_doc":
        text = "No skipping. It’s that fkng important"
        keyboard = [
            [InlineKeyboardButton("OK", callback_data="skip_ok")],
            [InlineKeyboardButton("Go Back", callback_data="skip_back")],
        ]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "skip_ok":
        text = "Oh and hey! See you!"
        keyboard = [[InlineKeyboardButton("Subscribe", url="https://linktree.com/cllllllllllllb")]]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "skip_back":
        # возвращаемся к предыдущему шагу
        text = "Hey there, meet cllb — the music community-label that kinda accidentally started itself (but stuck around on purpose)"
        keyboard = [[InlineKeyboardButton("NICE", callback_data="nice")]]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "read_doc":
        manifesto = (
            "the cllllllllllllb manifesto\n\n"
            "We’re not a \"label\". We’re a crew, a bunch of people who can’t stop making stuff and hyping each other up. "
            "Music’s not something we drop — it’s something we accidentally turn into a whole thing at 2am. Creativity here is more “send voice note while eating noodles” than “boardroom energy.”\n\n"
            "We don’t care how many streams you got. We care if someone played it three times in a row ‘cause it hit. We don’t chase formats. we chase goosebumps.\n\n"
            "We don’t sign artists. we notice them. and then build a tiny universe around them.\n"
            "cllb was born ‘cause we wanted a space where no one had to pretend to \"fit in.\"\n\n"
            "Where weird is hot. and rough edges mean it’s alive. that weird voice memo you almost deleted? yeah, that’s the one. "
            "We’re not scared of stuff that makes the algorithm uncomfortable.\n\n"
            "We move like a pack of creatively chaotic raccoons. Somebody drops an idea in chat — boom. Someone’s mixing, someone’s drawing, someone’s pitching a blog. "
            "You could be a DJ, a coder, a poet, or just someone with oddly good vibes — it all matters.\n\n"
            "This isn’t an industry. It’s a group project with no teacher.\n\n"
            "We’re not promising fame or funding or fame and funding. We’re promising to stick around. "
            "from “this is just a draft but…” to a gig in a country you’ve never been to.\n\n"
            "There’s no contracts here. No KPIs. but sometimes you get a sticker and five people saying “omg” at once. "
            "If you’re here, you’re already part of the magic. Right now. Not when you’re “ready.”\n\n"
            "This isn’t business.\n"
            "This is lowkey a cult (just kidding)\n"
            "Not a product. A group hug in mp3."
        )
        await query.message.reply_text(manifesto)

# ========== MAIN ==========
def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
