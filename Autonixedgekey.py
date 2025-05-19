from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import telegram

# Bot Token
TELEGRAM_BOT_TOKEN = '7809510285:AAHKhezm6axMchFaG1p24i9XIKYhxYTf9Lk'

# Trading Key
TRADING_KEY = "autonixedgekey"

# Channel Username
CHANNEL_USERNAME = "@autonix001"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/autonix001")],
        [InlineKeyboardButton("📥 Receive Trading Key", callback_data="get_key")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 *Welcome!*\n\n"
        "To receive your *Trading Key*, you need to join our official Telegram channel.\n"
        "After joining, tap *Receive Trading Key* below 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# Handle inline button callbacks
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "get_key":
        try:
            # Verify if user is a member of the channel
            member_status = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
            status = member_status.status

            if status in ["member", "administrator", "creator"]:
                # User is a valid member
                await query.edit_message_text(
                    text=f"✅ You're verified!\n\nHere is your trading key:\n\n`{TRADING_KEY}`",
                    parse_mode="Markdown"
                )
            else:
                # User is not a member
                await query.edit_message_text(
                    text="❌ You haven't joined our channel yet.\n\n"
                         "Please join\n\n"
                         "Once you've joined, tap *Receive Trading Key* again.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/autonix001")],
                        [InlineKeyboardButton("📥 Receive Trading Key", callback_data="get_key")],
                    ]),
                    parse_mode="Markdown"
                )
        except telegram.error.BadRequest:
            # Could not verify (e.g., user has blocked the channel or hasn't joined at all)
            await query.edit_message_text(
                text="⚠️ We couldn't verify your channel membership.\n"
                     "Please make sure you've joined the channel, then try again.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 Join Channel", url="https://t.me/autonix001")],
                    [InlineKeyboardButton("📥 Receive Trading Key", callback_data="get_key")],
                ]),
                parse_mode="Markdown"
            )

def start_Autonixedgekey_bot():
    print("🚀 Starting Autonixedgekey Bot...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.run_polling()
