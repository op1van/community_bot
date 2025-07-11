"""
telegram_bot.py
Рабочий пример под python-telegram-bot v20+
Сохрани как bot.py (или другое имя) и деплой на Render.

❗️Чувствительные данные забираем из переменных окружения,
а не хардкодим в файле.
"""

import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from notion_client import Client as NotionClient

# === Константы из окружения ===
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# === Инициализация ===
logging.basicConfig(level=logging.INFO)
notion = NotionClient(auth=NOTION_TOKEN)
user_data: dict[int, dict[str, str]] = {}

# === Состояния ===
(
    NAME,
    COUNTRY,
    INSTAGRAM,
    SPOTIFY,
    ABOUT,
    PLANS,
    LIVE,
    DEMOS,
    COLLABS,
    SONGWRITER,
    PRODUCE,
) = range(11)

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "hey man there is collaba - the music community label that accidentally started itself"
    keyboard = [[InlineKeyboardButton("Nice", callback_data="step_1")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# === Inline-кнопки ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "step_1":
        text = "there are a few questions ahead we would love you to answer  but please read the manifesto first"
        keyboard = [
            [InlineKeyboardButton("the important doc", callback_data="read_doc")],
            [InlineKeyboardButton("no time to read", callback_data="skip_doc")],
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "skip_doc":
        text = "no option to go forward. sorry it is flkng important"
        keyboard = [
            [InlineKeyboardButton("ok", callback_data="end_bot")],
            [InlineKeyboardButton("go back", callback_data="step_1")],
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "read_doc":
        manifesto = (
            "*the cllllllllllllb manifesto*\n\n"
            "We’re not a “label”. We’re a crew...\n\n"
            "_welcome to cllb._"
        )
        keyboard = [
            [
                InlineKeyboardButton(
                    "i totally share your values, guys",
                    callback_data="agree_manifesto",
                )
            ],
            [
                InlineKeyboardButton(
                    "doesn't suits for me sorry guys",
                    callback_data="reject_manifesto",
                )
            ],
        ]
        await query.edit_message_text(
            manifesto,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    elif query.data == "reject_manifesto":
        text = "by the way subscribe\n\nhttps://linktree.com/cllllllllllllb"
        keyboard = [
            [InlineKeyboardButton("ok", callback_data="end_bot")],
            [InlineKeyboardButton("go back", callback_data="read_doc")],
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "agree_manifesto":
        text = "ok, thanks\nand now it is your turn.\nHave we met before??"
        keyboard = [
            [
                InlineKeyboardButton(
                    "ready to introduce myself / 10 mins is recommended time for the questionnaire",
                    callback_data="start_survey",
                )
            ]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "start_survey":
        keyboard = [
            [InlineKeyboardButton("artist", callback_data="role_artist")],
            [InlineKeyboardButton("musician", callback_data="role_musician")],
            [InlineKeyboardButton("designer", callback_data="role_designer")],
            [InlineKeyboardButton("videomaker", callback_data="role_videomaker")],
            [InlineKeyboardButton("all together", callback_data="role_all")],
            [InlineKeyboardButton("mom calls me my little star", callback_data="role_star")],
        ]
        await query.edit_message_text("who are you?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "end_bot":
        await query.edit_message_text("👋 Bye.")

    elif query.data == "role_artist":
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
        }
        context.user_data["state"] = NAME
        await query.edit_message_text("Name/artist name *")


# === Обработка текстовых ответов ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    text = update.message.text.strip()
    state = context.user_data.get("state")

    if state == NAME:
        user_data[chat_id]["Name"] = text
        context.user_data["state"] = COUNTRY
        await update.message.reply_text("Country *")

    elif state == COUNTRY:
        user_data[chat_id]["Country"] = text
        context.user_data["state"] = INSTAGRAM
        await update.message.reply_text("Instagram *\nLink, please")

    elif state == INSTAGRAM:
        user_data[chat_id]["Instagram"] = text
        context.user_data["state"] = SPOTIFY
        await update.message.reply_text("Spotify (if it exists)")

    elif state == SPOTIFY:
        user_data[chat_id]["Spotify"] = text
        context.user_data["state"] = ABOUT
        await update.message.reply_text("About me\nIf you want to share any links, put them here")

    elif state == ABOUT:
        user_data[chat_id]["About"] = text
        context.user_data["state"] = PLANS
        await update.message.reply_text("Plans *\nTell us about your upcoming releases, projects...")

    elif state == PLANS:
        user_data[chat_id]["Plans"] = text
        context.user_data["state"] = LIVE
        await update.message.reply_text("Live videos *")

    elif state == LIVE:
        user_data[chat_id]["Live"] = text
        context.user_data["state"] = DEMOS
        await update.message.reply_text("Demos *\nOnly SoundCloud, please")

    elif state == DEMOS:
        user_data[chat_id]["Demos"] = text
        context.user_data["state"] = COLLABS
        await update.message.reply_text(
            "Are you open for collaborations? *",
            reply_markup=ReplyKeyboardMarkup([["yes"], ["no"]], one_time_keyboard=True, resize_keyboard=True),
        )

    elif state == COLLABS:
        user_data[chat_id]["Collaborations"] = text
        context.user_data["state"] = SONGWRITER
        await update.message.reply_text(
            "Are you a songwriter? Or someone from your team is? *",
            reply_markup=ReplyKeyboardMarkup(
                [["yes i am"], ["my teammate is"], ["no"]],
                one_time_keyboard=True,
                resize_keyboard=True,
            ),
        )

    elif state == SONGWRITER:
        user_data[chat_id]["Songwriter"] = text
        context.user_data["state"] = PRODUCE
        await update.message.reply_text(
            "Do you produce music yourself? *",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["yes i am also a soundproducer"],
                    ["no it is someone from my team"],
                    ["no"],
                ],
                one_time_keyboard=True,
                resize_keyboard=True,
            ),
        )

    elif state == PRODUCE:
        user_data[chat_id]["Produce"] = text
        await update.message.reply_text("Thanks! Your answers have been saved. 🌟")

        data = user_data[chat_id]
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": data["Name"]}}]},
                "Telegram": {"rich_text": [{"text": {"content": data["Telegram"]}}]},
                "Country": {"rich_text": [{"text": {"content": data["Country"]}}]},
                "Instagram": {"rich_text": [{"text": {"content": data["Instagram"]}}]},
                "Spotify": {"rich_text": [{"text": {"content": data["Spotify"]}}]},
                "About": {"rich_text": [{"text": {"content": data["About"]}}]},
                "Plans": {"rich_text": [{"text": {"content": data["Plans"]}}]},
                "Live": {"rich_text": [{"text": {"content": data["Live"]}}]},
                "Demos": {"rich_text": [{"text": {"content": data["Demos"]}}]},
                "Collaborations": {"select": {"name": data["Collaborations"]}},
                "Songwriter": {"select": {"name": data["Songwriter"]}},
                "Produce": {"select": {"name": data["Produce"]}},
            },
        )

        # очистка
        del user_data[chat_id]
        context.user_data.clear()


# === Запуск ===
def main() -> None:
    if not TELEGRAM_TOKEN:
        raise RuntimeError("BOT_TOKEN env var is missing")
    if not (NOTION_TOKEN and DATABASE_ID):
        raise RuntimeError("Notion env vars are missing")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()


if __name__ == "__main__":
    main()
