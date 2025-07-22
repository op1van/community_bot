import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes
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

user_state = {}

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
    chat_id = query.from_user.id

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
    elif data == "vibe_no":
        await query.message.reply_text(
            "😒",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("than subscribe", url="https://linktr.ee/cllllllllllllb")]
            ])
        )
    elif data == "vibe_yes":
        await query.message.reply_text(
            "Alrighty, have we crossed paths before?  Your turn 👀",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("10 mins to intro, but consent first", callback_data="consent_start")]
            ])
        )
    elif data == "consent_start":
        consent_text = (
            "<b>Consent *</b>\n\n"
            "By submitting this \"form\" you consent to the collection and processing of your personal data for the purpose of assembling a professional team. "
            "Your data may be transferred and stored outside your country of residence.  You can withdraw your consent at any time by letting @MilaIgnatevaa know. \n\n"
            "<a href='https://drive.google.com/file/d/1euqwTrqdoG2-9ySB9JivXdTT3Tb_R5sG/view'>I have read and agree to the Privacy Policy and Cookie Policy 🥸</a>"
        )
        await query.message.reply_text(consent_text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("10 mins to intro", callback_data="start_intro")]
            ])
        )
    elif data == "start_intro":
        await query.message.reply_text(
            "who are you?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("artist", callback_data="role_artist")],
                [InlineKeyboardButton("musician", callback_data="role_musician")],
                [InlineKeyboardButton("designer", callback_data="role_designer")],
                [InlineKeyboardButton("videomaker", callback_data="role_videomaker")],
                [InlineKeyboardButton("manager", callback_data="role_manager")],
                [InlineKeyboardButton("lawyer", callback_data="role_lawyer")],
                [InlineKeyboardButton("smm", callback_data="role_smm")],
                [InlineKeyboardButton("my mom calls me my little star", callback_data="role_star")],
            ])
        )
    elif data == "role_artist":
        user_state[chat_id] = "ask_name"
        await query.message.reply_text("What is your name, dear? \\ Artist name?")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    text = update.message.text.strip()
    state = user_state.get(chat_id)
    telegram_username = f"@{update.effective_user.username}" if update.effective_user.username else ""

    if state == "ask_name":
        # Сохраняем в Notion
        try:
            notion.pages.create(
                parent={"database_id": DATABASE_ID},
                properties={
                    "Name": {"title": [{"text": {"content": text}}]},
                    "Type": {"select": {"name": "Artist"}},
                    "Telegram": {"rich_text": [{"text": {"content": telegram_username}}]},
                }
            )
        except Exception as e:
            await update.message.reply_text(f"Не удалось записать в Notion: {e}")
        user_state[chat_id] = "ask_location"
        await update.message.reply_text(
            "Your location? We will send you an invitation to the local cllb party when it happens"
        )

def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
