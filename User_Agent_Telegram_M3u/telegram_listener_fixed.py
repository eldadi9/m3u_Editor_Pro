#!/usr/bin/env python3
"""
🎯 בוט טלגרם מאזין מתוקן - מבוסס על user_AgentV3.py
מתוקן לעבודה עם מבנה התיקיות החדש
"""

import sys, os, json, asyncio, requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telethon import TelegramClient, errors
from PyQt5.QtWidgets import QApplication
import re
import shutil
import chardet
import sqlite3
import hashlib
from collections import defaultdict, Counter
import time

# הוספת נתיב לתיקיית M3U_EDITOR
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
M3U_EDITOR_PATH = os.path.join(os.path.dirname(PROJECT_ROOT), "M3U_EDITOR")
sys.path.append(M3U_EDITOR_PATH)

try:
    from logo import inject_logo_to_line
    from m3u_EditorV3 import M3UEditor

    print("✅ M3U Editor modules loaded successfully")
except ImportError as e:
    print(f"⚠️ Warning: M3U Editor not found: {e}")


    # Create dummy classes to prevent crashes
    class DummyEditor:
        def hide(self): pass

        def loadM3UFromText(self, text): pass

        def regenerateM3UTextOnly(self): pass

        def exportM3UWithLogos(self, path):
            with open(path, 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n# Processed by Listener Bot\n")


    M3UEditor = DummyEditor
    inject_logo_to_line = lambda line, name: line

# הגדרות Qt
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
_qt_app = QApplication(sys.argv)

# טעינת משתני סביבה מהתיקייה הראשית
ENV_PATH = os.path.join(os.path.dirname(PROJECT_ROOT), '.env')
load_dotenv(ENV_PATH, override=True)

# קריאת הגדרות
api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
session_name = os.getenv("SESSION_NAME", "m3u_listener_session")
phone = os.getenv("TELEGRAM_PHONE")
password_2fa = os.getenv("TELEGRAM_2FA_PASSWORD")

# הגדרת תיקיות - יחסיות לתיקייה הראשית
BASE_DIR = os.path.dirname(PROJECT_ROOT)
download_dir = os.path.join(BASE_DIR, "DOWNLOADS", "telegram_downloads")
processed_dir = os.path.join(BASE_DIR, "DOWNLOADS", "processed_files")
portal_dir = os.path.join(BASE_DIR, "DOWNLOADS", "portal_converts")

# יצירת תיקיות
for dir_path in [download_dir, processed_dir, portal_dir]:
    os.makedirs(dir_path, exist_ok=True)

# קריאת רשימת קבוצות
groups_config_path = os.path.join(BASE_DIR, os.getenv("GROUPS_CONFIG", "groups_config.json"))
try:
    with open(groups_config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    group_links = cfg.get("groups", [])
    group_usernames = [link.rstrip('/').split('/')[-1] for link in group_links]
    print(f"📋 Loaded {len(group_usernames)} groups to monitor")
except Exception as e:
    print(f"❌ Error loading groups config: {e}")
    sys.exit(1)

# בדיקת הגדרות חיוניות
if not all((api_id, api_hash, phone, password_2fa)):
    print("❌ Missing required settings in .env file", file=sys.stderr)
    sys.exit(1)


# מחלקת סטטיסטיקות מתקדמת
class EnhancedStatistics:
    def __init__(self):
        self.start_time = datetime.now()
        self.stats = {
            'total_messages': 0,
            'files_found': 0,
            'files_downloaded': 0,
            'files_processed': 0,
            'portals_found': 0,
            'portals_converted': 0,
            'channels_total': 0,
            'groups_processed': 0,
            'errors': 0,
            'duplicates_skipped': 0
        }
        self.hash_set = set()
        self.download_history = []

    def log_download(self, filename, source, channels_count=0):
        """רישום הורדה"""
        self.stats['files_downloaded'] += 1
        self.stats['channels_total'] += channels_count
        self.download_history.append({
            'filename': filename,
            'source': source,
            'channels': channels_count,
            'time': datetime.now()
        })

    def is_duplicate(self, content):
        """בדיקת כפילות"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if content_hash in self.hash_set:
            self.stats['duplicates_skipped'] += 1
            return True
        self.hash_set.add(content_hash)
        return False

    def get_summary(self):
        """סיכום סטטיסטיקות"""
        runtime = datetime.now() - self.start_time
        return f"""
🎯 ==================== LISTENER BOT SUMMARY ====================
⏱️  Runtime: {runtime.total_seconds():.0f} seconds
📊 Messages scanned: {self.stats['total_messages']}
📁 Files found: {self.stats['files_found']}
⬇️  Files downloaded: {self.stats['files_downloaded']}
⚙️  Files processed: {self.stats['files_processed']}
🌐 Portals found: {self.stats['portals_found']}
🔄 Portals converted: {self.stats['portals_converted']}
📺 Total channels: {self.stats['channels_total']}
🏢 Groups processed: {self.stats['groups_processed']}
🔄 Duplicates skipped: {self.stats['duplicates_skipped']}
❌ Errors: {self.stats['errors']}
===============================================================
"""


# Logger משופר
class Logger:
    @staticmethod
    def info(msg):
        print(f"ℹ️  {datetime.now().strftime('%H:%M:%S')} | {msg}")

    @staticmethod
    def success(msg):
        print(f"✅ {datetime.now().strftime('%H:%M:%S')} | {msg}")

    @staticmethod
    def warning(msg):
        print(f"⚠️  {datetime.now().strftime('%H:%M:%S')} | {msg}")

    @staticmethod
    def error(msg):
        print(f"❌ {datetime.now().strftime('%H:%M:%S')} | {msg}")

    @staticmethod
    def debug(msg):
        if os.getenv("DEBUG", "false").lower() == "true":
            print(f"🔍 {datetime.now().strftime('%H:%M:%S')} | {msg}")


logger = Logger()


# פונקציות עזר
def read_file_with_encoding(filepath):
    """קריאת קובץ עם זיהוי קידוד"""
    try:
        with open(filepath, 'rb') as f:
            raw = f.read()
        detected = chardet.detect(raw)
        encoding = detected.get('encoding', 'utf-8')
        return raw.decode(encoding, errors='replace')
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return None


def download_m3u_from_url(url, save_dir):
    """הורדת M3U מ-URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # בדיקה שזה באמת M3U
        content = response.text
        if "#EXTM3U" not in content[:100]:
            logger.warning(f"Not a valid M3U file: {url[:50]}...")
            return None

        # יצירת שם קובץ
        filename = os.path.basename(url.split('?')[0])
        if not filename or '.' not in filename:
            filename = f"playlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.m3u"

        filepath = os.path.join(save_dir, filename)

        # שמירה
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.success(f"Downloaded: {filename}")
        return filepath

    except Exception as e:
        logger.error(f"Download failed for {url}: {e}")
        return None


def count_channels_in_m3u(content):
    """ספירת ערוצים בקובץ M3U"""
    return content.count('#EXTINF:')


def clean_and_process_m3u(filepath, output_dir, stats):
    """ניקוי ועיבוד קובץ M3U"""
    try:
        content = read_file_with_encoding(filepath)
        if not content:
            return None

        # בדיקת כפילות
        if stats.is_duplicate(content):
            logger.warning(f"Duplicate file skipped: {os.path.basename(filepath)}")
            return None

        # ספירת ערוצים
        channels_count = count_channels_in_m3u(content)

        # יצירת שם קובץ חדש
        basename = os.path.splitext(os.path.basename(filepath))[0]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{basename}_PROCESSED_{timestamp}.m3u"
        output_path = os.path.join(output_dir, new_filename)

        # עיבוד עם M3U Editor
        try:
            editor = M3UEditor()
            editor.hide()

            # הוספת לוגואים
            lines = content.splitlines()
            processed_lines = []

            for line in lines:
                if line.startswith("#EXTINF:"):
                    try:
                        match = re.search(r",(.+)", line)
                        name = match.group(1).strip() if match else ""
                        line = inject_logo_to_line(line, name)
                    except:
                        pass
                processed_lines.append(line)

            processed_content = "\n".join(processed_lines)

            editor.loadM3UFromText(processed_content)
            editor.regenerateM3UTextOnly()
            editor.exportM3UWithLogos(output_path)

            stats.stats['files_processed'] += 1
            logger.success(f"Processed: {new_filename} ({channels_count} channels)")

            return output_path, channels_count

        except Exception as e:
            logger.warning(f"M3U Editor processing failed: {e}")
            # שמירה פשוטה כ-fallback
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            stats.stats['files_processed'] += 1
            return output_path, channels_count

    except Exception as e:
        logger.error(f"Processing failed for {filepath}: {e}")
        stats.stats['errors'] += 1
        return None


def send_summary_to_bot(stats, files_processed):
    """שליחת סיכום לבוט טלגרם (אופציונלי)"""
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("MAIN_GROUP_ID")

    if not bot_token or not chat_id:
        logger.warning("Bot token or chat ID not configured")
        return

    try:
        message = f"""
🤖 **Telegram Listener Bot Report**

📊 **Summary:**
• Files downloaded: {stats.stats['files_downloaded']}
• Files processed: {stats.stats['files_processed']}
• Total channels: {stats.stats['channels_total']}
• Groups scanned: {stats.stats['groups_processed']}

⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

        response = requests.post(url, json=payload, timeout=10)
        if response.ok:
            logger.success("Summary sent to bot")
        else:
            logger.warning(f"Failed to send summary: {response.status_code}")

    except Exception as e:
        logger.error(f"Bot notification failed: {e}")


# פונקציה ראשית
async def main():
    """פונקציה ראשית של הבוט המאזין"""

    # הדפסת כותרת
    print("=" * 80)
    print("        🎧 TELEGRAM LISTENER BOT - ENHANCED VERSION")
    print("                    🔥 Ready to Monitor! 🔥")
    print("=" * 80)
    print()

    stats = EnhancedStatistics()
    session_path = os.path.join(BASE_DIR, session_name)

    # יצירת לקוח טלגרם
    client = TelegramClient(session_path, api_id, api_hash)

    try:
        logger.info("Connecting to Telegram...")
        await client.connect()
        logger.success("Connected successfully!")

        # אימות משתמש
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            code = input("📱 Enter the code you received: ").strip()
            try:
                await client.sign_in(phone, code)
            except errors.SessionPasswordNeededError:
                await client.sign_in(password=password_2fa)
            logger.success("Authentication successful!")

        # טעינת קבוצות
        entities = []
        logger.info(f"Loading {len(group_usernames)} groups...")

        for i, username in enumerate(group_usernames, 1):
            try:
                entity = await client.get_entity(username)
                entities.append(entity)
                logger.success(f"[{i}/{len(group_usernames)}] Loaded: {username}")
            except Exception as e:
                logger.error(f"[{i}/{len(group_usernames)}] Failed to load {username}: {e}")

        if not entities:
            logger.error("No groups loaded successfully!")
            return

        # הגדרת זמן חיפוש
        since_time = datetime.now().astimezone() - timedelta(hours=24)  # חיפוש מהיום האחרון
        logger.info(f"Scanning messages since: {since_time.strftime('%Y-%m-%d %H:%M')}")

        print("\n" + "=" * 80)
        print("                     🔍 STARTING SCAN...")
        print("=" * 80)

        # סריקת קבוצות
        for group_idx, entity in enumerate(entities, 1):
            group_name = entity.username or str(entity.id)
            stats.stats['groups_processed'] += 1

            logger.info(f"\n📡 [{group_idx}/{len(entities)}] Scanning group: {group_name}")

            # יצירת תיקייה לקבוצה
            group_dir = os.path.join(download_dir, group_name)
            os.makedirs(group_dir, exist_ok=True)

            messages_scanned = 0
            files_found_in_group = 0

            try:
                async for message in client.iter_messages(entity, limit=100):
                    messages_scanned += 1
                    stats.stats['total_messages'] += 1

                    # בדיקת תאריך
                    if message.date < since_time:
                        continue

                    # דילוג על הודעות ריקות
                    if not message.message and not message.file:
                        continue

                    # יצירת תיקיית יום
                    day_folder = message.date.strftime("%Y-%m-%d")
                    day_dir = os.path.join(group_dir, day_folder)
                    os.makedirs(day_dir, exist_ok=True)

                    downloaded_file = None

                    # טיפול בקבצים מצורפים
                    if message.file and message.file.name:
                        filename = message.file.name.lower()
                        if filename.endswith(('.m3u', '.m3u8')):
                            stats.stats['files_found'] += 1
                            files_found_in_group += 1

                            # הורדת קובץ
                            file_path = os.path.join(day_dir, message.file.name)
                            if not os.path.exists(file_path):
                                downloaded_file = await message.download_media(day_dir)
                                if downloaded_file:
                                    logger.success(f"📥 Downloaded: {message.file.name}")
                                    stats.log_download(message.file.name, group_name)

                    # חיפוש URLs בטקסט
                    elif message.message:
                        text = message.message
                        urls = re.findall(r'https?://[^\s]+', text)

                        for url in urls:
                            if any(ext in url.lower() for ext in ['.m3u', '.m3u8', 'get.php']):
                                stats.stats['files_found'] += 1
                                files_found_in_group += 1

                                logger.info(f"🔗 Found URL: {url[:50]}...")
                                downloaded_file = download_m3u_from_url(url, day_dir)
                                if downloaded_file:
                                    stats.log_download(os.path.basename(downloaded_file), group_name)
                                break

                    # עיבוד הקובץ שהורד
                    if downloaded_file:
                        result = clean_and_process_m3u(downloaded_file, processed_dir, stats)
                        if result:
                            processed_file, channels_count = result
                            logger.success(f"✨ Created: {os.path.basename(processed_file)} ({channels_count} channels)")
                            stats.stats['channels_total'] += channels_count

            except Exception as e:
                logger.error(f"Error scanning group {group_name}: {e}")
                stats.stats['errors'] += 1

            # סיכום קבוצה
            logger.info(f"📊 Group {group_name} summary:")
            logger.info(f"   • Messages scanned: {messages_scanned}")
            logger.info(f"   • Files found: {files_found_in_group}")

        await client.disconnect()
        logger.success("Disconnected from Telegram")

        # הדפסת סיכום כולל
        print("\n" + "=" * 80)
        print(stats.get_summary())
        print("=" * 80)

        # שליחת דוח לבוט (אופציונלי)
        if stats.stats['files_downloaded'] > 0:
            send_summary_to_bot(stats, stats.stats['files_processed'])

        logger.success("🎉 Scan completed successfully!")

        # פתיחת תיקיית קבצים מעובדים
        if stats.stats['files_processed'] > 0:
            try:
                os.startfile(processed_dir)
                logger.info(f"📂 Opened processed files folder: {processed_dir}")
            except:
                logger.info(f"📂 Processed files saved to: {processed_dir}")

    except Exception as e:
        logger.error(f"Critical error: {e}")
        stats.stats['errors'] += 1

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        input("Press Enter to exit...")