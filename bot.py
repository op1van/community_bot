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
    # Designer states (добавлено)
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
    manifesto = (
        "the cllllllllllllb manifesto\n\n"
        "[ВСТАВЬ СЮДА ПОЛНЫЙ ТЕКСТ MANIFESTO БЕЗ СОКРАЩЕНИЙ]\n\n"
        "welcome to cllb."
    )
    text = (
        "Hey there, meet cllb — the music community-label that kinda accidentally started itself (but stuck around on purpose)"
    )
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
            "the cllllllllllllb manifesto\n\n"
            "[ВСТАВЬ СЮДА ПОЛНЫЙ ТЕКСТ MANIFESTO БЕЗ СОКРАЩЕНИЙ]\n\n"
            "welcome to cllb."
        )
        keyboard = [
            [
                InlineKeyboardButton(
                    "100% Vibing With Your Values",
                    callback_data="agree_manifesto",
                )
            ],
            [
                InlineKeyboardButton(
                    "Not My Vibe Sorry Folks",
                    callback_data="reject_manifesto",
                )
            ],
        ]
        await query.edit_message_text(
            manifesto,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=None,
        )
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
            [
                InlineKeyboardButton(
                    "Ok Intro Me 10 Min Tops",
                    callback_data="start_survey",
                )
            ]
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
    elif query.data == "role_musician":
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
            "Type": "Musician",
        }
        context.user_data["state"] = NAME
        await query.edit_message_text("Name/artist name *")
    # --- Новый блок: Designer ---
    elif query.data == "role_designer":
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
            "Type": "Designer",
        }
        context.user_data["state"] = D_NAME
        await query.edit_message_text("What is your name?")
    # Остальные роли можно добавить по аналогии

    # Designer specialization выбор через inline-кнопки
    # обработчик designer_specialization_handler — см. ниже

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    text = update.message.text.strip()
    state = context.user_data.get("state")

    # === MUSICIAN FLOW === (изначальный твой вариант)
    if state == NAME:
        user_data[chat_id]["Name"] = text
        created = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": user_data[chat_id]["Name"]}}]},
                "Telegram": {"rich_text": [{"text": {"content": user_data[chat_id]["Telegram"]}}]},
                "Type": {"select": {"name": user_data[chat_id]["Type"]}},
            },
        )
        user_page_id[chat_id] = created["id"]
        context.user_data["state"] = INSTAGRAM
        await update.message.reply_text("Social networks")
    elif state == INSTAGRAM:
        user_data[chat_id]["Instagram"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = COUNTRY
        await update.message.reply_text("Location")
    elif state == COUNTRY:
        user_data[chat_id]["Country"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Country": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = OCCUPATION
        keyboard = [
            ["Singer"],
            ["Sound Engineer"],
            ["Composer"],
            ["Arranger"],
            ["Sound Designer"],
        ]
        await update.message.reply_text(
            "What is your occupation as a musician?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
    elif state == OCCUPATION:
        user_data[chat_id]["Occupation"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Occupation": {"select": {"name": text}}},
        )
        context.user_data["state"] = INSTRUMENTS
        keyboard = [["Yep"], ["No"]]
        await update.message.reply_text(
            "Do you play any instruments?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
    elif state == INSTRUMENTS:
        user_data[chat_id]["Instruments"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Instruments": {"select": {"name": text}}},
        )
        context.user_data["state"] = INSTRUMENTS_CONTEXT
        await update.message.reply_text(
            "What instruments do you play if you do?\nPut - if you are not",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif state == INSTRUMENTS_CONTEXT:
        user_data[chat_id]["Instruments Context"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Instruments Context": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = SING
        keyboard = [["Yes"], ["No"]]
        await update.message.reply_text(
            "Do you sing?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
    elif state == SING:
        user_data[chat_id]["Sing"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Sing": {"select": {"name": text}}},
        )
        context.user_data["state"] = MIXING
        keyboard = [
            ["Yes I Am A Professional"],
            ["Yes I Am An Amateur"],
            ["No"],
        ]
        await update.message.reply_text(
            "What is your proficiency in mixing/mastering?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
    elif state == MIXING:
        user_data[chat_id]["Mixing"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Mixing": {"select": {"name": text}}},
        )
        context.user_data["state"] = GENRE
        await update.message.reply_text(
            "What genre do you identify with?\nIf multiple please write them all down",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif state == GENRE:
        user_data[chat_id]["Genre"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Genre": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = DEMOS
        await update.message.reply_text(
            "Track/song/demo/beat\nPlease send Soundcloud link"
        )
    elif state == DEMOS:
        user_data[chat_id]["Demos"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Demos": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = LIVE
        await update.message.reply_text(
            "Vocal performance (for singers)\nPlease send Soundcloud/YouTube link if you are not a singer put -"
        )
    elif state == LIVE:
        user_data[chat_id]["Live"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Live": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = COLLABORATIONS
        keyboard = [
            ["Face To Face"],
            ["Online"],
            ["I Am Not Sure"],
        ]
        await update.message.reply_text(
            "How do you want to collaborate with other musicians?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
    elif state == COLLABORATIONS:
        user_data[chat_id]["Collaborations"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Collaborations": {"select": {"name": text}}},
        )
        context.user_data["state"] = EXPERIENCE
        await update.message.reply_text(
            "How many years have you been in music industry?",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif state == EXPERIENCE:
        user_data[chat_id]["Experience"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Experience": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = PLANS
        await update.message.reply_text(
            "Plans\nTell us about your upcoming releases projects any personal or career plans you have for the near future\nThis is your space to outline your creative direction and aspirations"
        )
    elif state == PLANS:
        user_data[chat_id]["Plans"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Plans": {"rich_text": [{"text": {"content": text}}]}},
        )
        await update.message.reply_text("Thanks! Your answers have been saved. 🌟")
        del user_data[chat_id]
        del user_page_id[chat_id]
        context.user_data.clear()

    # === DESIGNER FLOW ===
    elif state == D_NAME:
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
    occ_map = {
        "designer_occ_interface": "Interface Designer",
        "designer_occ_graphic": "Graphic Designer",
        "designer_occ_motion": "Motion Designer",
        "designer_occ_fashion": "Fashion Designer",
    }
    occ = occ_map.get(query.data)
    if not occ:
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
