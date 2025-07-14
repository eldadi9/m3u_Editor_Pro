import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = "-1002464592389"  # או שם של קבוצה ציבורית

def test_send():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": "🔁 בדיקת שליחה",
    }
    r = requests.post(url, data=payload)
    print(r.status_code, r.text)

test_send()
