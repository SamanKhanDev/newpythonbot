from flask import Flask
from telethon import TelegramClient, events
from telethon.tl import types
import asyncio
from threading import Thread
from datetime import datetime  # 🕒 Hozirgi vaqtni olish uchun

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlavoti yangilandi 1.3 version ✅"

# Telegram API ma'lumotlari
api_id = 1150656  # To'g'ri API ID kiriting
api_hash = "fb33d7c76f5bdaab44d5145537de31c0"  # To'g'ri API hash kiriting
bot_token = "8108266498:AAHTewUwY8lXDlfklgvnzDC_4raqp2csdHc"  # Telegram bot tokeni

# Sessiyani saqlash uchun fayl nomlari
USER_SESSION = "user_session"
BOT_SESSION = "bot_session"

# Telegram client yaratish
user_client = TelegramClient(USER_SESSION, api_id, api_hash)  
bot = TelegramClient(BOT_SESSION, api_id, api_hash)  

last_code = "Hali kod olinmadi."
subscribers = {}

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if event.sender_id not in subscribers:
        subscribers[event.sender_id] = {'valid': False, 'blocked': False}
    await event.respond("Salom! Kodni kiriting......")

@bot.on(events.NewMessage(pattern='/block'))
async def block(event):
    if event.sender_id in subscribers:
        subscribers[event.sender_id]['blocked'] = True
        await event.respond("Siz bloklandiz! 🚫")
    else:
        await event.respond("Avval /start buyrug‘ini yuboring.")

@bot.on(events.NewMessage(pattern='/bumen'))
async def unblock(event):
    if event.sender_id in subscribers:
        subscribers[event.sender_id]['blocked'] = False
        await event.respond("Siz endi blokdan chiqdingiz! ✅")
    else:
        await event.respond("Avval /start buyrug‘ini yuboring.")

@bot.on(events.NewMessage)
async def receive_code(event):
    if event.sender_id in subscribers:
        now = datetime.now().strftime("%H%M")  # 🕒 Hozirgi vaqtni HHMM formatida olish
        if event.text == now:  # Foydalanuvchi ayni vaqtni kiritsa
            subscribers[event.sender_id]['valid'] = True
            await event.respond("Kod to‘g‘ri! ✅ Endi 777000'dan kelgan yangi kodni kuting...")
            await event.delete()  # Xabarni o‘chirish

        if subscribers[event.sender_id]['valid'] and not subscribers[event.sender_id]['blocked']:
            await event.respond(f"Yangi Telegram kodi: {last_code}")
        elif subscribers[event.sender_id]['blocked']:
            await event.respond("Siz bloklandiz va kod yuborilmaydi. 🚫")


@user_client.on(events.NewMessage(from_users=777000))
async def new_code_handler(event):
    global last_code
    last_code = event.text
    for user_id, status in subscribers.items():
        if status['valid'] and not status['blocked']:
            await bot.send_message(user_id, f"Yangi Telegram kodi: {last_code}")

async def main():
    await user_client.start()
    await bot.start(bot_token=bot_token)
    print("✅ Bot va user_client ishga tushdi...")

    try:
        await asyncio.gather(
            user_client.run_until_disconnected(),
            bot.run_until_disconnected()
        )
    except asyncio.CancelledError:
        print("❌ Bot o‘chirildi.")

def run_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    # Flask serverni alohida thread-da ishga tushiramiz
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("❌ Bot to‘xtatildi.")
