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
artist_data = {}

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
        artist_data[chat_id] = {}
        user_state[chat_id] = "ask_name"
        await query.message.reply_text("What is your name, dear? \\ Artist name?")
    elif data == "ok":
        # After final step, show vibe check-in
        vibe_text = (
            "<b>Do we have collaba vibe check-in? Yes, we do!</b>\n\n"
            "1. Be real. name things as it is, don’t shame them.\n"
            "2. Feedback? Yes. Rudeness? Nope.\n"
            "3. Burnt out? Say so. We’ll hold it down till you bounce back.\n"
            "4. Made a promise? Keep it. No pressure, but don’t ghost.\n"
            "5. Feeling lost or inactive for 2 weeks? You might quietly get dropped from the project. No hard feelings.\n"
            "6. Talkers ≠ doers. If you’re just chatting but not contributing — you’re chilling, not collabing.\n"
            "7. No bosses, no minions. But trust? Big yes.\n"
            "8. No pedestals. We’re all figuring it out — even the OGs.\n"
            "9. Leaving? All good. Just clean your room before you go.\n"
            "10. Invite cool people. Protect the vibe.\n"
            "11. Don’t lurk forever. Speak up. Help out.\n"
            "12. Fail? Cool. Try again. This is a playground.\n"
            "13. Start fires (creative ones). Light someone up.\n"
            "14. No to war, hate, or cultural theft. We don’t work with people who oppress or dehumanise — in any form.\n"
            "15. Respect the inner circle. Ask before sharing private convos.\n\n"
            "<blockquote>Bonus track:\nIf you act on behalf of cllb — remember, you’re repping all of us. So filter the toxicity, and please… no -isms (sexism, racism, ableism, etc). Not our jam.</blockquote>"
        )
        await query.message.reply_text(vibe_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("collaba, suppose I'm already сrushed on", callback_data="already_crushed")]
        ]))
    elif data == "already_crushed":
        what_you_get = (
            "<b>What you get with cllb</b>\n\n"
            "<b>If you’re an artist:</b>\n"
            "• Real support (like actually)\n"
            "• Feedback that’s not from your mom\n"
            "• Help with mix, visuals, promo, and gigs\n"
            "• Space to test, mess up, bounce back\n"
            "• Digital & physical releases\n"
            "• Your track on a playlist next to someone famous (maybe)\n\n"
            "<b>If you’re a creative/human person in the chat:</b>\n"
            "• Add real stuff to your portfolio (not just client decks)\n"
            "• Be part of something weird + good\n"
            "• Launch side quests, join collabs\n"
            "• Use your skillset to do culture, not just content\n"
            "• Build trust, not titles\n\n"
            "<b>If you’re breathing:</b>\n"
            "• Friends\n"
            "• Chaos\n"
            "• Creative fuel\n"
            "• A stage we’re all building together"
        )
        await query.message.reply_text(what_you_get, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("continue", callback_data="ask_dm")]
        ]))
    elif data == "ask_dm":
        dm_block = (
            "<b>Do you have a question? Ask them</b>\n\n"
            "They scout, curate, troubleshoot, build, and occasionally cry in the group chat. They keep it all moving, connecting dots and people like it’s a Mario Kart shortcut.\n\n"
            "DM:\n"
            "Dasha – [@daria_kraski] – if you got lost\n"
            "Eugene – [@boysdontexist] – if you've lost your soul/ mind/ purpose\n"
            "Mila – [@MilaIgnatevaa] – if you've lost the cllb passwords\n"
            "Emil – [@colasigna] – if you've lost a cool guy from the community comments\n"
            "Ivan – [@🕳️] – one day he will text you first\n"
        )
        await query.message.reply_text(dm_block, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("continue", callback_data="showup")]
        ]))
    elif data == "showup":
        await query.message.reply_text(
            "Wanna get noticed? Just show up and do your thing",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("OK OK OK I promise", callback_data="fun_ready")],
                [InlineKeyboardButton("lowkey just vibing and watching", callback_data="just_vibing")]
            ])
        )
    elif data == "just_vibing":
        await query.message.reply_text(
            "😒",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("than subscribe", url="https://linktr.ee/cllllllllllllb")]
            ])
        )
    elif data == "fun_ready":
        await query.message.reply_text(
            "Looks like you're ready for some fun, huh?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("join community", url="https://t.me/+p9m9pRjBvi4xNWMy")]
            ])
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    text = update.message.text.strip()
    state = user_state.get(chat_id)
    telegram_username = f"@{update.effective_user.username}" if update.effective_user.username else ""

    # Сценарий для Artist
    if state == "ask_name":
        artist_data[chat_id] = {
            "Name": text,
            "Type": "Artist",
            "Telegram": telegram_username,
        }
        user_state[chat_id] = "ask_location"
        await update.message.reply_text(
            "Your location? We will send you an invitation to the local cllb party when it happens"
        )
    elif state == "ask_location":
        artist_data[chat_id]["Location"] = text
        user_state[chat_id] = "ask_about"
        await update.message.reply_text(
            "In a few words tell us about yourself? Are you a songwriter? Or someone from your team is? Do you produce music yourself?  How do you prefer to collaborate with other musicians? Any upcoming releases, projects, or personal  plans? \n\nWe are here for U! So let us to know ⭐️ better 👀"
        )
    elif state == "ask_about":
        artist_data[chat_id]["About"] = text
        user_state[chat_id] = "ask_demo"
        await update.message.reply_text("Any fresh demos to share? Only soundcloud 💅🏿")
    elif state == "ask_demo":
        artist_data[chat_id]["Demo"] = text
        user_state[chat_id] = "ask_link"
        await update.message.reply_text("Please add the link - your web site \\ bandcamp \\ insta \\ spotify \\ youtube 👀")
    elif state == "ask_link":
        artist_data[chat_id]["Link"] = text
        user_state[chat_id] = "ask_idea"
        await update.message.reply_text("Tell a bit about the idea you would like to implement with collaba community? And what do you need to make a dream come true?")
    elif state == "ask_idea":
        artist_data[chat_id]["Idea"] = text
        # Сохраняем в Notion
        try:
            notion.pages.create(
                parent={"database_id": DATABASE_ID},
                properties={
                    "Name": {"title": [{"text": {"content": artist_data[chat_id]["Name"]}}]},
                    "Type": {"rich_text": [{"text": {"content": artist_data[chat_id]["Type"]}}]},
                    "Telegram": {"rich_text": [{"text": {"content": artist_data[chat_id]["Telegram"]}}]},
                    "Location": {"rich_text": [{"text": {"content": artist_data[chat_id]["Location"]}}]},
                    "About": {"rich_text": [{"text": {"content": artist_data[chat_id]["About"]}}]},
                    "Demo": {"rich_text": [{"text": {"content": artist_data[chat_id]["Demo"]}}]},
                    "Link": {"rich_text": [{"text": {"content": artist_data[chat_id]["Link"]}}]},
                    "Idea": {"rich_text": [{"text": {"content": artist_data[chat_id]["Idea"]}}]},
                }
            )
        except Exception as e:
            await update.message.reply_text(f"Не удалось записать в Notion: {e}")
        user_state[chat_id] = "final_thankyou"
        await update.message.reply_text(
            "Thank you! Got it!\n\nJust a few things left to share and you are allllmost here vibing with all of us 💿🥵",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ok", callback_data="ok")]
            ])
        )

def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
