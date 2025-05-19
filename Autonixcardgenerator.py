import random
import time
import logging
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from datetime import datetime, timedelta
import json

def is_approved(user_id):
    try:
        with open("approved_users.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"approved_users": []}

    return user_id in data["approved_users"]

cooldowns = {}

user_generation_count = {}

paid_users = set()

approved_users = set()

TELEGRAM_BOT_TOKEN = "7564968494:AAERRDJ1STgPhUFMa34b-Mv8sAZm_MYJPyM"
ADMIN_ID = 6056419001
FREE_CARD_LIMIT = 5
COOLDOWN_SECONDS = 6 * 60 * 60 

import logging

logging.basicConfig(level=logging.INFO)

# Suppress httpx logs
logging.getLogger("httpx").setLevel(logging.WARNING)

# Optionally suppress telegram logs
logging.getLogger("telegram").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

COUNTRY_TO_CODE = {
    "UNITED STATES": "US",
    "FRANCE": "FR",
    "POLAND": "PL",
    "KENYA": "KE",
    "CANADA": "CA",
    "SOUTH AFRICA": "ZA",
    "UNITED KINGDOM": "GB",
    "INDIA": "IN",
    "SPAIN": "ES",
    "AUSTRALIA": "AU"
}


def country_code_to_flag(country_code):
    return ''.join(chr(ord(c) + 127397) for c in country_code.upper())


BIN_DATA = {
    "400005": {"Bank": "---", "Card": "VISA", "Type": "DEBIT", "Category": "BUSINESS", "Country": "UNITED STATES", "Valid": "Yes"},
    "411111": {"Bank": "JPMORGAN CHASE BANK, N.A.", "Card": "VISA", "Type": "CREDIT", "Category": "---", "Country": "UNITED STATES", "Valid": "Yes"},
    "455660": {"Bank": "NATIXIS", "Card": "VISA", "Type": "DEBIT", "Category": "ELECTRON", "Country": "FRANCE", "Valid": "Yes"},
    "491761": {"Bank": "BANK POLSKA KASA OPIEKI S.A. (BANK PEKAO SA)", "Card": "VISA", "Type": "CREDIT", "Category": "BUSINESS", "Country": "POLAND", "Valid": "Yes"},
    "442461": {"Bank": "UNITED BANK FOR AFRICA", "Card": "VISA", "Type": "DEBIT", "Category": "CLASSIC", "Country": "KENYA", "Valid": "Yes"},
    "520473": {"Bank": "RBC ROYAL BANK", "Card": "VISA", "Type": "CREDIT", "Category": "GOLD", "Country": "CANADA", "Valid": "Yes"},
    "539983": {"Bank": "STANDARD BANK", "Card": "VISA", "Type": "DEBIT", "Category": "PLATINUM", "Country": "SOUTH AFRICA", "Valid": "Yes"},
    "531142": {"Bank": "HSBC", "Card": "VISA", "Type": "CREDIT", "Category": "PREMIUM", "Country": "UNITED KINGDOM", "Valid": "Yes"},
    "456783": {"Bank": "STATE BANK OF INDIA", "Card": "VISA", "Type": "DEBIT", "Category": "CLASSIC", "Country": "INDIA", "Valid": "Yes"},
    "401288": {"Bank": "BANK OF AMERICA", "Card": "VISA", "Type": "CREDIT", "Category": "PLATINUM", "Country": "UNITED STATES", "Valid": "Yes"},
    "427020": {"Bank": "BANCO SANTANDER", "Card": "VISA", "Type": "CREDIT", "Category": "STANDARD", "Country": "SPAIN", "Valid": "Yes"},
    "451416": {"Bank": "ANZ", "Card": "VISA", "Type": "DEBIT", "Category": "STANDARD", "Country": "AUSTRALIA", "Valid": "Yes"},
}

ADDRESS_DATA = {
    "UNITED STATES": {"Postal": "10001", "City": "New York", "State": "New York"},
    "FRANCE": {"Postal": "75001", "City": "Paris", "State": ""},
    "POLAND": {"Postal": "00-001", "City": "Warsaw", "State": ""},
    "KENYA": {"Postal": "00100", "City": "Nairobi", "State": ""},
    "CANADA": {"Postal": "M5H 2N2", "City": "Toronto", "State": "Ontario"},
    "SOUTH AFRICA": {"Postal": "2000", "City": "Johannesburg", "State": "Gauteng"},
    "UNITED KINGDOM": {"Postal": "EC1A 1BB", "City": "London", "State": ""},
    "INDIA": {"Postal": "110001", "City": "New Delhi", "State": "Delhi"},
    "SPAIN": {"Postal": "28001", "City": "Madrid", "State": ""},
    "AUSTRALIA": {"Postal": "2000", "City": "Sydney", "State": "New South Wales"}
}

user_generation_count = {}
user_selection = {}

# Command to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    welcome_text = (
        "Welcome to the Card Generator Bot! 🎉\n\n"
        "You can generate random card details by following the steps below.\n\n"
        "Click 'Get Card' to start the process."
    )

    start_keyboard = [
    [InlineKeyboardButton("💳 Get Card", callback_data="get_card")],
    [InlineKeyboardButton("🔓 Upgrade to Unlimited", callback_data="payment_info")],
    [InlineKeyboardButton("📞 Contact Customer Care", url="https://t.me/autonix_assistant_bot")]
]


    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(start_keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    await query.answer()

    data = query.data

    # Handle card request
    if data == "get_card":
        countries = list(set(info["Country"] for info in BIN_DATA.values()))
        keyboard = [
            [InlineKeyboardButton(country.title(), callback_data=f"country_{country}")]
            for country in countries
        ]
        await query.edit_message_text("🌍 Choose a country:", reply_markup=InlineKeyboardMarkup(keyboard))

    # Handle country selection
    elif data.startswith("country_"):
        selected_country = data.split("_", 1)[1]
        user_selection[user_id] = {"country": selected_country}
        quantity_buttons = [
            [InlineKeyboardButton(str(q), callback_data=f"quantity_{q}")]
            for q in range(1, 6)
        ]
        code = COUNTRY_TO_CODE.get(selected_country.upper(), "")
        flag = country_code_to_flag(code) if code else "🌍"
        await query.edit_message_text(
        f"{flag} Country: {selected_country.title()}\n\nHow many cards do you want?",
        reply_markup=InlineKeyboardMarkup(quantity_buttons)
    )


    # Handle quantity selection
    elif data.startswith("quantity_"):
        quantity = int(data.split("_")[1])
        user_selection[user_id]["quantity"] = quantity
        await query.edit_message_text(
            f"✅ Country: {user_selection[user_id]['country'].title()}\n"
            f"💳 Quantity: {quantity}\n\nReady?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Generate", callback_data="generate_cards")]
            ])
        )

    # Handle payment info request
    elif data == "payment_info":
        await query.edit_message_text(
            "🔐 To unlock unlimited card generation for all countries, please make a one-time payment.\n\n"
            "Click the button below to go to our payment bot. Once you’ve paid, come back here and press '✅ I Have Paid'.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💸 Go to Payment Bot", url="https://t.me/autonix_card_payment_bot")],
                [InlineKeyboardButton("✅ I Have Paid", callback_data="confirm_payment")]
            ])
        )

    # Handle payment confirmation
    elif data == "confirm_payment":
        if user_id in paid_users or user_id in approved_users:
            paid_users.add(user_id)
            await query.edit_message_text(
                "🎉 Payment confirmed! You now have unlimited access to all countries' cards.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 Get Card", callback_data="get_card")]
                ])
            )
        else:
            await query.edit_message_text(
                "⏳ Your payment is pending approval by the admin.\n\n"
                "Please wait a few minutes after submitting your proof in the payment bot.\n\n"
                "Click below to go to the payment bot if you haven’t yet.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💸 Go to Payment Bot", url="https://t.me/autonix_card_payment_bot")]
                ])
            )

    # Handle card generation
    elif data == "generate_cards":
        if user_id not in user_selection:
            await query.edit_message_text("Session expired. Please start again with /start.")
            return

        country = user_selection[user_id]["country"]
        quantity = user_selection[user_id]["quantity"]

        now = time.time()
        user_data = user_generation_count.setdefault(user_id, {})
        count, last_time = user_data.get(country, [0, 0])

        if now - last_time >= COOLDOWN_SECONDS:
            count = 0
            last_time = now

        # ✅ Auto-unlock access if user is approved
        if is_approved(user_id):
            paid_users.add(user_id)

        # ⛔ Enforce free user limits if not paid
        if user_id not in paid_users and count >= FREE_CARD_LIMIT:
            remaining = int(COOLDOWN_SECONDS - (now - last_time))
            h, m, s = remaining // 3600, (remaining % 3600) // 60, remaining % 60
            await query.edit_message_text(
                f"⚠️ You've reached the 6-hour card limit for {country.title()}.\n"
                f"⏳ Try again in {h}h {m}m {s}s.\n\n"
                f"To continue generating cards without waiting, upgrade to unlimited access.\n\n"
                f"Or choose a different country to keep going.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🌍 Choose Another Country", callback_data="get_card")],
                    [InlineKeyboardButton("🔓 Upgrade to Unlimited", callback_data="payment_info")]
                ])
            )
            return

        # 🎴 Generate the cards
        available_bins = [bin for bin, data in BIN_DATA.items() if data["Country"] == country.upper()]
        if not available_bins:
            await query.edit_message_text("❌ No BINs available for this country.")
            return

        to_generate = quantity if user_id in paid_users else min(quantity, FREE_CARD_LIMIT - count)

        cards = []
        for _ in range(to_generate):
            bin_code = random.choice(available_bins)
            info = BIN_DATA[bin_code]
            card_number = bin_code + ''.join(str(random.randint(0, 9)) for _ in range(10))
            exp = f"{random.randint(1, 12):02d}/{random.randint(25, 28)}"
            cvv = f"{random.randint(100, 999)}"
            address = ADDRESS_DATA.get(info["Country"].upper(), {})

            cards.append(
                f"<b>💳 CARD:</b> {card_number}|{exp}|{cvv}\n"
                f"<b>🏛 BANK:</b> {info['Bank']}\n"
                f"<b>🌐 TYPE:</b> {info['Type']} {info['Card']} - {info['Category']}\n"
                f"<b>🌍 COUNTRY:</b> {info['Country']}\n"
                f"<b>📍 ADDRESS:</b> {address.get('City', '')}, {address.get('State', '')}, {address.get('Postal', '')}\n"
                f"{'='*30}"
            )

        # Track usage
        user_generation_count[user_id][country] = [count + to_generate, last_time]

        await context.bot.send_message(chat_id, "\n\n".join(cards), parse_mode="HTML")

        # 🎁 Promo section
        promo_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌟 Trade using our lite Bot", url="https://t.me/autonix_lite_bot")],
            [InlineKeyboardButton("🌟 Trade using our Pro Bot", url="https://t.me/autonix_pro_bot")],
            [InlineKeyboardButton("🌟 Join Our Telegram Channel", url="https://t.me/autonix001")]
        ])
        await context.bot.send_message(
            chat_id,
            text=(
                f"🎉 <b>Card generation complete!</b>\n\n"
                f"• Follow our <a href='https://t.me/autonix001'>channel</a>.\n"
                f"• Try our other bots and website for more tools.\n\n"
                f"<b>Happy trading!</b> 🔥"
            ),
            reply_markup=promo_keyboard,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram.ext import Application, ContextTypes

# Initialize the bot application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Command to handle help requests
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Here's how you can use the bot:\n\n"
        "1. Click 'Get Card' to start generating card details.\n"
        "2. Choose your desired country and number of cards.\n"
        "3. Click 'Generate' to create your cards.\n"
        "4. After generating cards, explore trading options and more through the provided buttons."
    )
    await update.message.reply_text(help_text)

def start_Autonixcardgenerator_bot():
        print("Starting the card generation bot...")
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(CallbackQueryHandler(help, pattern="help"))
        application.run_polling()