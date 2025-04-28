import os
import requests
import random
from dotenv import load_dotenv

# טוען משתני סביבה
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = "-1002464592389"
TOPIC_ID = 6

# חתימות EG מתחלפות
signatures = [
    "◢◤ 𝗘𝗚 ◥◣\n⚡️ 𝘾𝙊𝘿𝙀. 𝘾𝙍𝙀𝘼𝙏𝙀. 𝘿𝙊 𝙈𝘼𝙂𝙄𝘾 ⚡️\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n📡 STREAM • SYNC • SHARE\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n📺 IPTV IS POWERED HERE\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n📲 APPS • LINKS • UPDATES\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n🛰️ SIGNALS FROM THE UNDERGROUND\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n🎛️ STREAM. CODE. UPGRADE.\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n🧠 SMART CONTENT FOR SMART PEOPLE\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n📦 UNPACKING THE INTERNET\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n🔥 BEST LINKS. NO NOISE.\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n🔁 DAILY STREAM. ZERO DELAY.\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n📥 DOWNLOADING A BETTER WORLD\n╰┈➤ https://t.me/Olam_Haoradot_IL"
    "◢◤ 𝗘𝗚 ◥◣\n🚀 Always Moving Forward\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n🌍 Your World of Streaming\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n🎯 Precision. Speed. Content.\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n💎 Where Quality Matters\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n📀 Streams, Apps, Upgrades\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n🧩 Puzzle Completed: Perfect Playlist\n╰┈➤ https://t.me/Olam_Haoradot_IL"
    "◢◤ EG | Digital Excellence ◥◣\nwww.OlamHaoradot.com",
    "◢◤ EG | Precision in Every Byte ◥◣\nwww.OlamHaoradot.com",
    "◢◤ EG | Innovation. Speed. Trust. ◥◣\nwww.OlamHaoradot.com",
    "◢◤ EG | Crafted for Professionals ◥◣\nwww.OlamHaoradot.com",
    "◢◤ EG | Beyond Boundaries ◥◣\nwww.OlamHaoradot.com",
    "◢◤ EG | Curated Digital Solutions ◥◣\nwww.OlamHaoradot.com",
    "◢◤ EG | Streamlined. Elevated. Unlocked. ◥◣\nwww.OlamHaoradot.com",
    "◢◤ EG | Redefining Streaming Standards ◥◣\nwww.OlamHaoradot.com",
    "◢◤ EG | Powering Your Content Journey ◥◣\nwww.OlamHaoradot.com",
    "◢◤ EG | Intelligence in Every Stream ◥◣\nwww.OlamHaoradot.com"
    "◢◤ 𝗘𝗚 ◥◣\n🚀 BOOST YOUR PLAYLISTS\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n🔍 FIND. STREAM. ENJOY.\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n🧠 SMART STREAMING SOLUTIONS\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n🛠 BUILD YOUR IPTV WORLD\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n🎯 TARGET • STREAM • CONQUER\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n🛰 SATELLITE OF STREAMS\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n📈 UPGRADE. EVOLVE. STREAM.\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n🎧 PLAY. CONNECT. EXPERIENCE.\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n🧩 PIECE BY PIECE - COMPLETE STREAMS\n╰┈➤ https://t.me/Olam_Haoradot_IL",
    "◢◤ 𝗘𝗚 ◥◣\n🔰 TRUSTED STREAMING HUB\n╰┈➤ https://t.me/Olam_Haoradot_IL",

        

]


# משפטים לפלייליסט
playlist_phrases = [
    "פלייליסט חדש באוויר",
    "עלה פלייליסט חדש",
    "הגיע עדכון חדש",
    "עלינו עם פלייליסט",
    "הורידו את החדש",
    "חדש בעולם ההורדות",
    "העדכון חם מהתנור",
    "תפסו את הפלייליסט",
    "הפלייליסט כבר פה",
    "הפלייליסט בדרך אליכם"
]

def get_random_caption():
    signature = random.choice(signatures)
    phrase = random.choice(playlist_phrases)
    return f"{signature}\n\n📺 {phrase} 🎉"

def send_to_telegram(file_path, token=BOT_TOKEN, chat_id=CHAT_ID, topic_id=TOPIC_ID, filename=None, caption=None, image_path=None):
    """
    שולח קובץ לטלגרם עם חתימה רנדומלית וטקסט מתחלף.
    :param file_path: נתיב לקובץ לשליחה
    :param caption: ניתן להזין טקסט קבוע (לא חובה)
    """
    try:
        url = f"https://api.telegram.org/bot{token}/sendDocument"
        with open(file_path, "rb") as f:
            files = {"document": (filename or os.path.basename(file_path), f)}
            data = {
                "chat_id": chat_id,
                "caption": caption or get_random_caption(),
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
