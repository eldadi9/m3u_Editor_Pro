#!/usr/bin/env python3
import sys
import os
import asyncio
from datetime import datetime
from telethon import TelegramClient, events
from PyQt5.QtWidgets import QApplication
from m3u_EditorV3 import M3UEditor
import requests
from dotenv import load_dotenv

# === 1. טעינת משתני סביבה ===
# צרו קובץ .env באותה תיקיה עם השורות הבאות:
# TELEGRAM_API_ID=26204498
# TELEGRAM_API_HASH=effcbe85799f64ab3f83cb020e036123
# BOT_TOKEN=123456789:ABCdefGhIjKlmnOPqrsTUVwxyZ
load_dotenv()
api_id    = int(os.getenv('TELEGRAM_API_ID'))
api_hash  = os.getenv('TELEGRAM_API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# === 2. הגדרות טלגרם ===
# החליפו בשמו או ב-ID של הקבוצה שלכם
listen_chats = ['@Olam_Haoradot_IL']

async def run_agent(editor: M3UEditor):
    # אתחול TelegramClient כבוט headless
    client = TelegramClient('m3u_agent_session', api_id, api_hash)
    await client.start(bot_token=bot_token)
    print('Agent started – listening for M3U in Telegram…')

    @client.on(events.NewMessage(chats=listen_chats))
    async def handler(event):
        m3u_text = None

        # 1. הורדת קובץ .m3u אם מצורף
        if event.file and event.file.name.lower().endswith('.m3u'):
            path = await event.download_media()
            with open(path, 'r', encoding='utf-8') as f:
                m3u_text = f.read()

        # 2. או הורדת קישור .m3u מההודעה
        else:
            text = event.message.message or ''
            url = next((w for w in text.split() if w.lower().endswith('.m3u')), None)
            if url:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200 and resp.text.startswith('#EXTM3U'):
                    m3u_text = resp.text

        # אם לא מצאנו תוכן – בורחים
        if not m3u_text:
            return

        # 3. טעינת התוכן למערכת שלך
        editor.loadM3UFromText(m3u_text)

        # 4. הרצת תהליכים אוטומטיים
        editor._translateAll()     # תרגום כל הערוצים לאנגלית
        editor.checkDoubles()      # בדיקת כפילויות
        editor.runSmartScan()      # סריקה חכמה

        # 5. ייצוא קובץ חדש
        timestamp   = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'cleaned_playlist_{timestamp}.m3u'
        editor.exportM3UWithLogos(output_file)

        # 6. שליחה חזרה לטלגרם
        await event.reply('✅ הנה הקובץ המעובד:', file=output_file)

    # המתנה עד ש־TelegramClient יתנתק
    await client.run_until_disconnected()

def main():
    # 0. הכנה של סביבת PyQt (למניעת קריסה כשמשתמשים ב-QWidget)
    app = QApplication(sys.argv)

    # יצירת ה-Editor שלך והסתרתו
    editor = M3UEditor()
    editor.hide()

    # הפעלת הסוכן
    asyncio.run(run_agent(editor))

if __name__ == '__main__':
    main()
