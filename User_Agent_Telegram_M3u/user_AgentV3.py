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


def cleanup_session_files(session_path):
    """
    ניקוי מלא של קבצי session עם בדיקות נוספות
    """
    logger.info("🧹 מתחיל ניקוי קבצי session...")

    extensions = [
        '.session',
        '.session-journal',
        '.session-shm',
        '.session-wal',
        '.session.lock'  # הוספת קובץ נעילה
    ]

    cleaned_count = 0
    for ext in extensions:
        file_path = f"{session_path}{ext}"

        # נסה לסגור חיבורים פתוחים
        if ext == '.session':
            try:
                # נסה לסגור את ה-DB אם הוא פתוח
                import gc
                gc.collect()  # נקה זיכרון

                # המתן רגע לפני מחיקה
                import time
                time.sleep(0.5)
            except:
                pass

        # מחק את הקובץ
        for attempt in range(3):  # 3 ניסיונות
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"✓ נמחק: {file_path}")
                    cleaned_count += 1
                    break
            except PermissionError:
                if attempt < 2:
                    logger.warning(f"⏳ ממתין לשחרור {file_path}...")
                    time.sleep(1)
                else:
                    logger.error(f"❌ לא ניתן למחוק: {file_path}")
            except FileNotFoundError:
                break
            except Exception as e:
                logger.error(f"שגיאה במחיקת {file_path}: {e}")
                break

    if cleaned_count > 0:
        logger.success(f"🧹 נוקו {cleaned_count} קבצי session")

    return cleaned_count > 0


def is_session_locked_enhanced(session_path):
    """
    בדיקה משופרת אם session נעול עם ניסיון לשחרר
    """
    db_path = f"{session_path}.session"

    if not os.path.exists(db_path):
        return False

    # בדיקה ראשונית
    try:
        conn = sqlite3.connect(db_path, timeout=1.0)
        conn.execute('PRAGMA schema_version;')
        conn.close()
        return False
    except sqlite3.OperationalError as e:
        if 'database is locked' in str(e) or 'database is busy' in str(e):
            logger.warning("🔒 Session נעול, מנסה לשחרר...")

            # נסה לשחרר את הנעילה
            try:
                # סגור תהליכים אחרים שמשתמשים בקובץ
                import psutil
                current_pid = os.getpid()

                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['pid'] != current_pid:
                        try:
                            for file in proc.open_files():
                                if db_path in file.path:
                                    logger.warning(f"🔓 סוגר תהליך {proc.info['name']} (PID: {proc.info['pid']})")
                                    proc.terminate()
                                    proc.wait(timeout=3)
                        except:
                            pass
            except ImportError:
                logger.debug("psutil לא מותקן, מדלג על בדיקת תהליכים")
            except:
                pass

            return True
    except Exception as e:
        logger.error(f"שגיאה בבדיקת session: {e}")
        return True

    return False


# שימוש בפונקציות המשופרות ב-main:
async def main():
    """חלק מתוך הפונקציה הראשית - החלף את החלק הרלוונטי"""

    session_path = os.path.join(HERE, session_name)

    # בדיקה ראשונית
    if is_session_locked_enhanced(session_path):
        logger.warning("⚠️ זוהה session נעול")

        # ניסיון ניקוי
        if cleanup_session_files(session_path):
            logger.success("✅ Session נוקה בהצלחה")

            # המתן רגע לוודא שהכל נסגר
            await asyncio.sleep(1)
        else:
            logger.error("❌ לא הצלחתי לנקות את ה-session")

            # אפשרות לבקש מהמשתמש
            response = input("\n❓ לנסות להמשיך בכל זאת? (y/n): ").strip().lower()
            if response != 'y':
                logger.info("👋 יוצא מהתוכנית...")
                return

    # המשך עם החיבור לטלגרם...
    client = TelegramClient(session_path, api_id, api_hash)
    # ...


def create_progress_bar(current, total, bar_length=50):
    """יצירת בר התקדמות יפה"""
    if total == 0:
        return "⬜" * bar_length

    progress = current / total
    filled = int(bar_length * progress)
    bar = "🟩" * filled + "⬜" * (bar_length - filled)
    percentage = progress * 100

    return f"[{bar}] {percentage:.1f}% ({current}/{total})"


import pandas as pd
from datetime import datetime
import os


def create_excel_report(statistics, summary_lines, output_dir):
    """
    יצירת דוח Excel מפורט עם מספר גליונות
    """
    try:
        # יצירת תיקיית דוחות
        reports_dir = os.path.join(output_dir, 'דוחות')
        os.makedirs(reports_dir, exist_ok=True)

        # שם הקובץ עם תאריך ושעה
        report_file = os.path.join(reports_dir, f'דוח_סריקה_{datetime.now():%Y%m%d_%H%M%S}.xlsx')

        # יצירת Writer
        with pd.ExcelWriter(report_file, engine='openpyxl') as writer:

            # גליון 1: סיכום כללי
            summary_data = {
                'מדד': [
                    'סה"כ ערוצים',
                    'ערוצים ייחודיים',
                    'קבצים שנמצאו',
                    'זמן ריצה (שניות)'
                ],
                'ערך': [
                    statistics.stats['total_channels'],
                    len(statistics.stats['unique_channels']),
                    len(summary_lines),
                    (datetime.now() - statistics.start_time).total_seconds()
                ]
            }
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='סיכום', index=False)

            # גליון 2: התפלגות איכות
            quality_data = pd.DataFrame(
                list(statistics.stats['quality_distribution'].items()),
                columns=['איכות', 'כמות']
            )
            quality_data['אחוז'] = (quality_data['כמות'] /
                                    quality_data['כמות'].sum() * 100).round(1)
            quality_data.to_excel(writer, sheet_name='איכות', index=False)

            # גליון 3: קטגוריות
            categories_data = pd.DataFrame(
                list(statistics.stats['categories'].items()),
                columns=['קטגוריה', 'ערוצים']
            )
            categories_data = categories_data.sort_values('ערוצים', ascending=False)
            categories_data.to_excel(writer, sheet_name='קטגוריות', index=False)

            # גליון 4: ערוצים לפי קבוצה
            groups_data = []
            for group, channels in statistics.stats['channels_by_group'].items():
                groups_data.append({
                    'קבוצה': group,
                    'מספר ערוצים': len(channels),
                    'ערוצים': ', '.join([ch.get('name', '') for ch in channels[:10]])
                })

            if groups_data:
                df_groups = pd.DataFrame(groups_data)
                df_groups.to_excel(writer, sheet_name='קבוצות', index=False)

            # גליון 5: קבצים שנמצאו
            files_data = []
            for line in summary_lines:
                parts = line.split('|')
                if len(parts) >= 2:
                    files_data.append({
                        'קבוצה': parts[0].strip().replace('📁', '').strip(),
                        'קובץ': parts[1].strip().replace('📄', '').strip() if len(parts) > 1 else '',
                        'פרטים': parts[2].strip() if len(parts) > 2 else ''
                    })

            if files_data:
                df_files = pd.DataFrame(files_data)
                df_files.to_excel(writer, sheet_name='קבצים', index=False)

            # עיצוב הגליונות
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]

                # התאמת רוחב עמודות
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter

                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass

                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

        logger.success(f"📊 דוח Excel נוצר: {report_file}")

        # פתיחת הקובץ אוטומטית
        try:
            os.startfile(report_file)
        except:
            pass

        return report_file

    except ImportError:
        logger.warning("⚠️ pandas או openpyxl לא מותקנים. התקן עם: pip install pandas openpyxl")
        return None
    except Exception as e:
        logger.error(f"שגיאה ביצירת דוח Excel: {e}")
        return None


# הוספה לסוף הפונקציה main():
# excel_report = create_excel_report(statistics, summary_lines, download_dir)

class ChannelSearchEngine:
    """
    מנוע חיפוש חכם לערוצים
    """

    def __init__(self):
        self.channels_db = []
        self.index = {}

    def add_channels_from_m3u(self, content, source_file):
        """הוספת ערוצים מקובץ M3U"""
        lines = content.splitlines()

        for i, line in enumerate(lines):
            if line.startswith('#EXTINF:'):
                channel = {'source': source_file, 'line_num': i}

                # חילוץ שם
                match = re.search(r',(.+)$', line)
                if match:
                    channel['name'] = match.group(1).strip()

                # חילוץ לוגו
                match = re.search(r'tvg-logo="([^"]*)"', line)
                if match:
                    channel['logo'] = match.group(1)

                # חילוץ קבוצה
                match = re.search(r'group-title="([^"]*)"', line)
                if match:
                    channel['group'] = match.group(1)

                # URL בשורה הבאה
                if i + 1 < len(lines) and not lines[i + 1].startswith('#'):
                    channel['url'] = lines[i + 1].strip()

                self.channels_db.append(channel)

                # בניית אינדקס
                name_lower = channel.get('name', '').lower()
                for word in name_lower.split():
                    if word not in self.index:
                        self.index[word] = []
                    self.index[word].append(len(self.channels_db) - 1)

    def search(self, query, limit=10):
        """חיפוש ערוצים"""
        query_lower = query.lower()
        results = []
        scores = {}

        # חיפוש מדויק
        for i, channel in enumerate(self.channels_db):
            name = channel.get('name', '').lower()
            score = 0

            # התאמה מלאה
            if query_lower == name:
                score = 100
            # התאמה חלקית
            elif query_lower in name:
                score = 80
            # מילים בודדות
            else:
                words_matched = sum(1 for word in query_lower.split() if word in name)
                if words_matched > 0:
                    score = 60 * (words_matched / len(query_lower.split()))

            if score > 0:
                scores[i] = score

        # מיון לפי ציון
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # החזרת התוצאות
        for idx, score in sorted_results[:limit]:
            channel = self.channels_db[idx].copy()
            channel['score'] = score
            results.append(channel)

        return results

    def find_duplicates(self):
        """מציאת ערוצים כפולים"""
        duplicates = {}

        for channel in self.channels_db:
            name = channel.get('name', '')
            if name in duplicates:
                duplicates[name].append(channel)
            else:
                duplicates[name] = [channel]

        # החזר רק כפילויות
        return {name: channels for name, channels in duplicates.items() if len(channels) > 1}

    def get_statistics(self):
        """סטטיסטיקות על הערוצים"""
        stats = {
            'total': len(self.channels_db),
            'with_logo': sum(1 for ch in self.channels_db if ch.get('logo')),
            'groups': len(set(ch.get('group', 'General') for ch in self.channels_db)),
            'sources': len(set(ch.get('source', '') for ch in self.channels_db))
        }
        return stats

    def export_unique_playlist(self, output_file):
        """ייצוא רשימת ערוצים ייחודית"""
        seen_names = set()
        unique_channels = []

        for channel in self.channels_db:
            name = channel.get('name', '')
            if name and name not in seen_names:
                seen_names.add(name)
                unique_channels.append(channel)

        # יצירת M3U
        m3u_content = "#EXTM3U\n"
        for channel in unique_channels:
            extinf = f"#EXTINF:-1"

            if channel.get('logo'):
                extinf += f' tvg-logo="{channel["logo"]}"'
            if channel.get('group'):
                extinf += f' group-title="{channel["group"]}"'

            extinf += f",{channel.get('name', 'Unknown')}\n"
            extinf += f"{channel.get('url', '')}\n"

            m3u_content += extinf

        # שמירה לקובץ
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(m3u_content)

        logger.success(f"📝 יוצא רשימה ייחודית עם {len(unique_channels)} ערוצים")
        return len(unique_channels)


# שימוש במנוע החיפוש:
def interactive_channel_search(search_engine):
    """ממשק אינטראקטיבי לחיפוש ערוצים"""
    print("\n" + "=" * 60)
    print("         🔍 מנוע חיפוש ערוצים 🔍")
    print("=" * 60)
    print("פקודות: search <שם>, duplicates, stats, export, quit")
    print("-" * 60)

    while True:
        command = input("\n🔍 > ").strip().lower()

        if command == 'quit' or command == 'exit':
            break

        elif command.startswith('search '):
            query = command[7:]
            results = search_engine.search(query)

            if results:
                print(f"\nנמצאו {len(results)} תוצאות:")
                for i, channel in enumerate(results, 1):
                    print(f"{i}. {channel['name']} (ציון: {channel['score']})")
                    if channel.get('group'):
                        print(f"   קבוצה: {channel['group']}")
                    print(f"   מקור: {channel['source']}")
            else:
                print("לא נמצאו תוצאות")

        elif command == 'duplicates':
            dups = search_engine.find_duplicates()
            if dups:
                print(f"\nנמצאו {len(dups)} ערוצים כפולים:")
                for name, channels in list(dups.items())[:10]:
                    print(f"• {name}: {len(channels)} מופעים")
            else:
                print("לא נמצאו כפילויות")

        elif command == 'stats':
            stats = search_engine.get_statistics()
            print("\n📊 סטטיסטיקות:")
            print(f"• סה\"כ ערוצים: {stats['total']}")
            print(f"• עם לוגו: {stats['with_logo']}")
            print(f"• קבוצות: {stats['groups']}")
            print(f"• מקורות: {stats['sources']}")

        elif command == 'export':
            output = os.path.join(download_dir, f'unique_channels_{datetime.now():%Y%m%d_%H%M%S}.m3u')
            count = search_engine.export_unique_playlist(output)
            print(f"✅ יוצאו {count} ערוצים ייחודיים ל: {output}")

        elif command == 'help':
            print("פקודות זמינות:")
            print("  search <שם> - חיפוש ערוץ")
            print("  duplicates - הצגת כפילויות")
            print("  stats - סטטיסטיקות")
            print("  export - ייצוא רשימה ייחודית")
            print("  quit - יציאה")

        else:
            print("פקודה לא מוכרת. הקלד 'help' לעזרה")


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
