import os
import re
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
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

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

notion = NotionClient(auth=NOTION_TOKEN)

user_data = {}
user_page_id = {}

(
    NAME,
    COUNTRY,
    OCCUPATION,
    GENRE,
    DEMOS,
    ABOUT,
    INSTAGRAM,
    INSTRUMENTS_CONTEXT,
    PLANS,
) = range(9)

def clean_text(text: str) -> str:
    return re.sub(r'[^a-zA-Z ]+', '', text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "Hey there, meet cllb — the music community-label that kinda accidentally started itself (but stuck around on purpose)"
    keyboard = [[InlineKeyboardButton("Nice", callback_data="step_1")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "step_1":
        text = "Few questions coming up — but first, read the manifesto. It’s kinda sacred"
        keyboard = [
            [InlineKeyboardButton("The Important Doc", callback_data="read_doc")],
            [InlineKeyboardButton("No Time To Read", callback_data="skip_doc")],
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "skip_doc":
        text = "No skipping. It’s that fkng important"
        keyboard = [
            [InlineKeyboardButton("Ok", callback_data="end_bot")],
            [InlineKeyboardButton("Go Back", callback_data="step_1")],
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "read_doc":
        manifesto = (
            "the cllllllllllllb manifesto\n\n[ВСТАВЬ СЮДА ПОЛНЫЙ ТЕКСТ MANIFESTO БЕЗ СОКРАЩЕНИЙ]\n\nwelcome to cllb."
        )
        keyboard = [
            [InlineKeyboardButton("100% Vibing With Your Values", callback_data="agree_manifesto")],
            [InlineKeyboardButton("Not My Vibe Sorry Folks", callback_data="reject_manifesto")],
        ]
        await query.edit_message_text(manifesto, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "reject_manifesto":
        text = "Oh and hey — hit that subscribe button\n\nhttps://linktree.com/cllllllllllllb"
        keyboard = [
            [InlineKeyboardButton("Ok", callback_data="end_bot")],
            [InlineKeyboardButton("Go Back", callback_data="read_doc")],
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "agree_manifesto":
        text = "Alrighty, your turn. Have we crossed paths before? 👀"
        keyboard = [
            [InlineKeyboardButton("Ok Intro Me 10 Min Tops", callback_data="start_survey")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "start_survey":
        keyboard = [
            [InlineKeyboardButton("Artist", callback_data="role_artist")],
            [InlineKeyboardButton("Musician", callback_data="role_musician")],
            [InlineKeyboardButton("Designer", callback_data="role_designer")],
            [InlineKeyboardButton("Videomaker", callback_data="role_videomaker")],
            [InlineKeyboardButton("Mom Calls Me My Little Star", callback_data="role_star")],
        ]
        await query.edit_message_text("Who are you?", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "end_bot":
        await query.edit_message_text("👋 Bye.")
    elif query.data == "role_designer":
        context.user_data["role_type"] = "Designer"
        # Создаём словарь сразу, но без остальных полей
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
            "Type": "Designer",
        }
        context.user_data["state"] = NAME
        await query.edit_message_text("What is your name?")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    text = update.message.text.strip()
    state = context.user_data.get("state")

    text_clean = clean_text(text)

    if chat_id not in user_data:
        # Вдруг пользователь начал писать без прохождения старта
        user_data[chat_id] = {
            "Telegram": f"@{update.effective_user.username}" if update.effective_user.username else "",
            "TG_ID": str(chat_id),
            "Type": context.user_data.get("role_type", "Designer"),
        }

    if state == NAME:
        user_data[chat_id]["Name"] = text_clean
        try:
            created = notion.pages.create(
                parent={"database_id": DATABASE_ID},
                properties={
                    "Name": {"title": [{"text": {"content": user_data[chat_id]["Name"]}}]},
                    "Telegram": {"rich_text": [{"text": {"content": user_data[chat_id]["Telegram"]}}]},
                    "Type": {"select": {"name": user_data[chat_id]["Type"]}},
                },
            )
            user_page_id[chat_id] = created["id"]
            logging.info(f"Created Notion page for user {chat_id} with ID {user_page_id[chat_id]}")
        except Exception as e:
            logging.error(f"Failed to create Notion page for user {chat_id}: {e}")
            await update.message.reply_text("Failed to save your data. Please try again.")
            return
        context.user_data["state"] = COUNTRY
        await update.message.reply_text("Your location?")
    elif state == COUNTRY:
        user_data[chat_id]["Country"] = text_clean
        if chat_id not in user_page_id:
            logging.error(f"user_page_id missing for user {chat_id} at COUNTRY step")
            await update.message.reply_text("Something went wrong. Please restart the bot.")
            return
        try:
            notion.pages.update(
                page_id=user_page_id[chat_id],
                properties={"Country": {"rich_text": [{"text": {"content": text_clean}}]}},
            )
            logging.info(f"Updated Country for user {chat_id}")
        except Exception as e:
            logging.error(f"Failed to update Country for user {chat_id}: {e}")
            await update.message.reply_text("Failed to save your data. Please try again.")
            return
        context.user_data["state"] = OCCUPATION
        keyboard = [
            ["Interface Designer"],
            ["Web Design"],
            ["Graphic Design"],
            ["Illustration"],
            ["3D Design"],
            ["Fashion Design"],
        ]
        await update.message.reply_text(
            "What is your specialization?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
    elif state == OCCUPATION:
        selected_option = text.strip()
        user_data[chat_id]["Occupation"] = selected_option
        if chat_id not in user_page_id:
            logging.error(f"user_page_id missing for user {chat_id} at OCCUPATION step")
            await update.message.reply_text("Something went wrong. Please restart the bot.")
            return
        try:
            notion.pages.update(
                page_id=user_page_id[chat_id],
                properties={"Occupation": {"select": {"name": selected_option}}},
            )
            logging.info(f"Updated Occupation for user {chat_id}")
        except Exception as e:
            logging.error(f"Failed to update Occupation for user {chat_id}: {e}")
            await update.message.reply_text("Failed to save your data. Please try again.")
            return
        context.user_data["state"] = GENRE
        await update.message.reply_text(
            "What are your specific skills?",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif state == GENRE:
        user_data[chat_id]["Genre"] = text_clean
        if chat_id not in user_page_id:
            logging.error(f"user_page_id missing for user {chat_id} at GENRE step")
            await update.message.reply_text("Something went wrong. Please restart the bot.")
            return
        try:
            notion.pages.update(
                page_id=user_page_id[chat_id],
                properties={"Genre": {"rich_text": [{"text": {"content": text_clean}}]}},
            )
            logging.info(f"Updated Genre for user {chat_id}")
        except Exception as e:
            logging.error(f"Failed to update Genre for user {chat_id}: {e}")
            await update.message.reply_text("Failed to save your data. Please try again.")
            return
        context.user_data["state"] = DEMOS
        await update.message.reply_text("Portfolio")
    elif state == DEMOS:
        user_data[chat_id]["Demos"] = text_clean
        if chat_id not in user_page_id:
            logging.error(f"user_page_id missing for user {chat_id} at DEMOS step")
            await update.message.reply_text("Something went wrong. Please restart the bot.")
            return
        try:
            notion.pages.update(
                page_id=user_page_id[chat_id],
                properties={"Demos": {"rich_text": [{"text": {"content": text_clean}}]}},
            )
            logging.info(f"Updated Demos for user {chat_id}")
        except Exception as e:
            logging.error(f"Failed to update Demos for user {chat_id}: {e}")
            await update.message.reply_text("Failed to save your data. Please try again.")
            return
        context.user_data["state"] = ABOUT
        await update.message.reply_text("Describe your design style")
    elif state == ABOUT:
        user_data[chat_id]["About"] = text_clean
        if chat_id not in user_page_id:
            logging.error(f"user_page_id missing for user {chat_id} at ABOUT step")
            await update.message.reply_text("Something went wrong. Please restart the bot.")
            return
        try:
            notion.pages.update(
                page_id=user_page_id[chat_id],
                properties={"About": {"rich_text": [{"text": {"content": text_clean}}]}},
            )
            logging.info(f"Updated About for user {chat_id}")
        except Exception as e:
            logging.error(f"Failed to update About for user {chat_id}: {e}")
            await update.message.reply_text("Failed to save your data. Please try again.")
            return
        context.user_data["state"] = INSTAGRAM
        await update.message.reply_text("Social networks\nInstagram for example")
    elif state == INSTAGRAM:
        user_data[chat_id]["Instagram"] = text_clean
        if chat_id not in user_page_id:
            logging.error(f"user_page_id missing for user {chat_id} at INSTAGRAM step")
            await update.message.reply_text("Something went wrong. Please restart the bot.")
            return
        try:
            notion.pages.update(
                page_id=user_page_id[chat_id],
                properties={"Instagram": {"rich_text": [{"text": {"content": text_clean}}]}},
            )
            logging.info(f"Updated Instagram for user {chat_id}")
        except Exception as e:
            logging.error(f"Failed to update Instagram for user {chat_id}: {e}")
            await update.message.reply_text("Failed to save your data. Please try again.")
            return
        context.user_data["state"] = INSTRUMENTS_CONTEXT
        await update.message.reply_text("What programs softwares and tools do you use in your work")
    elif state == INSTRUMENTS_CONTEXT:
        user_data[chat_id]["Instruments Context"] = text_clean
        if chat_id not in user_page_id:
            logging.error(f"user_page_id missing for user {chat_id} at INSTRUMENTS_CONTEXT step")
            await update.message.reply_text("Something went wrong. Please restart the bot.")
            return
        try:
            notion.pages.update(
                page_id=user_page_id[chat_id],
                properties={"Instruments Context": {"rich_text": [{"text": {"content": text_clean}}]}},
            )
            logging.info(f"Updated Instruments Context for user {chat_id}")
        except Exception as e:
            logging.error(f"Failed to update Instruments Context for user {chat_id}: {e}")
            await update.message.reply_text("Failed to save your data. Please try again.")
            return
        context.user_data["state"] = PLANS
        await update.message.reply_text("Tell a bit about your dream in our project\nYour ideas for collaba community")
    elif state == PLANS:
        user_data[chat_id]["Plans"] = text_clean
        if chat_id not in user_page_id:
            logging.error(f"user_page_id missing for user {chat_id} at PLANS step")
            await update.message.reply_text("Something went wrong. Please restart the bot.")
            return
        try:
            notion.pages.update(
                page_id=user_page_id[chat_id],
                properties={"Plans": {"rich_text": [{"text": {"content": text_clean}}]}},
            )
            logging.info(f"Updated Plans for user {chat_id}")
        except Exception as e:
            logging.error(f"Failed to update Plans for user {chat_id}: {e}")
            await update.message.reply_text("Failed to save your data. Please try again.")
            return
        await update.message.reply_text("Thanks Your answers have been saved 🌟")
        del user_data[chat_id]
        del user_page_id[chat_id]
        context.user_data.clear()

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
