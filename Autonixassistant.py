from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "7547927549:AAEKpw1yLzMRlYk6nX53KEMuWpvP5A4eCjo"
ADMIN_USER_ID = 8138483951

HELP_TOPICS = {
    "create_account": "🆕 **Creating a Deriv Account**\n\nTo get started, simply tap this link to create your free account:\n👉 [Create Account](https://track.deriv.com/_AmZyUaWfEMJB4VdSfJsOp2Nd7ZgqdRLk/1)\n\nOnce you're registered, you’ll gain access to all trading tools and bots 🚀",
    "api_token": "🔑 **What is a Deriv API Token?**\n\nA Deriv API token is your unique access key for trading with bots and apps securely.\n\nGenerate yours here:\n👉 [Get API Token](https://app.deriv.com/account/api-token)\n\nMake sure to keep it safe! 🔐",
    "trading_key": (
    "📈 **What is a Trading Key?**\n\n"
    "A **trading key** is a secure API token created with special permissions, used by our bots to trade on your behalf without exposing your full account access.\n\n"
    "🔐 This key allows the bot to place trades and stay secure while protecting your main account.\n\n"
    "💡 To generate your trading key, use the bot that matches your subscription:\n"
    "👉 [Lite Version Key Bot](https://t.me/autonix_lite_key_bot)\n"
    "👉 [Pro Version Key Bot](https://t.me/autonix_pro_key_bot)\n\n"
    "Make sure to keep your key safe, and don’t share it with anyone!"
),
    "trading_hub": (
    "📊 **Welcome to Our Trading Hub \n\n"
    "Explore all our cutting-edge trading bots designed to help automate your trading, minimize risks, and boost profitability 📈💹.\n\n"
    "Whether you're a beginner or a seasoned trader, our tools are tailored to fit your style 🧠💼.\n\n"
    "🚀 Tap the button below to access the hub and start your smart trading journey!"
),


    "min_stake": "💵 **Minimum Stake on Deriv**\n\nThe minimum stake usually starts from **$0.35**, depending on the asset and contract type. It’s perfect for starting small and scaling up as you learn 📊",
    "deposit": "💰 **How to Deposit**\n\n1. Log in to your Deriv account.\n2. Go to the **Cashier** section.\n3. Choose **Deposit** and pick your preferred method (crypto, payment agents, cards, etc).\n\nAll deposits are fast and secure 🔒",
    "withdraw": "🏧 **How to Withdraw**\n\n1. Log in to Deriv and go to **Cashier > Withdraw**\n2. Choose your withdrawal method (same as deposit usually).\n3. Confirm the request and check your email.\n\nPayouts are quick and smooth ✅",
}

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🆕 Creating an account", callback_data="create_account")],
        [InlineKeyboardButton("🔑 What is Deriv API token?", callback_data="api_token")],
        [InlineKeyboardButton("📈 What is a trading key?", callback_data="trading_key")],
        [InlineKeyboardButton("💵 Minimum stake?", callback_data="min_stake")],
        [InlineKeyboardButton("💰 How to deposit?", callback_data="deposit")],
        [InlineKeyboardButton("🏧 How to withdraw?", callback_data="withdraw")],
        [InlineKeyboardButton("📊 Access Our Trading Hub", callback_data="trading_hub")],
        [InlineKeyboardButton("👨‍💼 Talk to a human agent", callback_data="talk_human")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_menu")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 Welcome to Autonix Customer Care\n\n"
        "We're here to help you succeed in your trading journey 📈💡.\n\n"
        "Select one of the support topics below or access our trading hub to explore powerful tools and bots built to optimize your experience 🚀",
        reply_markup=get_main_menu()
    )


async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = query.data

    if topic == "trading_hub":
        await query.edit_message_text(
            text=HELP_TOPICS[topic],
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Go to Trading Hub", url="https://t.me/autonix_bot")],
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_menu")]
            ]),
            parse_mode="Markdown"
        )
        return

    elif topic == "back_to_menu":
        await query.edit_message_text(
            "🔽 Please choose from the options below:",
            reply_markup=get_main_menu()
        )
        return

    elif topic == "talk_human":
        await query.edit_message_text("👨‍💼 A human agent will contact you shortly. Please wait...")
        await context.bot.send_message(
            chat_id=ADMIN_USER_ID,
            text=f"📬 User @{query.from_user.username or query.from_user.full_name} (ID: {query.from_user.id}) is requesting support.\n\nReply to this message to respond.",
            reply_to_message_id=None
        )
        context.user_data["last_contact"] = query.from_user.id
        return

    # Default help topic response
    response = HELP_TOPICS.get(topic, "ℹ️ No info available.")
    await query.edit_message_text(
        text=response,
        reply_markup=get_back_menu(),
        parse_mode="Markdown"
    )

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and update.effective_user.id == ADMIN_USER_ID:
        original_text = update.message.reply_to_message.text

        user_id_line = original_text.split("ID: ")[-1]
        user_id = int(user_id_line.split(")")[0])

        await context.bot.send_message(
            chat_id=user_id,
            text=f"💬 **Message from support**:\n\n{update.message.text}",
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Message delivered to the user.")
    else:
        return

def start_assistant_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_reply))

    print("🤖 Bot is up and running...")
    app.run_polling()