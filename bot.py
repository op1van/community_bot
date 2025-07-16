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

# ========== ENV ==========
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

logging.basicConfig(level=logging.INFO)
notion = NotionClient(auth=NOTION_TOKEN)
user_data: dict[int, dict[str, str]] = {}
user_page_id: dict[int, str] = {}

# ========== STATES ==========
(
    NAME, INSTAGRAM, COUNTRY, OCCUPATION, INSTRUMENTS, INSTRUMENTS_CONTEXT, SING, MIXING, GENRE,
    DEMOS, EXPERIENCE,
    D_NAME, D_COUNTRY, D_OCCUPATION, D_GENRE, D_DEMOS, D_ABOUT, D_INSTAGRAM, D_INSTRUMENTS_CONTEXT, D_PLANS,
    A_NAME, A_COUNTRY, A_INSTAGRAM, A_SPOTIFY, A_DEMOS, A_SONGWRITER, A_PRODUCE,
    V_NAME, V_COUNTRY, V_OCCUPATION, V_GENRE, V_DEMOS, V_INSTAGRAM, V_PLANS, V_INSTRUMENTS_CONTEXT, V_ABOUT,
    LS_NAME, LS_COUNTRY, LS_GENRE, LS_INSTAGRAM, LS_PLANS,
    POST_1, POST_2, POST_3, FINAL_CHOICE, VIBE_CHECK
) = range(46)

# ========== TEXT BLOCKS ==========
POSTFLOW_1_PART1 = """what is cllllllllllllb?

we’re not a label-label.
we’re a music-flavored community with zero chill for perfection and a soft spot for weird sounds, late-night ideas, and collabs that make no sense on paper.
no contracts. no suits. no “what’s your monthly reach?”
just real people, real stuff, real moments."""

POSTFLOW_1_PART2 = """our vibe / our mission

we’re building a cultural glitch in the matrix.
a home for songs that live in voice notes. demos that never made it past “yo check this out.”
sounds that hit you in the chest before they hit the charts (if ever).

from local telegram chats to worldwide playlists.
from kitchen-table mixes to vinyl.
from "idk if this is good" to "holy sh*t, this moves."

we’re a door. a bridge. a meme. a moment.
and yeah, a tiny bit of a movement."""

POSTFLOW_1_PART3 = """our not-so-corporate values

feeling over perfection
if it hits — it fits. even if recorded on a toaster.

co-creation over isolation
you don’t have to suffer in silence. suffer with us — it’s more fun. one beat in the chat and boom — a team is born.

community over industry
we don’t shape-shift for spotify. we make stuff for people."""

POSTFLOW_2_PART1 = """what we believe

we’re not chasing formats — we’re chasing goosebumps.
if it doesn’t hit somewhere between your ribs and your third eye? skip.

we’re not here for viral hits (unless they’re accidentally iconic).
we’re here for meaning, memory, and the kind of sound that makes your brain go huh, okay wow.

this isn’t a startup pitch.
it’s a bridge — between diy chaos and pro polish. between notes app bars and festival stages. between “idk if this is anything” and “this changed my week.”

we don’t wait for green lights.
we start where we are — busted laptop, cracked plugins, 2am self-doubt and all.
no permission needed.
just press go."""

POSTFLOW_2_PART2 = """how we actually operate

if a track goes off?
boom — we spin up a team: mixheads, cover designers, write-y types, promo ninjas.
one post in the chat and suddenly it’s a mini label sprint.

there’s no form to apply.
no “why do you want this role” nonsense.
just vibes and timing.
if it clicks — we’re on."""

POSTFLOW_2_PART3 = """how the cllb crew’s got your back

dm us:
dasha – [@daria_kraski] – if you got lost
eugene – [@boysdontexist] – if you've lost your soul/ mind/ purpose
mila – [@milalgnatevaa] – if you've lost the cllb passwords
emil – [@colasigna] – if you've lost a cool guy from the community comments
bogdan – [@dolgopolsque] – if you found a great solution on how to make cllb even more visually attractive
ivan – [@ 🕳] – one day he will text you first"""

FINAL_CHOICE_TEXT = """wanna get noticed? just show up and do your thing"""

POSTFLOW_3 = """what you get with cllb team

if you’re an artist:
• real support (like actually)
• feedback that’s not from your mom
• help with mix, visuals, promo, and gigs
• space to test, mess up, bounce back
• digital & physical releases
• your track on a playlist next to someone famous (maybe)

if you’re a creative/human person in the chat:
• add real stuff to your portfolio (not just client decks)
• be part of something weird + good
• launch side quests, join collabs
• use your skillset to do culture, not just content
• build trust, not titles

if you’re breathing:
• friends
• chaos
• creative fuel
• a stage we’re all building together"""

POSTFLOW_FINAL = """the core pokémons

they scout, curate, troubleshoot, build, and occasionally cry in the group chat.
they keep it all moving, connecting dots and people like it’s a mario kart shortcut."""

FINAL_WORDS = """final words

we’re not a label.
we’re not an agency.
we’re not chasing virality.
we’re just making things that mean something, with people who care.
you don’t need permission.
you don’t need to be perfect.
you just need to show up."""

VIBE_CHECK_TEXT = """do we have collaba vibe check-in? yes, we do!

1. be real. name things as it is, don’t shame them.
2. feedback? yes. rudeness? nope.
3. burnt out? say so. we’ll hold it down till you bounce back.
4. made a promise? keep it. no pressure, but don’t ghost.
5. feeling lost or inactive for 2 weeks? you might quietly get dropped from the project. no hard feelings.
6. talkers ≠ doers. if you’re just chatting but not contributing — you’re chilling, not collabing.
7. no bosses, no minions. but trust? big yes.
8. no pedestals. we’re all figuring it out — even the ogs.
9. leaving? all good. just clean your room before you go.
10. invite cool people. protect the vibe.
11. don’t lurk forever. speak up. help out.
12. fail? cool. try again. this is a playground.
13. start fires (creative ones). light someone up.
14. no to war, hate, or cultural theft. we don’t work with people who oppress or dehumanise — in any form.
15. respect the inner circle. ask before sharing private convos.

bonus track:
if you act on behalf of cllb — remember, you’re repping all of us. so filter the toxicity, and please… no -isms (sexism, racism, ableism, etc). not our jam."""

# ========== BUTTON HANDLER ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "continue_post_1":
        await context.bot.send_message(chat_id=query.message.chat_id, text=POSTFLOW_1_PART2, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Got It", callback_data="continue_post_1b")]]))
    elif query.data == "continue_post_1b":
        await context.bot.send_message(chat_id=query.message.chat_id, text=POSTFLOW_1_PART3, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Got It", callback_data="continue_post_2")]]))
    elif query.data == "continue_post_2":
        await context.bot.send_message(chat_id=query.message.chat_id, text=POSTFLOW_2_PART1, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Got It", callback_data="continue_post_2b")]]))
    elif query.data == "continue_post_2b":
        await context.bot.send_message(chat_id=query.message.chat_id, text=POSTFLOW_2_PART2, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Got It", callback_data="continue_post_2c")]]))
    elif query.data == "continue_post_2c":
        await context.bot.send_message(chat_id=query.message.chat_id, text=POSTFLOW_2_PART3, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_3")]]))
    elif query.data == "continue_post_3":
        await context.bot.send_message(chat_id=query.message.chat_id, text=FINAL_CHOICE_TEXT, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Ok Ok Ok I Promise", callback_data="ok_i_promise")],
            [InlineKeyboardButton("Lowkey Just Vibing And Watching", callback_data="just_vibing")],
        ]))
    elif query.data == "ok_i_promise":
        await context.bot.send_message(chat_id=query.message.chat_id, text=POSTFLOW_3, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Got It", callback_data="final_pokemons")]]))
    elif query.data == "final_pokemons":
        await context.bot.send_message(chat_id=query.message.chat_id, text=POSTFLOW_FINAL, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Got It", callback_data="final_words")]]))
    elif query.data == "final_words":
        await context.bot.send_message(chat_id=query.message.chat_id, text=FINAL_WORDS, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Got It", callback_data="vibe_check")]]))
    elif query.data == "vibe_check":
        await context.bot.send_message(chat_id=query.message.chat_id, text=VIBE_CHECK_TEXT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Subscribe", url="https://t.me/+p9m9pRjBvi4xNWMy")]]))

# ========== MAIN ==========
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
