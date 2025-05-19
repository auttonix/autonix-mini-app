import asyncio
import json
import nest_asyncio
import websockets
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

nest_asyncio.apply()

WEBSOCKET_URL = "wss://ws.binaryws.com/websockets/v3?app_id=62714"
TELEGRAM_BOT_TOKEN = "8109474041:AAEb0mk8kemDBbN2_HNHIi2NmmyC5i4uUVI"
TRADING_KEY = "yourtradingkey"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("✅ Agree", callback_data="agree")]]
    await update.message.reply_text(
        "⚠️ Trading binary options involves risks. Do you agree?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_agreement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    context.user_data["agreed"] = True
    context.user_data["next_step"] = "api_token"
    await query.edit_message_text("✅ Welcome!\n\nPlease enter your Deriv API Token to proceed.")

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    next_step = context.user_data.get("next_step")

    if not next_step:
        await update.message.reply_text("Please start with /start.")
        return

    if next_step == "api_token":
        await authorize_user(update, context, user_input)
    elif next_step == "trading_key":
        await verify_trading_key(update, context, user_input)
    elif next_step == "stake":
        await save_stake(update, context, user_input)
    elif next_step == "take_profit":
        await save_take_profit(update, context, user_input)
    elif next_step == "stop_loss":
        await save_stop_loss(update, context, user_input)

async def authorize_user(update: Update, context: ContextTypes.DEFAULT_TYPE, api_token: str):
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            await websocket.send(json.dumps({"authorize": api_token}))
            response = json.loads(await websocket.recv())

            if "error" in response:
                await update.message.reply_text(f"❌ Authorization failed: {response['error']['message']}")
                return

            context.user_data.update({
                "api_token": api_token,
                "user_name": response["authorize"].get("fullname", "User"),
                "account_balance": response["authorize"].get("balance", 0)
            })

            await update.message.reply_text(
                f"✅ API Token Authenticated!\n👤 {context.user_data['user_name']}\n💰 {context.user_data['account_balance']} USD\n\n"
                "🔑 Now, enter your trading key to continue.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❓ I don't have a key", url="https://t.me/Autonixedgekey_bot")]
                ])
            )
            context.user_data["next_step"] = "trading_key"
    except Exception as e:
        await update.message.reply_text(f"⚠️ WebSocket error: {e}")

async def verify_trading_key(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str):
    if user_input == TRADING_KEY:
        await update.message.reply_text(
            "✅ Trading key authenticated!\n📊 Please select the trading symbol:",
            reply_markup=symbol_selection_keyboard()
        )
        context.user_data["next_step"] = "symbol"
    else:
        await update.message.reply_text("❌ Invalid trading key. Please try again.")

async def handle_symbol_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_symbol = query.data
    context.user_data["symbol"] = selected_symbol
    await query.edit_message_text(f"✅ Symbol selected: {selected_symbol}")

    trade_type_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Even", callback_data="even"),
         InlineKeyboardButton("Odd", callback_data="odd"),
         InlineKeyboardButton("Both", callback_data="both")]
    ])
    await query.message.reply_text("📈 Choose trade type:", reply_markup=trade_type_keyboard)
    context.user_data["next_step"] = "trade_type"

async def handle_trade_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_trade_type = query.data
    context.user_data["trade_type"] = selected_trade_type
    await query.edit_message_text(f"🎯 Trade type selected: {selected_trade_type.upper()}")

    await query.message.reply_text("💰 Enter your Stake Amount (e.g., 1.0)")
    context.user_data["next_step"] = "stake"

async def save_stake(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str):
    if not user_input.replace('.', '', 1).isdigit():
        await update.message.reply_text("❌ Please enter a valid number for the stake.")
        return
    context.user_data["stake"] = float(user_input)
    context.user_data["current_stake"] = float(user_input)
    context.user_data["total_profit"] = 0
    await update.message.reply_text("✅ Stake saved! Now enter your Take Profit target.")
    context.user_data["next_step"] = "take_profit"

async def save_take_profit(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str):
    if not user_input.replace('.', '', 1).isdigit():
        await update.message.reply_text("❌ Please enter a valid number for Take Profit.")
        return
    context.user_data["take_profit"] = float(user_input)
    await update.message.reply_text("✅ Take Profit saved! Now enter your Stop Loss target.")
    context.user_data["next_step"] = "stop_loss"

async def save_stop_loss(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str):
    if not user_input.replace('.', '', 1).isdigit():
        await update.message.reply_text("❌ Please enter a valid number for Stop Loss.")
        return
    context.user_data["stop_loss"] = float(user_input)
    await update.message.reply_text(
        "🎯 Setup complete! Use buttons below to start trading.",
        reply_markup=start_stop_trading_keyboard()
    )
    context.user_data["next_step"] = None

async def start_trading_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🚀 Trading started!")
    context.user_data["trading_active"] = True
    asyncio.create_task(execute_trades(query.message, context))

def symbol_selection_keyboard():
    symbols = [
        [("Volatility 10 (1s)", "1HZ10V"), ("Volatility 10", "R_10")],
        [("Volatility 25 (1s)", "1HZ25V"), ("Volatility 25", "R_25")],
        [("Volatility 50 (1s)", "1HZ50V"), ("Volatility 50", "R_50")],
        [("Volatility 75 (1s)", "1HZ75V"), ("Volatility 75", "R_75")],
        [("Volatility 100 (1s)", "1HZ100V"), ("Volatility 100", "R_100")]
    ]
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data=data) for text, data in row] for row in symbols])

def start_stop_trading_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Start Trading", callback_data="start_trading")],
        [InlineKeyboardButton("⏹️ Stop Trading", callback_data="stop_trading")]
    ])

async def execute_trades(update, context):
    api_token = context.user_data["api_token"]
    trade_type = context.user_data["trade_type"]
    symbol = context.user_data["symbol"]
    stake = context.user_data["stake"]
    total_profit = context.user_data.get("total_profit", 0)
    balance = context.user_data.get("account_balance", 0)
    take_profit = context.user_data["take_profit"]
    stop_loss = context.user_data["stop_loss"]
    user_name = context.user_data["user_name"]
    chat_id = update.chat.id

    last_digit_history = []

    async with websockets.connect(WEBSOCKET_URL) as websocket:
        await websocket.send(json.dumps({"authorize": api_token}))
        await websocket.recv()

        await websocket.send(json.dumps({"ticks": symbol, "subscribe": 1}))
        await update.reply_text(f"📈 Subscribed to {symbol} ticks.")

        while context.user_data.get("trading_active", True):
            message = json.loads(await websocket.recv())

            if message.get("msg_type") != "tick":
                continue

            price = message["tick"]["quote"]
            last_digit = int(str(price)[-1])

            last_digit_history.append(last_digit)

            # Keep only the last 10 digits
            if len(last_digit_history) > 10:
                last_digit_history.pop(0)

            if len(last_digit_history) < 10:
                continue  # Wait until 10 digits available

            even_count = sum(1 for d in last_digit_history if d % 2 == 0)
            odd_count = sum(1 for d in last_digit_history if d % 2 != 0)

            even_confidence = (even_count / 10) * 100
            odd_confidence = (odd_count / 10) * 100

            # Hot streak detection (last 3 digits)
            last_3 = last_digit_history[-3:]
            if all(d % 2 == 0 for d in last_3):
                hot_streak = "even"
            elif all(d % 2 != 0 for d in last_3):
                hot_streak = "odd"
            else:
                hot_streak = None

            decision = None
            reason = ""

            if hot_streak == "even" and (trade_type in ["even", "both"]):
                decision = "DIGITEVEN"
                reason = "🔥 Hot Streak (Even detected)"
            elif hot_streak == "odd" and (trade_type in ["odd", "both"]):
                decision = "DIGITODD"
                reason = "🔥 Hot Streak (Odd detected)"
            elif even_confidence >= 70 and (trade_type in ["even", "both"]):
                decision = "DIGITEVEN"
                reason = f"✅ High Confidence Even ({even_confidence:.1f}%)"
            elif odd_confidence >= 70 and (trade_type in ["odd", "both"]):
                decision = "DIGITODD"
                reason = f"✅ High Confidence Odd ({odd_confidence:.1f}%)"

            # If no clear decision, skip
            if not decision:
                continue

            # Send decision analysis
            await context.bot.send_message(
                chat_id,
                f"📊 Last 10 Digits: {last_digit_history}\n"
                f"⚡ {reason}\n"
                f"💵 Stake: ${context.user_data['current_stake']:.2f}\n"
                f"🚀 Placing trade now..."
            )

            # Place the trade
            await websocket.send(json.dumps({
                "buy": 1,
                "price": context.user_data["current_stake"],
                "parameters": {
                    "amount": context.user_data["current_stake"],
                    "basis": "stake",
                    "contract_type": decision,
                    "currency": "USD",
                    "duration": 1,
                    "duration_unit": "t",
                    "symbol": symbol
                }
            }))
            response = json.loads(await websocket.recv())

            if "buy" in response:
                contract_id = response["buy"]["contract_id"]

                await websocket.send(json.dumps({
                    "proposal_open_contract": 1,
                    "contract_id": contract_id,
                    "subscribe": 1
                }))

                while True:
                    contract_update = json.loads(await websocket.recv())
                    if contract_update.get("msg_type") == "proposal_open_contract":
                        contract = contract_update["proposal_open_contract"]
                        if contract.get("is_sold"):
                            payout = contract["payout"]
                            profit = contract["profit"]
                            is_win = profit >= 0
                            total_profit += profit
                            balance += profit

                            context.user_data["total_profit"] = total_profit
                            context.user_data["account_balance"] = balance

                            await context.bot.send_message(
                                chat_id,
                                f"{'🏆 Win!' if is_win else '❌ Loss!'}\n"
                                f"💵 Payout: <b>${payout:.2f}</b>\n"
                                f"📊 Total Profit: <b>${total_profit:.2f}</b>\n"
                                f"💼 Balance: <b>${balance:.2f}</b>",
                                parse_mode="HTML"
                            )

                            if total_profit >= take_profit:
                                await context.bot.send_message(
                                    chat_id,
                                    f"🎯 <b>Take Profit Reached!</b>\nSession ended.",
                                    parse_mode="HTML"
                                )
                                context.user_data["trading_active"] = False
                                return

                            if total_profit <= -stop_loss:
                                await context.bot.send_message(
                                    chat_id,
                                    f"🛑 <b>Stop Loss Hit!</b>\nSession ended.",
                                    parse_mode="HTML"
                                )
                                context.user_data["trading_active"] = False
                                return

                            if is_win:
                                context.user_data["current_stake"] = stake
                            else:
                                context.user_data["current_stake"] *= 2  # Martingale

                            break
            else:
                await update.reply_text("⚠️ Trade placement failed. Retrying...")

async def run_trading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Trading started!")
    asyncio.create_task(execute_trades(update.message, context))

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_trading))
    app.add_handler(CallbackQueryHandler(handle_agreement, pattern="^agree$"))
    app.add_handler(CallbackQueryHandler(handle_symbol_selection, pattern="^(1HZ10V|R_10|1HZ25V|R_25|1HZ50V|R_50|1HZ75V|R_75|1HZ100V|R_100)$"))
    app.add_handler(CallbackQueryHandler(handle_trade_selection, pattern="^(even|odd|both)$"))
    app.add_handler(CallbackQueryHandler(start_trading_callback, pattern="^start_trading$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))

    app.run_polling()

if __name__ == "__main__":
    main()
