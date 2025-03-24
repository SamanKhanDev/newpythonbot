from flask import Flask
from telethon import TelegramClient, events
from telethon.tl import types
import asyncio
from threading import Thread
from datetime import datetime  # 🕒 Hozirgi vaqtni olish uchun




app = Flask(__name__)

from flask import Flask

app = Flask(__name__)

from flask import Flask

app = Flask(__name__)

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <style>
            body {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background-color: #1a202c;
                color: white;
                font-family: Arial, sans-serif;
                font-size: 24px;
                font-weight: bold;
                text-align: center;
                flex-direction: column;
            }
            .container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .typing {
                display: inline-block;
                border-right: 3px solid white;
                white-space: nowrap;
                overflow: hidden;
                width: 0;
                animation: typing 3s steps(30, end) forwards, disappear 6s infinite;
            }
            .typing2 {
                display: inline-block;
                border-right: 3px solid white;
                white-space: nowrap;
                overflow: hidden;
                width: 0;
                margin-top: 20px;
                animation: typing2 3s steps(30, end) forwards 6s, disappear 12s infinite;
            }
            .lock-message {
                margin-top: 30px;
                font-size: 18px;
                display: flex;
                align-items: center;
                gap: 10px;
                opacity: 0;
                animation: fadeIn 3s forwards 12s;
            }
            @keyframes typing {
                from { width: 0; }
                to { width: 100%; }
            }
            @keyframes typing2 {
                from { width: 0; }
                to { width: 100%; }
            }
            @keyframes disappear {
                0% { opacity: 1; }
                80% { opacity: 1; }
                100% { opacity: 0; }
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="typing">Bot ishlavoti yangilandi <span style="color: #48bb78;">1.8 version ✅</span></div>
            <div class="typing2">Men senga yordam beraman, Telegramingni ochish uchun ...</div>
            <div class="lock-message">
                <span style="font-size: 24px;">🔒</span>
                <span>Bemalol ishlatishing mumkin!</span>
            </div>
        </div>
    </body>
    </html>
    '''
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
    
    await event.respond("Salom! Kodni kiriting...... " )

@bot.on(events.NewMessage(pattern='/block'))
async def block(event):
    if event.sender_id in subscribers:
        subscribers[event.sender_id]['blocked'] = True
        await event.respond("Siz bloklandiz! 🚫")
    else:
        await event.respond("Avval /start buyrug‘ini yuboring.")

@bot.on(events.NewMessage(pattern='/bumenda'))
async def unblock(event):
    if event.sender_id in subscribers:
        subscribers[event.sender_id]['blocked'] = False
        subscribers[event.sender_id]['valid'] = False  # ❗ Blokdan chiqqanda valid holatini o‘chiramiz
        await event.respond("✅ Siz endi blokdan chiqdingiz! Yana kod olish uchun PIN kiriting.")
    else:
        await event.respond("Avval /start buyrug‘ini yuboring.")

@bot.on(events.NewMessage)

@bot.on(events.NewMessage)
async def receive_code(event):
    if event.sender_id in subscribers:
        now = datetime.now().strftime("%H%M")  # 🕒 Hozirgi vaqtni HHMM formatida olish
        
        if event.text == now:  # PIN kod to‘g‘ri bo‘lsa
            subscribers[event.sender_id]['valid'] = True
            subscribers[event.sender_id]['sent_code'] = False  # ❗ SMS jo‘natilgan flagini o‘chirib qo‘yamiz
            await event.respond("✅ PIN to‘g‘ri! Endi Telegram'dan kelgan yangi kodni kuting...")
            await event.delete()  # PIN kod xabarini o‘chirish

        elif subscribers[event.sender_id]['valid'] and not subscribers[event.sender_id]['blocked']:
            await event.respond("📩 Kod hali kelmadi. Iltimos, kuting...")

        elif subscribers[event.sender_id]['blocked']:
            await event.respond("🚫 Siz bloklangansiz va kod yuborilmaydi.")
        else:
            await event.respond("❌ Avval PIN kodni to‘g‘ri kiriting.")

@user_client.on(events.NewMessage(from_users=777000))
async def new_code_handler(event):
    global last_code
    import re

    # 777000'dan kelgan xabardan faqat kodni olish (masalan: "12345 is your Telegram code")
    match = re.search(r'\b\d{5,6}\b', event.text)
    if match:
        last_code = match.group(0)
    else:
        return  # Agar kod topilmasa, hech narsa qilmaymiz

    for user_id, status in subscribers.items():
        if status['valid'] and not status['blocked'] and not status.get('sent_code', False):  
            await bot.send_message(user_id, f"🔑 Yangi Telegram kodi: {last_code}")
            
            # ✅ Kod jo‘natildi, endi yana yuborilmasligi uchun flag qo‘yamiz
            subscribers[user_id]['sent_code'] = True  


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
