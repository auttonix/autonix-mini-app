import asyncio
import json
from datetime import datetime
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler
from telegram.constants import ParseMode

BOT_TOKEN = "8115406246:AAHB6GKMSCcWFl4IGDcdQa3i9S9_AyjSq-Y"
CHANNEL_ID = "@autonix001"


schedule = {
    "Monday": {
    "08:00 AM": "Good morning, traders! 🌞 Start your week with a solid foundation. Here are the key market insights for the week ahead: \n\n1️⃣ Major economic reports to watch this week (e.g., interest rate decisions, inflation data).\n2️⃣ Trending symbols on Deriv: Look out for opportunities in Forex pairs like EUR/USD or commodities like Gold. \n3️⃣ Strategy of the Week: Use our advanced TWBBESTBOTS tools to analyze digit patterns and refine your entries.\n\nPlan your trades, and let’s conquer the markets together! 💪",
    "09:30 AM": "💡 **Quick Tip:** Remember to check market sentiment indicators. Use tools like the fear and greed index or sentiment analysis to guide your trading decisions. ✅",
    "10:00 AM": "📊 **Market Insight:** Don’t forget to check for overnight market updates. Focus on your watchlist and start identifying potential trade setups.",
    "11:00 AM": "📌 **Motivation Monday:** A successful trader is not the one who always wins but the one who learns from losses and adapts. Stay disciplined and focused today. 🚀",
    "01:00 PM": "💡 **Midday Reminder:** Trading is 80% preparation and 20% execution. Use this time to review market movements from the morning and refine your afternoon strategy. Don’t forget to set stop losses and profit targets for every trade. 📊",
    "02:30 PM": "🌟 **Pro Tip:** Use price action to confirm your entries and exits. Look for key levels of support and resistance to make data-driven decisions. 📉📈",
    "03:00 PM": "🔔 **Afternoon Boost:** Are you managing your risk effectively? Always follow the 1% rule to preserve capital and grow your account steadily. 📈",
    "05:00 PM": "📚 **Learning Hour:** Dedicate this time to brushing up on a trading concept. Learn about candlestick patterns, trendlines, or a new trading strategy to expand your knowledge base. 📘",
    "06:30 PM": "🛠️ **Tool Spotlight:** Have you tried our premium tools yet? TWBBESTBOTS can make your trading life easier with automated insights and analysis. Don’t miss out!",
    "08:00 PM": "🌙 **Evening Recap:** How did your trading day go? Use this time to review your performance. Identify trades that went well and those that didn’t, and take notes for improvement tomorrow. Remember, consistency and learning from mistakes lead to long-term success. 🚀",
    "09:30 PM": "✨ **End-of-Day Reflection:** Trading is a journey, not a sprint. Celebrate your small wins, analyze setbacks, and get ready to tackle the markets tomorrow with a refreshed mindset! 🌟"
    },
    "Tuesday": {
        "08:00 AM": "🌅 **Morning Kickstart:**\nStart your trading day with a quick review of the market: \n\n1️⃣ Check for overnight market updates that could impact today’s trades. \n2️⃣ Review open positions and adjust targets if necessary.\n3️⃣ Focus Symbol: Try trading the DIGITOVER/UNDER strategy with today’s tick analysis. Don’t forget to set clear parameters for risk management!\n\nLet’s make today a winning one! 📈",
        "10:00 AM": "🔍 **Quick Tip:** Pay attention to high-impact news events today. Use our TWBBESTBOTS platform to analyze tick trends and patterns for better entries.",
        "01:00 PM": "🚀 **Strategy Spotlight:** This afternoon, let’s discuss the importance of patience in trading. Waiting for high-probability setups is better than forcing trades. Remember, your capital is your weapon—don’t waste it on unnecessary risks. Stay disciplined! 💪",
        "03:00 PM": "📈 **Trade Check:** Mid-afternoon is a great time to revisit your trading goals. Are you staying disciplined and following your plan?",
        "08:00 PM": "🎉 **End-of-Day Wrap-Up:**\nHow did your strategies perform today? Share your wins and lessons in the comments! Remember, every loss is a lesson, and every win builds confidence. Let’s prepare for tomorrow by refining our strategies. 🌟"
    },
    "Wednesday": {
        "08:00 AM": "Good morning, traders! 🌞 Midweek means it’s time to refocus and assess your progress:\n\n1️⃣ Analyze how the markets have moved since Monday. Are there any emerging trends?\n2️⃣ Use TWBBESTBOTS tools to review your trades and identify areas for improvement.\n3️⃣ Stick to your trading plan and avoid impulsive decisions!\n\nLet’s make today a productive day. 🚀",
        "10:00 AM": "💡 **Mid-Morning Insight:** Stay updated with market conditions and focus on high-probability trades. Discipline over emotions!",
        "01:00 PM": "🔎 **Market Analysis Update:** Take a look at the current trends in the markets you’re trading. Is there a clear direction? If not, it might be better to wait for more favorable setups. Always remember: No trade is better than a bad trade. 📊",
        "03:00 PM": "📘 **Strategy Tip:** Review your risk-reward ratio for today’s trades. Are you targeting at least 2:1 for each setup?",
        "08:00 PM": "📘 **Evening Review:**\nTake a moment to reflect on your trading journey this week so far:\n\n✅ What have you learned?\n✅ Which strategies have been most effective?\n✅ What adjustments will you make tomorrow?\n\nSuccess in trading is built day by day—keep going! 💡"
    },
    "Thursday": {
    "09:00 AM": "📊 **Market Analysis:**\nTake a moment to assess the current market conditions. Are there any news events or economic indicators that could impact your trading strategy today? Stay informed and adjust your plans accordingly.",
    "11:00 AM": "🛠️ **Strategy Check:**\nReview your current trading strategies. Are they aligned with the prevailing market trends? Consider utilizing TWBBESTBOTS' customizable strategies to enhance your approach.",
    "12:00 PM": "💡 **Educational Break:**\nDedicate this time to learning. Read an article or watch a tutorial to expand your trading knowledge. Continuous learning is key to staying ahead in the markets.",
    "02:00 PM": "📈 **Performance Review:**\nAnalyze your trades from the morning session. What patterns are emerging? Use these insights to inform your decisions for the rest of the day.",
    "04:00 PM": "🧘 **Mindfulness Moment:**\nTrading can be stressful. Take a short break to clear your mind. A calm and focused trader makes better decisions.",
    "05:00 PM": "🔍 **Risk Management:**\nAssess your risk exposure. Are you adhering to your risk management rules? Remember, protecting your capital is paramount.",
    "06:00 PM": "📅 **Plan for Tomorrow:**\nBegin outlining your trading plan for the next day. Setting clear objectives now can lead to better performance tomorrow.",
    "07:00 PM": "🛠️ **Tool Optimization:**\nExplore new features on TWBBESTBOTS that can enhance your trading efficiency. Staying updated with your tools can provide a competitive edge.",
    "09:00 PM": "📚 **Reflect and Document:**\nUpdate your trading journal with today's experiences. Documenting your trades helps in identifying strengths and areas for improvement.",
    "10:00 PM": "🌌 **Evening Wind Down:**\nDisconnect from the markets and relax. A well-rested mind is crucial for making sound trading decisions."
    },
    "Friday": {
    "08:00 AM": "🌟 **Friday Focus:**\n Here are three things to focus on today:\n\n1️⃣ Avoid unnecessary risks—don’t ruin a good week with impulsive trades.\n2️⃣ Lock in profits and stay disciplined.\n3️⃣ Plan your weekend analysis to review your performance and prepare for next week.\n\nLet’s finish strong! 💪",
    "09:30 AM": "🔔 **Market Momentum:** Check the market trends and spot any early opportunities. Are there any patterns developing? Take advantage of the calm before midday volatility.",
    "10:00 AM": "📢 **Reminder:** Stick to our strategy and avoid chasing the market. Let the opportunities come to you.",
    "11:30 AM": "📊 **Performance Snapshot:** Mid-morning is a great time to assess your trades. Are you on track with your goals? Adjust positions if needed but stay calm and focused. 📈",
    "12:00 PM": "💡 **Pro Tip:** Avoid revenge trading—it's better to wait for clear setups than to force trades. Protect your capital at all costs!",
    "01:00 PM": "🧠 **Weekly Review Tips:** Use this afternoon to assess your overall trading performance:\n\n✅ How many trades did you win vs. lose?\n✅ Were your strategies effective?\n✅ What can you do differently next week?\n\nReflection is the key to growth in trading! 🚀",
    "02:00 PM": "📋 **Market Watch:** As we approach the afternoon session, double-check for high-probability setups. Review key levels and prepare for the market’s next move.",
    "03:00 PM": "📋 **Trade Check:** Keep an eye on the clock. Wrap up your week with disciplined trades and don’t overtrade before the weekend.",
    "04:30 PM": "⚠️ **Risk Management Reminder:** It’s easy to get caught up in end-of-week excitement. Stay cautious and ensure your stops and limits are in place. 🛑",
    "05:00 PM": "🔍 **Key Insights:** Reflect on today’s top trades. What strategies worked well? Make a note to use those insights for next week’s plan.",
    "06:30 PM": "🚀 **Motivational Boost:** Trading success is a marathon, not a sprint. Celebrate your small wins today and keep pushing for consistent growth!",
    "07:00 PM": "📈 **Weekend Prep Checklist:**\n\n1️⃣ Backup your trading journal and analyze this week’s performance.\n2️⃣ Review missed opportunities and identify improvement areas.\n3️⃣ Plan your educational activities for the weekend.",
    "08:00 PM": "🎉 **Weekend Prep:** Congratulations on completing another trading week! Spend the evening relaxing and preparing for the week ahead. Remember, balance is essential—take time to recharge and come back stronger. See you on Monday! 🌟",
    "09:30 PM": "📘 **Weekly Learnings:** Jot down three key lessons from the week. How can you apply these to improve your trades next week? Learning never stops!",
    "10:30 PM": "🌙 **Mindset Matters:** Trading is as much about psychology as it is about strategy. Reflect on how well you managed emotions this week and set goals to improve your mental game. 🧠",
    "11:30 PM": "💤 **Final Thought:** As the week ends, remind yourself of why you started trading. Keep your vision in mind and stay committed to the journey. Success takes time, effort, and patience! ✨"
    },
    "Saturday": {
    "08:00 AM": "☀️ **Weekend Trading Start:** A new day, new opportunities! Here’s how to make the most of Saturday:\n\n1️⃣ Review trends from Friday. \n2️⃣ Look for stable patterns in volatility indices.\n3️⃣ Stick to high-probability setups and use proper risk management.\n\nLet’s get started! 🚀",
    "09:00 AM": "🛠 **Trading Tool Check:** Ensure your indicators are updated and your trading platform is functioning smoothly. Avoid missing opportunities due to technical issues.",
    "10:00 AM": "🔎 **Market Focus:** Mid-morning is a great time to analyze patterns in Volatility 25 and Volatility 75 indices. Are they trending or ranging? Adjust your strategies accordingly.",
    "11:00 AM": "📌 **Tip:** Always analyze the spread before entering trades. Wider spreads can eat into your profits, especially during the weekend.",
    "12:00 PM": "💡 **Saturday Tip:** Use smaller trade sizes during the weekend to test new strategies or refine existing ones. Weekends are perfect for experimentation without risking too much capital.",
    "01:00 PM": "⚖️ **Risk Check:** Have you set your stop loss for each trade? Weekend markets can move quickly; protect your capital at all times.",
    "02:00 PM": "📈 **Strategy Check:** Are you seeing consistent results today? If not, it might be better to pause trading and analyze market conditions.",
    "03:00 PM": "💬 **Community Time:** Engage with other traders and discuss current market conditions. Sometimes a fresh perspective can reveal new insights.",
    "04:00 PM": "🧠 **Mindset Reminder:** Trading on weekends requires focus. Take short breaks to clear your mind and stay sharp for the next trade.",
    "05:00 PM": "🔔 **Alert:** Monitor Volatility 100 and Step Index for potential evening breakouts. Adjust your strategy to catch these moves.",
    "06:00 PM": "🌟 **Educational Break:** Spend time improving your skills. Watch a webinar, read a trading book, or practice on a demo account. Every bit of learning adds up.",
    "07:00 PM": "📚 **Strategy Spotlight:** Explore advanced strategies like Martingale or Trend Continuation for volatility indices. Remember to test thoroughly before using them on a live account.",
    "08:00 PM": "📊 **Evening Analysis:** Use the evening to review your trades. Look for areas where you could have improved and note your observations for tomorrow.",
    "09:00 PM": "📝 **Weekly Recap:** Start summarizing your week’s trading performance. What were your top trades and lessons learned?",
    "10:00 PM": "🌙 **End-of-Day Reflection:** Trading is a 24/7 opportunity, but that doesn’t mean you need to trade non-stop. Reflect on today’s performance, and take time to recharge for tomorrow."
    },
    "Sunday": {
        "08:00 AM": "☀️ **Sunday Kickoff:** The markets are alive and full of opportunities. Start your day with a quick review of key indices like Volatility 50 and Boom/Bust 300. 🚀",
        "10:00 AM": "📊 **Market Analysis:** Look for breakout patterns or reversals in your favorite volatility indices. Ensure you’re sticking to your trading plan and risk management rules.",
        "12:00 PM": "💡 **Sunday Strategy:** Don’t overtrade. Weekends can be slower for some markets, so focus on quality over quantity.",
        "02:00 PM": "⚡ **Power Hour:** Midday often presents great setups. Check the charts for consolidation patterns or strong trends and act accordingly.",
        "04:00 PM": "📈 **Educational Tip:** Use Sundays to prepare for the upcoming week. Research economic events or study advanced trading strategies to stay ahead of the curve.",
        "06:00 PM": "🛠️ **Tool Spotlight:** Use TWBBESTBOTS to optimize your entries and exits. Set your parameters carefully and let the tools work for you.",
        "08:00 PM": "🎉 **Sunday Wins:** Reflect on your best trades of the weekend. What went right? How can you replicate that success?",
        "10:00 PM": "💤 **Weekend Wrap-Up:** As the weekend winds down, review your trading journal and prepare for Monday. Rest well and recharge for a successful week ahead!"
    }

}

bot = Bot(token=BOT_TOKEN)

async def send_greeting():
    try:
        greeting_message = "Hello everyone! Are you ready to make some crazy profits? 🚀"
        sent_message = await bot.send_message(chat_id=CHANNEL_ID, text=greeting_message)
        await asyncio.sleep(5)
        await bot.delete_message(chat_id=CHANNEL_ID, message_id=sent_message.message_id)
        print("Greeting message sent and deleted.")
    except Exception as e:
        print(f"Error in send_greeting: {e}")

async def send_message(content):
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=content, parse_mode=ParseMode.MARKDOWN)
        print(f"Message sent: {content}")
    except Exception as e:
        print(f"Error in send_message: {e}")

async def post_scheduled_content():
    while True:
        now = datetime.now()
        current_time = now.strftime("%I:%M %p")
        current_day = now.strftime("%A")

        if current_day in schedule and current_time in schedule[current_day]:
            content = schedule[current_day][current_time]
            print(f"Sending scheduled content: {content}")
            await send_message(content)

        await asyncio.sleep(60)  

async def start(update: Update, context):
    await update.message.reply_text("✅ Bot is active and scheduling posts!")

def start_admin_bot():
    """Starts the bot and the scheduling task."""
    print("Starting the admin bot...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))

    loop = asyncio.get_event_loop()
    loop.create_task(send_greeting())
    loop.create_task(post_scheduled_content())

    application.run_polling()