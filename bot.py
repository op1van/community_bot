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

logging.basicConfig(level=logging.INFO)
notion = NotionClient(auth=NOTION_TOKEN)
user_data: dict[int, dict[str, str]] = {}
user_page_id: dict[int, str] = {}

(
    # Artist states
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
    # Musician states (сдвигаются после 11)
    M_NAME,
    M_INSTAGRAM,
    M_COUNTRY,
    M_OCCUPATION,
    M_INSTRUMENTS,
    M_INSTRUMENTS_CONTEXT,
    M_SING,
    M_MIXING,
    M_GENRE,
    M_DEMOS,
    M_LIVE,
    M_COLLABORATIONS,
    M_EXPERIENCE,
    M_PLANS,
) = range(25)

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
            "...(manifesto text as before)...\n\n"
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
                    "Not My Vibe, Sorry Folks",
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
                    "Ok, Intro Me. 10 Min Tops",
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
            [InlineKeyboardButton("All Together", callback_data="role_all")],
            [InlineKeyboardButton("Mom Calls Me My Little Star", callback_data="role_star")],
        ]
        await query.edit_message_text("Who are you?", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "end_bot":
        await query.edit_message_text("👋 Bye.")
    elif query.data == "role_artist":
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
            "Type": "Artist",
        }
        context.user_data["state"] = NAME
        await query.edit_message_text("Name/artist name *")
    elif query.data == "role_musician":
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
            "Type": "Musician",
        }
        context.user_data["state"] = M_NAME
        await query.edit_message_text("Name/artist name *")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    text = update.message.text.strip()
    state = context.user_data.get("state")

    # === MUSICIAN FLOW (одна строка Notion) ===
    if state == M_NAME:
        user_data[chat_id]["Name"] = text
        created = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": user_data[chat_id]["Name"]}}]},
                "Telegram": {"rich_text": [{"text": {"content": user_data[chat_id]["Telegram"]}}]},
                "Type": {"select": {"name": user_data[chat_id]["Type"]}},
            },
        )
        # Сохраняем id строки
        user_page_id[chat_id] = created["id"]
        context.user_data["state"] = M_INSTAGRAM
        await update.message.reply_text("Instagram *\nLink, please")

    elif state == M_INSTAGRAM:
        user_data[chat_id]["Instagram"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = M_COUNTRY
        await update.message.reply_text("Country *")

    elif state == M_COUNTRY:
        user_data[chat_id]["Country"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Country": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = M_OCCUPATION
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

    elif state == M_OCCUPATION:
        user_data[chat_id]["Occupation"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Occupation": {"select": {"name": text}}},
        )
        context.user_data["state"] = M_INSTRUMENTS
        keyboard = [["Yep"], ["No"]]
        await update.message.reply_text(
            "Do you play any instruments?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        )

    elif state == M_INSTRUMENTS:
        user_data[chat_id]["Instruments"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Instruments": {"select": {"name": text}}},
        )
        if text.lower() == "yep":
            context.user_data["state"] = M_INSTRUMENTS_CONTEXT
            await update.message.reply_text("What instruments do you play?")
        else:
            user_data[chat_id]["Instruments Context"] = "-"
            context.user_data["state"] = M_SING
            keyboard = [["Yep"], ["No"]]
            await update.message.reply_text(
                "Do you sing?",
                reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
            )

    elif state == M_INSTRUMENTS_CONTEXT:
        user_data[chat_id]["Instruments Context"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Instruments Context": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = M_SING
        keyboard = [["Yep"], ["No"]]
        await update.message.reply_text(
            "Do you sing?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        )

    elif state == M_SING:
        user_data[chat_id]["Sing"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Sing": {"select": {"name": text}}},
        )
        if text.lower() == "yep":
            context.user_data["state"] = M_LIVE
            await update.message.reply_text(
                "Vocal performance (for singers)\nPlease send Soundcloud/YouTube link"
            )
        else:
            context.user_data["state"] = M_MIXING
            keyboard = [
                ["Yes, I Am A Professional"],
                ["Yes, I Am An Amateur"],
                ["No"],
            ]
            await update.message.reply_text(
                "What is your proficiency in mixing/mastering?",
                reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
            )
    elif state == M_LIVE:
        user_data[chat_id]["Live"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Live": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = M_MIXING
        keyboard = [
            ["Yes, I Am A Professional"],
            ["Yes, I Am An Amateur"],
            ["No"],
        ]
        await update.message.reply_text(
            "What is your proficiency in mixing/mastering?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
    elif state == M_MIXING:
        user_data[chat_id]["Mixing"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Mixing": {"select": {"name": text}}},
        )
        context.user_data["state"] = M_GENRE
        await update.message.reply_text(
            "What genre do you identify with?\nIf multiple please write them all down"
        )

    elif state == M_GENRE:
        user_data[chat_id]["Genre"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Genre": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = M_DEMOS
        await update.message.reply_text(
            "Track/song/demo/beat\nPlease send Soundcloud link"
        )
    elif state == M_DEMOS:
        user_data[chat_id]["Demos"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Demos": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = M_COLLABORATIONS
        keyboard = [
            ["Face To Face"],
            ["Online"],
            ["I Am Not Sure"],
        ]
        await update.message.reply_text(
            "How do you want to collaborate with other musicians?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
    elif state == M_COLLABORATIONS:
        user_data[chat_id]["Collaborations"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Collaborations": {"select": {"name": text}}},
        )
        context.user_data["state"] = M_EXPERIENCE
        await update.message.reply_text(
            "How many years have you been in music industry?"
        )
    elif state == M_EXPERIENCE:
        user_data[chat_id]["Experience"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Experience": {"rich_text": [{"text": {"content": text}}]}},
        )
        context.user_data["state"] = M_PLANS
        await update.message.reply_text(
            "Plans\nTell us about your upcoming releases, projects, any personal or career plans you have for the near future\nThis is your space to outline your creative direction and aspirations"
        )
    elif state == M_PLANS:
        user_data[chat_id]["Plans"] = text
        notion.pages.update(
            page_id=user_page_id[chat_id],
            properties={"Plans": {"rich_text": [{"text": {"content": text}}]}},
        )
        await update.message.reply_text("Thanks! Your answers have been saved. 🌟")
        del user_data[chat_id]
        del user_page_id[chat_id]
        context.user_data.clear()

    # === ARTIST FLOW (можешь скопировать из своего кода, логика аналогична ===
    # ...

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
