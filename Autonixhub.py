from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler

TELEGRAM_BOT_TOKEN = "7918879272:AAFUlBbYE1gjFWizxTYbl4YPAQ0JC1JkUVQ"

BOT_LIST = {
    "Autonix Free Bot": "https://t.me/autonix_free_bot",
    "Autonix Edge Bot": "https://t.me/AutonixEdge_bot",
    "Autonix Pro Bot": "https://t.me/autonix_pro_bot",
    "Autonix Lite Bot": "https://t.me/autonix_lite_bot",
    "Card Generator Bot": "https://t.me/autonix_card_generator_bot"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"👋 Hello <b>{user.first_name}</b>!\n\n"
        "Welcome to the <b>Autonix Bot Hub</b> — your gateway to all our powerful Telegram bots.\n\n"
        "👇 Select a bot below to get started:"
    )

    keyboard = [
        [InlineKeyboardButton("💳 Autonix Card Generator", url=BOT_LIST["Card Generator Bot"])],
        [InlineKeyboardButton("🤖 Autonix Free Bot", url=BOT_LIST["Autonix Free Bot"])],
        [InlineKeyboardButton("🤖 Autonix Edge Bot", url=BOT_LIST["Autonix Edge Bot"])],
        [InlineKeyboardButton("🚀 Autonix Pro Bot", url=BOT_LIST["Autonix Pro Bot"])],
        [InlineKeyboardButton("⚡ Autonix Lite Bot", url=BOT_LIST["Autonix Lite Bot"])],
        [InlineKeyboardButton("📢 Join Telegram Channel", url="https://t.me/autonix001")],
        [InlineKeyboardButton("📞 Contact Customer Care", url="https://t.me/autonix_assistant_bot")]
    ]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=welcome_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
def start_Autonixhub_bot():
    print("Starting the autonix hub bot...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # Run the bot until manually stopped
    print("🤖 Autonix Bot Hub is running...")
    app.run_polling()