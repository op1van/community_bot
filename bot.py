import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes
)

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")

if not TELEGRAM_TOKEN:
    raise RuntimeError("BOT_TOKEN env var is missing")

user_state = {}    # хранит текущий шаг пользователя
user_data = {}     # позже будем сохранять ответы сюда


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

    # ───── STEP 1 → STEP 2 (Consent screen)
    if data == "step_1_done":
        user_state[chat_id]["step"] = 1

        consent_text = (
            "Few questions coming up, but first — let’s make sure we have your <b>Consent *</b>\n\n"
            "By submitting this \"form\" you consent to the collection and processing of your personal data "
            "for the purpose of assembling a professional team. Your data may be transferred and stored "
            "outside your country of residence. You can withdraw your consent at any time by letting "
            "<b>@MilaIgnatevaa</b> know.\n\n"
            "<a href='https://drive.google.com/file/u/2/d/1euqwTrqdoG2-9ySB9JivXdTT3Tb_R5sG/view'>"
            "I have read and agree to the Privacy Policy and Cookie Policy 🥸</a>"
        )

        keyboard = [
            [InlineKeyboardButton("Consent", callback_data="step_2_done")]
        ]

        await query.message.reply_text(
            consent_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ───── STEP 2 → STEP 3 (следующий вопрос)
    elif data == "step_2_done":
        user_state[chat_id]["step"] = 2

        await query.message.reply_text(
            "Consent received ✔️\n\nГотов идти дальше!",
        )

        # На следующем шаге мы будем задавать уже первый вопрос с записью
        # Но добавим позже


# ──────────────────────────────────────────────
# TEXT HANDLER (пока пустой, ответ не сохраняем)
# ──────────────────────────────────────────────
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    state = user_state.get(chat_id)

    if not state:
        await update.message.reply_text("Press /start to begin.")
        return

    step = state["step"]

    # пока мы не принимаем текстовые ответы — только кнопки
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
