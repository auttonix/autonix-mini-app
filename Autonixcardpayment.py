import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import json

def add_approved_user(user_id):
    try:
        with open("approved_users.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"approved_users": []}

    if user_id not in data["approved_users"]:
        data["approved_users"].append(user_id)
        with open("approved_users.json", "w") as f:
            json.dump(data, f)


# Bot Token & Admin ID
TOKEN = "7955854251:AAGm2Pw6vRJxOaadG0_Pjf090MhwF1oc1uw"
ADMIN_ID = 8138483951

# Memory storage
approved_users = set()
user_payment_method = {}

# Logging
import logging

# Set your main log level
logging.basicConfig(level=logging.INFO)

# Suppress httpx logs
logging.getLogger("httpx").setLevel(logging.WARNING)

# Optionally suppress telegram logs
logging.getLogger("telegram").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the Payment Bot!\n\n"
        "💳 To subscribe and unlock unlimited card generation, please pay <b>$30</b>.\n\n"
        "Choose your preferred payment method below:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💵 PayPal", callback_data="paypal")],
            [InlineKeyboardButton("💰 Binance (USDT)", callback_data="binance")],
            [InlineKeyboardButton("📱 M-Pesa", callback_data="mpesa")]
        ])
    )

# Handle payment method selection
async def handle_method_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    method = query.data
    user_payment_method[user_id] = method

    await query.answer()
    
    if method == "paypal":
        msg = (
            "🧾 <b>PayPal Instructions</b>\n\n"
            "Send <b>$30</b> via PayPal:\n"
            "🔗 <a href='https://www.paypal.com/ncp/payment/XQN42G8FWLF7Y'>Click Here to Pay</a>\n\n"
            "📸 After payment, send the transaction ID or a screenshot here."
        )
    elif method == "binance":
        msg = (
            "🧾 <b>Binance USDT (BEP-20)</b>\n\n"
            "Amount: <b>$30 USDT</b>\n"
            "Wallet: <code>0x3391130f64cb8a135b304b778a7e8523a1f4916d</code>\n"
            "Binance Pay ID: <b>207715971</b>\n\n"
            "📸 Send TxID or screenshot here after payment."
        )
    elif method == "mpesa":
        msg = (
            "🧾 <b>M-Pesa Instructions</b>\n\n"
            "Till Number: <b>8496752</b>\n"
            "Amount: <b>KES equivalent of $30</b>\n\n"
            "📸 After payment, send the confirmation code or screenshot here."
        )
    else:
        msg = "❌ Invalid method selected."

    await query.edit_message_text(msg, parse_mode="HTML")

# Handle proof of payment
async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    name = update.message.from_user.full_name
    method = user_payment_method.get(user_id, "Unknown")
    
    # Prepare message for admin
    caption = f"📥 <b>New Payment Proof</b>\n👤 Name: {name}\n🆔 ID: <code>{user_id}</code>\n💳 Method: {method}"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]
    ])

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=file_id, caption=caption, parse_mode="HTML", reply_markup=keyboard)
    elif update.message.text:
        proof = update.message.text
        full_msg = f"{caption}\n\n🧾 Proof:\n{proof}"
        await context.bot.send_message(chat_id=ADMIN_ID, text=full_msg, parse_mode="HTML", reply_markup=keyboard)
    else:
        await update.message.reply_text("❌ Please send a valid screenshot or text confirmation.")
        return

    await update.message.reply_text("✅ Your proof has been received. Please wait for admin approval.")

# Admin decision handler
async def handle_admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    action, user_id_str = data.split("_")
    user_id = int(user_id_str)

    if update.effective_user.id != ADMIN_ID:
        await query.edit_message_text("❌ You are not authorized to perform this action.")
        return

    if action == "approve":
        approved_users.add(user_id)
        add_approved_user(user_id)  # ✅ Save to shared file

        await context.bot.send_message(chat_id=user_id, text="🎉 Your payment has been approved! You can now generate unlimited cards.")
        await query.edit_message_text("✅ User has been approved.")
    elif action == "reject":
        await context.bot.send_message(chat_id=user_id, text="❌ Your payment proof was not accepted. Please contact support or retry.")
        await query.edit_message_text("❌ Payment rejected.")
    else:
        await query.edit_message_text("❌ Unknown action.")

# /status command
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in approved_users:
        await update.message.reply_text("✅ You are approved! You can now use the Card Generator Bot.")
    else:
        await update.message.reply_text("⏳ Your payment is pending approval.")

def start_Autonixcardpayment_bot():
     print("Starting the card payment bot...")
    
     app = Application.builder().token(TOKEN).build()
     app.add_handler(CommandHandler("start", start))
     app.add_handler(CommandHandler("status", status))
     app.add_handler(CallbackQueryHandler(handle_method_selection, pattern="^(paypal|binance|mpesa)$"))
     app.add_handler(CallbackQueryHandler(handle_admin_decision, pattern="^(approve|reject)_"))
     app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_proof))
     app.run_polling()