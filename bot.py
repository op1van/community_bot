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
    DEMOS, LIVE, COLLABORATIONS, EXPERIENCE, PLANS,
    D_NAME, D_COUNTRY, D_OCCUPATION, D_GENRE, D_DEMOS, D_ABOUT, D_INSTAGRAM, D_INSTRUMENTS_CONTEXT, D_PLANS,
    A_NAME, A_COUNTRY, A_INSTAGRAM, A_SPOTIFY, A_ABOUT, A_PLANS, A_LIVE, A_DEMOS, A_COLLABORATIONS, A_SONGWRITER, A_PRODUCE,
    V_NAME, V_COUNTRY, V_OCCUPATION, V_GENRE, V_DEMOS, V_INSTAGRAM, V_PLANS, V_INSTRUMENTS_CONTEXT, V_ABOUT,
    LS_NAME, LS_COUNTRY, LS_GENRE, LS_INSTAGRAM, LS_PLANS,
    POST_1, POST_2, POST_3, FINAL_CHOICE, VIBE_CHECK
) = range(53)

# ========== TEXT BLOCKS ==========

MANIFESTO_TEXT = (
    "the cllllllllllllb manifesto\n\n"
    "We’re not a “label”. We’re a crew, a bunch of people who can’t stop making stuff and hyping each other up. "
    "Music’s not something we drop — it’s something we accidentally turn into a whole thing at 2am. Creativity here is more “send voice note while eating noodles” than “boardroom energy.”\n\n"
    "We don’t care how many streams you got. We care if someone played it three times in a row ‘cause it hit. We don’t chase formats. we chase goosebumps.\n\n"
    "We don’t sign artists. we notice them. and then build a tiny universe around them.\n"
    "cllb was born ‘cause we wanted a space where no one had to pretend to “fit in.”\n\n"
    "Where weird is hot. and rough edges mean it’s alive. that weird voice memo you almost deleted? yeah, that’s the one. "
    "We’re not scared of stuff that makes the algorithm uncomfortable.\n\n"
    "We move like a pack of creatively chaotic raccoons. Somebody drops an idea in chat — boom. Someone’s mixing, someone’s drawing, someone’s pitching a blog. "
    "You could be a DJ, a coder, a poet, or just someone with oddly good vibes — it all matters.\n\n"
    "This isn’t an industry. It’s a group project with no teacher.\n\n"
    "We’re not promising fame or funding or fame and funding. We’re promising to stick around. "
    "from “this is just a draft but…” to a gig in a country you’ve never been to.\n\n"
    "There’s no contracts here. No KPIs. but sometimes you get a sticker and five people saying “omg” at once. If you’re here, you’re already part of the magic. Right now. Not when you’re “ready.”\n\n"
    "This isn’t business.\n"
    "This is lowkey a cult (just kidding)\n"
    "Not a product. A group hug in mp3.\n\n"
)

POSTFLOW_1 = (
    "Thank you! Got it!\n\n"
    "Ok, still here awesome just a few things left to share and you are allllmost here vibing with all of us:\n\n"
    "What is cllllllllllllb?\n\n"
    "We’re not a label-label.\n"
    "We’re a music-flavored community with zero chill for perfection and a soft spot for weird sounds, late-night ideas, and collabs that make no sense on paper.\n"
    "No contracts. No suits. No “what’s your monthly reach?”\n"
    "Just real people, real stuff, real moments.\n\n"
    "Our vibe / our mission\n\n"
    "We’re building a cultural glitch in the matrix.\n"
    "A home for songs that live in voice notes. Demos that never made it past “yo check this out.”\n"
    "Sounds that hit you in the chest before they hit the charts (if ever).\n\n"
    "From local Telegram chats to worldwide playlists.\n"
    "From kitchen-table mixes to vinyl.\n"
    "From \"idk if this is good\" to \"holy sh*t, this MOVES.\"\n\n"
    "We’re a door. A bridge. A meme. A moment.\n"
    "And yeah, a tiny bit of a movement.\n\n"
    "Our Not-So-Corporate Values\n\n"
    "Feeling over perfection\n"
    "If it hits — it fits. Even if recorded on a toaster.\n\n"
    "Co-creation over isolation\n"
    "You don’t have to suffer in silence. Suffer with us — it’s more fun. One beat in the chat and boom — a team is born.\n\n"
    "Community over industry\n"
    "We don’t shape-shift for Spotify. We make stuff for people with souls.\n\n"
    "Curation over contracts\n"
    "You’re not a stat. A release isn’t a KPI. It’s a time capsule.\n\n"
    "Self-joy over Pretending to be cooler than you are\n"
    "Cringe is real. So is freedom. We pick freedom."
)

POSTFLOW_2 = (
    "What We Believe\n\n"
    "We’re not chasing formats — we’re chasing goosebumps.\n"
    "If it doesn’t hit somewhere between your ribs and your third eye? Skip.\n\n"
    "We’re not here for viral hits (unless they’re accidentally iconic).\n"
    "We’re here for meaning, memory, and the kind of sound that makes your brain go huh, okay wow.\n\n"
    "This isn’t a startup pitch.\n"
    "It’s a bridge — between DIY chaos and pro polish. Between Notes app bars and festival stages. Between “idk if this is anything” and “this changed my week.”\n\n"
    "We don’t wait for green lights.\n"
    "We start where we are — busted laptop, cracked plugins, 2AM self-doubt and all.\n"
    "No permission needed.\n"
    "Just press go.\n\n"
    "How we actually operate\n\n"
    "If a track goes off?\n"
    "Boom — we spin up a team: mixheads, cover designers, write-y types, promo ninjas.\n"
    "One post in the chat and suddenly it’s a mini label sprint.\n\n"
    "There’s no form to apply.\n"
    "No “why do you want this role” nonsense.\n"
    "Just vibes and timing.\n"
    "If it clicks — we’re on.\n\n"
    "How the cllb crew’s got your back\n\n"
    "Got an idea? Cool.\n"
    "Drop it in chat and someone will hop on:\n"
    "mix your track\n"
    "sketch a cover\n"
    "write a lil blurb\n"
    "pitch it to press\n\n"
    "We talk in TG, calls, group threads, memes, sometimes IRL.\n"
    "You don’t have to be loud — just show up and care a little."
)

POSTFLOW_3 = (
    "What You Get With cllb\n\n"
    "If you’re an artist:\n"
    "• Real support (like actually)\n"
    "• Feedback that’s not from your mom\n"
    "• Help with mix, visuals, promo, and gigs\n"
    "• Space to test, mess up, bounce back\n"
    "• Digital & physical releases\n"
    "• Your track on a playlist next to someone famous (maybe)\n\n"
    "If you’re a creative/human person in the chat:\n"
    "• Add real stuff to your portfolio (not just client decks)\n"
    "• Be part of something weird + good\n"
    "• Launch side quests, join collabs\n"
    "• Use your skillset to do culture, not just content\n"
    "• Build trust, not titles\n\n"
    "If you’re breathing:\n"
    "• Friends\n"
    "• Chaos\n"
    "• Creative fuel\n"
    "• A stage we’re all building together\n\n"
    "The core Pokémons aka the cllb team\n\n"
    "They scout, curate, troubleshoot, build, and occasionally cry in the group chat.\n"
    "They keep it all moving, connecting dots and people like it’s a Mario Kart shortcut.\n\n"
    "DM us:\n"
    "Dasha – [@daria_kraski] – if you got lost\n"
    "Eugene – [@boysdontexist] – if you've lost your soul/ mind/ purpose\n"
    "Mila – [@MilaIgnatevaa] – if you've lost the cllb passwords\n"
    "Emil – [@colasigna] – if you've lost a cool guy from the community comments\n"
    "Bogdan – [@dolgopolsque] – if you found a great solution on how to make cllb even more visually attractive\n"
    "Ivan – [@🕳️] – one day he will text you first\n\n"
    "Final Words\n\n"
    "We’re not a label.\n"
    "We’re not an agency.\n"
    "We’re not chasing virality.\n"
    "We’re just making things that mean something, with people who care.\n"
    "You don’t need permission.\n"
    "You don’t need to be perfect.\n"
    "You just need to show up.\n"
)

FINAL_CHOICE_TEXT = (
    "Wanna get noticed? Just show up and do your thing"
)
VIBE_CHECK_TEXT = (
    "Do we have collaba vibe check-in? Yes, we do!\n\n"
    "1.     Be real. name things as it is, don’t shame them.\n"
    "2.     Feedback? Yes. Rudeness? Nope.\n"
    "3.     Burnt out? Say so. We’ll hold it down till you bounce back.\n"
    "4.     Made a promise? Keep it. No pressure, but don’t ghost.\n"
    "5.     Feeling lost or inactive for 2 weeks? You might quietly get dropped from the project. No hard feelings.\n"
    "6.     Talkers ≠ doers. If you’re just chatting but not contributing — you’re chilling, not collabing.\n"
    "7.     No bosses, no minions. But trust? Big yes.\n"
    "8.     No pedestals. We’re all figuring it out — even the OGs.\n"
    "9.     Leaving? All good. Just clean your room before you go.\n"
    "10.  Invite cool people. Protect the vibe.\n"
    "11.  Don’t lurk forever. Speak up. Help out.\n"
    "12.  Fail? Cool. Try again. This is a playground.\n"
    "13.  Start fires (creative ones). Light someone up.\n"
    "14.  No to war, hate, or cultural theft. We don’t work with people who oppress or dehumanise — in any form.\n"
    "15.  Respect the inner circle. Ask before sharing private convos.\n\n"
    "Bonus track:\n"
    "If you act on behalf of cllb — remember, you’re repping all of us. So filter the toxicity, and please… no -isms (sexism, racism, ableism, etc). Not our jam."
)
READY_FOR_FUN_TEXT = (
    "Looks like you're ready for some fun, huh?"
)
JUST_VIBING_TEXT = (
    "Oh and hey! See you!"
)

# ========== START SCREEN ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Hey there, meet cllb — the music community-label that kinda accidentally started itself (but stuck around on purpose)"
    )
    keyboard = [[InlineKeyboardButton("Nice", callback_data="step_1")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ========== BUTTON HANDLERS (MAIN FLOW) ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Manifesto steps
    if query.data == "step_1":
        text = "Few questions coming up — but first, read the manifesto. It’s kinda sacred"
        keyboard = [
            [InlineKeyboardButton("The Important Doc", callback_data="read_doc")],
            [InlineKeyboardButton("No Time To Read", callback_data="skip_doc")],
        ]
        await context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "skip_doc":
        text = "No skipping. It’s that fkng important"
        keyboard = [
            [InlineKeyboardButton("Ok", callback_data="end_bot")],
            [InlineKeyboardButton("Go Back", callback_data="step_1")],
        ]
        await context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "read_doc":
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
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=MANIFESTO_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    elif query.data == "reject_manifesto":
        keyboard = [
            [InlineKeyboardButton("Subscribe", url="https://linktr.ee/cllllllllllllb")],
        ]
        await context.bot.send_message(chat_id=query.message.chat_id, text=JUST_VIBING_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
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
        await context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "start_survey":
        keyboard = [
            [InlineKeyboardButton("Artist", callback_data="role_artist")],
            [InlineKeyboardButton("Musician", callback_data="role_musician")],
            [InlineKeyboardButton("Designer", callback_data="role_designer")],
            [InlineKeyboardButton("Videomaker", callback_data="role_videomaker")],
            [InlineKeyboardButton("Mom Calls Me My Little Star", callback_data="role_star")],
        ]
        await context.bot.send_message(chat_id=query.message.chat_id, text="Who are you?", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "end_bot":
        keyboard = [
            [InlineKeyboardButton("Subscribe", url="https://linktr.ee/cllllllllllllb")],
        ]
        await context.bot.send_message(chat_id=query.message.chat_id, text=JUST_VIBING_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data.clear()
        user_data.pop(query.from_user.id, None)
        user_page_id.pop(query.from_user.id, None)
    # ==== Ветка выбора роли ====
    elif query.data == "role_musician":
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
            "Type": "Musician",
        }
        context.user_data["state"] = NAME
        await context.bot.send_message(chat_id=query.message.chat_id, text="Name/artist name *")
    elif query.data == "role_artist":
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
            "Type": "Artist",
        }
        context.user_data["state"] = A_NAME
        await context.bot.send_message(chat_id=query.message.chat_id, text="Name/artist name")
    elif query.data == "role_designer":
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
            "Type": "Designer",
        }
        context.user_data["state"] = D_NAME
        await context.bot.send_message(chat_id=query.message.chat_id, text="What is your name?")
    elif query.data == "role_videomaker":
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
            "Type": "Videomaker",
        }
        context.user_data["state"] = V_NAME
        await context.bot.send_message(chat_id=query.message.chat_id, text="What is your name?")
    elif query.data == "role_star":
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
            "Type": "Little Star",
        }
        context.user_data["state"] = LS_NAME
        await context.bot.send_message(chat_id=query.message.chat_id, text="What is your name?")
    # ========== POSTFLOW ==========
    elif query.data == "continue_post_1":
        context.user_data["state"] = POST_2
        await context.bot.send_message(chat_id=query.message.chat_id, text=POSTFLOW_2, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_2")]]))
    elif query.data == "continue_post_2":
        context.user_data["state"] = POST_3
        await context.bot.send_message(chat_id=query.message.chat_id, text=POSTFLOW_3, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_3")]]))
    elif query.data == "continue_post_3":
        context.user_data["state"] = FINAL_CHOICE
        keyboard = [
            [InlineKeyboardButton("Ok Ok Ok I Promise", callback_data="ok_i_promise")],
            [InlineKeyboardButton("Lowkey Just Vibing And Watching", callback_data="just_vibing")],
        ]
        await context.bot.send_message(chat_id=query.message.chat_id, text=FINAL_CHOICE_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "just_vibing":
        keyboard = [
            [InlineKeyboardButton("Subscribe", url="https://linktr.ee/cllllllllllllb")],
        ]
        await context.bot.send_message(chat_id=query.message.chat_id, text=JUST_VIBING_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "back_to_final_choice":
        context.user_data["state"] = FINAL_CHOICE
        keyboard = [
            [InlineKeyboardButton("Ok Ok Ok I Promise", callback_data="ok_i_promise")],
            [InlineKeyboardButton("Lowkey Just Vibing And Watching", callback_data="just_vibing")],
        ]
        await context.bot.send_message(chat_id=query.message.chat_id, text=FINAL_CHOICE_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "ok_i_promise":
        context.user_data["state"] = VIBE_CHECK
        await context.bot.send_message(chat_id=query.message.chat_id, text=VIBE_CHECK_TEXT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("cllb, I Think Love U Already", callback_data="love_u")]]))
    elif query.data == "love_u":
        keyboard = [
            [InlineKeyboardButton("Subscribe", url="https://linktr.ee/cllllllllllllb")],
        ]
        await context.bot.send_message(chat_id=query.message.chat_id, text=JUST_VIBING_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data.clear()
        user_data.pop(query.from_user.id, None)
        user_page_id.pop(query.from_user.id, None)

# ========== TEXT HANDLER (ВСЕ ВОПРОСЫ ВСЕХ FLOW + POSTFLOW) ==========
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    text = update.message.text.strip()
    state = context.user_data.get("state")

    # --- MUSICIAN FLOW ---
    if state == NAME:
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
        context.user_data["state"] = INSTAGRAM
        await update.message.reply_text("Social networks")
    elif state == INSTAGRAM:
        user_data[chat_id]["Instagram"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = COUNTRY
        await update.message.reply_text("Location")
    elif state == COUNTRY:
        user_data[chat_id]["Country"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = OCCUPATION
        keyboard = [["Singer"], ["Sound Engineer"], ["Composer"], ["Arranger"], ["Sound Designer"]]
        await update.message.reply_text("What is your occupation as a musician?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    elif state == OCCUPATION:
        user_data[chat_id]["Occupation"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Occupation": {"select": {"name": text}}})
        context.user_data["state"] = INSTRUMENTS
        keyboard = [["Yep"], ["No"]]
        await update.message.reply_text("Do you play any instruments?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    elif state == INSTRUMENTS:
        user_data[chat_id]["Instruments"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instruments": {"select": {"name": text}}})
        context.user_data["state"] = INSTRUMENTS_CONTEXT
        await update.message.reply_text("What instruments do you play if you do?\nPut - if you are not", reply_markup=ReplyKeyboardRemove())
    elif state == INSTRUMENTS_CONTEXT:
        user_data[chat_id]["Instruments Context"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instruments Context": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = SING
        keyboard = [["Yes"], ["No"]]
        await update.message.reply_text("Do you sing?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    elif state == SING:
        user_data[chat_id]["Sing"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Sing": {"select": {"name": text}}})
        context.user_data["state"] = MIXING
        keyboard = [["Yes I Am A Professional"], ["Yes I Am An Amateur"], ["No"]]
        await update.message.reply_text("What is your proficiency in mixing/mastering?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    elif state == MIXING:
        user_data[chat_id]["Mixing"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Mixing": {"select": {"name": text}}})
        context.user_data["state"] = GENRE
        await update.message.reply_text("What genre do you identify with?\nIf multiple please write them all down", reply_markup=ReplyKeyboardRemove())
    elif state == GENRE:
        user_data[chat_id]["Genre"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Genre": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = DEMOS
        await update.message.reply_text("Track/song/demo/beat\nPlease send Soundcloud link")
    elif state == DEMOS:
        user_data[chat_id]["Demos"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Demos": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = LIVE
        await update.message.reply_text("Vocal performance (for singers)\nPlease send Soundcloud/YouTube link if you are not a singer put -")
    elif state == LIVE:
        user_data[chat_id]["Live"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Live": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = COLLABORATIONS
        keyboard = [["Face To Face"], ["Online"], ["I Am Not Sure"]]
        await update.message.reply_text("How do you want to collaborate with other musicians?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    elif state == COLLABORATIONS:
        user_data[chat_id]["Collaborations"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Collaborations": {"select": {"name": text}}})
        context.user_data["state"] = EXPERIENCE
        await update.message.reply_text("How many years have you been in music industry?", reply_markup=ReplyKeyboardRemove())
    elif state == EXPERIENCE:
        user_data[chat_id]["Experience"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Experience": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = PLANS
        await update.message.reply_text("Plans\nTell us about your upcoming releases projects any personal or career plans you have for the near future\nThis is your space to outline your creative direction and aspirations")
    elif state == PLANS:
        user_data[chat_id]["Plans"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = POST_1
        await update.message.reply_text(POSTFLOW_1, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_1")]]))

    # --- ARTIST FLOW ---
    elif state == A_NAME:
        user_data[chat_id]["Name"] = text
        created = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": text}}]},
                "Telegram": {"rich_text": [{"text": {"content": user_data[chat_id]["Telegram"]}}]},
                "Type": {"select": {"name": "Artist"}},
            },
        )
        user_page_id[chat_id] = created["id"]
        context.user_data["state"] = A_COUNTRY
        await update.message.reply_text("Country")
    elif state == A_COUNTRY:
        user_data[chat_id]["Country"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_INSTAGRAM
        await update.message.reply_text("Instagram")
    elif state == A_INSTAGRAM:
        user_data[chat_id]["Instagram"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_SPOTIFY
        await update.message.reply_text("Spotify")
    elif state == A_SPOTIFY:
        user_data[chat_id]["Spotify"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Spotify": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_ABOUT
        await update.message.reply_text("About me\nIf you want to share any links, put them here")
    elif state == A_ABOUT:
        user_data[chat_id]["About"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"About": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_PLANS
        await update.message.reply_text("Plans\nTell us about your upcoming releases, projects, any personal or career plans you have for the near future\nThis is your space to outline your creative direction and aspirations")
    elif state == A_PLANS:
        user_data[chat_id]["Plans"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_LIVE
        await update.message.reply_text("Live videos")
    elif state == A_LIVE:
        user_data[chat_id]["Live"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Live": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_DEMOS
        await update.message.reply_text("Demos\nOnly soundcloud, please")
    elif state == A_DEMOS:
        user_data[chat_id]["Demos"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Demos": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_COLLABORATIONS
        keyboard = [
            [InlineKeyboardButton("Yes", callback_data="artist_collab_yes")],
            [InlineKeyboardButton("No", callback_data="artist_collab_no")],
        ]
        await update.message.reply_text("Are you open for collaborations?", reply_markup=InlineKeyboardMarkup(keyboard))

    # --- DESIGNER FLOW ---
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
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = D_OCCUPATION
        keyboard = [
            [InlineKeyboardButton("Interface Designer", callback_data="designer_occ_interface")],
            [InlineKeyboardButton("Graphic Designer", callback_data="designer_occ_graphic")],
            [InlineKeyboardButton("Motion Designer", callback_data="designer_occ_motion")],
            [InlineKeyboardButton("Fashion Designer", callback_data="designer_occ_fashion")],
        ]
        await update.message.reply_text("What is your specialization?", reply_markup=InlineKeyboardMarkup(keyboard))
    elif state == D_GENRE:
        user_data[chat_id]["Genre"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Genre": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = D_DEMOS
        await update.message.reply_text("Portfolio")
    elif state == D_DEMOS:
        user_data[chat_id]["Demos"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Demos": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = D_ABOUT
        await update.message.reply_text("Describe your design style")
    elif state == D_ABOUT:
        user_data[chat_id]["About"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"About": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = D_INSTAGRAM
        await update.message.reply_text("Social networks")
    elif state == D_INSTAGRAM:
        user_data[chat_id]["Instagram"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = D_INSTRUMENTS_CONTEXT
        await update.message.reply_text("What programs/softwares and tools do you use in your work?")
    elif state == D_INSTRUMENTS_CONTEXT:
        user_data[chat_id]["Instruments Context"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instruments Context": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = D_PLANS
        await update.message.reply_text("Tell a bit about the idea you would like to host with collaba community")
    elif state == D_PLANS:
        user_data[chat_id]["Plans"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = POST_1
        await update.message.reply_text(POSTFLOW_1, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_1")]]))

    # --- VIDEOMAKER FLOW ---
    elif state == V_NAME:
        user_data[chat_id]["Name"] = text
        created = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": text}}]},
                "Telegram": {"rich_text": [{"text": {"content": user_data[chat_id]["Telegram"]}}]},
                "Type": {"select": {"name": "Videomaker"}},
            },
        )
        user_page_id[chat_id] = created["id"]
        context.user_data["state"] = V_COUNTRY
        await update.message.reply_text("Your location?")
    elif state == V_COUNTRY:
        user_data[chat_id]["Country"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = V_OCCUPATION
        await update.message.reply_text("What is your position?")
    elif state == V_OCCUPATION:
        user_data[chat_id]["Occupation"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Occupation": {"select": {"name": text}}})
        context.user_data["state"] = V_GENRE
        await update.message.reply_text("What are your specific skills?")
    elif state == V_GENRE:
        user_data[chat_id]["Genre"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Genre": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = V_DEMOS
        await update.message.reply_text("Portfolio")
    elif state == V_DEMOS:
        user_data[chat_id]["Demos"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Demos": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = V_INSTAGRAM
        await update.message.reply_text("Social networks")
    elif state == V_INSTAGRAM:
        user_data[chat_id]["Instagram"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = V_PLANS
        await update.message.reply_text("Tell a bit about the idea you would like to host with collaba community")
    elif state == V_PLANS:
        user_data[chat_id]["Plans"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = V_INSTRUMENTS_CONTEXT
        await update.message.reply_text("Do you have any equipment? If yes, what kind?")
    elif state == V_INSTRUMENTS_CONTEXT:
        user_data[chat_id]["Instruments Context"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instruments Context": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = V_ABOUT
        await update.message.reply_text("What programs and tools do you use in your work?")
    elif state == V_ABOUT:
        user_data[chat_id]["About"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"About": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = POST_1
        await update.message.reply_text(POSTFLOW_1, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_1")]]))

    # --- LITTLE STAR FLOW ---
    elif state == LS_NAME:
        user_data[chat_id]["Name"] = text
        created = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": text}}]},
                "Telegram": {"rich_text": [{"text": {"content": user_data[chat_id]["Telegram"]}}]},
                "Type": {"select": {"name": "Little Star"}},
            },
        )
        user_page_id[chat_id] = created["id"]
        context.user_data["state"] = LS_COUNTRY
        await update.message.reply_text("Your location?")
    elif state == LS_COUNTRY:
        user_data[chat_id]["Country"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = LS_GENRE
        await update.message.reply_text("What are your specific skills?")
    elif state == LS_GENRE:
        user_data[chat_id]["Genre"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Genre": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = LS_INSTAGRAM
        await update.message.reply_text("Social networks")
    elif state == LS_INSTAGRAM:
        user_data[chat_id]["Instagram"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = LS_PLANS
        await update.message.reply_text("Tell a bit about the idea you would like to host with collaba community")
    elif state == LS_PLANS:
        user_data[chat_id]["Plans"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = POST_1
        await update.message.reply_text(POSTFLOW_1, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_1")]]))


# ========== HANDLERS FOR INLINE BUTTONS (DESIGNER OCC, ARTIST COLLAB, SONGWRITER, PRODUCE) ==========
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
    notion.pages.update(page_id=user_page_id[chat_id], properties={"Occupation": {"select": {"name": occ}}})
    context.user_data["state"] = D_GENRE
    await context.bot.send_message(chat_id=query.message.chat_id, text="What are your specific skills?")
    await query.answer()

async def artist_collab_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    if query.data == "artist_collab_yes":
        collab = "Yes"
    elif query.data == "artist_collab_no":
        collab = "No"
    else:
        await query.answer()
        return
    user_data[chat_id]["Collaborations"] = collab
    notion.pages.update(page_id=user_page_id[chat_id], properties={"Collaborations": {"select": {"name": collab}}})
    context.user_data["state"] = A_SONGWRITER
    keyboard = [
        [InlineKeyboardButton("Yes I Am", callback_data="artist_sw_yes")],
        [InlineKeyboardButton("My Teammate Is", callback_data="artist_sw_teammate")],
        [InlineKeyboardButton("No", callback_data="artist_sw_no")],
    ]
    await context.bot.send_message(chat_id=query.message.chat_id, text="Are you a songwriter? Or someone from your team is?", reply_markup=InlineKeyboardMarkup(keyboard))
    await query.answer()

async def artist_songwriter_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    sw_map = {
        "artist_sw_yes": "Yes I Am",
        "artist_sw_teammate": "My Teammate Is",
        "artist_sw_no": "No"
    }
    sw = sw_map.get(query.data)
    if not sw:
        await query.answer()
        return
    user_data[chat_id]["Songwriter"] = sw
    notion.pages.update(page_id=user_page_id[chat_id], properties={"Songwriter": {"select": {"name": sw}}})
    context.user_data["state"] = A_PRODUCE
    keyboard = [
        [InlineKeyboardButton("Yes I Am A Professional", callback_data="artist_prod_prof")],
        [InlineKeyboardButton("Yes I Am An Amateur", callback_data="artist_prod_amateur")],
        [InlineKeyboardButton("No", callback_data="artist_prod_no")],
    ]
    await context.bot.send_message(chat_id=query.message.chat_id, text="Do you produce music yourself?", reply_markup=InlineKeyboardMarkup(keyboard))
    await query.answer()

async def artist_produce_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    prod_map = {
        "artist_prod_prof": "Yes I Am A Professional",
        "artist_prod_amateur": "Yes I Am An Amateur",
        "artist_prod_no": "No"
    }
    prod = prod_map.get(query.data)
    if not prod:
        await query.answer()
        return
    user_data[chat_id]["Produce"] = prod
    notion.pages.update(page_id=user_page_id[chat_id], properties={"Produce": {"select": {"name": prod}}})
    # ПОСТФЛОУ!
    context.user_data["state"] = POST_1
    await context.bot.send_message(chat_id=query.message.chat_id, text=POSTFLOW_1, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_1")]]))
    await query.answer()

# ========== MAIN ==========
def main() -> None:
    if not TELEGRAM_TOKEN:
        raise RuntimeError("BOT_TOKEN env var is missing")
    if not (NOTION_TOKEN and DATABASE_ID):
        raise RuntimeError("Notion env vars are missing")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(?!designer_occ_|artist_collab_|artist_sw_|artist_prod_).*"))
    app.add_handler(CallbackQueryHandler(designer_specialization_handler, pattern="^designer_occ_"))
    app.add_handler(CallbackQueryHandler(artist_collab_handler, pattern="^artist_collab_"))
    app.add_handler(CallbackQueryHandler(artist_songwriter_handler, pattern="^artist_sw_"))
    app.add_handler(CallbackQueryHandler(artist_produce_handler, pattern="^artist_prod_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
