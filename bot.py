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
    V_NAME, V_SOCIAL, V_LOCATION, V_ABOUT, V_PLANS,
    # Star states
    S_NAME, S_SOCIAL, S_LOCATION, S_ABOUT, S_PLANS
) = range(44)

# ========== POSTFLOW TEXT ==========
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
        await query.message.reply_text(
            "Few questions coming up — but first, read the manifesto. It’s kinda sacred",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("The Important Doc", callback_data="read_doc")],
                [InlineKeyboardButton("No Time To Read", callback_data="skip_doc")],
            ])
        )

    # Read manifesto (always send full text!)
    elif data == "read_doc":
        await query.message.reply_text(
            MANIFESTO,
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

    # Musician flow start
    elif data == "role_musician":
        user_data[chat_id] = {"Telegram": f"@{query.from_user.username}" if query.from_user.username else "", "Type": "Musician"}
        context.user_data["state"] = M_NAME
        await query.message.reply_text("Name / Artist name *")

    # Designer flow start
    elif data == "role_designer":
        user_data[chat_id] = {"Telegram": f"@{query.from_user.username}" if query.from_user.username else "", "Type": "Designer"}
        context.user_data["state"] = D_NAME
        await query.message.reply_text("What is your name?")

    # Videomaker flow start
    elif data == "role_videomaker":
        user_data[chat_id] = {"Telegram": f"@{query.from_user.username}" if query.from_user.username else "", "Type": "Videomaker"}
        context.user_data["state"] = V_NAME
        await query.message.reply_text("Name / Videomaker name *")

    # Star flow start
    elif data == "role_star":
        user_data[chat_id] = {"Telegram": f"@{query.from_user.username}" if query.from_user.username else "", "Type": "Star"}
        context.user_data["state"] = S_NAME
        await query.message.reply_text("Name / Star name *")

    # ========== DESIGNER BUTTONS ==========
    # Designer: Occupation (specialization)
    elif data in ("designer_occ_interface", "designer_occ_graphic", "designer_occ_motion", "designer_occ_fashion"):
        occ_map = {
            "designer_occ_interface": "Interface Designer",
            "designer_occ_graphic": "Graphic Designer",
            "designer_occ_motion": "Motion Designer",
            "designer_occ_fashion": "Fashion Designer"
        }
        occupation = occ_map[data]
        await query.message.reply_text(occupation)
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Occupation": {"select": {"name": occupation}}})
        context.user_data["state"] = D_SKILLS
        await query.message.reply_text("What are your specific skills?")

    # ========== POSTFLOW & OTHER ==========
    # Continue postflow
    elif data == "continue_post_1":
        await query.message.reply_text("Welcome to the crew! 🎉")

# ========== TEXT HANDLER ==========
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    text = update.message.text.strip()
    state = context.user_data.get("state")

    # ========== ARTIST FLOW ==========
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

    # ========== VIDEOMAKER FLOW ==========
    elif state == V_NAME:
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
        context.user_data["state"] = V_SOCIAL
        await update.message.reply_text("Social networks")

    elif state == V_SOCIAL:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = V_LOCATION
        await update.message.reply_text("Location")

    elif state == V_LOCATION:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = V_ABOUT
        await update.message.reply_text("About you")

    elif state == V_ABOUT:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"About": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = V_PLANS
        await update.message.reply_text("Plans")

    elif state == V_PLANS:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        await update.message.reply_text(
            POSTFLOW_1,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_1")]])
        )

    # ========== STAR FLOW ==========
    elif state == S_NAME:
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
        context.user_data["state"] = S_SOCIAL
        await update.message.reply_text("Social networks")

    elif state == S_SOCIAL:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Instagram": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = S_LOCATION
        await update.message.reply_text("Location")

    elif state == S_LOCATION:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Country": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = S_ABOUT
        await update.message.reply_text("About you")

    elif state == S_ABOUT:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"About": {"rich_text": [{"text": {"content": text}}]}})
        context.user_data["state"] = S_PLANS
        await update.message.reply_text("Plans")

    elif state == S_PLANS:
        notion.pages.update(page_id=user_page_id[chat_id], properties={"Plans": {"rich_text": [{"text": {"content": text}}]}})
        await update.message.reply_text(
            POSTFLOW_1,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Continue", callback_data="continue_post_1")]])
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
