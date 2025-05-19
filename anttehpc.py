import asyncio
import datetime
import logging
import platform
import psutil
import requests
import socket
import subprocess
import sys
import os
import cv2
import sounddevice as sd
import numpy as np
import wave
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters



from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ---------------- Configuration ----------------
BOT_TOKEN = '7582491258:AAHBR7H2G3Lv467O6HaI7FjkGEXkWcIosS0'
CHAT_ID = '8138483951'
battery_alert_sent = False

# ---------------- Logging Setup ----------------

# ---------------- Inline Menu ----------------
MAIN_MENU = InlineKeyboardMarkup([ 
    [InlineKeyboardButton("📊 Status", callback_data="status")],
    [InlineKeyboardButton("🔋 Battery", callback_data="battery"),
     InlineKeyboardButton("🧠 CPU", callback_data="cpu"),
     InlineKeyboardButton("💾 Memory", callback_data="memory")],
    [InlineKeyboardButton("🗄️ Disk", callback_data="disk"),
     InlineKeyboardButton("🌐 Network", callback_data="network")],
    [InlineKeyboardButton("🌡️ Temperature", callback_data="temperature"),
     InlineKeyboardButton("📋 Processes", callback_data="processes")],
    [InlineKeyboardButton("⏱️ Uptime", callback_data="uptime"),
     InlineKeyboardButton("🖥️ System", callback_data="system")],
    [InlineKeyboardButton("🌍 IP", callback_data="ip"),
     InlineKeyboardButton("🖧 Devices", callback_data="devices")],
    [InlineKeyboardButton("📶 Wi-Fi", callback_data="wifi"),
     InlineKeyboardButton("⚙️ Load", callback_data="load")],
    [InlineKeyboardButton("👤 Users", callback_data="users"),
     InlineKeyboardButton("🛡️ Firewall", callback_data="firewall")],
    [InlineKeyboardButton("🔍 Search File", callback_data="search"),
     InlineKeyboardButton("📁 List Dir", callback_data="listdir")],
    [InlineKeyboardButton("📸 Take Photo", callback_data="take_photo"),
     InlineKeyboardButton("🎤 Record Audio", callback_data="record_audio")]
])

# ---------------- Helper Functions ----------------

async def take_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Answer the callback query to stop the loading spinner
    await update.callback_query.answer()

    # Capture the photo from the camera
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if not ret:
        await update.callback_query.edit_message_text("📸 Failed to access the camera.", reply_markup=MAIN_MENU)
        return

    # Save the captured photo to a file
    photo_path = "photo.jpg"
    cv2.imwrite(photo_path, frame)
    cam.release()

    # Send the photo to the user
    with open(photo_path, 'rb') as photo_file:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_file)

    # Optionally, you can update the message with a new status or remove the inline keyboard
    await update.callback_query.edit_message_text("📸 Photo has been taken and sent!", reply_markup=MAIN_MENU)

async def record_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ask the user for the duration of the recording
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("⏱️ How long would you like to record the audio for? Please reply with the duration in seconds.")

    # Set the state for the bot to expect a reply with the duration
    context.user_data['recording'] = True

async def handle_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'recording' in context.user_data:
        try:
            # Parse the duration from the user's reply
            duration = int(update.message.text)
            if duration <= 0:
                raise ValueError("Duration must be greater than 0.")
            
            del context.user_data['recording']  # Clear the state

            # Proceed with recording audio
            fs = 44100  # Sample rate (standard is 44100 Hz)
            filename = "audio_recording.wav"

            await update.message.reply_text(f"🎤 Recording audio for {duration} seconds... Please wait.")

            # Record the audio
            audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='int16')
            sd.wait()  # Wait for the recording to finish

            # Save the audio to file
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(2)  # Stereo
                wf.setsampwidth(2)  # 2 bytes per sample
                wf.setframerate(fs)
                wf.writeframes(audio_data.tobytes())

            # Send the recorded audio to the user
            with open(filename, 'rb') as audio_file:
                await update.message.reply_audio(audio=audio_file)

            await update.message.reply_text(f"🎤 Audio recorded for {duration} seconds and sent!")

        except ValueError:
            await update.message.reply_text("⚠️ Invalid duration. Please reply with a positive integer in seconds.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    else:
        # If the user replies with a duration without triggering the 'Record Audio' first
        await update.message.reply_text("⚠️ Please use the 'Record Audio' button first to start the process.")

async def send_reply(update, context, text):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=MAIN_MENU)
    else:
        await update.message.reply_text(text, reply_markup=MAIN_MENU)

# ---------------- Command Functions ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 System Monitor Bot Ready!", reply_markup=MAIN_MENU)

async def battery_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    battery = psutil.sensors_battery()
    if not battery:
        return await send_reply(update, context, "🔋 Battery info not available.")
    plugged = "Charging" if battery.power_plugged else "Not Charging"
    await send_reply(update, context, f"🔋 Battery: {battery.percent}% | {plugged}")

async def cpu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usage = psutil.cpu_percent(interval=1)
    cores = psutil.cpu_count()
    await send_reply(update, context, f"🧠 CPU Usage: {usage}%\n🧠 Cores: {cores}")

async def memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mem = psutil.virtual_memory()
    await send_reply(update, context,
        f"💾 Memory: {mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB\n"
        f"💾 Usage: {mem.percent}%")

async def disk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    disk = psutil.disk_usage('/')
    await send_reply(update, context,
        f"🗄️ Disk: {disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB\n"
        f"🗄️ Usage: {disk.percent}%")

async def network_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    net = psutil.net_io_counters()
    await send_reply(update, context,
        f"🌐 Sent: {net.bytes_sent // (1024**2)}MB\n"
        f"🌐 Received: {net.bytes_recv // (1024**2)}MB")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    battery = psutil.sensors_battery()
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    await send_reply(update, context,
        f"📊 Status\n🔋 Battery: {battery.percent if battery else 'N/A'}% {'(Charging)' if battery and battery.power_plugged else ''}\n"
        f"🧠 CPU: {cpu}%\n💾 RAM: {mem.percent}%\n🗄️ Disk: {disk.percent}%")

async def temperature_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    temps = psutil.sensors_temperatures()
    if not temps:
        return await send_reply(update, context, "🌡️ Temperature info not available.")
    message = "🌡️ Temperatures:\n"
    for name, entries in temps.items():
        for entry in entries:
            if entry.current:
                message += f"{name} - {entry.label or 'Sensor'}: {entry.current}°C\n"
    await send_reply(update, context, message.strip())

async def processes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top = sorted(psutil.process_iter(['pid', 'name', 'memory_percent']), key=lambda p: p.info['memory_percent'], reverse=True)[:5]
    msg = "📋 Top 5 Processes by Memory:\n" + "\n".join(
        f"{p.info['name']} (PID {p.info['pid']}) - {p.info['memory_percent']:.2f}%"
        for p in top)
    await send_reply(update, context, msg)

async def uptime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot_time
    await send_reply(update, context,
        f"⏱️ Uptime: {str(uptime).split('.')[0]}\n🖥️ Boot: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")

async def system_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uname = platform.uname()
    await send_reply(update, context,
        f"🖥️ {uname.system} {uname.release} {uname.version}\nCPU: {uname.processor}\nNode: {uname.node}")

async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: public_ip = requests.get('https://api.ipify.org').text
    except: public_ip = "Unavailable"
    local_ip = socket.gethostbyname(socket.gethostname())
    await send_reply(update, context, f"🌍 Public IP: {public_ip}\n🏠 Local IP: {local_ip}")

async def devices_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        output = subprocess.check_output("arp -a", shell=True).decode()
        await send_reply(update, context, f"🖧 Connected Devices:\n{output}")
    except Exception as e:
        await send_reply(update, context, f"Error: {e}")

async def wifi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sys.platform.startswith("win"):
        try:
            output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode()
            await send_reply(update, context, f"📶 Wi-Fi Info:\n{output}")
        except Exception as e:
            await send_reply(update, context, f"Wi-Fi error: {e}")
    else:
        await send_reply(update, context, "Wi-Fi info is for Windows only.")

async def load_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if hasattr(os, "getloadavg"):
        load1, load5, load15 = os.getloadavg()
        await send_reply(update, context, f"📈 Load: {load1:.2f}, {load5:.2f}, {load15:.2f}")
    else:
        await send_reply(update, context, "Load info not available.")

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = psutil.users()
    if users:
        msg = "\n".join(f"{u.name} on {u.terminal}" for u in users)
        await send_reply(update, context, f"👤 Active Users:\n{msg}")
    else:
        await send_reply(update, context, "No users logged in.")

async def firewall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if sys.platform.startswith("win"):
            output = subprocess.check_output("netsh advfirewall show allprofiles", shell=True).decode()
            await send_reply(update, context, f"🛡️ Firewall Info:\n{output}")
        else:
            await send_reply(update, context, "Firewall info is available on Windows only.")
    except Exception as e:
        await send_reply(update, context, f"Error: {e}")

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = context.args
    if query:
        try:
            result = subprocess.check_output(f"find / -name {query[0]}", shell=True).decode()
            await send_reply(update, context, f"🔍 Search Results:\n{result}")
        except Exception as e:
            await send_reply(update, context, f"Error: {e}")
    else:
        await send_reply(update, context, "Please provide a file name to search.")

async def listdir_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        output = subprocess.check_output("ls", shell=True).decode()
        await send_reply(update, context, f"📁 Directory Listing:\n{output}")
    except Exception as e:
        await send_reply(update, context, f"Error: {e}")

def start_anttehpc_bot():
    print("Starting the pc watchdog bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_duration))
    app.add_handler(CallbackQueryHandler(battery_command, pattern="battery"))
    app.add_handler(CallbackQueryHandler(cpu_command, pattern="cpu"))
    app.add_handler(CallbackQueryHandler(memory_command, pattern="memory"))
    app.add_handler(CallbackQueryHandler(disk_command, pattern="disk"))
    app.add_handler(CallbackQueryHandler(network_command, pattern="network"))
    app.add_handler(CallbackQueryHandler(status_command, pattern="status"))
    app.add_handler(CallbackQueryHandler(temperature_command, pattern="temperature"))
    app.add_handler(CallbackQueryHandler(processes_command, pattern="processes"))
    app.add_handler(CallbackQueryHandler(uptime_command, pattern="uptime"))
    app.add_handler(CallbackQueryHandler(system_info_command, pattern="system"))
    app.add_handler(CallbackQueryHandler(ip_command, pattern="ip"))
    app.add_handler(CallbackQueryHandler(devices_command, pattern="devices"))
    app.add_handler(CallbackQueryHandler(wifi_command, pattern="wifi"))
    app.add_handler(CallbackQueryHandler(load_command, pattern="load"))
    app.add_handler(CallbackQueryHandler(users_command, pattern="users"))
    app.add_handler(CallbackQueryHandler(firewall_command, pattern="firewall"))
    app.add_handler(CallbackQueryHandler(search_command, pattern="search"))
    app.add_handler(CallbackQueryHandler(listdir_command, pattern="listdir"))
    app.add_handler(CallbackQueryHandler(take_photo, pattern="take_photo"))
    app.add_handler(CallbackQueryHandler(record_audio, pattern="record_audio"))

    app.run_polling()