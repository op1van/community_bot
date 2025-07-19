import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from notion_client import Client as NotionClient

# ========== ENVIRONMENT VARIABLES ==========
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if not TELEGRAM_TOKEN:
    raise RuntimeError("BOT_TOKEN env var is missing")
if not (NOTION_TOKEN and DATABASE_ID):
    raise RuntimeError("Notion env vars are missing")

# ========== NOTION CLIENT ==========
notion = NotionClient(auth=NOTION_TOKEN)

# ========== STORAGE ==========
user_data: dict[int, dict[str, str]] = {}
user_page_id: dict[int, str] = {}

# ========== STATES ==========
(
    A_NAME, A_COUNTRY, A_INSTAGRAM, A_SPOTIFY,
    A_ABOUT, A_PLANS, A_LIVE, A_DEMOS, A_COLLAB,
    A_SONGWRITER, A_PRODUCE
) = range(11)

# ========== POSTFLOW TEXT ==========
POSTFLOW_1 = (
    "Thank you! Got it!\n\n"
    "Ok, still here awesome just a few things left to share and you are allllmost here vibing with all of us:\n"
    "What is cllllllllllllb?\n\n"
    "We’re not a label-label.\n"
    "We’re a music-flavored community with zero chill for perfection and a soft spot for weird sounds, late-night ideas, and collabs that make no sense on paper. \\"
    "No contracts. No suits. No “what’s your monthly reach?” Just real people, real stuff, real moments. Our vibe / our mission\n\n"
    "We’re building a cultural glitch in the matrix. A home for songs that live in voice notes. Demos that never made it past “yo check this out.”\n"
    "Sounds that hit you in the chest before they hit the charts (if ever). From local Telegram chats to worldwide playlists. From kitchen-table mixes to vinyl. From \"idk if this is good\" to \"holy sh*t, this MOVES.\"\n"
    "We’re a door. A bridge. A meme. A moment. And yeah, a tiny bit of a movement. Our Not-So-Corporate Values\n\n"
    "Feeling over perfection\n"
    "If it hits — it fits. Even if recorded on a toaster.\n"
    "Co-creation over isolation\n"
    "You don’t have to suffer in silence. Suffer with us — it’s more fun. One beat in the chat and boom — a team is born.\n"
    "Community over industry\n"
    "We don’t shape-shift for Spotify. We make stuff for people with souls.\n"
    "Curation over contracts\n"
    "You’re not a stat. A release isn’t a KPI. It’s a time capsule.\n"
    "Self-joy over Pretending to be cooler than you are\n"
    "Cringe is real. So is freedom. We pick freedom."
)

# ========== START HANDLER ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Hey there, meet cllb — the music community-label that kinda accidentally started itself "
        "(but stuck around on purpose)"
    )
    keyboard = [[InlineKeyboardButton("NICE", callback_data="nice")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ========== BUTTON HANDLER ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.from_user.id

    # Step 1
    if data == "nice":
        await query.message.reply_text(
            "Few questions coming up — but first, read the manifesto. It’s kinda sacred",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("The Important Doc", callback_data="read_doc")],
                [InlineKeyboardButton("No Time To Read", callback_data="skip_doc")],
            ])
        )

    # Skip manifesto
    elif data == "skip_doc":
        await query.message.reply_text(
            "No skipping. It’s that fkng important",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("OK", callback_data="skip_ok")],
                [InlineKeyboardButton("Go Back", callback_data="skip_back")],
            ])
        )
    elif data == "skip_ok":
        await query.message.reply_text(
            "Oh and hey! See you!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Subscribe", url="https://linktree.com/cllllllllllllb")]
            ])
        )
    elif data == "skip_back":
        # back to manifesto prompt
        await query.message.reply_text(
            "Few questions coming up — but first, read the manifesto. It’s kinda sacred",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("The Important Doc", callback_data="read_doc")],
                [InlineKeyboardButton("No Time To Read", callback_data="skip_doc")],
            ])
        )

    # Read manifesto
    elif data == "read_doc":
        manifesto = (
            "the cllllllllllllb manifesto\n\n"
            "We’re not a “label”. We’re a crew... (и т.д.)"
        )
        await query.message.reply_text(
            manifesto,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("100% Vibing With Your Values", callback_data="agree_manifesto")],
                [InlineKeyboardButton("Not My Vibe Sorry Folks", callback_data="reject_manifesto")],
            ])
        )

    # Manifesto response
    elif data == "reject_manifesto":
        await query.message.reply_text(
            "Oh and hey! See you!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Subscribe", url="https://linktree.com/cllllllllllllb")]
            ])
        )
    elif data == "agree_manifesto":
        await query.message.reply_text(
            "Alrighty, your turn. Have we crossed paths before? 👀",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Ok Intro Me 10 Min Tops", callback_data="start_survey")]
            ])
        )

    # Start survey
    elif data == "start_survey":
        await query.message.reply_text(
            "Who are you?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Artist", callback_data="role_artist")],
                [InlineKeyboardButton("Musician", callback_data="role_musician")],
                [InlineKeyboardButton("Designer", callback_data="role_designer")],
                [InlineKeyboardButton("Videomaker", callback_data="role_videomaker")],
                [InlineKeyboardButton("My Mom Call Me My Little Star", callback_data="role_star")],
            ])
        )

    # Artist flow start
    elif data == "role_artist":
        user_data[chat_id] = {"Telegram": f"@{query.from_user.username}" if query.from_user.username else "", "Type": "Artist"}
        context.user_data["state"] = A_NAME
        await query.message.reply_text("Name / Artist name *")

    # Collaborations
    elif data in ("artist_collab_yes", "artist_collab_no"):
        collab = "Yes" if data == "artist_collab_yes" else "No"
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Collaborations": {"select": {"name": collab}}})
        context.user_data["state"] = A_SONGWRITER
        await query.message.reply_text(
            "Are you a songwriter? Or someone from your team is?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Yes I Am", callback_data="artist_sw_yes")],
                [InlineKeyboardButton("My Teammate Is", callback_data="artist_sw_teammate")],
                [InlineKeyboardButton("No", callback_data="artist_sw_no")],
            ])
        )

    # Songwriter
    elif data in ("artist_sw_yes", "artist_sw_teammate", "artist_sw_no"):
        sw_map = {"artist_sw_yes": "Yes I Am", "artist_sw_teammate": "My Teammate Is", "artist_sw_no": "No"}
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Songwriter": {"select": {"name": sw_map[data]}}})
        context.user_data["state"] = A_PRODUCE
        await query.message.reply_text(
            "Do you produce music yourself?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Yes I Am A Professional", callback_data="artist_prod_prof")],
                [InlineKeyboardButton("Yes I Am An Amateur", callback_data="artist_prod_amateur")],
                [InlineKeyboardButton("No", callback_data="artist_prod_no")],
            ])
        )

    # Produce
    elif data in ("artist_prod_prof", "artist_prod_amateur", "artist_prod_no"):
        prod_map = {"artist_prod_prof": "Yes I Am A Professional", "artist_prod_amateur": "Yes I Am An Amateur", "artist_prod_no": "No"}
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Produce": {"select": {"name": prod_map[data]}}})
        # Postflow message
        await query.message.reply_text(
            POSTFLOW_1,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_1")]])
        )

    # Continue postflow
    elif data == "continue_post_1":
        # Следующие шаги или финал
        await query.message.reply_text("Welcome to the crew! 🎉")

# ========== TEXT HANDLER ==========
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    text = update.message.text.strip()
    state = context.user_data.get("state")

    # Artist: Name
    if state == A_NAME:
        user_data[chat_id]["Name"] = text
        created = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": text}}]},
                "Telegram": {"rich_text": [{"text": {"content": user_data[chat_id]["Telegram"]}}]},
                "Type": {"select": {"name": user_data[chat_id]["Type"]}},
            },
        )
        user_page_id[chat_id] = created["id"]
        context.user_data["state"] = A_COUNTRY
        await update.message.reply_text("Country")

    # Artist: Country
    elif state == A_COUNTRY:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_INSTAGRAM
        await update.message.reply_text("Instagram")

    # Artist: Instagram
    elif state == A_INSTAGRAM:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_SPOTIFY
        await update.message.reply_text("Spotify")

    # Artist: Spotify
    elif state == A_SPOTIFY:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Spotify": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_ABOUT
        await update.message.reply_text(
            "About me\nIf you want to share any links, put them here"
        )

    # Artist: About
    elif state == A_ABOUT:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"About": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_PLANS
        await update.message.reply_text(
            "Plans\nTell us about your upcoming releases, projects, any personal or career plans you have for the near future. "
            "This is your space to outline your creative direction and aspirations"
        )

    # Artist: Plans
    elif state == A_PLANS:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_LIVE
        await update.message.reply_text("Live videos")

    # Artist: Live
    elif state == A_LIVE:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Live": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_DEMOS
        await update.message.reply_text("Demos\nOnly soundcloud, please")

    # Artist: Demos
    elif state == A_DEMOS:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Demos": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_COLLAB
        await update.message.reply_text(
            "Are you open for collaborations?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Yes", callback_data="artist_collab_yes")],
                [InlineKeyboardButton("No", callback_data="artist_collab_no")],
            ])
        )

# ========== MAIN ==========
def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
