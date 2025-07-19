import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from notion_client import Client as NotionClient

# ========== ENVIRONMENT VARIABLES ==========
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if not TELEGRAM_TOKEN:
    raise RuntimeError("BOT_TOKEN env var is missing")
if not (NOTION_TOKEN and DATABASE_ID):
    raise RuntimeError("Notion env vars are missing")

# ========== INITIALIZE CLIENTS ==========
logging.basicConfig(level=logging.INFO)
notion = NotionClient(auth=NOTION_TOKEN)
user_data: dict[int, dict[str, str]] = {}
user_page_id: dict[int, str] = {}

# ========== STATES ==========
A_NAME = 0

# ========== START & HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Hey there, meet cllb — the music community-label that kinda accidentally started itself "
        "(but stuck around on purpose)"
    )
    keyboard = [[InlineKeyboardButton("NICE", callback_data="nice")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.from_user.id

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
        # возвращаемся к шагу о манифесте
        text = "Few questions coming up — but first, read the manifesto. It’s kinda sacred"
        keyboard = [
            [InlineKeyboardButton("The Important Doc", callback_data="read_doc")],
            [InlineKeyboardButton("No Time To Read", callback_data="skip_doc")],
        ]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "read_doc":
        manifesto = (
            "the cllllllllllllb manifesto\n\n"
            "We’re not a “label”. We’re a crew, a bunch of people who can’t stop making stuff and hyping each other up. "
            "Music’s not something we drop — it’s something we accidentally turn into a whole thing at 2am. Creativity here is more “send voice note while eating noodles” than “boardroom energy.”\n\n"
            "We don’t care how many streams you got. We care if someone played it three times in a row ‘cause it hit. We don’t chase formats. we chase goosebumps.\n\n"
            "We don’t sign artists. we notice them. and then build a tiny universe around them.\n"
            "cllb was born ‘cause we wanted a space where no one had to pretend to “fit in.”\n\n"
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
        keyboard = [
            [InlineKeyboardButton("100% Vibing With Your Values", callback_data="agree_manifesto")],
            [InlineKeyboardButton("Not My Vibe Sorry Folks", callback_data="reject_manifesto")],
        ]
        await query.message.reply_text(manifesto, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "reject_manifesto":
        text = "Oh and hey! See you!"
        keyboard = [[InlineKeyboardButton("Subscribe", url="https://linktree.com/cllllllllllllb")]]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "agree_manifesto":
        text = "Alrighty, your turn. Have we crossed paths before? 👀"
        keyboard = [[InlineKeyboardButton("Ok Intro Me 10 Min Tops", callback_data="start_survey")]]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "start_survey":
        text = "Who are you?"
        keyboard = [
            [InlineKeyboardButton("Artist", callback_data="role_artist")],
            [InlineKeyboardButton("Musician", callback_data="role_musician")],
            [InlineKeyboardButton("Designer", callback_data="role_designer")],
            [InlineKeyboardButton("Videomaker", callback_data="role_videomaker")],
            [InlineKeyboardButton("My Mom Call Me My Little Star", callback_data="role_star")],
        ]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "role_artist":
        # сохраняем базовые данные и запрашиваем имя
        user_data[chat_id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "Type": "Artist",
        }
        context.user_data["state"] = A_NAME
        await query.message.reply_text("Name / Artist name *")

# Обработка текста для состояния A_NAME
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    state = context.user_data.get("state")
    if state == A_NAME:
        name = update.message.text.strip()
        user_data[chat_id]["Name"] = name
        # создаём запись в Notion
        created = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": name}}]},
                "Telegram": {"rich_text": [{"text": {"content": user_data[chat_id]["Telegram"]}}]},
                "Type": {"select": {"name": user_data[chat_id]["Type"]}},
            },
        )
        user_page_id[chat_id] = created["id"]
        # здесь дальше можно запрашивать следующие поля
        # сбрасываем состояние
        context.user_data.pop("state", None)
        await update.message.reply_text("Got it! What's next?")

# ========== MAIN ==========
def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
