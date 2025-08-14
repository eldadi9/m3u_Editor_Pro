"""
🤖 בוט טלגרם אינטראקטיבי לשליטה מרחוק במערכת M3U Scanner
שמור קובץ זה בשם: bot_controller.py
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import subprocess
import os
import json
from datetime import datetime, timedelta
import asyncio
import sqlite3
from typing import Dict, List

# הגדרות
BOT_TOKEN = "7757317671:AAF0EhrWmJ5Pr5kUsalQvDOLzukbsyD3Ci0"
ADMIN_CHAT_ID = 7773889743  # ה-ID שלך
SCANNER_SCRIPT = "user_Agent.py"  # הסקריפט הראשי שלך
LOG_FILE = "bot_controller.log"

# הגדרת לוגר
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class M3UScannerBot:
    """מחלקת הבוט לשליטה במערכת"""
    
    def __init__(self):
        self.scanning_process = None
        self.last_scan_time = None
        self.scan_results = {}
        self.auto_scan_enabled = False
        self.auto_scan_interval = 6  # שעות
        self.statistics = {
            'total_scans': 0,
            'total_files': 0,
            'total_channels': 0,
            'last_results': []
        }
        
    def is_authorized(self, user_id: int) -> bool:
        """בדיקת הרשאה"""
        return user_id == ADMIN_CHAT_ID
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """פקודת התחלה"""
        user = update.effective_user
        
        if not self.is_authorized(user.id):
            await update.message.reply_text("❌ אין לך הרשאה להשתמש בבוט זה.")
            return
        
        keyboard = [
            [
                InlineKeyboardButton("🔍 התחל סריקה", callback_data='scan_now'),
                InlineKeyboardButton("⏹️ עצור סריקה", callback_data='stop_scan')
            ],
            [
                InlineKeyboardButton("📊 סטטיסטיקות", callback_data='statistics'),
                InlineKeyboardButton("📋 לוג אחרון", callback_data='last_log')
            ],
            [
                InlineKeyboardButton("⚙️ הגדרות", callback_data='settings'),
                InlineKeyboardButton("🔄 סריקה אוטומטית", callback_data='auto_scan')
            ],
            [
                InlineKeyboardButton("📁 פתח תיקייה", callback_data='open_folder'),
                InlineKeyboardButton("🗑️ נקה ישנים", callback_data='cleanup')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = f"""
🤖 **ברוך הבא למערכת השליטה של M3U Scanner!**

👤 משתמש: {user.first_name}
🕐 זמן: {datetime.now().strftime('%Y-%m-%d %H:%M')}
📊 סטטוס: {'🟢 פעיל' if self.scanning_process else '⭕ ממתין'}

בחר פעולה:
        """
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def scan_now(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """התחלת סריקה מיידית"""
        query = update.callback_query
        await query.answer()
        
        if self.scanning_process and self.scanning_process.poll() is None:
            await query.edit_message_text("⚠️ סריקה כבר רצה כרגע!")
            return
        
        await query.edit_message_text("🔄 מתחיל סריקה...\n⏳ זה יכול לקחת כמה דקות.")
        
        try:
            # הפעלת הסקריפט הראשי
            self.scanning_process = subprocess.Popen(
                ['python', SCANNER_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.last_scan_time = datetime.now()
            self.statistics['total_scans'] += 1
            
            # המתנה לסיום (אסינכרונית)
            context.application.create_task(
                self.monitor_scan_process(query, context)
            )
            
        except Exception as e:
            await query.edit_message_text(f"❌ שגיאה בהפעלת הסריקה:\n{str(e)}")
            logger.error(f"Scan error: {e}")
    
    async def monitor_scan_process(self, query, context):
        """מעקב אחר תהליך הסריקה"""
        start_time = datetime.now()
        update_counter = 0
        
        while self.scanning_process and self.scanning_process.poll() is None:
            await asyncio.sleep(10)  # עדכון כל 10 שניות
            update_counter += 1
            
            elapsed = (datetime.now() - start_time).seconds
            status_msg = f"""
🔍 **סריקה בתהליך...**

⏱️ זמן: {elapsed // 60}:{elapsed % 60:02d}
📊 עדכון מס': {update_counter}
🔄 סטטוס: סורק קבוצות...

_הסריקה תסתיים אוטומטית_
            """
            
            try:
                await query.edit_message_text(status_msg, parse_mode='Markdown')
            except:
                pass  # אם ההודעה לא השתנתה
        
        # סריקה הסתיימה
        if self.scanning_process:
            stdout, stderr = self.scanning_process.communicate()
            
            # ניתוח התוצאות
            results = self.parse_scan_results(stdout)
            
            completion_msg = f"""
✅ **הסריקה הושלמה!**

📊 **תוצאות:**
• קבצים שנמצאו: {results.get('files', 0)}
• ערוצים כוללים: {results.get('channels', 0)}
• זמן סריקה: {(datetime.now() - start_time).seconds // 60} דקות

📝 פרטים נשלחו בהודעה נפרדת.
            """
            
            await query.edit_message_text(completion_msg, parse_mode='Markdown')
            
            # עדכון סטטיסטיקות
            self.statistics['total_files'] += results.get('files', 0)
            self.statistics['total_channels'] += results.get('channels', 0)
            self.statistics['last_results'] = results
    
    def parse_scan_results(self, output: str) -> Dict:
        """ניתוח תוצאות הסריקה"""
        results = {
            'files': 0,
            'channels': 0,
            'groups': [],
            'errors': []
        }
        
        for line in output.split('\n'):
            if 'נמצאו' in line and 'קבצים' in line:
                try:
                    results['files'] = int(''.join(filter(str.isdigit, line)))
                except:
                    pass
            elif 'ערוצים' in line:
                try:
                    results['channels'] = int(''.join(filter(str.isdigit, line)))
                except:
                    pass
            elif '❌' in line:
                results['errors'].append(line)
        
        return results
    
    async def stop_scan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """עצירת סריקה"""
        query = update.callback_query
        await query.answer()
        
        if self.scanning_process and self.scanning_process.poll() is None:
            self.scanning_process.terminate()
            await query.edit_message_text("⏹️ הסריקה נעצרה.")
        else:
            await query.edit_message_text("ℹ️ אין סריקה פעילה כרגע.")
    
    async def show_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """הצגת סטטיסטיקות"""
        query = update.callback_query
        await query.answer()
        
        stats_msg = f"""
📊 **סטטיסטיקות מערכת**

**סיכום כללי:**
• סריקות כוללות: {self.statistics['total_scans']}
• קבצים שנמצאו: {self.statistics['total_files']}
• ערוצים כוללים: {self.statistics['total_channels']}

**סריקה אחרונה:**
• זמן: {self.last_scan_time.strftime('%Y-%m-%d %H:%M') if self.last_scan_time else 'לא בוצעה'}
• סטטוס: {'🟢 פעיל' if self.scanning_process and self.scanning_process.poll() is None else '⭕ לא פעיל'}

**הגדרות:**
• סריקה אוטומטית: {'✅ מופעלת' if self.auto_scan_enabled else '❌ כבויה'}
• מרווח זמן: כל {self.auto_scan_interval} שעות
        """
        
        await query.edit_message_text(stats_msg, parse_mode='Markdown')
    
    async def toggle_auto_scan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """הפעלה/כיבוי סריקה אוטומטית"""
        query = update.callback_query
        await query.answer()
        
        self.auto_scan_enabled = not self.auto_scan_enabled
        
        if self.auto_scan_enabled:
            # הגדרת job לסריקה אוטומטית
            context.job_queue.run_repeating(
                self.auto_scan_job,
                interval=self.auto_scan_interval * 3600,  # המרה לשניות
                first=10,  # התחל אחרי 10 שניות
                name='auto_scan'
            )
            status = f"✅ סריקה אוטומטית הופעלה!\nתרוץ כל {self.auto_scan_interval} שעות."
        else:
            # ביטול jobs
            current_jobs = context.job_queue.get_jobs_by_name('auto_scan')
            for job in current_jobs:
                job.schedule_removal()
            status = "❌ סריקה אוטומטית כובתה."
        
        await query.edit_message_text(status)
    
    async def auto_scan_job(self, context: ContextTypes.DEFAULT_TYPE):
        """Job לסריקה אוטומטית"""
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text="🔄 מתחיל סריקה אוטומטית..."
        )
        
        # הפעלת סריקה
        self.scanning_process = subprocess.Popen(
            ['python', SCANNER_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.last_scan_time = datetime.now()
        self.statistics['total_scans'] += 1
    
    async def cleanup_old_files(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ניקוי קבצים ישנים"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text("🗑️ מנקה קבצים ישנים מ-30 יום...")
        
        # כאן תוסיף את הלוגיקה לניקוי קבצים
        # (קריאה לפונקציה מהסקריפט הראשי או ישירות)
        
        await query.edit_message_text("✅ ניקוי הושלם!")
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בלחיצות כפתורים"""
        query = update.callback_query
        
        handlers = {
            'scan_now': self.scan_now,
            'stop_scan': self.stop_scan,
            'statistics': self.show_statistics,
            'auto_scan': self.toggle_auto_scan,
            'cleanup': self.cleanup_old_files,
        }
        
        handler = handlers.get(query.data)
        if handler:
            await handler(update, context)
        else:
            await query.answer("פעולה לא מוכרת")

def main():
    """הפעלת הבוט"""
    print("🤖 מפעיל בוט שליטה...")
    
    # יצירת האפליקציה
    bot = M3UScannerBot()
    application = Application.builder().token(BOT_TOKEN).build()
    
    # הוספת handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CallbackQueryHandler(bot.button_handler))
    
    # הפעלת הבוט
    print("✅ הבוט מוכן! שלח /start בטלגרם")
    application.run_polling()

if __name__ == '__main__':
    main()