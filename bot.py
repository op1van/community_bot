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

# ========== env ==========
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

logging.basicConfig(level=logging.INFO)
notion = NotionClient(auth=NOTION_TOKEN)
user_data: dict[int, dict[str, str]] = {}
user_page_id: dict[int, str] = {}

# ========== states ==========
(
    name, instagram, country, occupation, instruments, instruments_context, sing, mixing, genre,
    demos, live, collaborations, experience, plans,
    d_name, d_country, d_occupation, d_genre, d_demos, d_about, d_instagram, d_instruments_context, d_plans,
    a_name, a_country, a_instagram, a_spotify, a_about, a_plans, a_live, a_demos, a_collaborations, a_songwriter, a_produce,
    v_name, v_country, v_occupation, v_genre, v_demos, v_instagram, v_plans, v_instruments_context, v_about,
    ls_name, ls_country, ls_genre, ls_instagram, ls_plans,
    post_1, post_2, post_3, final_choice, vibe_check
) = range(53)

# ========== text blocks ==========

MANIFESTO_TEXT = (
    "the cllllllllllllb manifesto\n\n"
    "we’re not a “label”. we’re a crew, a bunch of people who can’t stop making stuff and hyping each other up. "
    "music’s not something we drop — it’s something we accidentally turn into a whole thing at 2am. creativity here is more “send voice note while eating noodles” than “boardroom energy.”\n\n"
    "we don’t care how many streams you got. we care if someone played it three times in a row ‘cause it hit. we don’t chase formats. we chase goosebumps.\n\n"
    "we don’t sign artists. we notice them. and then build a tiny universe around them.\n"
    "cllb was born ‘cause we wanted a space where no one had to pretend to “fit in.”\n\n"
    "where weird is hot. and rough edges mean it’s alive. that weird voice memo you almost deleted? yeah, that’s the one. "
    "we’re not scared of stuff that makes the algorithm uncomfortable.\n\n"
    "we move like a pack of creatively chaotic raccoons. somebody drops an idea in chat — boom. someone’s mixing, someone’s drawing, someone’s pitching a blog. "
    "you could be a dj, a coder, a poet, or just someone with oddly good vibes — it all matters.\n\n"
    "this isn’t an industry. it’s a group project with no teacher.\n\n"
    "we’re not promising fame or funding or fame and funding. we’re promising to stick around. "
    "from “this is just a draft but…” to a gig in a country you’ve never been to.\n\n"
    "there’s no contracts here. no kpis. but sometimes you get a sticker and five people saying “omg” at once. if you’re here, you’re already part of the magic. right now. not when you’re “ready.”\n\n"
    "this isn’t business.\n"
    "this is lowkey a cult (just kidding)\n"
    "not a product. a group hug in mp3.\n\n"
    "welcome to cllb."
)

POSTFLOW_1 = (
    "what is cllllllllllllb?\n\n"
    "we’re not a label-label.\n"
    "we’re a music-flavored community with zero chill for perfection and a soft spot for weird sounds, late-night ideas, and collabs that make no sense on paper.\n"
    "no contracts. no suits. no “what’s your monthly reach?”\n"
    "just real people, real stuff, real moments.\n\n"
    "our vibe / our mission\n\n"
    "we’re building a cultural glitch in the matrix.\n"
    "a home for songs that live in voice notes. demos that never made it past “yo check this out.”\n"
    "sounds that hit you in the chest before they hit the charts (if ever).\n\n"
    "from local telegram chats to worldwide playlists.\n"
    "from kitchen-table mixes to vinyl.\n"
    "from \"idk if this is good\" to \"holy sh*t, this moves.\"\n\n"
    "we’re a door. a bridge. a meme. a moment.\n"
    "and yeah, a tiny bit of a movement.\n\n"
    "our not-so-corporate values\n\n"
    "feeling over perfection\n"
    "if it hits — it fits. even if recorded on a toaster.\n\n"
    "co-creation over isolation\n"
    "you don’t have to suffer in silence. suffer with us — it’s more fun. one beat in the chat and boom — a team is born.\n\n"
    "community over industry\n"
    "we don’t shape-shift for spotify. we make stuff for people with souls.\n\n"
    "curation over contracts\n"
    "you’re not a stat. a release isn’t a kpi. it’s a time capsule.\n\n"
    "self-joy over pretending to be cooler than you are\n"
    "cringe is real. so is freedom. we pick freedom."
)

POSTFLOW_2 = (
    "what we believe\n\n"
    "we’re not chasing formats — we’re chasing goosebumps.\n"
    "if it doesn’t hit somewhere between your ribs and your third eye? skip.\n\n"
    "we’re not here for viral hits (unless they’re accidentally iconic).\n"
    "we’re here for meaning, memory, and the kind of sound that makes your brain go huh, okay wow.\n\n"
    "this isn’t a startup pitch.\n"
    "it’s a bridge — between diy chaos and pro polish. between notes app bars and festival stages. between “idk if this is anything” and “this changed my week.”\n\n"
    "we don’t wait for green lights.\n"
    "we start where we are — busted laptop, cracked plugins, 2am self-doubt and all.\n"
    "no permission needed.\n"
    "just press go.\n\n"
    "how we actually operate\n\n"
    "if a track goes off?\n"
    "boom — we spin up a team: mixheads, cover designers, write-y types, promo ninjas.\n"
    "one post in the chat and suddenly it’s a mini label sprint.\n\n"
    "there’s no form to apply.\n"
    "no “why do you want this role” nonsense.\n"
    "just vibes and timing.\n"
    "if it clicks — we’re on.\n\n"
    "how the cllb crew’s got your back\n\n"
    "got an idea? cool.\n"
    "drop it in chat and someone will hop on:\n"
    "mix your track\n"
    "sketch a cover\n"
    "write a lil blurb\n"
    "pitch it to press\n\n"
    "we talk in tg, calls, group threads, memes, sometimes irl.\n"
    "you don’t have to be loud — just show up and care a little."
)

POSTFLOW_3 = (
    "what you get with cllb\n\n"
    "if you’re an artist:\n"
    "• real support (like actually)\n"
    "• feedback that’s not from your mom\n"
    "• help with mix, visuals, promo, and gigs\n"
    "• space to test, mess up, bounce back\n"
    "• digital & physical releases\n"
    "• your track on a playlist next to someone famous (maybe)\n\n"
    "if you’re a creative/human person in the chat:\n"
    "• add real stuff to your portfolio (not just client decks)\n"
    "• be part of something weird + good\n"
    "• launch side quests, join collabs\n"
    "• use your skillset to do culture, not just content\n"
    "• build trust, not titles\n\n"
    "if you’re breathing:\n"
    "• friends\n"
    "• chaos\n"
    "• creative fuel\n"
    "• a stage we’re all building together\n\n"
    "the core gremlins aka the cllb team\n\n"
    "they scout, curate, troubleshoot, build, and occasionally cry in the group chat.\n"
    "they keep it all moving, connecting dots and people like it’s a mario kart shortcut.\n\n"
    "dm us:\n"
    "dasha – [@daria_kraski]\n"
    "mila – [@milaignatevaa]\n"
    "eugene – [@boysdontexist]\n"
    "emil – [@colasigna]\n"
    "bogdan – [@dolgopolsque]\n"
    "ivan – [@🕳️]\n\n"
    "final words\n\n"
    "we’re not a label.\n"
    "we’re not an agency.\n"
    "we’re not chasing virality.\n"
    "we’re just making things that mean something, with people who care.\n"
    "you don’t need permission.\n"
    "you don’t need to be perfect.\n"
    "you just need to show up.\n"
    "welcome to cllllllllllllb."
)

FINAL_CHOICE_TEXT = (
    "wanna get noticed? just show up and do your thing"
)
VIBE_CHECK_TEXT = (
    "do we have collaba vibe check-in? yes, we do!\n\n"
    "1.     be real. name things as it is, don’t shame them.\n"
    "2.     feedback? yes. rudeness? nope.\n"
    "3.     burnt out? say so. we’ll hold it down till you bounce back.\n"
    "4.     made a promise? keep it. no pressure, but don’t ghost.\n"
    "5.     feeling lost or inactive for 2 weeks? you might quietly get dropped from the project. no hard feelings.\n"
    "6.     talkers ≠ doers. if you’re just chatting but not contributing — you’re chilling, not collabing.\n"
    "7.     no bosses, no minions. but trust? big yes.\n"
    "8.     no pedestals. we’re all figuring it out — even the ogs.\n"
    "9.     leaving? all good. just clean your room before you go.\n"
    "10.  invite cool people. protect the vibe.\n"
    "11.  don’t lurk forever. speak up. help out.\n"
    "12.  fail? cool. try again. this is a playground.\n"
    "13.  start fires (creative ones). light someone up.\n"
    "14.  no to war, hate, or cultural theft. we don’t work with people who oppress or dehumanise — in any form.\n"
    "15.  respect the inner circle. ask before sharing private convos.\n\n"
    "bonus track:\n"
    "if you act on behalf of cllb — remember, you’re repping all of us. so filter the toxicity, and please… no -isms (sexism, racism, ableism, etc). not our jam."
)
READY_FOR_FUN_TEXT = (
    "looks like you're ready for some fun, huh?"
)
JUST_VIBING_TEXT = (
    "oh and hey — hit that subscribe button\n\nhttps://linktree.com/cllllllllllllb"
)

# ========== start screen ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "hey there, meet cllb — the music community-label that kinda accidentally started itself (but stuck around on purpose)"
    )
    keyboard = [[InlineKeyboardButton("nice", callback_data="step_1")]]
    await update.message.reply_text(text)

# ========== button handlers (main flow) ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "step_1":
        text = "few questions coming up — but first, read the manifesto. it’s kinda sacred"
        keyboard = [
            [InlineKeyboardButton("the important doc", callback_data="read_doc")],
            [InlineKeyboardButton("no time to read", callback_data="skip_doc")],
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "skip_doc":
        text = "no skipping. it’s that fkng important"
        keyboard = [
            [InlineKeyboardButton("ok", callback_data="end_bot")],
            [InlineKeyboardButton("go back", callback_data="step_1")],
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "read_doc":
        keyboard = [
            [
                InlineKeyboardButton(
                    "100% vibing with your values",
                    callback_data="agree_manifesto",
                )
            ],
            [
                InlineKeyboardButton(
                    "not my vibe sorry folks",
                    callback_data="reject_manifesto",
                )
            ],
        ]
        await query.edit_message_text(
            MANIFESTO_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=None,
        )
    elif query.data == "reject_manifesto":
        text = JUST_VIBING_TEXT
        keyboard = [
            [InlineKeyboardButton("ok", callback_data="end_bot")],
            [InlineKeyboardButton("go back", callback_data="read_doc")],
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "agree_manifesto":
        text = "alrighty, your turn. have we crossed paths before? 👀"
        keyboard = [
            [
                InlineKeyboardButton(
                    "ok intro me 10 min tops",
                    callback_data="start_survey",
                )
            ]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "start_survey":
        keyboard = [
            [InlineKeyboardButton("artist", callback_data="role_artist")],
            [InlineKeyboardButton("musician", callback_data="role_musician")],
            [InlineKeyboardButton("designer", callback_data="role_designer")],
            [InlineKeyboardButton("videomaker", callback_data="role_videomaker")],
            [InlineKeyboardButton("mom calls me my little star", callback_data="role_star")],
        ]
        await query.edit_message_text("who are you?", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "end_bot":
        await query.edit_message_text("👋 bye.")
        context.user_data.clear()
        user_data.pop(query.from_user.id, None)
        user_page_id.pop(query.from_user.id, None)
    elif query.data == "role_musician":
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
            "Type": "musician",
        }
        context.user_data["state"] = name
        await query.edit_message_text("name/artist name *")
    elif query.data == "role_artist":
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
            "Type": "artist",
        }
        context.user_data["state"] = a_name
        await query.edit_message_text("name/artist name")
    elif query.data == "role_designer":
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
            "Type": "designer",
        }
        context.user_data["state"] = d_name
        await query.edit_message_text("what is your name?")
    elif query.data == "role_videomaker":
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
            "Type": "videomaker",
        }
        context.user_data["state"] = v_name
        await query.edit_message_text("what is your name?")
    elif query.data == "role_star":
        user_data[query.from_user.id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "TG_ID": str(query.from_user.id),
            "Type": "little star",
        }
        context.user_data["state"] = ls_name
        await query.edit_message_text("what is your name?")
    elif query.data == "continue_post_1":
        context.user_data["state"] = post_2
        await query.edit_message_text(POSTFLOW_2, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("continue", callback_data="continue_post_2")]]))
    elif query.data == "continue_post_2":
        context.user_data["state"] = post_3
        await query.edit_message_text(POSTFLOW_3, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("continue", callback_data="continue_post_3")]]))
    elif query.data == "continue_post_3":
        context.user_data["state"] = final_choice
        keyboard = [
            [InlineKeyboardButton("ok ok ok i promise", callback_data="ok_i_promise")],
            [InlineKeyboardButton("lowkey just vibing and watching", callback_data="just_vibing")],
        ]
        await query.edit_message_text(FINAL_CHOICE_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "just_vibing":
        keyboard = [
            [InlineKeyboardButton("ok", callback_data="end_bot")],
            [InlineKeyboardButton("go back", callback_data="back_to_final_choice")],
        ]
        await query.edit_message_text(JUST_VIBING_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "back_to_final_choice":
        context.user_data["state"] = final_choice
        keyboard = [
            [InlineKeyboardButton("ok ok ok i promise", callback_data="ok_i_promise")],
            [InlineKeyboardButton("lowkey just vibing and watching", callback_data="just_vibing")],
        ]
        await query.edit_message_text(FINAL_CHOICE_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "ok_i_promise":
        context.user_data["state"] = vibe_check
        await query.edit_message_text(VIBE_CHECK_TEXT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("cllb, i think love u already", callback_data="love_u")]]))
    elif query.data == "love_u":
        await query.edit_message_text(READY_FOR_FUN_TEXT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("join community", url="https://t.me/addlist/QfvdyHJcGfg2NGZi")]]))
        context.user_data.clear()
        user_data.pop(query.from_user.id, None)
        user_page_id.pop(query.from_user.id, None)

# ========== designer specialization handler ==========
async def designer_specialization_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    occ_map = {
        "designer_occ_interface": "interface designer",
        "designer_occ_graphic": "graphic designer",
        "designer_occ_motion": "motion designer",
        "designer_occ_fashion": "fashion designer",
    }
    occ = occ_map.get(query.data)
    if not occ:
        await query.answer()
        return
    user_data[chat_id]["Occupation"] = occ
    notion.pages.update(page_id=user_page_id[chat_id], properties={"Occupation": {"select": {"name": occ}}})
    context.user_data["state"] = d_genre
    await query.edit_message_text("what are your specific skills?")

# ========== artist collab/songwriter/produce handlers ==========
async def artist_collab_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    if query.data == "artist_collab_yes":
        collab = "yes"
    elif query.data == "artist_collab_no":
        collab = "no"
    else:
        await query.answer()
        return
    user_data[chat_id]["Collaborations"] = collab
    notion.pages.update(page_id=user_page_id[chat_id], properties={"Collaborations": {"select": {"name": collab}}})
    context.user_data["state"] = a_songwriter
    keyboard = [
        [InlineKeyboardButton("yes i am", callback_data="artist_sw_yes")],
        [InlineKeyboardButton("my teammate is", callback_data="artist_sw_teammate")],
        [InlineKeyboardButton("no", callback_data="artist_sw_no")],
    ]
    await query.edit_message_text("are you a songwriter? or someone from your team is?", reply_markup=InlineKeyboardMarkup(keyboard))

async def artist_songwriter_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    sw_map = {
        "artist_sw_yes": "yes i am",
        "artist_sw_teammate": "my teammate is",
        "artist_sw_no": "no"
    }
    sw = sw_map.get(query.data)
    if not sw:
        await query.answer()
        return
    user_data[chat_id]["Songwriter"] = sw
    notion.pages.update(page_id=user_page_id[chat_id], properties={"Songwriter": {"select": {"name": sw}}})
    context.user_data["state"] = a_produce
    keyboard = [
        [InlineKeyboardButton("yes i am a professional", callback_data="artist_prod_prof")],
        [InlineKeyboardButton("yes i am an amateur", callback_data="artist_prod_amateur")],
        [InlineKeyboardButton("no", callback_data="artist_prod_no")],
    ]
    await query.edit_message_text("do you produce music yourself?", reply_markup=InlineKeyboardMarkup(keyboard))

async def artist_produce_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    prod_map = {
        "artist_prod_prof": "yes i am a professional",
        "artist_prod_amateur": "yes i am an amateur",
        "artist_prod_no": "no"
    }
    prod = prod_map.get(query.data)
    if not prod:
        await query.answer()
        return
    user_data[chat_id]["Produce"] = prod
    notion.pages.update(page_id=user_page_id[chat_id], properties={"Produce": {"select": {"name": prod}}})
    context.user_data["state"] = post_1
    await query.edit_message_text(POSTFLOW_1, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("continue", callback_data="continue_post_1")]]))

# ========== text handler ==========
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    text = update.message.text.strip().lower()
    if any(c.isupper() for c in text):
        await update.message.reply_text("please use only lowercase letters 🌚")
        return

    state = context.user_data.get("state")

    # musician flow
    if state == name:
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
        context.user_data["state"] = instagram
        await update.message.reply_text("social networks")
    elif state == instagram:
        user_data[chat_id]["Instagram"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = country
        await update.message.reply_text("location")
    elif state == country:
        user_data[chat_id]["Country"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = occupation
        keyboard = [["singer"], ["sound engineer"], ["composer"], ["arranger"], ["sound designer"]]
        await update.message.reply_text("what is your occupation as a musician?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    elif state == occupation:
        user_data[chat_id]["Occupation"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Occupation": {"select": {"name": text}}})
        context.user_data["state"] = instruments
        keyboard = [["yep"], ["no"]]
        await update.message.reply_text("do you play any instruments?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    elif state == instruments:
        user_data[chat_id]["Instruments"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instruments": {"select": {"name": text}}})
        context.user_data["state"] = instruments_context
        await update.message.reply_text("what instruments do you play if you do?\nput - if you are not", reply_markup=ReplyKeyboardRemove())
    elif state == instruments_context:
        user_data[chat_id]["Instruments Context"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instruments Context": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = sing
        keyboard = [["yes"], ["no"]]
        await update.message.reply_text("do you sing?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    elif state == sing:
        user_data[chat_id]["Sing"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Sing": {"select": {"name": text}}})
        context.user_data["state"] = mixing
        keyboard = [["yes i am a professional"], ["yes i am an amateur"], ["no"]]
        await update.message.reply_text("what is your proficiency in mixing/mastering?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    elif state == mixing:
        user_data[chat_id]["Mixing"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Mixing": {"select": {"name": text}}})
        context.user_data["state"] = genre
        await update.message.reply_text("what genre do you identify with?\nif multiple please write them all down", reply_markup=ReplyKeyboardRemove())
    elif state == genre:
        user_data[chat_id]["Genre"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Genre": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = demos
        await update.message.reply_text("track/song/demo/beat\nplease send soundcloud link")
    elif state == demos:
        user_data[chat_id]["Demos"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Demos": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = live
        await update.message.reply_text("vocal performance (for singers)\nplease send soundcloud/youtube link if you are not a singer put -")
    elif state == live:
        user_data[chat_id]["Live"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Live": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = collaborations
        keyboard = [["face to face"], ["online"], ["i am not sure"]]
        await update.message.reply_text("how do you want to collaborate with other musicians?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    elif state == collaborations:
        user_data[chat_id]["Collaborations"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Collaborations": {"select": {"name": text}}})
        context.user_data["state"] = experience
        await update.message.reply_text("how many years have you been in music industry?", reply_markup=ReplyKeyboardRemove())
    elif state == experience:
        user_data[chat_id]["Experience"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Experience": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = plans
        await update.message.reply_text("plans\ntell us about your upcoming releases projects any personal or career plans you have for the near future\nthis is your space to outline your creative direction and aspirations")
    elif state == plans:
        user_data[chat_id]["Plans"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = post_1
        await update.message.reply_text(POSTFLOW_1, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("continue", callback_data="continue_post_1")]]))

    # artist flow
    elif state == a_name:
        user_data[chat_id]["Name"] = text
        created = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": text}}]},
                "Telegram": {"rich_text": [{"text": {"content": user_data[chat_id]["Telegram"]}}]},
                "Type": {"select": {"name": "artist"}},
            },
        )
        user_page_id[chat_id] = created["id"]
        context.user_data["state"] = a_country
        await update.message.reply_text("country")
    elif state == a_country:
        user_data[chat_id]["Country"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = a_instagram
        await update.message.reply_text("instagram")
    elif state == a_instagram:
        user_data[chat_id]["Instagram"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = a_spotify
        await update.message.reply_text("spotify")
    elif state == a_spotify:
        user_data[chat_id]["Spotify"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Spotify": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = a_about
        await update.message.reply_text("about me\nif you want to share any links, put them here")
    elif state == a_about:
        user_data[chat_id]["About"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"About": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = a_plans
        await update.message.reply_text("plans\ntell us about your upcoming releases, projects, any personal or career plans you have for the near future\nthis is your space to outline your creative direction and aspirations")
    elif state == a_plans:
        user_data[chat_id]["Plans"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = a_live
        await update.message.reply_text("live videos")
    elif state == a_live:
        user_data[chat_id]["Live"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Live": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = a_demos
        await update.message.reply_text("demos\nonly soundcloud, please")
    elif state == a_demos:
        user_data[chat_id]["Demos"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Demos": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = a_collaborations
        keyboard = [
            [InlineKeyboardButton("yes", callback_data="artist_collab_yes")],
            [InlineKeyboardButton("no", callback_data="artist_collab_no")],
        ]
        await update.message.reply_text("are you open for collaborations?", reply_markup=InlineKeyboardMarkup(keyboard))

    # designer flow
    elif state == d_name:
        user_data[chat_id]["Name"] = text
        created = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": text}}]},
                "Telegram": {"rich_text": [{"text": {"content": user_data[chat_id]["Telegram"]}}]},
                "Type": {"select": {"name": "designer"}},
            },
        )
        user_page_id[chat_id] = created["id"]
        context.user_data["state"] = d_country
        await update.message.reply_text("your location?")
    elif state == d_country:
        user_data[chat_id]["Country"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = d_occupation
        keyboard = [
            [InlineKeyboardButton("interface designer", callback_data="designer_occ_interface")],
            [InlineKeyboardButton("graphic designer", callback_data="designer_occ_graphic")],
            [InlineKeyboardButton("motion designer", callback_data="designer_occ_motion")],
            [InlineKeyboardButton("fashion designer", callback_data="designer_occ_fashion")],
        ]
        await update.message.reply_text("what is your specialization?", reply_markup=InlineKeyboardMarkup(keyboard))
    elif state == d_genre:
        user_data[chat_id]["Genre"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Genre": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = d_demos
        await update.message.reply_text("portfolio")
    elif state == d_demos:
        user_data[chat_id]["Demos"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Demos": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = d_about
        await update.message.reply_text("describe your design style")
    elif state == d_about:
        user_data[chat_id]["About"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"About": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = d_instagram
        await update.message.reply_text("social networks")
    elif state == d_instagram:
        user_data[chat_id]["Instagram"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = d_instruments_context
        await update.message.reply_text("what programs/softwares and tools do you use in your work?")
    elif state == d_instruments_context:
        user_data[chat_id]["Instruments Context"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instruments Context": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = d_plans
        await update.message.reply_text("tell a bit about your dream in our project: your ideas for collaba community")
    elif state == d_plans:
        user_data[chat_id]["Plans"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = post_1
        await update.message.reply_text(POSTFLOW_1, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("continue", callback_data="continue_post_1")]]))

    # videomaker flow
    elif state == v_name:
        user_data[chat_id]["Name"] = text
        created = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": text}}]},
                "Telegram": {"rich_text": [{"text": {"content": user_data[chat_id]["Telegram"]}}]},
                "Type": {"select": {"name": "videomaker"}},
            },
        )
        user_page_id[chat_id] = created["id"]
        context.user_data["state"] = v_country
        await update.message.reply_text("your location?")
    elif state == v_country:
        user_data[chat_id]["Country"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = v_occupation
        await update.message.reply_text("what is your position?")
    elif state == v_occupation:
        user_data[chat_id]["Occupation"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Occupation": {"select": {"name": text}}})
        context.user_data["state"] = v_genre
        await update.message.reply_text("what are your specific skills?")
    elif state == v_genre:
        user_data[chat_id]["Genre"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Genre": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = v_demos
        await update.message.reply_text("portfolio")
    elif state == v_demos:
        user_data[chat_id]["Demos"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Demos": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = v_instagram
        await update.message.reply_text("social networks")
    elif state == v_instagram:
        user_data[chat_id]["Instagram"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = v_plans
        await update.message.reply_text("tell a bit about your dream in our project: your ideas for collaba community")
    elif state == v_plans:
        user_data[chat_id]["Plans"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = v_instruments_context
        await update.message.reply_text("do you have any equipment? if yes, what kind?")
    elif state == v_instruments_context:
        user_data[chat_id]["Instruments Context"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instruments Context": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = v_about
        await update.message.reply_text("what programs and tools do you use in your work?")
    elif state == v_about:
        user_data[chat_id]["About"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"About": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = post_1
        await update.message.reply_text(POSTFLOW_1, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("continue", callback_data="continue_post_1")]]))

    # little star flow
    elif state == ls_name:
        user_data[chat_id]["Name"] = text
        created = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": text}}]},
                "Telegram": {"rich_text": [{"text": {"content": user_data[chat_id]["Telegram"]}}]},
                "Type": {"select": {"name": "little star"}},
            },
        )
        user_page_id[chat_id] = created["id"]
        context.user_data["state"] = ls_country
        await update.message.reply_text("your location?")
    elif state == ls_country:
        user_data[chat_id]["Country"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = ls_genre
        await update.message.reply_text("what are your specific skills?")
    elif state == ls_genre:
        user_data[chat_id]["Genre"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Genre": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = ls_instagram
        await update.message.reply_text("social networks")
    elif state == ls_instagram:
        user_data[chat_id]["Instagram"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = ls_plans
        await update.message.reply_text("tell a bit about your dream in our project: your ideas for collaba community")
    elif state == ls_plans:
        user_data[chat_id]["Plans"] = text
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = post_1
        await update.message.reply_text(POSTFLOW_1, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("continue", callback_data="continue_post_1")]]))

# ========== main ==========
def main() -> None:
    if not TELEGRAM_TOKEN:
        raise RuntimeError("bot_token env var is missing")
    if not (NOTION_TOKEN and DATABASE_ID):
        raise RuntimeError("notion env vars are missing")
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
