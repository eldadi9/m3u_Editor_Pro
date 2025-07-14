from telethon.sync import TelegramClient
import os
from dotenv import load_dotenv

# טען משתני סביבה מה-.env
load_dotenv()

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
phone = os.getenv("TELEGRAM_USER_PHONE")

with TelegramClient("m3u_user_agent_session", api_id, api_hash) as client:
    client.start(phone=phone)
    print("✅ Session created and saved successfully")
