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

sys.path.append("C:/Users/Master_PC/Desktop/IPtv_projects/Projects Eldad/M3u_Editor_EldadV1/M3U_EDITOR")

from logo import inject_logo_to_line
from m3u_EditorV3 import M3UEditor

SKIP_COPY = os.getenv("SKIP_COPY", "false").lower() == "true"

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
_qt_app = QApplication(sys.argv)

# ✅ טען משתני סביבה
HERE = os.path.dirname(__file__)
load_dotenv(os.path.join(HERE, '.env'), override=True)

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
session_name = os.getenv("SESSION_NAME", "m3u_user_agent_session")
download_dir = os.path.abspath(os.getenv("DOWNLOAD_FOLDER"))
groups_config = os.getenv("GROUPS_CONFIG")
phone = os.getenv("TELEGRAM_PHONE")
password_2fa = os.getenv("TELEGRAM_2FA_PASSWORD")

# ✅ בדיקה בסיסית
if not all((api_id, api_hash, download_dir, groups_config, phone, password_2fa)):
    print("❌ חסרים משתנים ב־.env", file=sys.stderr)
    sys.exit(1)

os.makedirs(download_dir, exist_ok=True)

# ✅ טען קבוצות
with open(os.path.join(HERE, groups_config), 'r', encoding='utf-8') as f:
    cfg = json.load(f)
group_links = cfg.get("groups", [])
group_usernames = [link.rstrip('/').split('/')[-1] for link in group_links]


# ==================== פונקציות חדשות מדהימות ====================

class M3UStatistics:
    """מחלקה לסטטיסטיקות מתקדמות"""

    def __init__(self):
        self.start_time = datetime.now()
        self.stats = {
            'channels_by_group': defaultdict(list),
            'quality_distribution': Counter(),
            'categories': Counter(),
            'duplicate_channels': [],
            'total_channels': 0,
            'unique_channels': set(),
            'processing_times': [],
            'file_sizes': []
        }

    def analyze_m3u_content(self, content, group_name):
        """ניתוח תוכן M3U לסטטיסטיקות"""
        channels = []
        lines = content.splitlines()

        for i, line in enumerate(lines):
            if line.startswith('#EXTINF:'):
                # חילוץ מידע על הערוץ
                channel_info = {}

                # חילוץ שם
                match = re.search(r',(.+)$', line)
                if match:
                    channel_info['name'] = match.group(1).strip()

                # חילוץ קבוצה
                match = re.search(r'group-title="([^"]*)"', line)
                if match:
                    channel_info['group'] = match.group(1)

                # זיהוי איכות
                name_lower = channel_info.get('name', '').lower()
                if '4k' in name_lower or 'uhd' in name_lower:
                    channel_info['quality'] = '4K'
                elif 'hd' in name_lower or '1080' in name_lower:
                    channel_info['quality'] = 'HD'
                elif 'sd' in name_lower or '480' in name_lower:
                    channel_info['quality'] = 'SD'
                else:
                    channel_info['quality'] = 'Standard'

                channels.append(channel_info)

                # עדכון סטטיסטיקות
                self.stats['quality_distribution'][channel_info['quality']] += 1
                self.stats['categories'][channel_info.get('group', 'General')] += 1
                self.stats['unique_channels'].add(channel_info.get('name', ''))

        self.stats['channels_by_group'][group_name].extend(channels)
        self.stats['total_channels'] += len(channels)

        return len(channels)

    def get_summary(self):
        """קבלת סיכום סטטיסטיקות"""
        duration = (datetime.now() - self.start_time).total_seconds()

        summary = f"""
📊 ==================== סטטיסטיקות מפורטות ====================
⏱️ זמן ריצה כולל: {duration:.2f} שניות
📺 סה"כ ערוצים: {self.stats['total_channels']}
🎯 ערוצים ייחודיים: {len(self.stats['unique_channels'])}

📡 התפלגות איכות:
"""
        for quality, count in self.stats['quality_distribution'].most_common():
            percentage = (count / self.stats['total_channels'] * 100) if self.stats['total_channels'] > 0 else 0
            summary += f"   • {quality}: {count} ({percentage:.1f}%)\n"

        summary += "\n📁 קטגוריות פופולריות:\n"
        for category, count in self.stats['categories'].most_common(5):
            summary += f"   • {category}: {count} ערוצים\n"

        summary += "\n🏆 קבוצות מובילות:\n"
        sorted_groups = sorted(self.stats['channels_by_group'].items(),
                               key=lambda x: len(x[1]), reverse=True)
        for group, channels in sorted_groups[:3]:
            summary += f"   • {group}: {len(channels)} ערוצים\n"

        return summary


class EnhancedLogger:
    """מערכת לוגים משופרת עם צבעים"""

    @staticmethod
    def info(message):
        print(f"✅ {datetime.now().strftime('%H:%M:%S')} | {message}")

    @staticmethod
    def warning(message):
        print(f"⚠️ {datetime.now().strftime('%H:%M:%S')} | {message}")

    @staticmethod
    def error(message):
        print(f"❌ {datetime.now().strftime('%H:%M:%S')} | {message}")

    @staticmethod
    def success(message):
        print(f"🎉 {datetime.now().strftime('%H:%M:%S')} | {message}")

    @staticmethod
    def debug(message):
        if os.getenv("DEBUG", "false").lower() == "true":
            print(f"🔍 {datetime.now().strftime('%H:%M:%S')} | {message}")


logger = EnhancedLogger()


def create_progress_bar(current, total, bar_length=50):
    """יצירת בר התקדמות יפה"""
    if total == 0:
        return "⬜" * bar_length

    progress = current / total
    filled = int(bar_length * progress)
    bar = "🟩" * filled + "⬜" * (bar_length - filled)
    percentage = progress * 100

    return f"[{bar}] {percentage:.1f}% ({current}/{total})"


def format_file_size(size_bytes):
    """פורמט יפה לגודל קובץ"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


# ==================== הפונקציות המקוריות שלך ====================

def read_file_with_detected_encoding(filepath):
    """קריאת קובץ עם זיהוי קידוד משופר"""
    try:
        with open(filepath, 'rb') as f:
            raw = f.read()

        # ניסיון עם chardet
        detected = chardet.detect(raw)
        encoding = detected['encoding'] or 'utf-8'
        confidence = detected.get('confidence', 0)

        logger.debug(f"זוהה קידוד {encoding} עם ביטחון {confidence:.2f}")

        if confidence < 0.7:
            # אם הביטחון נמוך, ננסה קידודים נפוצים
            encodings_to_try = ['utf-8', 'utf-8-sig', 'windows-1251', 'latin1', 'cp1252']
            for enc in encodings_to_try:
                try:
                    return raw.decode(enc)
                except UnicodeDecodeError:
                    continue

        return raw.decode(encoding, errors='replace')
    except Exception as e:
        logger.error(f"שגיאה בקריאת קובץ {filepath}: {e}")
        return None


def compute_hash_from_text(text):
    """חישוב hash משופר"""
    normalized = re.sub(r'\s+', ' ', text.strip())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def send_summary_to_bot(total_downloaded: int, summary_lines: list, new_files_path: str, stats: M3UStatistics = None):
    """שליחת סיכום משופר לבוט"""
    BOT_TOKEN = "7757317671:AAF0EhrWmJ5Pr5kUsalQvDOLzukbsyD3Ci0"
    CHAT_ID = 7773889743
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    if total_downloaded == 0:
        message = "📭 לא נמצאו קבצי M3U חדשים בסריקה האחרונה."
    else:
        message = f"✅ הסתיימה סריקה.\nנמצאו {total_downloaded} קבצים:\n\n"

        # הגבלת מספר השורות ל-10
        if len(summary_lines) > 10:
            message += "\n\n".join(summary_lines[:10])
            message += f"\n\n... ועוד {len(summary_lines) - 10} קבצים"
        else:
            message += "\n\n".join(summary_lines)

    # הוספת סטטיסטיקות אם יש
    if stats:
        message += f"\n\n📊 סיכום:\n"
        message += f"• סה\"כ ערוצים: {stats.stats['total_channels']}\n"
        message += f"• ערוצים ייחודיים: {len(stats.stats['unique_channels'])}\n"

        # איכות מובילה
        if stats.stats['quality_distribution']:
            top_quality = stats.stats['quality_distribution'].most_common(1)[0]
            message += f"• איכות נפוצה: {top_quality[0]} ({top_quality[1]} ערוצים)"

    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        if response.ok:
            logger.success("הודעת סיכום נשלחה לבוט")
        else:
            logger.warning(f"שגיאה בשליחה: {response.status_code}")
    except Exception as e:
        logger.error(f"שגיאת שליחה: {e}")
    finally:
        show_new_files_folder(new_files_path)


def is_session_locked(session_path):
    """בדיקה אם session נעול"""
    db_path = f"{session_path}.session"
    if not os.path.exists(db_path):
        return False
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute('PRAGMA schema_version;')
        return False
    except sqlite3.OperationalError as e:
        if 'database is locked' in str(e):
            return True
        return False


def download_m3u_via_http(token: str, dest_dir: str) -> str | None:
    """הורדת M3U משופרת עם retry"""
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            logger.debug(f"ניסיון {attempt + 1} להוריד: {token[:50]}...")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            r = requests.get(token, timeout=15, allow_redirects=True, headers=headers)
            r.raise_for_status()

            try:
                text = r.content.decode('utf-8-sig')
            except UnicodeDecodeError:
                text = r.text

            if "#EXTM3U" not in text[:100]:
                logger.warning(f"אין EXTM3U בנתונים: {token[:50]}...")
                return None

            basename = os.path.basename(token.split('?')[0])
            if not basename or '.' not in basename:
                basename = f"playlist_{datetime.now():%Y%m%d_%H%M%S}.m3u"

            saved_path = os.path.join(dest_dir, basename)
            if os.path.exists(saved_path):
                logger.info(f"קובץ כבר קיים: {basename}")
                return None

            with open(saved_path, "wb") as f:
                f.write(r.content)

            file_size = format_file_size(len(r.content))
            logger.success(f"הורד: {basename} ({file_size})")
            return saved_path

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout בניסיון {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            continue
        except Exception as ex:
            logger.error(f"שגיאה בהורדה: {ex}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            continue

    return None


def show_new_files_folder(path: str):
    """פתיחת תיקיית קבצים חדשים"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    logger.info(f"תיקיית קבצים חדשים: {path}")
    try:
        os.startfile(path)
    except Exception as e:
        logger.warning(f"לא ניתן לפתוח את התיקייה: {e}")


def copy_to_new_files_folder(src_path: str, base_download_dir: str):
    """העתקה משופרת לתיקיית קבצים חדשים"""
    try:
        rel = os.path.relpath(src_path, base_download_dir)
        dest = os.path.join(base_download_dir, 'קבצים חדשים', rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src_path, dest)
        logger.debug(f"מועתק ל'קבצים חדשים': {os.path.basename(dest)}")
    except Exception as e:
        logger.error(f"שגיאה בהעתקה: {e}")


# ==================== הפונקציה הראשית המשופרת ====================

async def main():
    """פונקציה ראשית משופרת עם כל הפיצ'רים החדשים"""
    import re

    # הדפסת באנר פתיחה
    print("=" * 70)
    print("       🚀 TELEGRAM M3U SCANNER - ENHANCED VERSION 🚀")
    print("                    💎 By Eldad - V2.0 💎")
    print("=" * 70)
    print()

    # אתחול סטטיסטיקות
    statistics = M3UStatistics()

    session_path = os.path.join(HERE, session_name)

    if is_session_locked(session_path):
        logger.warning("קובץ session נעול, מנקה...")
        for ext in ['.session', '.session-journal', '.session-shm', '.session-wal']:
            try:
                os.remove(f"{session_path}{ext}")
                logger.debug(f"נמחק {session_path}{ext}")
            except FileNotFoundError:
                continue

    client = TelegramClient(session_path, api_id, api_hash)

    try:
        logger.info("מתחבר לטלגרם...")
        await client.connect()
        logger.success("התחברות הצליחה!")
    except Exception as e:
        logger.error(f"שגיאה בהתחברות: {e}")
        return

    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        code = input("✉️ קוד שהתקבל: ").strip()
        try:
            await client.sign_in(phone, code)
        except errors.SessionPasswordNeededError:
            await client.sign_in(password=password_2fa)
        logger.success("אימות הושלם!")

    entities = []
    print("\n📡 טוען קבוצות...")
    for i, uname in enumerate(group_usernames, 1):
        try:
            ent = await client.get_entity(uname)
            entities.append(ent)
            print(f"  [{i}/{len(group_usernames)}] ✅ {uname}")
        except Exception as e:
            print(f"  [{i}/{len(group_usernames)}] ❌ {uname}: {e}")

    since_time = datetime.now().astimezone() - timedelta(hours=36)
    logger.info(f"סורק הודעות מ: {since_time.strftime('%Y-%m-%d %H:%M')}")

    editor = M3UEditor()
    editor.hide()

    total_downloaded = 0
    hash_set = set()
    summary_lines = []

    print("\n" + "=" * 70)
    print("                    🔍 מתחיל סריקה...")
    print("=" * 70)

    for group_idx, ent in enumerate(entities, 1):
        saved_any = 0
        group_name = ent.username or str(ent.id)
        group_dir = os.path.join(download_dir, group_name)
        os.makedirs(group_dir, exist_ok=True)

        print(f"\n📨 [{group_idx}/{len(entities)}] סורק קבוצה: {group_name}")
        print("-" * 50)

        msg_count = 0
        group_start_time = time.time()

        async for msg in client.iter_messages(ent, limit=200):
            msg_count += 1

            # הצגת התקדמות כל 20 הודעות
            if msg_count % 20 == 0:
                print(f"  {create_progress_bar(msg_count, 200)}")

            if msg.date < since_time:
                continue

            if not msg.message and not msg.file:
                continue

            day_folder = msg.date.strftime("%Y-%m-%d")
            group_day_dir = os.path.join(group_dir, day_folder)
            os.makedirs(group_day_dir, exist_ok=True)

            saved_path = None

            # טיפול בקבצים
            if msg.file and msg.file.name and msg.file.name.lower().endswith(('.m3u', '.m3u8')):
                saved_path = os.path.join(group_day_dir, msg.file.name)
                if os.path.exists(saved_path):
                    logger.debug(f"קובץ קיים: {msg.file.name}")
                    continue

                saved_path = await msg.download_media(group_day_dir)
                if saved_path:
                    file_size = format_file_size(os.path.getsize(saved_path))
                    logger.success(f"הורד קובץ: {msg.file.name} ({file_size})")
            else:
                # חיפוש URLs
                urls = [u for u in re.findall(r'https?://[^\s]+', msg.message or "")
                        if '.m3u' in u or '.m3u8' in u or 'get.php' in u.lower()]

                for url in urls:
                    logger.info(f"בודק קישור: {url[:50]}...")
                    saved = download_m3u_via_http(url, group_day_dir)
                    if saved:
                        saved_path = saved
                        break

            if not saved_path:
                continue

            saved_any += 1
            total_downloaded += 1

            # עיבוד הקובץ
            try:
                logger.debug(f"טוען קובץ: {saved_path}")
                m3u_text = read_file_with_detected_encoding(saved_path)

                if m3u_text:
                    # ניתוח סטטיסטיקות
                    channels_count = statistics.analyze_m3u_content(m3u_text, group_name)
                    logger.info(f"נמצאו {channels_count} ערוצים בקובץ")

                    # הזרקת לוגואים
                    new_lines = []
                    for line in m3u_text.splitlines():
                        if line.startswith("#EXTINF:"):
                            try:
                                match = re.search(r",(.+)", line)
                                name = match.group(1).strip() if match else ""
                                line = inject_logo_to_line(line, name)
                            except Exception as e:
                                logger.debug(f"שגיאה בהזרקת לוגו: {e}")
                        new_lines.append(line)
                    m3u_text = "\n".join(new_lines)

                    # בדיקת כפילות
                    h = compute_hash_from_text(m3u_text)
                    if h in hash_set:
                        logger.warning(f"כפילות נמצאה: {os.path.basename(saved_path)}")
                        continue
                    hash_set.add(h)

                    # עיבוד עם העורך
                    editor.loadM3UFromText(m3u_text)
                    editor.regenerateM3UTextOnly()
                    basename = os.path.splitext(os.path.basename(saved_path))[0]
                    cleaned = os.path.join(group_day_dir, f"{basename}_NEW_{msg.date:%Y%m%d_%H%M%S}.m3u")
                    editor.exportM3UWithLogos(cleaned)
                    logger.success(f"נשמר: {os.path.basename(cleaned)}")

                    if not SKIP_COPY:
                        copy_to_new_files_folder(cleaned, download_dir)

                    summary_lines.append(
                        f"📁 {group_name} | 📄 {os.path.basename(cleaned)}\n"
                        f"👤 ID: {msg.sender_id} | 🕓 {msg.date.strftime('%Y-%m-%d %H:%M')} | "
                        f"📺 {channels_count} ערוצים"
                    )

            except Exception as e:
                logger.error(f"שגיאה בעיבוד: {e}")

        # סיכום קבוצה
        group_time = time.time() - group_start_time
        print(f"\n  📊 סיכום {group_name}:")
        print(f"     • הודעות נסרקו: {msg_count}")
        print(f"     • קבצים נמצאו: {saved_any}")
        print(f"     • זמן סריקה: {group_time:.2f} שניות")

        if saved_any == 0:
            print(f"     📭 אין קבצים חדשים")

    await client.disconnect()
    logger.info("התנתקות מטלגרם")

    # הצגת סטטיסטיקות מפורטות
    print("\n" + "=" * 70)
    print(statistics.get_summary())
    print("=" * 70)

    print(f"\n🎯 סיום סריקה. נמצאו {total_downloaded} קבצים.")

    # פתיחת תיקייה
    new_files_path = os.path.join(download_dir, 'קבצים חדשים')
    show_new_files_folder(new_files_path)

    # שליחת סיכום לבוט
    logger.info("שולח סיכום לבוט...")
    send_summary_to_bot(total_downloaded, summary_lines, new_files_path, statistics)

    print("\n✨ תודה שהשתמשת במערכת! ✨")


# ✅ הרצה
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ בוטל על ידי המשתמש")
    except Exception as e:
        print(f"\n❌ שגיאה כללית: {e}")
        import traceback

        traceback.print_exc()