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
    text = (
        "Hey there, meet cllb — the music community-label that kinda accidentally started itself (but stuck around on purpose)"
    )
    keyboard = [[InlineKeyboardButton("Nice", callback_data="step_1")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# === Inline-кнопки ===
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
            "We’re not a “label”. We’re a crew, a bunch of people who can’t stop making stuff and hyping each other up. "
            "Music’s not something we drop — it’s something we accidentally turn into a whole thing at 2am. "
            "Creativity here is more “send voice note while eating noodles” than “boardroom energy.”\n\n"
            "We don’t care how many streams you got. We care if someone played it three times in a row ‘cause it hit. "
            "We don’t chase formats. we chase goosebumps.\n\n"
            "We don’t sign artists. we notice them. and then build a tiny universe around them.\n"
            "cllb was born ‘cause we wanted a space where no one had to pretend to “fit in.”\n\n"
            "Where weird is hot. and rough edges mean it’s alive. that weird voice memo you almost deleted? yeah, that’s the one. "
            "We’re not scared of stuff that makes the algorithm uncomfortable.\n\n"
            "We move like a pack of creatively chaotic raccoons. Somebody drops an idea in chat — boom. "
            "Someone’s mixing, someone’s drawing, someone’s pitching a blog. "
            "You could be a DJ, a coder, a poet, or just someone with oddly good vibes — it all matters.\n\n"
            "This isn’t an industry. It’s a group project with no teacher.\n\n"
            "We’re not promising fame or funding or fame and funding. We’re promising to stick around.\n"
            "from “this is just a draft but…” to a gig in a country you’ve never been to.\n\n"
            "There’s no contracts here. No KPIs. but sometimes you get a sticker and five people saying “omg” at once. "
            "If you’re here, you’re already part of the magic. Right now. Not when you’re “ready.”\n\n"
            "This isn’t business.\n"
            "This is lowkey a cult (just kidding)\n"
            "Not a product. A group hug in mp3.\n\n"
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

    # (В будущем: здесь аналогично реализовать для других ролей)

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
                "Type": {"select": {"name": data["Type"]}},
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
