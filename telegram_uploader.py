import requests
import os  # חובה אם אתה משתמש ב-os.path

# === Telegram Upload Config ===
BOT_TOKEN = "7757317671:AAHlq8yWLzP4mrgEovVoVZb_2j9ilWt0OlQ"
CHAT_ID = "-1002464592389"
TOPIC_ID = 6

def send_to_telegram(file_path, token=BOT_TOKEN, chat_id=CHAT_ID, topic_id=TOPIC_ID, filename=None):
    """
    שולח קובץ לטלגרם לקבוצה וטופיק ספציפיים.
    """
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    try:
        with open(file_path, "rb") as f:
            files = {"document": (filename or os.path.basename(file_path), f)}
            data = {
                "chat_id": chat_id,
                "caption": "📺 עדכון פלייליסט חדש 🎉",
            }
            if topic_id:
                data["message_thread_id"] = topic_id

            response = requests.post(url, data=data, files=files)

        if response.status_code == 200:
            print("✅ הקובץ נשלח לטלגרם בהצלחה.")
            return True
        else:
            print(f"❌ שגיאה בהעלאה: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"⚠️ שגיאה כללית בשליחה לטלגרם: {e}")
        return False
