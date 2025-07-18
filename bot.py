import os
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
    # Artist states
    A_NAME, A_COUNTRY, A_INSTAGRAM, A_SPOTIFY,
    A_ABOUT, A_PLANS, A_LIVE, A_DEMOS, A_COLLAB,
    A_SONGWRITER, A_PRODUCE,
    # Musician states
    M_NAME, M_SOCIAL, M_LOCATION, M_OCCUPATION, M_INSTRUMENTS, M_INST_CONTEXT,
    M_SING, M_MIXING, M_GENRE, M_DEMOS, M_VOCAL, M_COLLAB, M_EXPERIENCE, M_PLANS,
    # Designer states
    D_NAME, D_LOCATION, D_OCCUPATION, D_SKILLS, D_DEMOS, D_STYLE, D_SOCIAL, D_GENRE, D_PLANS,
    # Videomaker states
    V_NAME, V_LOCATION, V_OCCUPATION, V_GENRE, V_DEMOS, V_SOCIAL, V_PLANS, V_INSTR_CONTEXT, V_ABOUT,
    # Little Star states
    LS_NAME, LS_LOCATION, LS_ABOUT, LS_SOCIAL, LS_PLANS,
    # Postflow screens
    POST_1, POST_2, POST_3, POST_PROMISE, POST_FINAL
) = range(53)

# ========== POSTFLOW TEXTS ==========
POSTFLOW_1 = (
    "Thank you! Got it!\n\n"
    "Ok, still here awesome just a few things left to share and you are allllmost here vibing with all of us:\n"
    "What is cllllllllllllb?\n\n"
    "We’re not a label-label.\n"
    "We’re a music-flavored community with zero chill for perfection and a soft spot for weird sounds, late-night ideas, and collabs that make no sense on paper.\n"
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
    "You just need to show up."
)

POSTFLOW_PROMISE = (
    "Do we have collaba vibe check-in? Yes, we do!\n\n"
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
    "Bonus track:\n"
    "If you act on behalf of cllb — remember, you’re repping all of us. So filter the toxicity, and please… no -isms (sexism, racism, ableism, etc). Not our jam."
)

POSTFLOW_FINAL = (
    "Looks like you're ready for some fun, huh?"
)

MANIFESTO = (
    "the cllllllllllllb manifesto\n\n"
    "We’re not a “label”. We’re a crew, a bunch of people who can’t stop making stuff and hyping each other up. "
    "Music’s not something we drop — it’s something we accidentally turn into a whole thing at 2am. Creativity here is more “send voice note while eating noodles” than “boardroom energy.”\n\n"
    "We don’t care how many streams you got. We care if someone played it three times in a row ‘cause it hit. We don’t chase formats. we chase goosebumps.\n\n"
    "We don’t sign artists. we notice them. and then build a tiny universe around them.\n"
    "cllb was born ‘cause we wanted a space where no one had to pretend to “fit in.”\n\n"
    "Where weird is hot. and rough edges mean it’s alive. that weird voice memo you almost deleted? yeah, that’s the one. We’re not scared of stuff that makes the algorithm uncomfortable.\n\n"
    "We move like a pack of creatively chaotic raccoons. Somebody drops an idea in chat — boom. Someone’s mixing, someone’s drawing, someone’s pitching a blog. You could be a DJ, a coder, a poet, or just someone with oddly good vibes — it all matters.\n\n"
    "This isn’t an industry. It’s a group project with no teacher.\n\n"
    "We’re not promising fame or funding or fame and funding. We’re promising to stick around. from “this is just a draft but…” to a gig in a country you’ve never been to.\n\n"
    "There’s no contracts here. No KPIs. but sometimes you get a sticker and five people saying “omg” at once. If you’re here, you’re already part of the magic. Right now. Not when you’re “ready.”\n\n"
    "This isn’t business.\n"
    "This is lowkey a cult (just kidding)\n"
    "Not a product. A group hug in mp3."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Hey there, meet cllb — the music community-label that kinda accidentally started itself "
        "(but stuck around on purpose)"
    )
    keyboard = [[InlineKeyboardButton("NICE", callback_data="nice")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.from_user.id

    # Start
    if data == "nice":
        await query.message.reply_text(
            "Few questions coming up — but first, read the manifesto. It’s kinda sacred",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("The Important Doc", callback_data="read_doc")],
                [InlineKeyboardButton("No Time To Read", callback_data="skip_doc")],
            ])
        )
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
        await query.message.reply_text(
            "Few questions coming up — but first, read the manifesto. It’s kinda sacred",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("The Important Doc", callback_data="read_doc")],
                [InlineKeyboardButton("No Time To Read", callback_data="skip_doc")],
            ])
        )
    elif data == "read_doc":
        await query.message.reply_text(
            MANIFESTO,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("100% Vibing With Your Values", callback_data="agree_manifesto")],
                [InlineKeyboardButton("Not My Vibe Sorry Folks", callback_data="reject_manifesto")],
            ])
        )
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

    # Role selection
    elif data == "role_artist":
        user_data[chat_id] = {"Telegram": f"@{query.from_user.username}" if query.from_user.username else "", "Type": "Artist"}
        context.user_data["state"] = A_NAME
        await query.message.reply_text("Name / Artist name *")
    elif data == "role_musician":
        user_data[chat_id] = {"Telegram": f"@{query.from_user.username}" if query.from_user.username else "", "Type": "Musician"}
        context.user_data["state"] = M_NAME
        await query.message.reply_text("Name / Artist name *")
    elif data == "role_designer":
        user_data[chat_id] = {"Telegram": f"@{query.from_user.username}" if query.from_user.username else "", "Type": "Designer"}
        context.user_data["state"] = D_NAME
        await query.message.reply_text("What is your name?")
    elif data == "role_videomaker":
        user_data[chat_id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "Type": "Videomaker"
        }
        context.user_data["state"] = V_NAME
        await query.message.reply_text("What is your name?")
    elif data == "role_star":
        user_data[chat_id] = {
            "Telegram": f"@{query.from_user.username}" if query.from_user.username else "",
            "Type": "Little Star"
        }
        context.user_data["state"] = LS_NAME
        await query.message.reply_text("What is your name?")
    elif data == "continue_post_1":
        context.user_data["state"] = POST_1
        await query.message.reply_text(
            POSTFLOW_2,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_2")]])
        )
    elif data == "continue_post_2":
        context.user_data["state"] = POST_2
        await query.message.reply_text(
            POSTFLOW_3,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_3")]])
        )
    elif data == "continue_post_3":
        context.user_data["state"] = POST_3
        await query.message.reply_text(
            "Wanna get noticed? Just show up and do your thing",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("OK OK OK I Promise", callback_data="ok_promise")],
                [InlineKeyboardButton("Lowkey Just Vibing And Watching", callback_data="just_vibing")]
            ])
        )
    elif data == "just_vibing":
        await query.message.reply_text(
            "Oh and hey! See you!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Subscribe", url="https://linktree.com/cllllllllllllb")]
            ])
        )
    elif data == "ok_promise":
        context.user_data["state"] = POST_PROMISE
        await query.message.reply_text(
            POSTFLOW_PROMISE,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("cllb, I Think Love U Already", callback_data="final_love")]])
        )
    elif data == "final_love":
        context.user_data["state"] = POST_FINAL
        await query.message.reply_text(
            POSTFLOW_FINAL,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Community", url="https://t.me/+p9m9pRjBvi4xNWMy")]])
        )

    # ARTIST SELECT BUTTONS
    elif data in ("artist_collab_yes", "artist_collab_no"):
        collab = "Yes" if data == "artist_collab_yes" else "No"
        await query.message.reply_text(collab)
        try:
            notion.pages.update(page_id=user_page_id[chat_id], properties={"Collaborations": {"select": {"name": collab}}})
        except Exception as e:
            await query.message.reply_text(f"Ошибка при обновлении поля select Collaborations: {e}")
        context.user_data["state"] = A_SONGWRITER
        await query.message.reply_text(
            "Are you a songwriter? Or someone from your team is?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Yes I Am", callback_data="artist_sw_yes")],
                [InlineKeyboardButton("My Teammate Is", callback_data="artist_sw_teammate")],
                [InlineKeyboardButton("No", callback_data="artist_sw_no")],
            ])
        )
    elif data in ("artist_sw_yes", "artist_sw_teammate", "artist_sw_no"):
        sw_map = {
            "artist_sw_yes": "Yes I Am",
            "artist_sw_teammate": "My Teammate Is",
            "artist_sw_no": "No"
        }
        sw = sw_map[data]
        await query.message.reply_text(sw)
        try:
            notion.pages.update(page_id=user_page_id[chat_id], properties={"Songwriter": {"select": {"name": sw}}})
        except Exception as e:
            await query.message.reply_text(f"Ошибка при обновлении поля select Songwriter: {e}")
        context.user_data["state"] = A_PRODUCE
        await query.message.reply_text(
            "Do you produce music yourself?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Yes I Am A Professional", callback_data="artist_prod_prof")],
                [InlineKeyboardButton("Yes I Am An Amateur", callback_data="artist_prod_amateur")],
                [InlineKeyboardButton("No", callback_data="artist_prod_no")],
            ])
        )
    elif data in ("artist_prod_prof", "artist_prod_amateur", "artist_prod_no"):
        prod_map = {"artist_prod_prof": "Yes I Am A Professional", "artist_prod_amateur": "Yes I Am An Amateur", "artist_prod_no": "No"}
        prod = prod_map[data]
        await query.message.reply_text(prod)
        try:
            notion.pages.update(page_id=user_page_id[chat_id], properties={"Produce": {"select": {"name": prod}}})
        except Exception as e:
            await query.message.reply_text(f"Ошибка при обновлении поля select Produce: {e}")
        await query.message.reply_text(
            POSTFLOW_1,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_1")]])
        )
    # DESIGNER SELECT BUTTONS
    elif data in (
        "designer_occ_interface",
        "designer_occ_graphic",
        "designer_occ_motion",
        "designer_occ_fashion"
    ):
        occ_map = {
            "designer_occ_interface": "Interface Designer",
            "designer_occ_graphic": "Graphic Designer",
            "designer_occ_motion": "Motion Designer",
            "designer_occ_fashion": "Fashion Designer"
        }
        occupation = occ_map[data]
        await query.message.reply_text(occupation)
        try:
            notion.pages.update(page_id=user_page_id[chat_id], properties={"Occupation": {"select": {"name": occupation}}})
        except Exception as e:
            await query.message.reply_text(f"Ошибка при обновлении поля select Occupation: {e}")
        context.user_data["state"] = D_SKILLS
        await query.message.reply_text("What are your specific skills?")
    # MUSICIAN SELECT BUTTONS
    elif data in ("musician_occ_singer", "musician_occ_engineer", "musician_occ_composer", "musician_occ_arranger"):
        occ_map = {
            "musician_occ_singer": "Singer",
            "musician_occ_engineer": "Sound Engineer",
            "musician_occ_composer": "Composer",
            "musician_occ_arranger": "Arranger"
        }
        occupation = occ_map[data]
        await query.message.reply_text(occupation)
        try:
            notion.pages.update(page_id=user_page_id[chat_id], properties={"Occupation": {"select": {"name": occupation}}})
        except Exception as e:
            await query.message.reply_text(f"Ошибка при обновлении поля select Occupation: {e}")
        context.user_data["state"] = M_INSTRUMENTS
        await query.message.reply_text(
            "Do you play any instruments?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Yes", callback_data="musician_instr_yes")],
                [InlineKeyboardButton("No", callback_data="musician_instr_no")],
            ])
        )
    elif data in ("musician_instr_yes", "musician_instr_no"):
        instr = "Yes" if data == "musician_instr_yes" else "No"
        await query.message.reply_text(instr)
        try:
            notion.pages.update(page_id=user_page_id[chat_id], properties={"Instruments": {"select": {"name": instr}}})
        except Exception as e:
            await query.message.reply_text(f"Ошибка при обновлении поля select Instruments: {e}")
        context.user_data["state"] = M_INST_CONTEXT
        await query.message.reply_text("What instruments do you play if you do?\n\nPut - if you are not")
    elif data in ("musician_sing_yes", "musician_sing_no"):
        sing = "Yes" if data == "musician_sing_yes" else "No"
        await query.message.reply_text(sing)
        try:
            notion.pages.update(page_id=user_page_id[chat_id], properties={"Sing": {"select": {"name": sing}}})
        except Exception as e:
            await query.message.reply_text(f"Ошибка при обновлении поля select Sing: {e}")
        context.user_data["state"] = M_MIXING
        await query.message.reply_text(
            "What is your proficiency in mixing/mastering?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Yes I Am A Professional", callback_data="musician_mix_prof")],
                [InlineKeyboardButton("Yes I Am An Amateur", callback_data="musician_mix_amateur")],
                [InlineKeyboardButton("No", callback_data="musician_mix_no")],
            ])
        )
    elif data in ("musician_mix_prof", "musician_mix_amateur", "musician_mix_no"):
        mix_map = {
            "musician_mix_prof": "Yes I Am A Professional",
            "musician_mix_amateur": "Yes I Am An Amateur",
            "musician_mix_no": "No"
        }
        mixing = mix_map[data]
        await query.message.reply_text(mixing)
        try:
            notion.pages.update(page_id=user_page_id[chat_id], properties={"Mixing": {"select": {"name": mixing}}})
        except Exception as e:
            await query.message.reply_text(f"Ошибка при обновлении поля select Mixing: {e}")
        context.user_data["state"] = M_GENRE
        await query.message.reply_text(
            "What genre do you identify with?\n\nIf multiple please write them all down"
        )
    elif data in ("musician_collab_ftf", "musician_collab_online", "musician_collab_unsure"):
        collab_map = {
            "musician_collab_ftf": "Face to Face",
            "musician_collab_online": "Online",
            "musician_collab_unsure": "I Am Not Sure"
        }
        collab = collab_map[data]
        await query.message.reply_text(collab)
        try:
            notion.pages.update(page_id=user_page_id[chat_id], properties={"Collaborations": {"select": {"name": collab}}})
        except Exception as e:
            await query.message.reply_text(f"Ошибка при обновлении поля select Collaborations: {e}")
        context.user_data["state"] = M_EXPERIENCE
        await query.message.reply_text("How many years have you been in music industry?")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    text = update.message.text.strip()
    state = context.user_data.get("state")

    # ========== VIDEOMAKER FLOW ==========
    if state == V_NAME:
        user_data[chat_id]["Name"] = text
        created = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": text}}]},
                "Type": {"select": {"name": "Videomaker"}},
                "Telegram": {"rich_text": [{"text": {"content": user_data[chat_id]["Telegram"]}}]},
            },
        )
        user_page_id[chat_id] = created["id"]
        context.user_data["state"] = V_LOCATION
        await update.message.reply_text("Your location?")
    elif state == V_LOCATION:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = V_OCCUPATION
        await update.message.reply_text("What is your position?")
    elif state == V_OCCUPATION:
        try:
            notion.pages.update(page_id=user_page_id[chat_id], properties={"Occupation": {"select": {"name": text}}})
        except Exception as e:
            await update.message.reply_text(f"Ошибка при записи в поле (select) Occupation: {e}")
        context.user_data["state"] = V_GENRE
        await update.message.reply_text("What are your specific skills?")
    elif state == V_GENRE:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Genre": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = V_DEMOS
        await update.message.reply_text("Portfolio")
    elif state == V_DEMOS:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Demos": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = V_SOCIAL
        await update.message.reply_text("Social networks")
    elif state == V_SOCIAL:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = V_PLANS
        await update.message.reply_text("Tell a bit about the idea you would like to host with collaba community")
    elif state == V_PLANS:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = V_INSTR_CONTEXT
        await update.message.reply_text("Do you have any equipment? If yes, what kind?")
    elif state == V_INSTR_CONTEXT:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instruments Context": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = V_ABOUT
        await update.message.reply_text("What programs and tools do you use in your work?")
    elif state == V_ABOUT:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"About": {"rich_text": [{"text": {"content": text}}]}})
        await update.message.reply_text(
            POSTFLOW_1,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_1")]])
        )
    # ========== LITTLE STAR FLOW ==========
    elif state == LS_NAME:
        user_data[chat_id]["Name"] = text
        created = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": text}}]},
                "Type": {"select": {"name": "Little Star"}},
                "Telegram": {"rich_text": [{"text": {"content": user_data[chat_id]["Telegram"]}}]},
            },
        )
        user_page_id[chat_id] = created["id"]
        context.user_data["state"] = LS_LOCATION
        await update.message.reply_text("Your location?")
    elif state == LS_LOCATION:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = LS_ABOUT
        await update.message.reply_text("What are your specific skills?")
    elif state == LS_ABOUT:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"About": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = LS_SOCIAL
        await update.message.reply_text("Social networks")
    elif state == LS_SOCIAL:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = LS_PLANS
        await update.message.reply_text("Tell a bit about the idea you would like to host with collaba community")
    elif state == LS_PLANS:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        await update.message.reply_text(
            POSTFLOW_1,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_1")]])
        )
    # ========== ARTIST FLOW ==========
    elif state == A_NAME:
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
    elif state == A_COUNTRY:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_INSTAGRAM
        await update.message.reply_text("Instagram")
    elif state == A_INSTAGRAM:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_SPOTIFY
        await update.message.reply_text("Spotify")
    elif state == A_SPOTIFY:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Spotify": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_ABOUT
        await update.message.reply_text("About me\nIf you want to share any links, put them here")
    elif state == A_ABOUT:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"About": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_PLANS
        await update.message.reply_text(
            "Plans\nTell us about your upcoming releases, projects, any personal or career plans you have for the near future. "
            "This is your space to outline your creative direction and aspirations"
        )
    elif state == A_PLANS:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_LIVE
        await update.message.reply_text("Live videos")
    elif state == A_LIVE:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Live": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = A_DEMOS
        await update.message.reply_text("Demos\nOnly soundcloud, please")
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
    # ========== MUSICIAN FLOW ==========
    elif state == M_NAME:
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
        context.user_data["state"] = M_SOCIAL
        await update.message.reply_text("Social networks")
    elif state == M_SOCIAL:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = M_LOCATION
        await update.message.reply_text("Location")
    elif state == M_LOCATION:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = M_OCCUPATION
        await update.message.reply_text(
            "What is your occupation as a musician?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Singer", callback_data="musician_occ_singer")],
                [InlineKeyboardButton("Sound Engineer", callback_data="musician_occ_engineer")],
                [InlineKeyboardButton("Composer", callback_data="musician_occ_composer")],
                [InlineKeyboardButton("Arranger", callback_data="musician_occ_arranger")],
            ])
        )
    elif state == M_INST_CONTEXT:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instruments Context": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = M_SING
        await update.message.reply_text(
            "Do you sing?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Yes", callback_data="musician_sing_yes")],
                [InlineKeyboardButton("No", callback_data="musician_sing_no")],
            ])
        )
    elif state == M_GENRE:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Genre": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = M_DEMOS
        await update.message.reply_text(
            "Track/song/demo/beat\n\nPlease send Soundcloud link"
        )
    elif state == M_DEMOS:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Demos": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = M_VOCAL
        await update.message.reply_text(
            "Vocal performance (for singers)\n\nPlease send Soundcloud/YouTube link if you are not a singer put -"
        )
    elif state == M_VOCAL:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Live": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = M_COLLAB
        await update.message.reply_text(
            "How do you want to collaborate with other musicians?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Face to Face", callback_data="musician_collab_ftf")],
                [InlineKeyboardButton("Online", callback_data="musician_collab_online")],
                [InlineKeyboardButton("I Am Not Sure", callback_data="musician_collab_unsure")],
            ])
        )
    elif state == M_EXPERIENCE:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Experience": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = M_PLANS
        await update.message.reply_text(
            "Plans\n\nTell us about your upcoming releases projects any personal or career plans you have for the near future. This is your space to outline your creative direction and aspirations"
        )
    elif state == M_PLANS:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        await update.message.reply_text(
            POSTFLOW_1,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_1")]])
        )
    # ========== DESIGNER FLOW ==========
    if state == D_NAME:
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
        context.user_data["state"] = D_LOCATION
        await update.message.reply_text("Your location?")
    elif state == D_LOCATION:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = D_OCCUPATION
        await update.message.reply_text(
            "What is your specialization?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Interface Designer", callback_data="designer_occ_interface")],
                [InlineKeyboardButton("Graphic Designer", callback_data="designer_occ_graphic")],
                [InlineKeyboardButton("Motion Designer", callback_data="designer_occ_motion")],
                [InlineKeyboardButton("Fashion Designer", callback_data="designer_occ_fashion")],
            ])
        )
    elif state == D_SKILLS:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instruments Context": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = D_DEMOS
        await update.message.reply_text("Portfolio")
    elif state == D_DEMOS:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Demos": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = D_STYLE
        await update.message.reply_text("Describe your design style")
    elif state == D_STYLE:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"About": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = D_SOCIAL
        await update.message.reply_text("Social networks")
    elif state == D_SOCIAL:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = D_GENRE
        await update.message.reply_text("What programs/softwares and tools do you use in your work?")
    elif state == D_GENRE:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Genre": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = D_PLANS
        await update.message.reply_text("Tell a bit about the idea you would like to host with collaba community")
    elif state == D_PLANS:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        await update.message.reply_text(
            POSTFLOW_1,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_1")]])
        )

def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
