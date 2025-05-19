from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from telegram.error import BadRequest

# Bot Token
TELEGRAM_BOT_TOKEN = '7910090668:AAFKaDq0C2vzL4bluF0AsMjnVf4_p2bjMYI'
ADMIN_ID = 8138483951
TRADING_KEY = "laTf183B9B3733C58BdAC15Df"

# Payment methods
payment_methods = {
    "Binance": "🔗 Binance Pay ID: 207715971\nUSDT Address: 0x3391130f64cb8a135b304b778a7e8523a1f4916d\nNetwork: BEP-20\nPlease send your TxID.",
    "M-Pesa": "🔗 M-Pesa Till Number: 8496752\nPlease send your M-Pesa Reference Code.",
}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Binance", callback_data="Binance")],
        [InlineKeyboardButton("📱 M-Pesa", callback_data="M-Pesa")],
        [InlineKeyboardButton("📞 Customer Care", url="https://t.me/+254772931080")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💼 Welcome to TWB Best Bots! To get our trading key, you need to pay $50 USD through one of the methods below.\n\nChoose your payment method:",
        reply_markup=reply_markup,
    )

# Handle payment method selection
async def handle_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    method = query.data
    context.user_data["selected_payment_method"] = method  # Store the selected payment method
    instructions = payment_methods.get(method, "Invalid payment method.")
    
    keyboard = [[InlineKeyboardButton("📞 Customer Care", url="https://t.me/+254772931080")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=f"You selected **{method}**.\n\n{instructions}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Handle transaction ID submission
async def handle_transaction_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    username = update.message.chat.username or "No username"
    first_name = update.message.chat.first_name or "No name"
    transaction_id = update.message.text
    payment_method = context.user_data.get("selected_payment_method", "Unknown")

    # Send transaction details to the admin for manual verification
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🔔 Payment verification needed!\n\n"
            f"User: {first_name}\n"
            f"Username: @{username}\n"
            f"User ID: {user_id}\n"
            f"Payment Method: {payment_method}\n"
            f"Transaction ID: {transaction_id}\n\n"
            f"Use /confirm {user_id} to confirm payment."
        )
    )

    # Acknowledge the user's submission with a customer care button
    keyboard = [[InlineKeyboardButton("📞 Contact Customer Care", url="https://t.me/+254772931080")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📩 Thank you! Your transaction ID has been submitted for verification.\n"
        "Our team will verify your payment and provide your trading key shortly.\n\n"
        "For any issues, please reach out to Customer Care.",
        reply_markup=reply_markup
    )

# Admin command to confirm payment
async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("⚠️ You are not authorized to use this command.")
        return

    try:
        # Extract user ID from the command
        user_id = int(update.message.text.split()[1])

        # Send the trading key to the user
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🎉 Payment confirmed! Here is your trading key:\n\n`{TRADING_KEY}`",
            parse_mode="Markdown"
        )

        # Notify the admin that the key was sent
        await update.message.reply_text("✅ Payment confirmation sent to the user.")

    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ Usage: /confirm <user_id>")

    except BadRequest as e:
        # Handle 'Chat not found' error
        if "chat not found" in str(e).lower():
            await update.message.reply_text(
                f"⚠️ Failed to send the trading key. The user (ID: {user_id}) has not interacted with the bot. "
                "Ask them to start the bot first by sending /start."
            )
        else:
            # Handle other BadRequest errors
            await update.message.reply_text(f"⚠️ An error occurred: {e}")
            
# Admin command to decline payment
async def decline_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("⚠️ You are not authorized to use this command.")
        return

    try:
        # Extract user ID from the command
        user_id = int(update.message.text.split()[1])

        # Notify the user that their payment was declined
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ Your payment could not be verified.\n\n"
                "Please double-check your transaction ID and try again, or contact our support team for help."
            )
        )

        # Notify the admin that the decline message was sent
        await update.message.reply_text("⚠️ Decline message sent to the user.")

    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ Usage: /decline <user_id>")

    except BadRequest as e:
        if "chat not found" in str(e).lower():
            await update.message.reply_text(
                f"⚠️ Failed to notify the user. The user (ID: {user_id}) has not interacted with the bot."
            )
        else:
            await update.message.reply_text(f"⚠️ An error occurred: {e}")


# Main function to set up the bot
def start_premiumkey_bot():
    print("Starting the pro key bot...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("confirm", confirm_payment))
    app.add_handler(CommandHandler("decline", decline_payment))

    
    # Callback query handler for payment methods
    app.add_handler(CallbackQueryHandler(handle_payment_method))

    # Message handler for transaction IDs
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction_id))

    # Start the bot
    app.run_polling()