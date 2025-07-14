#!/usr/bin/env python3
import os
from telethon.sync import TelegramClient
from dotenv import load_dotenv

# טען משתני סביבה
load_dotenv()

api_id = int(os.getenv("USER_API_ID"))
api_hash = os.getenv("USER_API_HASH")
phone = os.getenv("USER_PHONE_NUMBER")

# שם הקובץ שישמר בו ה-session
session_name = "user_m3u_session"

with TelegramClient(session_name, api_id, api_hash) as client:
    print("📞 שולח קוד התחברות לטלפון:", phone)
    client.start(phone=phone)
    print("✅ התחברות הצליחה. הקובץ user_m3u_session.session נוצר.")
