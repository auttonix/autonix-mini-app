import asyncio
import json
import datetime
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

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("✅ Agree", callback_data="agree")]]
    await update.message.reply_text(
        "⚠️ Trading binary options involves risks. Do you agree?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Handle user agreement
async def handle_agreement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    context.user_data["agreed"] = True
    context.user_data["next_step"] = "api_token"
    await query.edit_message_text("✅ Welcome!\n\nPlease enter your Deriv API Token to proceed.")

# Handle user inputs
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

# Authorize user
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
                    [InlineKeyboardButton("❓ Get a Key", url="https://t.me/Autonixedgekey_bot")]
                ])
            )
            context.user_data["next_step"] = "trading_key"
    except Exception as e:
        await update.message.reply_text(f"⚠️ WebSocket error: {e}")

# Verify trading key
async def verify_trading_key(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str):
    if user_input == TRADING_KEY:
        await update.message.reply_text(
            "✅ Trading key authenticated!\n📊 Please select the trading symbol:",
            reply_markup=symbol_selection_keyboard()
        )
        context.user_data["next_step"] = "symbol"
    else:
        await update.message.reply_text("❌ Invalid trading key. Please try again.")

# Select trading symbol
async def handle_symbol_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_symbol = query.data
    context.user_data["symbol"] = selected_symbol
    await query.edit_message_text(f"✅ Symbol selected: {selected_symbol}")
    await query.message.reply_text("💰 Enter your Stake Amount (e.g., 1.0)")
    context.user_data["next_step"] = "stake"

# Save stake
async def save_stake(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str):
    if not user_input.replace('.', '', 1).isdigit():
        await update.message.reply_text("❌ Please enter a valid number for the stake.")
        return
    context.user_data["stake"] = float(user_input)
    context.user_data["current_stake"] = float(user_input)
    context.user_data["total_profit"] = 0
    await update.message.reply_text("✅ Stake saved! Now enter your Take Profit target.")
    context.user_data["next_step"] = "take_profit"

# Save take profit
async def save_take_profit(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str):
    if not user_input.replace('.', '', 1).isdigit():
        await update.message.reply_text("❌ Please enter a valid number for Take Profit.")
        return
    context.user_data["take_profit"] = float(user_input)
    await update.message.reply_text("✅ Take Profit saved! Now enter your Stop Loss target.")
    context.user_data["next_step"] = "stop_loss"

# Save stop loss
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

# Start trading
async def start_trading_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🚀 Trading started!")
    context.user_data["trading_active"] = True
    asyncio.create_task(execute_trades(query.message, context))

# Build symbol selection
def symbol_selection_keyboard():
    symbols = [
        [("Volatility 10 (1s)", "1HZ10V"), ("Volatility 10", "R_10")],
        [("Volatility 25 (1s)", "1HZ25V"), ("Volatility 25", "R_25")],
        [("Volatility 50 (1s)", "1HZ50V"), ("Volatility 50", "R_50")],
        [("Volatility 75 (1s)", "1HZ75V"), ("Volatility 75", "R_75")],
        [("Volatility 100 (1s)", "1HZ100V"), ("Volatility 100", "R_100")]
    ]
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data=data) for text, data in row] for row in symbols])

# Start/Stop Trading keyboard
def start_stop_trading_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Start Trading", callback_data="start_trading")],
        [InlineKeyboardButton("⏹️ Stop Trading", callback_data="stop_trading")]
    ])

async def execute_trades(update, context):
    api_token = context.user_data["api_token"]
    symbol = context.user_data["symbol"]
    base_stake = context.user_data["stake"]
    current_stake = context.user_data.get("current_stake", base_stake)
    total_profit = context.user_data.get("total_profit", 0)
    balance = context.user_data.get("account_balance", 0)
    take_profit = context.user_data["take_profit"]
    stop_loss = context.user_data["stop_loss"]
    chat_id = update.chat_id


    price_history = []

    async with websockets.connect(WEBSOCKET_URL) as websocket:
        await websocket.send(json.dumps({"authorize": api_token}))
        await websocket.recv()

        await websocket.send(json.dumps({"ticks": symbol, "subscribe": 1}))
        await update.reply_text(f"📈 Subscribed to {symbol} ticks (Enhanced Mode).")


        while context.user_data.get("trading_active", True):
            # Time filter: Avoid trading outside safe hours
            now = datetime.datetime.utcnow()
            if now.hour < 6 or now.hour > 18:
                await asyncio.sleep(1)
                continue

            # Receive tick
            message = json.loads(await websocket.recv())
            if message.get("msg_type") != "tick":
                continue

            price = message["tick"]["quote"]
            price_history.append(price)

            if len(price_history) > 50:
                price_history.pop(0)

            if len(price_history) < 26:
                continue

            # --- Indicators ---
            last_price = price_history[-1]
            previous_price = price_history[-2]
            ema10 = calculate_ema(price_history[-10:])
            ema20 = calculate_ema(price_history[-20:])
            rsi = calculate_rsi(price_history[-14:])
            macd_line, macd_signal = calculate_macd(price_history)
            bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(price_history[-20:])
            volatility = calculate_volatility(price_history[-20:])

            # --- Generate Signals ---
            signals = []

            # RSI + Price Action
            resistance = max(price_history[-5:])
            support = min(price_history[-5:])
            if rsi < 30 and last_price > resistance:
                signals.append("CALL")
            elif rsi > 70 and last_price < support:
                signals.append("PUT")

            # EMA Cross
            if previous_price < ema10 and last_price > ema10:
                signals.append("CALL")
            elif previous_price > ema10 and last_price < ema10:
                signals.append("PUT")

            # MACD
            if macd_line > macd_signal:
                signals.append("CALL")
            elif macd_line < macd_signal:
                signals.append("PUT")

            # Volatility Control
            if volatility > 0.1:
                signals.append("TRADE")
            else:
                signals.append("SKIP")

            # Decision: All main indicators must agree
            if "SKIP" in signals:
                continue

            indicator_signals = signals[:-1]  # Exclude Volatility tag
            volatility_signal = signals[-1]

            if not (all(s == "CALL" for s in indicator_signals) or all(s == "PUT" for s in indicator_signals)):
                continue  # Mixed signals, skip

            decision = "CALL" if all(s == "CALL" for s in indicator_signals) else "PUT"

            # --- Place Trade ---
            await context.bot.send_message(
                chat_id,
                f"📈 Last Price: {last_price:.5f}\n"
                f"🔵 EMA10: {ema10:.5f}\n"
                f"🎯 RSI: {rsi:.2f}\n"
                f"📈 MACD Line: {macd_line:.5f}, Signal Line: {macd_signal:.5f}\n"
                f"🎯 Bollinger Bands: Upper {bb_upper:.5f}, Lower {bb_lower:.5f}\n"
                f"💨 Volatility: {volatility:.5f}\n\n"
                f"✅ Decision: <b>{decision}</b>\n"
                f"🚀 Stake: <b>${current_stake:.2f}</b>",
                parse_mode="HTML"
            )

            await websocket.send(json.dumps({
                "buy": 1,
                "price": current_stake,
                "parameters": {
                    "amount": current_stake,
                    "basis": "stake",
                    "contract_type": decision,
                    "currency": "USD",
                    "duration": 5,
                    "duration_unit": "t",
                    "symbol": symbol
                }
            }))

            # --- Wait for Trade Result ---
            response = json.loads(await websocket.recv())
            if "buy" not in response:
                await update.message.reply_text("⚠️ Trade placement failed. Retrying...")
                continue

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

                        # Check for take profit or stop loss
                        if total_profit >= take_profit:
                            await context.bot.send_message(
                                chat_id,
                                f"🎯 <b>Take Profit Reached!</b>\nSession Ended.",
                                parse_mode="HTML"
                            )
                            context.user_data["trading_active"] = False
                            return

                        if total_profit <= -stop_loss:
                            await context.bot.send_message(
                                chat_id,
                                f"🛑 <b>Stop Loss Hit!</b>\nSession Ended.",
                                parse_mode="HTML"
                            )
                            context.user_data["trading_active"] = False
                            return

                        # Martingale strategy: Win ➔ Reset stake, Loss ➔ Double stake
                        if is_win:
                            current_stake = base_stake
                        else:
                            current_stake *= 2  # Martingale x2
                        
                        context.user_data["current_stake"] = current_stake
                        break

# 📈 Calculate EMA (Exponential Moving Average)
def calculate_ema(prices, period=10):
    ema = prices[0]
    multiplier = 2 / (period + 1)
    for price in prices[1:]:
        ema = (price - ema) * multiplier + ema
    return ema

# 📈 Calculate MACD
def calculate_macd(prices):
    ema12 = calculate_ema(prices, 12)
    ema26 = calculate_ema(prices, 26)
    macd_line = ema12 - ema26
    signal_line = calculate_ema([macd_line], 9)
    return macd_line, signal_line

# 📈 Calculate RSI
def calculate_rsi(prices, period=14):
    gains, losses = [], []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        gains.append(max(0, diff))
        losses.append(max(0, -diff))
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# 📈 Calculate Bollinger Bands
def calculate_bollinger_bands(prices, period=20, std_dev_multiplier=2):
    sma = sum(prices[-period:]) / period
    variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
    std_dev = variance ** 0.5
    upper_band = sma + (std_dev_multiplier * std_dev)
    lower_band = sma - (std_dev_multiplier * std_dev)
    return upper_band, sma, lower_band

# 📈 Calculate Volatility
def calculate_volatility(prices):
    returns = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
    avg_return = sum(abs(r) for r in returns) / len(returns)
    return avg_return


# Run the bot
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_agreement, pattern="^agree$"))
    app.add_handler(CallbackQueryHandler(handle_symbol_selection, pattern="^(1HZ10V|R_10|1HZ25V|R_25|1HZ50V|R_50|1HZ75V|R_75|1HZ100V|R_100)$"))
    app.add_handler(CallbackQueryHandler(start_trading_callback, pattern="^start_trading$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))

    app.run_polling()

if __name__ == "__main__":
    main()
