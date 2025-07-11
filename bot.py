import os
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

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

logging.basicConfig(level=logging.INFO)
notion = NotionClient(auth=NOTION_TOKEN)
user_data: dict[int, dict[str, str]] = {}
user_page_id: dict[int, str] = {}

(
    NAME,
    INSTAGRAM,
    COUNTRY,
    OCCUPATION,
    INSTRUMENTS,
    INSTRUMENTS_CONTEXT,
    SING,
    MIXING,
    GENRE,
    DEMOS,
    LIVE,
    COLLABORATIONS,
    EXPERIENCE,
    PLANS,
    # Designer states start here
    D_NAME,
    D_COUNTRY,
    D_OCCUPATION,
    D_GENRE,
    D_DEMOS,
    D_ABOUT,
    D_INSTAGRAM,
    D_INSTRUMENTS_CONTEXT,
    D_PLANS,
) = range(23)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Hey there, meet cllb — the music community-label that kinda accidentally started itself (but stuck around on purpose)"
    )
    keyboard = [[InlineKeyboardButton("Nice", callback_data="step_1")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "step_1":
        keyboard = [
            [InlineKeyboardButton("Artist", callback_data="role_artist")],
            [InlineKeyboardButton("Musician", callback_data="role_musician")],
            [InlineKeyboardButton("Designer", callback_data="role_designer")],
            [InlineKeyboardButton("Videomaker", callback_data="role_videomaker")],
            [InlineKeyboardButton("Mom Calls Me My Little Star", callback_data="role_star")],
        ]
        await query.edit_message_text("Who are you?", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "role_designer":
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
            "Type": "Designer",
        }
        context.user_data["state"] = D_NAME
        await query.edit_message_text("What is your name?")
    # musician flow below (не трогаем), остальные роли можно добавить по аналогии

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    text = update.message.text.strip()
    state = context.user_data.get("state")

    # === DESIGNER FLOW ===
    if state == D_NAME:
        user_data[chat_id]["Name"] = text
        created = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": text}}]},
                "Telegram": {"rich_text": [{"text": {"content": user_data[chat_id]["Telegram"]}}]},
                "Type": {"select": {"name": "Designer"}},
            },
        )
        user_page_id[chat_id] = created["id"]
        context.user_data["state"] = D_COUNTRY
        await update.message.reply_text("Your location?")
    elif state == D_COUNTRY:
        user_data[chat_id]["Country"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Country": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = D_OCCUPATION
        keyboard = [
            [InlineKeyboardButton("Interface Designer", callback_data="designer_occ_interface")],
            [InlineKeyboardButton("Graphic Designer", callback_data="designer_occ_graphic")],
            [InlineKeyboardButton("Motion Designer", callback_data="designer_occ_motion")],
            [InlineKeyboardButton("Fashion Designer", callback_data="designer_occ_fashion")],
        ]
        await update.message.reply_text(
            "What is your specialization?",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    elif state == D_GENRE:
        user_data[chat_id]["Genre"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Genre": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = D_DEMOS
        await update.message.reply_text("Portfolio")
    elif state == D_DEMOS:
        user_data[chat_id]["Demos"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Demos": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = D_ABOUT
        await update.message.reply_text("Describe your design style")
    elif state == D_ABOUT:
        user_data[chat_id]["About"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"About": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = D_INSTAGRAM
        await update.message.reply_text("Social networks")
    elif state == D_INSTAGRAM:
        user_data[chat_id]["Instagram"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = D_INSTRUMENTS_CONTEXT
        await update.message.reply_text("What programs/softwares and tools do you use in your work?")
    elif state == D_INSTRUMENTS_CONTEXT:
        user_data[chat_id]["Instruments Context"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Instruments Context": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = D_PLANS
        await update.message.reply_text("Tell a bit about your dream in our project: your ideas for collaba community")
    elif state == D_PLANS:
        user_data[chat_id]["Plans"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Plans": {"rich_text": [{"text": {"content": text}}]}},
        )
        await update.message.reply_text("Thanks! Your answers have been saved. 🌟")
        del user_data[chat_id]
        del user_page_id[chat_id]
        context.user_data.clear()

async def designer_specialization_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    if query.data == "designer_occ_interface":
        occ = "Interface Designer"
    elif query.data == "designer_occ_graphic":
        occ = "Graphic Designer"
    elif query.data == "designer_occ_motion":
        occ = "Motion Designer"
    elif query.data == "designer_occ_fashion":
        occ = "Fashion Designer"
    else:
        await query.answer()
        return

    user_data[chat_id]["Occupation"] = occ
    notion.pages.update(
        page_id=user_page_id[chat_id],
        properties={"Occupation": {"select": {"name": occ}}},
    )
    context.user_data["state"] = D_GENRE
    await query.edit_message_text("What are your specific skills?")

def main() -> None:
    if not TELEGRAM_TOKEN:
        raise RuntimeError("BOT_TOKEN env var is missing")
    if not (NOTION_TOKEN and DATABASE_ID):
        raise RuntimeError("Notion env vars are missing")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(?!designer_occ_).*"))
    app.add_handler(CallbackQueryHandler(designer_specialization_handler, pattern="^designer_occ_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
