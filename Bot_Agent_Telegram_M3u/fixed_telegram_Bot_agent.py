
import sys
import os
import asyncio
import requests
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient, events, errors
from PyQt5.QtWidgets import QApplication
import logging
from telethon.tl.custom import Button

# לוג
logging.basicConfig(
    filename="agent.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# עורך M3U
sys.path.append("C:/Users/Master_PC/Desktop/IPtv_projects/Projects Eldad/M3u_Editor_EldadV1/M3U_EDITOR")
from m3u_EditorV3 import M3UEditor

# סביבה
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=ENV_PATH, override=True)
api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
bot_token = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")

listen_chats = [-1002464592389]
client = None

async def notify_admin(text):
    try:
        await client.send_message(7773889743, text)
    except Exception as e:
        print(f"⚠️ notify_admin error: {e}")

def log_to_db(file_name, message_text, sender, chat):
    conn = sqlite3.connect("group_downloads.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO group_downloads (
            file_name, message_text, downloader_id, username, first_name, last_name,
            chat_id, chat_title, download_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        file_name,
        message_text,
        sender.id,
        sender.username or "N/A",
        sender.first_name or "N/A",
        sender.last_name or "N/A",
        chat.id,
        getattr(chat, "title", "N/A"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()
    print("📝 נרשמה פעולה למסד group_downloads.db")

def create_group_db():
    conn = sqlite3.connect("group_downloads.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS group_downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            message_text TEXT,
            downloader_id INTEGER,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            chat_id INTEGER,
            chat_title TEXT,
            download_time TEXT
        )
    ''')
    conn.commit()
    conn.close()

async def run_agent(editor: M3UEditor):
    global client
    client = TelegramClient('m3u_agent_session', api_id, api_hash)
    await client.start(bot_token=bot_token)
    await notify_admin("✅ הסוכן הופעל ומאזין לקבוצות M3U")

    @client.on(events.NewMessage(pattern='/start'))
    async def send_menu(event):
        await event.respond(
            "בחר פעולה:",
            buttons=[
                [Button.inline("📄 הצג מידע", b"show_info")],
                [Button.inline("📤 שלח קובץ", b"send_file")]
            ]
        )

    @client.on(events.NewMessage(chats=listen_chats))
    async def handle_messages(event):
        sender = await event.get_sender()
        chat = await event.get_chat()
        text = (event.message.message or "").strip()
        full_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()

        print(f"📥 הודעה מ-{full_name} (@{sender.username or 'N/A'}) ID={sender.id}")
        print(f"🔹 טקסט: {text}")

        m3u_text = None
        file_name = None

        if event.file:
            path = await event.download_media()
            file_name = os.path.basename(path)
            print(f"🔽 הורד קובץ: {file_name}")
            if path.lower().endswith((".m3u", ".m3u8")):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        m3u_text = f.read()
                    await notify_admin("📥 קובץ פלייליסט נטען")
                except Exception as e:
                    print(f"❌ שגיאה בקריאת קובץ: {e}")

        elif any(token.lower().endswith((".m3u", ".m3u8")) for token in text.split()):
            for token in text.split():
                if token.lower().endswith((".m3u", ".m3u8")):
                    try:
                        resp = requests.get(token, timeout=10)
                        if resp.status_code < 400 and resp.text.strip().startswith("#EXTM3U"):
                            m3u_text = resp.text
                            file_name = token
                            print("📥 פלייליסט הובא מהאינטרנט")
                            break
                    except Exception as e:
                        print(f"⚠️ שגיאה ב־HTTP: {e}")

        if m3u_text:
            editor.loadM3UFromText(m3u_text)
            try:
                editor.regenerateM3UTextOnly()
            except: pass

            out_file = f"cleaned_{datetime.now():%Y%m%d_%H%M%S}.m3u"
            editor.exportM3UWithLogos(out_file)
            await client.send_file(event.chat_id, out_file, caption="✅ הנה הקובץ המעובד")
            file_name = out_file

        log_to_db(
            file_name=file_name,
            message_text=text,
            sender=sender,
            chat=chat
        )

    @client.on(events.CallbackQuery)
    async def handle_button_click(event):
        try:
            sender = await event.get_sender()
            chat = await event.get_chat()
            data = event.data.decode("utf-8") if event.data else "אין מידע"
            full_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()

            print(f"🟦 לחיצה על כפתור: {full_name} (@{sender.username or 'N/A'}) ID={sender.id}")
            print(f"🔹 תוכן: {data}")

            conn = sqlite3.connect("group_downloads.db")
            c = conn.cursor()
            c.execute('''
                INSERT INTO group_downloads (
                    file_name, message_text, downloader_id, username, first_name, last_name,
                    chat_id, chat_title, download_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                None,
                f"[Callback] {data}",
                sender.id,
                sender.username or "N/A",
                sender.first_name or "N/A",
                sender.last_name or "N/A",
                chat.id,
                getattr(chat, 'title', 'N/A'),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            conn.close()

            await event.answer("✅ הפעולה נרשמה")

        except Exception as e:
            print(f"❌ שגיאה בלחיצת כפתור: {e}")

    await client.run_until_disconnected()

def main():
    create_group_db()
    app = QApplication(sys.argv)
    editor = M3UEditor()
    editor.hide()
    asyncio.run(run_agent(editor))

if __name__ == "__main__":
    main()
