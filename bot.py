import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes
)

# ──────────────────────────────────────────────
# ENVIRONMENT VARIABLES
# ──────────────────────────────────────────────

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_WEBHOOK_URL = os.getenv("GOOGLE_WEBHOOK_URL")

NEW_DESCRIPTION = "collaba | community-owned music label"

requests.post(
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setMyDescription",
    json={"description": NEW_DESCRIPTION}
)

requests.post(
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setMyDescription",
    json={
        "description": NEW_DESCRIPTION,
        "language_code": "ru"
    }
)

requests.post(
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setMyDescription",
    json={
        "description": NEW_DESCRIPTION,
        "language_code": "en"
    }
)

requests.post(
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setMyShortDescription",
    json={"short_description": NEW_DESCRIPTION}
)

requests.post(
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setMyShortDescription",
    json={
        "short_description": NEW_DESCRIPTION,
        "language_code": "ru"
    }
)

requests.post(
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setMyShortDescription",
    json={
        "short_description": NEW_DESCRIPTION,
        "language_code": "en"
    }
)

if not TELEGRAM_TOKEN:
    raise RuntimeError("BOT_TOKEN env var is missing")
if not GOOGLE_WEBHOOK_URL:
    raise RuntimeError("GOOGLE_WEBHOOK_URL env var is missing")


# ──────────────────────────────────────────────
# STORAGE
# ──────────────────────────────────────────────

user_state = {}     # хранит шаг и flow
user_data = {}      # хранит ответы пользователя


# ──────────────────────────────────────────────
# START
# ──────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    user_state[chat_id] = {"step": 0}
    user_data[chat_id] = {}

    text = (
        "Hey there, meet cllb — community for musicians, made by "
        "<a href='https://www.instagram.com/cllllllllllllb/'>сollaba</a> team.\n"
        "Let’s take a closer look at each other 👀"
    )

    keyboard = [
        [InlineKeyboardButton("eyes wide open", callback_data="step_1_done")]
    ]

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ──────────────────────────────────────────────
# BUTTON HANDLER
# ──────────────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.from_user.id

    # STEP 1 → Consent screen
    if data == "step_1_done":
        user_state[chat_id]["step"] = 1

        consent_text = (
            "Few questions coming up, but first — let’s make sure we have your <b>Consent *</b>\n\n"
            "By submitting this \"form\" you consent to the collection and processing of your personal data "
            "for the purpose of assembling a professional team. Your data may be transferred and stored "
            "outside your country of residence. You can withdraw your consent at any time by letting "
            "<b>Ellie(@D0_oQ)</b> know.\n\n"
            "<a href='https://drive.google.com/file/d/15UHIGbDCtzKKQAJMtsfZvpkntU-i3Buu/view?usp=sharing'>"
            "I have read and agree to the Privacy Policy and Cookie Policy 🥸</a>"
        )

        keyboard = [[InlineKeyboardButton("Consent", callback_data="step_2_done")]]

        await query.message.reply_text(
            consent_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # STEP 2 → Member / Expert choice
    elif data == "step_2_done":
        user_state[chat_id]["step"] = 2

        keyboard = [
            [
                InlineKeyboardButton("Member", callback_data="member_flow"),
                InlineKeyboardButton("Expert", callback_data="expert_flow")
            ]
        ]

        await query.message.reply_text(
            "Are you applying to become a member or an expert?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # MEMBER FLOW START
    elif data == "member_flow":
        user_state[chat_id] = {"flow": "member", "step": 3}
        user_data[chat_id] = {}

        await query.message.reply_text("What is your name? Add your telegram @ as well")

    # EXPERT FLOW START
    elif data == "expert_flow":
        user_state[chat_id] = {"flow": "expert", "step": 3}
        user_data[chat_id] = {}

        await query.message.reply_text("What is your name? Add your telegram @ as well")

    # FINAL SUBMIT BUTTONS (deleted for member, kept for expert)
    elif data == "submit_expert":
        user_state[chat_id]["step"] = 999
        await query.message.reply_text(
            "See you inside! We’ll contact you soon after reviewing your application 🤝"
        )


# ──────────────────────────────────────────────
# TEXT HANDLER — MAIN FLOWS
# ──────────────────────────────────────────────

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    text = update.message.text.strip()
    state = user_state.get(chat_id)

    if not state:
        await update.message.reply_text("Press /start to begin.")
        return

    step = state["step"]
    flow = state.get("flow")
    telegram_username = f"@{update.effective_user.username}" if update.effective_user.username else ""

    # ──────────────────────────────────────────────
    # MEMBER FLOW
    # ──────────────────────────────────────────────

    if flow == "member":

        # Q1 — Name + Telegram
        if step == 3:
            user_data[chat_id]["Name"] = text
            user_data[chat_id]["Telegram"] = telegram_username
            user_state[chat_id]["step"] = 4

            await update.message.reply_text(
                "What is your role in music?\n\n"
                "Are you a singer, sound engineer, composer, arranger, songwriter, maybe a DJ?"
            )
            return

        # Q2 — Role
        if step == 4:
            user_data[chat_id]["Role"] = text
            user_state[chat_id]["step"] = 5

            await update.message.reply_text("What’s your mixing/mastering skill level?")
            return

        # Q3 — Mixing Level
        if step == 5:
            user_data[chat_id]["MixingLevel"] = text
            user_state[chat_id]["step"] = 6

            await update.message.reply_text("Do you play any instruments?")
            return

        # Q4 — Instruments
        if step == 6:
            user_data[chat_id]["Instruments"] = text
            user_state[chat_id]["step"] = 7

            await update.message.reply_text("How would you describe the genre of music you are working in?")
            return

        # Q5 — Genre
        if step == 7:
            user_data[chat_id]["Genre"] = text
            user_state[chat_id]["step"] = 8

            await update.message.reply_text(
                "Any fresh demos, releases to share?\n"
                "Spotify / Nina Protocol / Bandcamp / Soundcloud"
            )
            return

        # Q6 — Demos
        if step == 8:
            user_data[chat_id]["Demos"] = text
            user_state[chat_id]["step"] = 9

            await update.message.reply_text(
                "Please, add the link to your web site / insta / any platform you prefer"
            )
            return

        # Q7 — Links
        if step == 9:
            user_data[chat_id]["Links"] = text
            user_state[chat_id]["step"] = 10

            await update.message.reply_text(
                "This is the last one, promise!\n\n"
                "What idea would you like to work on with the collaba community?\n"
                "And what do you need to make a dream come true?"
            )
            return

        # Q8 — Idea → SEND TO GOOGLE SHEETS → FINAL SCREEN (NO LAST STEP)
        if step == 10:
            user_data[chat_id]["Idea"] = text

            # SEND TO GOOGLE SHEETS
            try:
                requests.post(GOOGLE_WEBHOOK_URL, json=user_data[chat_id])
            except Exception as e:
                await update.message.reply_text(f"Error saving to Sheets: {e}")

            user_state[chat_id]["step"] = 999

            keyboard = [
                [InlineKeyboardButton("Submit", url="https://t.me/+pNM6z-LJj5g3NWZi")]
            ]

            await update.message.reply_text(
                "Ok, we got it! THANK YOU! Here is your invitation link.\n"
                "Tap it to submit your application.\n\n"
                "See you inside! If you have any questions, text Emil – [@emilchensky];\n Liza - [@D0_oQ];\n German - [@German_M]",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return


    # ──────────────────────────────────────────────
    # EXPERT FLOW (unchanged)
    # ──────────────────────────────────────────────

    if flow == "expert":

        # Q1 — Name + Telegram
        if step == 3:
            user_data[chat_id]["Name"] = text
            user_data[chat_id]["Telegram"] = telegram_username
            user_state[chat_id]["step"] = 4

            await update.message.reply_text(
                "What is your professional role in the music industry?\n\n"
                "(producer, sound engineer, vocal coach, mixing/mastering engineer, composer, arranger, educator, A&R, manager, label rep etc.)"
            )
            return

        # Q2 — Professional Role
        if step == 4:
            user_data[chat_id]["Role"] = text
            user_state[chat_id]["step"] = 5

            await update.message.reply_text(
                "What areas of expertise can you contribute to the Collaba community?\n"
                "Are there specific topics or skills you could teach, mentor, or consult on?\n\n"
                "(vocal technique, DAW basics, mixing workflow, marketing for artists, songwriting structure, etc.)"
            )
            return

        # Q3 — Areas of expertise
        if step == 5:
            user_data[chat_id]["Expertise"] = text
            user_state[chat_id]["step"] = 6

            await update.message.reply_text(
                "What projects have you worked on that best represent your expertise?\n"
                "(Demos, releases, portfolio pieces — links welcome!)"
            )
            return

        # Q4 — Projects
        if step == 6:
            user_data[chat_id]["Projects"] = text
            user_state[chat_id]["step"] = 7

            await update.message.reply_text(
                "Which genres or music styles do you specialize in?"
            )
            return

        # Q5 — Genre
        if step == 7:
            user_data[chat_id]["Genre"] = text
            user_state[chat_id]["step"] = 8

            await update.message.reply_text(
                "How would you like to contribute to the Collaba community as an expert?\n"
                "(Workshops, 1:1 mentorship, feedback sessions, collabs, content creation)"
            )
            return

        # Q6 — Idea (Contribution format)
        if step == 8:
            user_data[chat_id]["Idea"] = text
            user_state[chat_id]["step"] = 9

            await update.message.reply_text(
                "Please, add links to your website / Instagram / Spotify / portfolio / any platform you prefer"
            )
            return

        # Q7 — Links
        if step == 9:
            user_data[chat_id]["Links"] = text
            user_state[chat_id]["step"] = 10

            await update.message.reply_text(
                "Last one, promise!\n\n"
                "Why do you want to join the Collaba community as an expert?"
            )
            return

        # Q8 — Motivation → SEND TO GOOGLE SHEETS → FINAL SCREEN
        if step == 10:
            user_data[chat_id]["Motivation"] = text

            # SEND TO GOOGLE SHEETS
            try:
                requests.post(GOOGLE_WEBHOOK_URL, json=user_data[chat_id])
            except Exception as e:
                await update.message.reply_text(f"Error saving to Sheets: {e}")

            user_state[chat_id]["step"] = 11

            keyboard = [
                [InlineKeyboardButton("Submit", url="https://t.me/+pNM6z-LJj5g3NWZi")]
            ]

            await update.message.reply_text(
                "Ok, we got it! THANK YOU!\n"
                "Tap here to submit your application — we will contact you as soon as we go through everything you’ve shared 🫶",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return


    # ──────────────────────────────────────────────
    # DEFAULT
    # ──────────────────────────────────────────────

    await update.message.reply_text("Please use the buttons 👆")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()


if __name__ == "__main__":
    main()
