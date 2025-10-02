import os
import sys

# תוסיף את התיקייה הנוכחית ל־sys.path כדי שפייתון ימצא את logo.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import re
import json
import threading
import pyperclip
import requests
import subprocess
import time
import tempfile
from tempfile import NamedTemporaryFile
import os, subprocess, tempfile
from logo import get_saved_logo
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QListWidgetItem
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QTimer
from m3u_filter_enhanced import M3UFilterEnhanced
from PyQt5.QtWidgets import QListWidget, QAbstractItemView
from PyQt5.QtCore import Qt


import os

print("Current directory:", os.getcwd())
print("Portal file exists:", os.path.exists("portal_extensions.py"))

try:
    from portal_extensions import AdvancedPortalConverter, convert_portal_to_m3u

    PORTAL_CONVERTER_AVAILABLE = True
    print("✅ Portal Converter loaded successfully")
except ImportError as e:
    PORTAL_CONVERTER_AVAILABLE = False
    print(f"⚠️ Portal Converter not available: {e}")

import shutil
from datetime import datetime, timedelta
from urllib.parse import urlparse

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFileDialog, QTextEdit, QInputDialog,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView,
    QHBoxLayout, QLabel, QMessageBox, QLineEdit, QAbstractItemView,
    QMenu, QAction, QCompleter, QProgressBar, QDialog, QComboBox,
    QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QColor, QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor
from logo import load_logo_cache, get_saved_logo, save_logo_for_channel, is_israeli_channel
from PyQt5.QtWidgets import QMessageBox, QInputDialog
from telegram_uploader import send_to_telegram
from deep_translator import GoogleTranslator
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import QThread, pyqtSignal
import re
import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QProgressDialog,
    QMessageBox, QInputDialog, QListWidgetItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QProgressDialog, QMessageBox
from deep_translator import GoogleTranslator

from utils.network import setup_session
APP_QSS = """
* { font-family: 'Segoe UI', Tahoma, Arial; }

/* שדות קלט ובחירה */
QLineEdit, QComboBox {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 4px 6px;
  font-size: 12px;
  padding: 6px 8px;
}
QLineEdit:focus, QComboBox:focus {
  border: 1px solid #2563eb;
}

/* כפתורים */
QPushButton {
  border-radius: 8px;
  padding: 7px 10px;
  padding: 7px 12px;
  background: #f3f4f6;
  font-size: 12px;
}
QPushButton:hover { background: #e5e7eb; }

/* כפתורי הדגשה אופציונליים לפי property */
QPushButton[accent="blue"]   { background: #2563eb; color: #ffffff; }
QPushButton[accent="blue"]:hover   { background: #1d4ed8; }
QPushButton[accent="green"]  { background: #16a34a; color: #ffffff; }
QPushButton[accent="purple"] { background: #7c3aed; color: #ffffff; }
QPushButton[accent="orange"] { background: #ea580c; color: #ffffff; }
QPushButton[danger="true"]   { background: #ef4444; color: #ffffff; }

/* מסגרות כרטיסים ואיזורי עבודה */
QFrame#ToolBar, QFrame#Filters, QFrame#ChannelsHeader, QFrame#Cards {
  background: #ffffff;
QListWidget {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

/* כותרת עליונה אופציונלית */
QWidget#HeaderBar {
  background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 #2563eb, stop:1 #1e40af);
  color: #ffffff;
}

/* תגיות קטנות */
QLabel#Tag {
  background: #dbeafe;
  color: #1e40af;
  border-radius: 9px;
  padding: 0px 6px;
  font-size: 11px;
}

/* כרטיס ערוץ */
QWidget#Card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  border-radius: 10px;
  background: #ffffff;
}

/* כותרת הערוץ עצמו */
QLabel#channel_label {
  color: #111827;
  font-weight: 600;
  font-size: 11px;
}
QListWidget::item { padding: 8px; }
QListWidget::item:hover { background: #f0f8ff; }
"""

# הוסף בסוף APP_QSS
QSS_CHANNELS = """
/* רשימות ערוצים */
/* נראות חזקה לרשימות ערוצים */
QListWidget, QListView {
  background: #ffffff;
  color: #111827;
  color: #111827;                /* טקסט כהה */
  alternate-background-color: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}
QListWidget::item, QListView::item {
  color: #111827;
  background: #ffffff;
  padding: 2px 4px;
  padding: 10px 14px;
  border-bottom: 1px solid #eef2f7;
}
QListWidget::item:selected, QListView::item:selected {
  background: #ffffff;
  background: #dbeafe;           /* כחול בהיר לבחירה */
  color: #111827;
}
QListWidget::item:hover, QListView::item:hover {
  background: #eef2ff;
  background: #eef2ff;           /* ריחוף עדין */
}
"""

EXTRA_QSS_HEADER = """
QWidget#HeaderBar {
  background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2563eb, stop:1 #1e40af);
  color: #ffffff;
  border-radius: 6px;
}
QWidget#HeaderBar QLabel#HeaderTitle {
  color: #ffffff;
  font-weight: 700;
  font-size: 16px;
}
QWidget#HeaderBar QPushButton {
  background: rgba(255,255,255,0.15);
  color: #ffffff;
  border-radius: 6px;
  padding: 4px 10px;
}
QWidget#HeaderBar QPushButton:hover {
  background: rgba(255,255,255,0.25);
}
"""
EXTRA_QSS_CARDS = """
QWidget#Card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
}
QWidget#Card:hover { background: #f9fafb; }

QLabel#Tag {
  background: #eef2ff;
  color: #1e3a8a;
  border-radius: 10px;
  padding: 1px 8px;
  border: 1px solid #e5e7eb;
}

QToolButton.ActionBtn {
  background: transparent;
  border: none;
  padding: 2px 4px;
}
QToolButton.ActionBtn:hover {
  background: #edf2f7;
  border-radius: 6px;
}

QLabel#CounterPill {
  background: #eef2ff;
  color: #1e3a8a;
  border: 1px solid #c7d2fe;
  border-radius: 999px;
  padding: 2px 10px;
  font-weight: 600;
}

QFrame#TopToolbar {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
}
"""

APP_QSS_LARGE = """
* { font-size: 12pt; }
QPushButton { font-size: 11pt; }
QLineEdit, QComboBox, QTextEdit { font-size: 11pt; }
QListWidget, QListView, QTreeWidget, QTableWidget { font-size: 12pt; }
"""

QSS_TAILWINDISH = """
/* רשימות */
QListWidget, QListView {
  background: #ffffff;
  color: #111827;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  alternate-background-color: #f8fafc;
}
QListWidget::item, QListView::item {
  padding: 6px 8px;
  border-bottom: 1px solid #eef2f7;
}
QListWidget::item:selected, QListView::item:selected {
  background: #dbeafe;
  color: #111827;
}
QListWidget::item:hover, QListView::item:hover {
  background: #eef2ff;
}

/* כרטיס ערוץ */
#Card {
  background: #ffffff;
}

/* תגיות קטנות (איכות/קטגוריה/מוסתר) */
#Tag {
  background: #e5e7eb;
  color: #111827;
  border-radius: 10px;
  padding: 0px 6px;
  margin-right: 4px;
}

/* כותרות סקשנים */
.sectionTitle {
  font-size: 18px;
  font-weight: 700;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 6px 10px;
}
/* רקע כללי */
QWidget {
    background-color: #f8f9fa;
    font-family: "Segoe UI", sans-serif;
    font-size: 8pt;
    color: #212529;
}

/* כפתורים */
QPushButton {
    background-color: #e2e6ea;
    border: 1px solid #ced4da;
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 26px;
}

QPushButton:hover {
    background-color: #dee2e6;
}

QPushButton:pressed {
    background-color: #cfd4da;
}

/* תוויות */
QLabel {
    padding: 0px;
    margin: 0px;
    font-weight: bold;
    font-size: 11pt;
}

/* ComboBox */
QComboBox {
    padding: 2px 6px;
    border: 1px solid #ced4da;
    border-radius: 4px;
    background-color: #ffffff;
}

/* רשימת ערוצים */
QListWidget, QListView {
    background-color: #ffffff;
    border: 1px solid #ced4da;
    padding: 2px;
}

QListWidget::item, QListView::item {
    padding: 4px 6px;
    margin: 1px 0;
    border: 1px solid transparent;
    border-radius: 4px;
}

QListWidget::item:selected {
    background-color: #cce5ff;
    border-color: #66afe9;
}

/* QTextEdit */
QTextEdit {
    background-color: #ffffff;
    border: 1px solid #ced4da;
    padding: 4px;
    font-family: Consolas, monospace;
    font-size: 10pt;
}

/* ScrollBars */
QScrollBar:vertical {
    width: 8px;
    background: #f1f1f1;
}

QScrollBar::handle:vertical {
    background: #adb5bd;
    border-radius: 4px;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    height: 8px;
    background: #f1f1f1;
}

QScrollBar::handle:horizontal {
    background: #adb5bd;
    border-radius: 4px;
}

/* שורת כלים עליונה */
QToolBar {
    background-color: #ffffff;
    spacing: 4px;
    padding: 4px;
    border: none;
}

/* כפתורי פעולה (קטגוריות) — צבעים */
.btn-green   { background:#16a34a; color:white; font-weight:700; border-radius:8px; }
.btn-orange  { background:#f97316; color:white; font-weight:700; border-radius:8px; }
.btn-red     { background:#ef4444; color:white; font-weight:700; border-radius:8px; }
.btn-navy    { background:#1e3a8a; color:white; font-weight:700; border-radius:8px; }
"""


# משתנים גלובליים
LOGO_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logos_db.json")
class ChannelListWidget(QListWidget):
    """
    QListWidget עם Drag&Drop פנימי ושמירת סדר לערוצים.
    לא משנה לוגיקה קיימת. רק מוסיף התמדה של הסדר לאחר גרירה.
    """
    def __init__(self, editor_parent):
        super().__init__(editor_parent)
        self.editor = editor_parent

        # הפעלות גרירה פנימית
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)   # בחירה מרובה נוחה
        self.setDragDropMode(QAbstractItemView.InternalMove)         # גרירה פנימית
        self.setDragEnabled(True)                                    # לאפשר התחלת גרירה
        self.setAcceptDrops(True)                                    # לאפשר שחרור
        self.viewport().setAcceptDrops(True)                         # לוודא קבלה ב-viewport
        self.setDropIndicatorShown(True)                             # אינדיקטור ויזואלי
        self.setDefaultDropAction(Qt.MoveAction)                     # העברה ולא העתקה

    def dropEvent(self, event):
        # מבצע את ההזזה ב-UI
        super().dropEvent(event)
        # ואז שומר את הסדר החדש במבנה הנתונים
        try:
            self._persist_order_after_reorder()
        except Exception:
            pass

    def _persist_order_after_reorder(self):
        """
        קורא אחרי גרירה, מסיק את הסדר החדש מה-QListWidget,
        ומעדכן את self.editor.categories[הקטגוריה הנוכחית].
        שומר גם את הפריטים שלא היו מוצגים (אם סיננת) בסוף לפי סדרם המקורי.
        """
        # קטגוריה נוכחית במסך הראשי
        cat_item = self.editor.categoryList.currentItem() if hasattr(self.editor, "categoryList") else None
        if not cat_item:
            return

        cat_name_ui = cat_item.text().split(" (")[0].strip()
        real_cat = {k.strip(): k for k in self.editor.categories}.get(cat_name_ui)
        if not real_cat:
            return

        # בונים סדר חדש מה-UI לפריטים המוצגים
        visible_entries = []
        for i in range(self.count()):
            it = self.item(i)
            if it is None:
                continue
            entry = it.data(Qt.UserRole)
            if entry:
                visible_entries.append(entry)

        # הפריטים הנותרים שלא מוצגים כעת (בגלל חיפוש או פילטר) נשמרים בסוף
        existing = self.editor.categories.get(real_cat, [])
        visible_set = set(visible_entries)
        rest = [e for e in existing if e not in visible_set]

        # התמדה של סדר חדש
        self.editor.categories[real_cat] = visible_entries + rest

        # רענונים עדינים
        if hasattr(self.editor, "updateCategoryList"):
            self.editor.updateCategoryList()

        if hasattr(self.editor, "updateM3UContent"):
            try:
                self.editor.updateM3UContent()
            except Exception:
                pass
        elif hasattr(self.editor, "regenerateM3UTextOnly"):
            try:
                text = self.editor.regenerateM3UTextOnly()
                if hasattr(self.editor, "textEdit"):
                    self.editor.textEdit.setPlainText(text)
            except Exception:
                pass



def detect_stream_quality(entry: str) -> str:
    e = entry.lower()
    if '4k' in e:              return '4K'
    if '1080' in e:            return 'FHD'
    if '720' in e or re.search(r'\bhd\b', e): return 'HD'
    if '480' in e or re.search(r'\bsd\b', e): return 'SD'
    return 'Unknown'

# --- NEW: color helpers for quality tag ---
def _quality_tag_css(q: str) -> str:
    base = "border-radius:10px; padding:0 8px; font-size:11px; font-weight:700;"
    q = (q or "").upper()
    if q == "4K":   return base + "background:#22c55e; color:#ffffff;"   # ירוק
    if q == "FHD":  return base + "background:#3b82f6; color:#ffffff;"   # כחול
    if q == "HD":   return base + "background:#f59e0b; color:#111827;"   # כתום
    if q == "SD":   return base + "background:#ef4444; color:#ffffff;"   # אדום
    return base + "background:#9ca3af; color:#111827;"                   # אפור (Unknown)


# --- REPLACE existing create_channel_widget with this full version ---
def create_channel_widget(name: str, quality: str, logo_url: str = "", category: str = "", hidden: bool = False) -> QWidget:
    from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QPixmap

    w = QWidget(); w.setObjectName("Card")
    root = QHBoxLayout(w)
    root.setContentsMargins(8, 4, 8, 4)
    root.setSpacing(10)

    # logo
    logo = QLabel(); logo.setFixedSize(40, 40); logo.setAlignment(Qt.AlignCenter)
    loaded = False
    if logo_url:
        try:
            pix = QPixmap()
            if pix.load(logo_url):
                logo.setPixmap(pix.scaled(40, 40, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
                loaded = True
        except Exception:
            loaded = False
    if not loaded:
        logo.setStyleSheet("background:#e5e7eb; border-radius:6px; color:#374151; font-size:16px;")
        logo.setText("📺")
    root.addWidget(logo)

    col = QVBoxLayout(); col.setSpacing(0)

    title = QLabel(name)
    title.setObjectName("channel_label")
    title.setStyleSheet("color:#111827; font-weight:700; font-size:14px;")
    title.setWordWrap(False)
    col.addWidget(title)

    # tags row
    row = QHBoxLayout(); row.setSpacing(6)

    q_tag = QLabel(quality or "Unknown")
    q_tag.setObjectName("Tag")
    q_tag.setStyleSheet(_quality_tag_css(quality))
    row.addWidget(q_tag)

    if category:
        cat_tag = QLabel(category); cat_tag.setObjectName("Tag")
        cat_tag.setStyleSheet("border-radius:10px; padding:0 8px; font-size:11px; background:#e5e7eb; color:#111827;")
        row.addWidget(cat_tag)

    if hidden:
        hid = QLabel("מוסתר"); hid.setObjectName("Tag")
        hid.setStyleSheet("border-radius:10px; padding:0 8px; font-size:11px; background:#fee2e2; color:#991b1b;")
        row.addWidget(hid)

    row.addStretch(1)
    col.addLayout(row)
    root.addLayout(col)

    w.setFixedHeight(48)
    w.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    return w


class CategoryTranslateThread(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict, dict, str)  # updated_categories, mapping, mode

    def __init__(self, categories, mode):
        super().__init__()
        self.categories = categories
        self.mode = mode

    def run(self):
        import re
        from deep_translator import GoogleTranslator

        def clean(text):
            return re.sub(r'[\r\n\t\x00-\x1F]', '', text).strip()

        def is_hebrew(text):
            return any('\u0590' <= c <= '\u05EA' for c in text)

        def is_english(text):
            return all(ord(c) < 128 for c in text if c.isalpha())

        updated_categories = {}
        category_mapping = {}

        translator_en = GoogleTranslator(source='auto', target='en')
        translator_he = GoogleTranslator(source='auto', target='iw')

        total = len(self.categories)
        for i, (old_name, channels) in enumerate(self.categories.items()):
            parts = [p.strip() for p in old_name.split('|')]
            eng = next((clean(p) for p in parts if is_english(p)), None)
            heb = next((clean(p) for p in parts if is_hebrew(p)), None)

            try:
                if self.mode == "English Only":
                    final_base = eng or clean(translator_en.translate(parts[0]))
                elif self.mode == "Hebrew Only":
                    final_base = heb or clean(translator_he.translate(parts[0]))
                else:
                    if not eng:
                        eng = clean(translator_en.translate(parts[0]))
                    if not heb:
                        heb = clean(translator_he.translate(parts[0]))
                    final_base = f"{eng} | {heb}"
            except:
                final_base = old_name  # fallback

            # התיקון: בדיקה אם הקטגוריה המתורגמת כבר קיימת
            if final_base in updated_categories:
                # אם כבר קיימת - הוסף ערוצים לקטגוריה הקיימת
                updated_categories[final_base].extend(channels)
            else:
                # אם לא קיימת - צור קטגוריה חדשה
                updated_categories[final_base] = channels

            category_mapping[old_name] = final_base
            self.progress.emit(i + 1, old_name)

        self.finished.emit(updated_categories, category_mapping, self.mode)


class ChannelTranslateThread(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict, dict)

    _cache = {}

    def __init__(self, categories_dict):
        super().__init__()
        self.categories = categories_dict
        self.trans = GoogleTranslator(source='auto', target='en')

    @staticmethod
    def _is_english(txt):
        return all(ord(c) < 128 for c in txt if c.isalpha())

    def run(self):
        # אוספים את כל השמות שצריך לתרגם
        to_translate = set()
        for lst in self.categories.values():
            for entry in lst:
                name = entry.split(" (")[0].strip()
                if name and not self._is_english(name):
                    to_translate.add(name)

        # מסירים מה-cache
        todo = [n for n in to_translate if n not in ChannelTranslateThread._cache]
        for i in range(0, len(todo), 50):
            chunk = todo[i:i + 50]
            try:
                results = self.trans.translate_batch(chunk)
                for orig, tr in zip(chunk, results):
                    ChannelTranslateThread._cache[orig] = tr
            except:
                for orig in chunk:
                    ChannelTranslateThread._cache[orig] = orig

        # כעת מיישמים את התרגום
        new_cats = {}
        mapping = {}
        count = 0
        total = sum(len(v) for v in self.categories.values())

        for cat, lst in self.categories.items():
            new_list = []
            for entry in lst:
                if "(" in entry and entry.endswith(")"):
                    name, rest = entry.split(" (", 1)
                    url = rest[:-1]
                else:
                    name, url = entry, ""

                if self._is_english(name):
                    new_name = name
                else:
                    new_name = ChannelTranslateThread._cache.get(name, name)

                new_entry = f"{new_name} ({url})" if url else new_name
                new_list.append(new_entry)
                mapping[entry] = new_entry

                count += 1
                self.progress.emit(count, name)

            new_cats[cat] = new_list

        self.finished.emit(new_cats, mapping)


class MoveChannelsDialog(QDialog):
    def __init__(self, parent=None, categories=None):
        super().__init__(parent)
        self.setWindowTitle("Move Selected Channels")
        self.setMinimumWidth(400)
        self.categories = categories or []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        label1 = QLabel("בחר קטגוריה קיימת להעברה:")
        self.categoryCombo = QComboBox()
        self.categoryCombo.addItems(self.categories)

        label2 = QLabel("או הזן שם קטגוריה חדשה:")
        self.newCategoryInput = QLineEdit()
        self.newCategoryInput.setPlaceholderText("קטגוריה חדשה...")

        layout.addWidget(label1)
        layout.addWidget(self.categoryCombo)
        layout.addWidget(label2)
        layout.addWidget(self.newCategoryInput)

        buttonBox = QHBoxLayout()
        self.okButton = QPushButton("✔ OK")
        self.cancelButton = QPushButton("✖ ביטול")
        self.okButton.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        self.cancelButton.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.okButton.clicked.connect(self.onAcceptClicked)
        self.cancelButton.clicked.connect(self.reject)

        buttonBox.addWidget(self.okButton)
        buttonBox.addWidget(self.cancelButton)
        layout.addLayout(buttonBox)

        self.setLayout(layout)

    def getSelectedCategory(self):
        return self.newCategoryInput.text().strip() if self.newCategoryInput.text().strip() else self.categoryCombo.currentText()

    def onAcceptClicked(self):
        new_name = self.newCategoryInput.text().strip()
        if new_name and new_name in self.categories:
            QMessageBox.warning(
                self,
                "Category Exists",
                f"הקטגוריה '{new_name}' כבר קיימת. בחר שם אחר או השתמש בקיימת.",
            )
            return  # אל תסגור את החלון
        self.accept()


class ExportGroupsDialog(QDialog):
    def __init__(self, categories, parent=None):
        super(ExportGroupsDialog, self).__init__(parent)
        self.categories = categories
        self.parent = parent
        self.setupUI()

    def setupUI(self):
        self.setGeometry(100, 100, 500, 300)
        self.setWindowTitle("Export Groups")
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.setStyleSheet("QDialog { border: 8px solid red; background-color: white;}")

        # Export Selected Group
        self.exportSelectedButton = QPushButton("Export Selected Groups", self)
        self.exportSelectedButton.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.exportSelectedButton.clicked.connect(self.exportSelected)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        layout.addWidget(self.exportSelectedButton)

        # Export All Groups
        self.exportAllButton = QPushButton("Export All Groups", self)
        self.exportAllButton.setStyleSheet("background-color: black; color: white; font-weight: bold;")
        self.exportAllButton.clicked.connect(self.exportAll)
        layout.addWidget(self.exportAllButton)

        # חדש: Export Current View
        self.exportCurrentViewButton = QPushButton("Export Current View", self)
        self.exportCurrentViewButton.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        self.exportCurrentViewButton.clicked.connect(self.exportCurrentView)
        layout.addWidget(self.exportCurrentViewButton)

        self.setLayout(layout)

    def exportCurrentView(self):
        """
        מייצא קובץ M3U יחיד מהתצוגה הנוכחית במסך הראשי:
        הקטגוריה שנבחרה + הסינון הנוכחי + רק מה שמוצג כרגע ב-list.
        לא מוחק ולא מחליף פונקציות קיימות.
        """
        # דרישת קיום parent עם רשימות
        if not hasattr(self, "parent") or not hasattr(self.parent, "channelList"):
            QMessageBox.warning(self, "Export", "Parent or channel list not available.")
            return

        # בדיקה שיש פריטים מוצגים
        if self.parent.channelList.count() == 0:
            QMessageBox.information(self, "Export", "אין ערוצים מוצגים לייצוא.")
            return

        # קטגוריה נוכחית במסך הראשי
        if not hasattr(self.parent, "categoryList") or self.parent.categoryList.currentItem() is None:
            QMessageBox.warning(self, "Export", "לא נבחרה קטגוריה במסך הראשי.")
            return

        cat_name_ui = self.parent.categoryList.currentItem().text().split(" (")[0].strip()

        # בחירת תיקיה ויצירת שם קובץ ברירת מחדל
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if not directory:
            return

        import os
        safe_category = "".join(c for c in cat_name_ui if c.isalnum() or c in " _-").rstrip()
        file_path = os.path.join(directory, f"{safe_category}_current.m3u")

        try:
            with open(file_path, "w", encoding="utf-8", newline="\n") as f:
                f.write("#EXTM3U\n")
                for i in range(self.parent.channelList.count()):
                    it = self.parent.channelList.item(i)
                    entry = it.data(Qt.UserRole) if it is not None else None
                    if not entry:
                        continue

                    name = entry.split(" (")[0].strip() if isinstance(entry, str) else str(entry)
                    url = self.parent.getUrl(entry) if hasattr(self.parent, "getUrl") else ""
                    if not url:
                        continue

                    extinf_line = self._build_extinf_with_logo_and_group(entry, name, cat_name_ui)
                    f.write(f"{extinf_line}\n{url}\n")

            QMessageBox.information(self, "Export", f"נוצר קובץ: {file_path}")
            self.show_toast("הייצוא הושלם", "success")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"שגיאה בייצוא: {e}")

    def _build_extinf_with_logo_and_group(self, entry, name, category):
        """
        בונה שורת EXTINF עם group-title ולוגו אם יש ב-logo_cache של ההורה.
        שימוש ב-extinf_lookup אם קיים, עם הזרקת group-title ו-tvg-logo במידת הצורך.
        """
        # extinf מתוך lookup לפי entry, ואם אין אז לפי name, ואם אין - נבנה מינימלי
        extinf = ""
        if hasattr(self, "parent") and hasattr(self.parent, "extinf_lookup"):
            extinf = self.parent.extinf_lookup.get(entry) or self.parent.extinf_lookup.get(name) or ""

        # לוגו מתוך cache
        logo_url = ""
        if hasattr(self, "parent") and hasattr(self.parent, "logo_cache"):
            v = self.parent.logo_cache.get(name)
            if isinstance(v, list) and v:
                logo_url = v[0]
            elif isinstance(v, str):
                logo_url = v

        if not extinf:
            # מינימלי
            if logo_url:
                return f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="{category}",{name}'
            return f'#EXTINF:-1 group-title="{category}",{name}'

        # אם קיים extinf, מבטיחים שיש בו פסיק, ואז מזריקים מאפיינים חסרים
        if "," not in extinf:
            # extinf לא תקין, נבנה חדש
            if logo_url:
                return f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="{category}",{name}'
            return f'#EXTINF:-1 group-title="{category}",{name}'

        props, old_name = extinf.split(",", 1)

        if 'group-title="' not in props:
            props += f' group-title="{category}"'
        if logo_url and 'tvg-logo="' not in props:
            props += f' tvg-logo="{logo_url}"'

        # שם הערוץ נעדיף את name הנוכחי שמופיע במסך
        return f"{props},{name}"

    def exportSelected(self):
        selectedCategory, ok = QInputDialog.getItem(self, "Select Group", "Choose a group to export:",
                                                    list(self.categories.keys()), 0, False)
        if ok and selectedCategory:
            directory = QFileDialog.getExistingDirectory(self, "Select Directory")
            if directory:
                self.exportGroup(selectedCategory, directory)
                pass

    def exportAll(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            for category in self.categories.keys():
                self.exportGroup(category, directory)
                pass

    def exportGroup(self, category, directory):
        safe_category = "".join(c for c in category if c.isalnum() or c in " _-").rstrip()
        file_path = os.path.join(directory, f"{safe_category}.m3u")

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write("#EXTM3U\n")
                for channel in self.categories[category]:
                    extinf_line = self.parent.extinf_lookup.get(channel) or ""
                    if not extinf_line:
                        name = channel.split(" (")[0].strip()
                        extinf_line = f'#EXTINF:-1 group-title="{category}",{name}'
                    elif 'group-title="' not in extinf_line:
                        props, name = extinf_line.split(",", 1)
                        extinf_line = f'{props} group-title="{category}",{name}'

                    url = self.parent.getUrl(channel)
                    file.write(f"{extinf_line}\n{url}\n")
                    self.show_toast(f"נוצר {os.path.basename(file_path)}", "success", 1500)


        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export {category}: {e}")


class M3UUrlConverterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("M3U URL Converter")
        self.setGeometry(100, 200, 600, 300)  # Adjust size as needed
        layout = QVBoxLayout(self)
        layout.setSpacing(10)  # Adjust spacing between widgets

        # Add Minimize, Maximize, and Close Buttons
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        # Styling the dialog frame and background
        self.setStyleSheet("QDialog { border: 5px solid red; background-color: white;}")

        # Input fields setup
        self.hostInput = QLineEdit(self)
        self.usernameInput = QLineEdit(self)
        self.passwordInput = QLineEdit(self)

        # ⏩ מעבר אוטומטי לשדה הבא בלחיצה על Enter
        self.hostInput.returnPressed.connect(lambda: self.usernameInput.setFocus())
        self.usernameInput.returnPressed.connect(lambda: self.passwordInput.setFocus())
        self.passwordInput.returnPressed.connect(lambda: self.convertButton.setFocus())

        # Convert button
        self.convertButton = QPushButton("Convert to M3U URL", self)
        self.convertButton.setStyleSheet("background-color: black; color: white; font-weight: bold;")
        self.convertButton.clicked.connect(self.convertToM3U)
        layout.addWidget(self.convertButton)

        # Download button
        self.downloadButton = QPushButton("Download M3U", self)
        self.downloadButton.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.downloadButton.clicked.connect(self.downloadOriginalM3U)
        layout.addWidget(self.downloadButton)

        # Result display
        self.resultLabel = QLabel("", self)
        layout.addWidget(self.resultLabel)
        self.copyButton = QPushButton("Copy Result", self)
        self.copyButton.setStyleSheet("background-color: black; color: white; font-weight: bold;")
        self.copyButton.clicked.connect(self.copyResultToClipboard)
        layout.addWidget(self.copyButton)

        # Labels and Inputs

        usernameLabel = QLabel("Username:", self)
        passwordLabel = QLabel("Password:", self)
        hostLabel = QLabel("Host (e.g., example.com:8080):", self)

        layout.addWidget(hostLabel)
        layout.addWidget(self.hostInput)
        layout.addWidget(usernameLabel)
        layout.addWidget(self.usernameInput)
        layout.addWidget(passwordLabel)
        layout.addWidget(self.passwordInput)

        self.setLayout(layout)

    def convertToM3U(self):
        import requests
        from urllib.parse import urlparse
        from PyQt5.QtWidgets import QMessageBox

        host_raw = self.hostInput.text().strip()
        username = self.usernameInput.text().strip()
        password = self.passwordInput.text().strip()

        if not (host_raw and username and password):
            QMessageBox.warning(self, "שגיאה", "נא למלא Host, Username ו-Password")
            return

        tmp = host_raw if host_raw.startswith(("http://", "https://")) else "http://" + host_raw
        parsed = urlparse(tmp)
        host_only = parsed.hostname
        given_port = parsed.port

        ports = ([given_port] if given_port else []) + [8080, 80, None]
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "*/*",
        })

        found = None
        for scheme in ("http", "https"):
            for port in ports:
                netloc = f"{host_only}:{port}" if port else host_only
                # ← החלפנו את הסדר: קודם m3u_plus
                for t in ("m3u_plus", "m3u"):
                    url = f"{scheme}://{netloc}/get.php?username={username}&password={password}&type={t}"
                    try:
                        resp = session.get(url, timeout=5, allow_redirects=True)
                        print(f"בדיקה: {url} → {resp.status_code}")
                        if resp.status_code < 400:
                            found = url
                            break
                    except requests.RequestException:
                        continue
                if found:
                    break
            if found:
                break

        if not found:
            QMessageBox.critical(self, "שגיאה", "לא נמצא URL תקין – בדוק Host ונסה שוב")
            self.copyButton.hide()
            self.downloadButton.hide()
            return

        self.m3uURL = found
        self.resultLabel.setText(found)
        self.copyButton.show()
        self.downloadButton.show()

    def copyResultToClipboard(self):
        import pyperclip
        from PyQt5.QtWidgets import QMessageBox

        if hasattr(self, "m3uURL"):
            pyperclip.copy(self.m3uURL)
            QMessageBox.information(self, "Copied", "M3U URL copied to clipboard.")
        else:
            QMessageBox.warning(self, "No URL", "Nothing to copy.")

    def downloadM3U(self):
        try:
            if not hasattr(self, 'm3uURL') or not self.m3uURL:
                QMessageBox.warning(self, "Missing URL", "Please generate a valid M3U URL first.")
                return

            # Headers חשובים – יש שרתים שלא עובדים בלי User-Agent
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "*/*"
            }

            session = setup_session()  # ← שורה חדשה לשיפור
            response = session.get(self.m3uURL, headers=headers, timeout=10)  # ← שימוש בשיפור
            response.raise_for_status()  # מרים שגיאה אם הקובץ לא ירד תקין

            # בדיקת תוכן
            content = response.text.strip()
            if not content.startswith("#EXTM3U"):
                QMessageBox.critical(self, "Invalid File", "Downloaded file is not a valid M3U playlist.")
                return

            # בחירת מיקום שמירה
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getSaveFileName(
                self, "Save M3U File", "playlist.m3u",
                "M3U Files (*.m3u);;All Files (*)", options=options
            )
            if fileName:
                with open(fileName, 'w', encoding='utf-8') as f:
                    f.write(content)
                QMessageBox.information(self, "Success", "The M3U file has been downloaded successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download M3U file:\n\n{str(e)}")

    def downloadOriginalM3U(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        import requests

        if not hasattr(self, 'm3uURL') or not self.m3uURL:
            QMessageBox.warning(self, "Missing URL", "Please generate a valid M3U URL first.")
            return

        # session עם כותרות של דפדפן
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "*/*",
        })

        try:
            resp = session.get(self.m3uURL, stream=True, timeout=15, allow_redirects=True)
            resp.raise_for_status()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download M3U:\n{e}")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Original M3U File",
            "playlist_original.m3u",
            "M3U Files (*.m3u);;All Files (*)"
        )
        if not path:
            return

        try:
            with open(path, "wb") as f:
                for chunk in resp.iter_content(8 * 1024):
                    f.write(chunk)
            QMessageBox.information(self, "Success", "Original M3U file saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")


class SmartScanDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Scan")
        self.setGeometry(300, 300, 300, 150)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        label = QLabel("Choose scan type:", self)
        layout.addWidget(label)

        self.categoryScanButton = QPushButton("Scan Current Category", self)
        self.allScanButton = QPushButton("Scan All Categories", self)

        layout.addWidget(self.categoryScanButton)
        layout.addWidget(self.allScanButton)


class SmartScanThread(QThread):
    progress = pyqtSignal(int, int, int, tuple)
    finished = pyqtSignal()

    def __init__(self, channels, duplicate_names=None):  # הפוך את duplicate_names לאופציונלי
        super().__init__()
        self.channels = channels
        self.duplicate_names = duplicate_names if duplicate_names is not None else set()
        self.stop_requested = False

    def run(self):
        checked = offline = duplicate = 0
        headers = {
            "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko)",
            "Accept": "*/*",
            "Connection": "close"
        }
        for name, url in self.channels:
            if self.stop_requested:
                # מחכים רגע קטן לפני יציאה כדי לא לקרוע סיגנלים באמצע
                time.sleep(0.05)
                break
            status = "Offline";
            reason = "Unknown"
            try:
                res = requests.get(url, headers=headers, stream=True, timeout=4)
                if res.status_code < 400 and any(x in res.text.lower() for x in ["#extm3u", ".ts", ".mp4", ".m3u8"]):
                    status = "Online";
                    reason = "OK"
                    # כאן תוכלו להוסיף בדיקות נוספות dup וכו׳
                else:
                    reason = f"HTTP {res.status_code}"
            except Exception as e:
                reason = str(e)
            checked += 1
            if status == "Offline":
                offline += 1
            # שידור עדכון
            self.progress.emit(checked, offline, duplicate, (name, url, status, reason))
        self.finished.emit()

    def stop(self):
        self.stop_requested = True


class URLCheckThread(QThread):
    progress_signal = pyqtSignal(int, int, int, tuple)
    finished_signal = pyqtSignal()

    def __init__(self, channels):
        super().__init__()
        self.channels = channels
        self.stop_requested = False

    def run(self):
        online, offline, checked = 0, 0, 0

        headers = {
            "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko)",
            "Accept": "*/*",
            "Connection": "close"
        }

        for name, url in self.channels:
            if self.stop_requested:
                break
                time.sleep(0.05)

            status = "Offline"
            reason = "Unknown"

            try:
                # שימוש ב-GET עם stream כדי לדמות נגן אמיתי
                res = requests.get(url, headers=headers, stream=True, timeout=4)

                if res.status_code < 400:
                    if "#EXTM3U" in res.text or url.endswith((".ts", ".m3u8", ".mp4", ".mp3", ".aac", ".mpd")):
                        status = "Online"
                        reason = ""
                        online += 1
                    else:
                        reason = "Invalid Stream Content"
                else:
                    reason = f"HTTP {res.status_code}"

            except requests.exceptions.Timeout:
                reason = "Timeout"
            except requests.exceptions.ConnectionError:
                reason = "Connection Error"
            except Exception as e:
                reason = str(e)

            if status == "Offline":
                offline += 1

            checked += 1
            parsed_url = urlparse(url)
            server = parsed_url.hostname or "Unknown"

            self.progress_signal.emit(checked, online, offline, (name, status, server, url))

        self.finished_signal.emit()

    def stop(self):
        self.stop_requested = True


class URLCheckerDialog(QDialog):
    def __init__(self, channels, channel_category_mapping, parent=None):
        super().__init__(parent)
        self.channels = channels
        self.channel_category_mapping = channel_category_mapping  # שמירת המידע
        self.results = []
        self.thread = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("URL Checker")
        self.setGeometry(150, 150, 1000, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        self.setStyleSheet("""
            QDialog {
                border: 5px solid red;
                background-color: white;
            }
        """)

        # Status summary layout
        summaryLayout = QHBoxLayout()

        self.checkedLabel = QLabel("Checked\n0", self)
        self.onlineLabel = QLabel("Online\n0", self)
        self.offlineLabel = QLabel("Offline\n0", self)

        for label in [self.checkedLabel, self.onlineLabel, self.offlineLabel]:
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(
                "font-size: 24px; background-color: #6A1B9A; color: white; padddef removeOfflineChannels(self, offline_channel_names):def removeOfflineChannels(self, offline_channel_names):ing: 20px; border-radius: 5px;")
            summaryLayout.addWidget(label)

        layout.addLayout(summaryLayout)

        self.statusLine = QLabel("Status: Waiting", self)
        layout.addWidget(self.statusLine)

        controlLayout = QHBoxLayout()

        self.channelCountLabel = QLabel(f"Channels Count: {len(self.channels)}", self)
        controlLayout.addWidget(self.channelCountLabel)

        self.searchInput = QLineEdit(self)
        self.searchInput.setPlaceholderText("Search Channels...")
        self.searchInput.textChanged.connect(self.updateFilter)
        controlLayout.addWidget(self.searchInput)

        self.statusFilter = QComboBox(self)
        self.statusFilter.addItems(["All", "Online", "Offline"])
        self.statusFilter.currentIndexChanged.connect(self.updateFilter)
        controlLayout.addWidget(self.statusFilter)

        layout.addLayout(controlLayout)

        self.channelTable = QTableWidget(self)
        self.channelTable.setColumnCount(5)
        self.channelTable.setHorizontalHeaderLabels(["Channel Name", "Category", "Status", "Server", "URL"])
        header = self.channelTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.channelTable)

        buttonsLayout = QHBoxLayout()

        self.checkBtn = QPushButton("Check URLs", self)
        self.checkBtn.setStyleSheet("background-color: purple; color: white; font-size: 16px; padding: 10px;")
        self.checkBtn.clicked.connect(self.startChecking)
        buttonsLayout.addWidget(self.checkBtn)

        self.stopBtn = QPushButton("Stop Checking", self)
        self.stopBtn.setStyleSheet("background-color: purple; color: white; font-size: 16px; padding: 10px;")
        self.stopBtn.clicked.connect(self.stopChecking)
        self.stopBtn.setEnabled(False)
        buttonsLayout.addWidget(self.stopBtn)

        layout.addLayout(buttonsLayout)

        self.selectOfflineBtn = QPushButton("Select Offline Channels", self)
        self.selectOfflineBtn.setStyleSheet(
            "background-color: purple; color: white; font-size: 16px; padding: 10px;"
        )
        self.selectOfflineBtn.clicked.connect(self.selectOfflineChannels)
        buttonsLayout.addWidget(self.selectOfflineBtn)

    def selectOfflineChannels(self):
        offline_channels = []

        # Clear previous selection in URL checker table
        self.channelTable.clearSelection()

        # Collect offline channels
        for row in range(self.channelTable.rowCount()):
            status_item = self.channelTable.item(row, 2)  # Status נמצא בעמודה 2
            if status_item.text().lower() == 'offline':
                channel_name = self.channelTable.item(row, 0).text()
                url = self.channelTable.item(row, 4).text().strip()
                offline_channels.append((channel_name.strip(), url))
                self.channelTable.selectRow(row)

        if not offline_channels:
            QMessageBox.information(
                self, "No Offline Channels",
                "There are no offline channels to select."
            )
            return

        # Call parent method to select these offline channels in main list
        if hasattr(self.parent(), 'selectChannelsByNames'):
            self.parent().selectChannelsByNameAndUrl(set(offline_channels))
            QMessageBox.information(
                self, "Offline Channels Selected",
                f"{len(offline_channels)} offline channels have been selected both here and in the main list."
            )
        else:
            QMessageBox.warning(
                self, "Selection Failed",
                "Could not find main editor method to select channels."
            )

    def startChecking(self):
        self.results.clear()
        self.channelTable.setRowCount(0)
        self.checkBtn.setEnabled(False)
        self.stopBtn.setEnabled(True)
        self.statusLine.setText("Status: Checking URLs...")

        self.thread = URLCheckThread(self.channels)
        self.thread.progress_signal.connect(self.updateProgress)
        self.thread.finished_signal.connect(self.checkingFinished)
        self.thread.start()

    def updateProgress(self, checked, online, offline, data):
        name, status, server, url = data
        self.results.append(data)
        self.addChannelToTable(name, status, server, url)
        self.checkedLabel.setText(f"Checked\n{checked}")
        self.onlineLabel.setText(f"Online\n{online}")
        self.offlineLabel.setText(f"Offline\n{offline}")
        self.statusLine.setText(f"Checking: {name}")

    def checkingFinished(self):
        self.checkBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)
        self.statusLine.setText("Status: Finished")

    def stopChecking(self):
        if self.thread:
            self.thread.stop()
            self.statusLine.setText("Status: Stopping...")

    def getCategoryByChannelName(self, channel_name):
        return self.channel_category_mapping.get(channel_name.lower().strip(), "Unknown")

    def addChannelToTable(self, name, status, server, url):
        row_position = self.channelTable.rowCount()
        self.channelTable.insertRow(row_position)

        category_name = self.getCategoryByChannelName(name)

        data_columns = [name, category_name, status, server, url]

        for col, data in enumerate(data_columns):
            item = QTableWidgetItem(data)
            if col == 2:  # Status
                item.setBackground(Qt.green if status == "Online" else Qt.red)
            else:
                item.setBackground(Qt.white)
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.channelTable.setItem(row_position, col, item)

    def updateFilter(self):
        search_text = self.searchInput.text().lower()
        status_filter = self.statusFilter.currentText()

        self.channelTable.setRowCount(0)

        for name, status, server, url in self.results:
            if (search_text in name.lower()) and (status_filter in [status, "All"]):
                self.addChannelToTable(name, status, server, url)


class SmartScanStatusDialog(QDialog):
    def __init__(self, channels, duplicates, parent=None):
        super().__init__(parent)

        # משתני אתחול חיוניים
        self.scan_results = []
        self.thread = None
        self._is_closing = False
        self.duplicates = duplicates if duplicates else []

        # Debug info
        print(f"[Init] Starting with {len(channels) if channels else 0} channels")
        print(f"[Init] Parent exists: {parent is not None}")
        print(f"[Init] Parent has categories: {hasattr(parent, 'categories') if parent else False}")

        # בדיקת תקינות נתונים משופרת
        if not channels or not isinstance(channels, (list, tuple)):
            # נסה לקבל channels מה-parent
            if parent and hasattr(parent, 'channels'):
                channels = parent.channels
                print(f"[Init] Retrieved {len(channels)} channels from parent")
            else:
                QMessageBox.warning(None, "Error", "No channels data available for scanning.")
                self.reject()
                return

        # שמור את הערוצים המקוריים
        original_channels = channels.copy()

        try:
            # בחירת אופן הסריקה
            scan_choice = self._showScanChoiceDialog()
            if scan_choice is None:
                self.reject()
                return

            # אם נבחרה קטגוריה ספציפית
            if scan_choice == "category":
                selected_category = self._showCategorySelectionDialog()
                if selected_category is None:
                    self.reject()
                    return

                print(f"[Init] Selected category: '{selected_category}'")

                # סנן ערוצים לפי הקטגוריה
                filtered_channels = self._filterChannelsByCategory(channels, selected_category)

                if not filtered_channels:
                    reply = QMessageBox.question(
                        self,
                        "No Channels Found",
                        f"No channels found in category: '{selected_category}'\n\n"
                        "This might happen if channel names don't match exactly.\n\n"
                        "Would you like to scan ALL channels instead?",
                        QMessageBox.Yes | QMessageBox.No
                    )

                    if reply == QMessageBox.Yes:
                        print("[Init] User chose to scan all channels instead")
                        channels = original_channels
                    else:
                        self.reject()
                        return
                else:
                    channels = filtered_channels
                    print(f"[Init] Using {len(channels)} filtered channels")

        except Exception as e:
            print(f"[Dialog Setup Error] {e}")
            import traceback
            traceback.print_exc()

            reply = QMessageBox.question(
                self,
                "Setup Error",
                f"Error during setup: {str(e)}\n\nWould you like to continue with scanning all channels?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply != QMessageBox.Yes:
                self.reject()
                return
            channels = original_channels

        # שמור את הערוצים הסופיים
        self.channels = channels

        # הגדרת החלון
        self.setWindowTitle("Smart Scan In Progress")
        self.resize(900, 500)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        # עיצוב מהיר ויעיל
        self.setStyleSheet(self._getOptimizedStyleSheet())

        # cache צבעים לביצועים מהירים
        self._color_cache = {
            'offline': QColor("#ffebee"),
            'duplicate': QColor("#fff3e0"),
            'online': QColor("#e8f5e8"),
            'white': QColor("white")
        }

        # בניית ה-UI
        self._buildUI()

        # התחל סריקה
        self._startScanning()

    def _getOptimizedStyleSheet(self):
        """StyleSheet מהיר ומאופטם"""
        return """
            QDialog { 
                border: 3px solid #2196F3; 
                background-color: #f0f8ff;
                border-radius: 10px;
            }
            QLabel { 
                color: #1976D2; 
                font-weight: bold;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton#stopBtn {
                background-color: #f44336;
            }
            QPushButton#markBtn {
                background-color: #ff9800;
            }
            QProgressBar {
                border: 2px solid #2196F3;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QTableWidget {
                border: 2px solid #2196F3;
                border-radius: 5px;
                gridline-color: #E0E0E0;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """

    def _buildUI(self):
        """בניית ממשק משתמש מהיר"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # כותרת
        title_label = QLabel("🔍 Smart Channel Scanner")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2;")
        layout.addWidget(title_label)

        # סטטיסטיקות
        self.labelStats = QLabel("Initializing scan...")
        self.labelStats.setStyleSheet("font-size: 14px; font-weight: bold; color: #1976D2; padding: 5px;")
        layout.addWidget(self.labelStats)

        # פס התקדמות
        self.progressBar = QProgressBar(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(len(self.channels))
        self.progressBar.setValue(0)
        layout.addWidget(self.progressBar)

        # סינון
        filter_layout = QHBoxLayout()
        filter_layout.setAlignment(Qt.AlignRight)

        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet("font-size: 12px; color: #1976D2;")

        self.filterCombo = QComboBox()
        self.filterCombo.setFixedWidth(120)
        self.filterCombo.addItems(["All", "Online", "Offline", "Duplicate"])
        self.filterCombo.currentIndexChanged.connect(self.applyFilter)

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filterCombo)
        layout.addLayout(filter_layout)

        # טבלה מהירה
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Channel", "Status", "Reason", "URL"])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)

        # כפתורים
        btnLayout = QHBoxLayout()

        self.stopBtn = QPushButton("Stop Scan")
        self.stopBtn.setObjectName("stopBtn")
        self.stopBtn.clicked.connect(self.stopScan)
        btnLayout.addWidget(self.stopBtn)

        self.markBtn = QPushButton("Mark Channels (Duplicates + Offline)")
        self.markBtn.setObjectName("markBtn")
        self.markBtn.clicked.connect(self.markProblematicChannels)
        btnLayout.addWidget(self.markBtn)

        layout.addLayout(btnLayout)

    def _normalizeChannels(self, channels):
        """
        ממיר רשימות ערוצים לפורמט אחיד של [(name, url)].
        תומך ב:
        - רשימה של tuples/list: (name, url)
        - רשימה של מחרוזות בפורמט "Name (URL)"
        - מתעלם מפריטים שלא ניתן לחלץ מהם URL תקין
        - מסיר כפילויות זהות בדיוק, תוך שמירה על סדר
        """
        normalized = []

        for ch in channels:
            try:
                name = None
                url = None

                # פורמט [(name, url)] או [name, url]
                if isinstance(ch, (list, tuple)) and len(ch) >= 2:
                    name = str(ch[0]).strip()
                    url = str(ch[1]).strip()

                # פורמט "Name (URL)"
                elif isinstance(ch, str):
                    s = ch.strip()
                    if " (" in s and s.endswith(")"):
                        # rsplit כדי לא לשבור שמות שמכילים "("
                        name_part, rest = s.rsplit(" (", 1)
                        name = name_part.strip()
                        url = rest[:-1].strip()  # הסרת ')'
                    else:
                        # אם זו מחרוזת שלא בפורמט "Name (URL)"
                        # נוודא שלפחות יש URL. אם אין - נדלג.
                        if s.lower().startswith(("http://", "https://")):
                            name = s  # שם זמני זהה ל־URL
                            url = s

                # ולידציית URL בסיסית
                if not url or not url.lower().startswith(("http://", "https://")):
                    continue

                # שם ברירת מחדל אם חסר
                if not name:
                    name = url

                normalized.append((name, url))

            except Exception:
                # פריט בעייתי - מדלגים
                continue

        # הסרת כפילויות זהות בדיוק תוך שמירה על הסדר
        seen = set()
        result = []
        for name, url in normalized:
            key = (name, url)
            if key in seen:
                continue
            seen.add(key)
            result.append((name, url))

        return result

    def _startScanning(self):
        """התחל את תהליך הסריקה"""
        if not self.channels:
            QMessageBox.warning(self, "Error", "No channels to scan.")
            self.reject()
            return

        try:
            # צור את ה-thread עם הערוצים (בלי duplicate_names סטטי)
            self.thread = SmartScanThread(self.channels, self.duplicates)

            # חבר את הסיגנלים
            self.thread.progress.connect(self.updateProgress)
            self.thread.finished.connect(self.scanFinished)

            # התחל את הסריקה
            self.thread.start()

            # הפעל טיימר לעדכון תצוגה
            if hasattr(self, 'timer'):
                self.timer.start(100)  # עדכון כל 100ms

        except Exception as e:
            print(f"[Scan Start Error] {e}")
            QMessageBox.critical(self, "Error", f"Failed to start scanning: {str(e)}")
            self.reject()

    def _showScanChoiceDialog(self):
        """חלון בחירת סריקה מהיר"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Choose Scan Type")
            dialog.setFixedSize(350, 150)
            dialog.setModal(True)

            layout = QVBoxLayout(dialog)

            title = QLabel("Select scanning method:")
            title.setStyleSheet("font-size: 16px; font-weight: bold;")
            layout.addWidget(title)

            btn_layout = QVBoxLayout()

            category_btn = QPushButton("Scan Specific Category")
            category_btn.clicked.connect(lambda: dialog.done(1))
            btn_layout.addWidget(category_btn)

            all_btn = QPushButton("Scan All Channels")
            all_btn.clicked.connect(lambda: dialog.done(2))
            btn_layout.addWidget(all_btn)

            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(lambda: dialog.done(0))
            btn_layout.addWidget(cancel_btn)

            layout.addLayout(btn_layout)

            result = dialog.exec_()
            if result == 1:
                return "category"
            elif result == 2:
                return "all"
            return None
        except Exception as e:
            print(f"[Scan Choice Dialog Error] {e}")
            return "all"

    def _showCategorySelectionDialog(self):
        """חלון בחירת קטגוריה מהיר ומשופר"""
        try:
            if not self.parent() or not hasattr(self.parent(), 'categories'):
                QMessageBox.warning(self, "No Categories", "No categories available.")
                return None

            categories = getattr(self.parent(), 'categories', {})
            if not categories:
                QMessageBox.warning(self, "No Categories", "No categories found.")
                return None

            dialog = QDialog(self)
            dialog.setWindowTitle("Select Category")
            dialog.setFixedSize(400, 300)
            dialog.setModal(True)

            layout = QVBoxLayout(dialog)

            title = QLabel("Choose category to scan:")
            title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
            layout.addWidget(title)

            # רשימה עם מידע
            category_list = QListWidget()
            category_list.setStyleSheet("font-size: 12px;")

            for category_name in sorted(categories.keys()):
                channel_count = len(categories[category_name])
                display_text = f"{category_name} ({channel_count} channels)"
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, category_name)
                category_list.addItem(item)

            # בחר את הפריט הראשון כברירת מחדל
            if category_list.count() > 0:
                category_list.setCurrentRow(0)

            layout.addWidget(category_list)

            info_label = QLabel("Select a category to scan only its channels")
            info_label.setStyleSheet("font-size: 10px; color: #666; margin-top: 5px;")
            layout.addWidget(info_label)

            btn_layout = QHBoxLayout()
            ok_btn = QPushButton("Select")
            ok_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 15px;")
            ok_btn.clicked.connect(lambda: dialog.accept())

            cancel_btn = QPushButton("Cancel")
            cancel_btn.setStyleSheet("background-color: #f44336; color: white; padding: 5px 15px;")
            cancel_btn.clicked.connect(lambda: dialog.reject())

            btn_layout.addWidget(ok_btn)
            btn_layout.addWidget(cancel_btn)
            layout.addLayout(btn_layout)

            if dialog.exec_() == QDialog.Accepted:
                current_item = category_list.currentItem()
                if current_item:
                    return current_item.data(Qt.UserRole)
            return None

        except Exception as e:
            print(f"[Category Selection Error] {e}")
            import traceback
            traceback.print_exc()
            return None

    def _filterChannelsByCategory(self, channels, selected_category):
        """סינון ערוצים אולטרה-מהיר עם אלגוריתם משופר"""
        try:
            if not self.parent() or not hasattr(self.parent(), 'categories'):
                print(f"[Filter] No parent or categories found")
                return channels

            categories = getattr(self.parent(), 'categories', {})
            category_channels = categories.get(selected_category, [])

            if not category_channels:
                print(f"[Filter] No channels in category: {selected_category}")
                return []

            print(f"[Filter] Category '{selected_category}' has {len(category_channels)} channels")

            # יצירת מילון לחיפוש מהיר O(1)
            category_names_dict = {}

            for ch in category_channels:
                try:
                    # נרמול השם
                    normalized = ch.strip().lower()
                    category_names_dict[normalized] = ch

                    # אם יש סוגריים, הוסף גם את השם בלעדיהם
                    if ' (' in ch:
                        base_name = ch.split(' (')[0].strip().lower()
                        category_names_dict[base_name] = ch

                except Exception as e:
                    print(f"[Filter] Error processing category channel '{ch}': {e}")
                    continue

            print(f"[Filter] Created lookup dict with {len(category_names_dict)} entries")

            # סינון מהיר עם lookup
            filtered = []
            seen = set()  # למניעת כפילויות

            for channel in channels:
                try:
                    channel_lower = channel.strip().lower()

                    # בדיקה מהירה במילון
                    if channel_lower in category_names_dict:
                        if channel not in seen:
                            filtered.append(channel)
                            seen.add(channel)
                        continue

                    # בדיקת שם בסיס
                    if ' (' in channel:
                        base_name = channel.split(' (')[0].strip().lower()
                        if base_name in category_names_dict:
                            if channel not in seen:
                                filtered.append(channel)
                                seen.add(channel)
                            continue

                    # חיפוש חלקי רק אם נדרש
                    for cat_key in category_names_dict:
                        if cat_key in channel_lower or channel_lower in cat_key:
                            if channel not in seen:
                                filtered.append(channel)
                                seen.add(channel)
                            break

                except Exception as e:
                    print(f"[Filter] Error processing channel '{channel}': {e}")
                    continue

            print(f"[Filter] Filtered result: {len(filtered)} unique channels matched")

            # אם לא נמצאו התאמות, החזר את ערוצי הקטגוריה בפורמט הנכון
            if not filtered and category_channels:
                print("[Filter] No matches found, converting category channels to tuples")
                # המרה לפורמט של tuples
                converted = []
                for ch in category_channels:
                    try:
                        if " (" in ch and ch.endswith(")"):
                            name = ch.split(" (")[0].strip()
                            url = ch.split(" (", 1)[1].rstrip(")")
                            converted.append((name, url))
                        else:
                            # אם הפורמט לא מוכר, נדלג
                            print(f"[Filter] Skipping invalid format: {ch}")
                    except Exception as e:
                        print(f"[Filter] Error converting channel: {e}")
                        continue
                return converted if converted else channels  # החזר את המקורי אם ההמרה נכשלה

            return filtered

        except Exception as e:
            print(f"[Filter Channels Error] {e}")
            import traceback
            traceback.print_exc()
            return channels

    def updateProgress(self, checked, offline, duplicate, data):
        """עדכון התקדמות אולטרה-מהיר"""
        try:
            if self._is_closing:
                return

            name, url, status, reason = data
            total = self.progressBar.maximum()
            problematic = offline + duplicate

            # עדכון טקסט
            self.labelStats.setText(
                f"Scanned: {checked}/{total} | Offline: {offline} | Duplicates: {duplicate} | Issues: {problematic}"
            )

            # עדכון פס התקדמות
            self.progressBar.setValue(checked)

            # שמירת תוצאה
            self.scan_results.append((name, status, reason, url))

            # הוספה לטבלה
            self._addTableRow(name, status, reason, url)

        except Exception as e:
            print(f"[Update Progress Error] {e}")

    def _addTableRow(self, name, status, reason, url):
        """הוספת שורה מהירה לטבלה"""
        try:
            if self._is_closing:
                return

            row = self.table.rowCount()
            self.table.insertRow(row)

            # הוספת פריטים
            self.table.setItem(row, 0, QTableWidgetItem(str(name)))

            status_item = QTableWidgetItem(str(status))

            # צביעה מהירה
            status_lower = str(status).lower()
            if "offline" in status_lower:
                status_item.setBackground(self._color_cache['offline'])
            elif "duplicate" in str(reason).lower():
                status_item.setBackground(self._color_cache['duplicate'])
            else:
                status_item.setBackground(self._color_cache['online'])

            self.table.setItem(row, 1, status_item)
            self.table.setItem(row, 2, QTableWidgetItem(str(reason)))
            self.table.setItem(row, 3, QTableWidgetItem(str(url)))

        except Exception as e:
            print(f"[Add Table Row Error] {e}")

    def refreshTable(self):
        """רענון טבלה מהיר"""
        try:
            if self._is_closing:
                return

            self.table.setRowCount(0)
            selected_filter = self.filterCombo.currentText().lower()

            for name, status, reason, url in self.scan_results:
                should_show = True

                if selected_filter != "all":
                    status_lower = status.lower()
                    reason_lower = reason.lower()

                    if selected_filter == "online" and "offline" in status_lower:
                        should_show = False
                    elif selected_filter == "offline" and "offline" not in status_lower:
                        should_show = False
                    elif selected_filter == "duplicate" and "duplicate" not in reason_lower:
                        should_show = False

                if should_show:
                    self._addTableRow(name, status, reason, url)

        except Exception as e:
            print(f"[Refresh Table Error] {e}")

    def applyFilter(self):
        """החלת סינון מהירה"""
        try:
            self.refreshTable()
        except Exception as e:
            print(f"[Apply Filter Error] {e}")

    def scanFinished(self):
        """סיום סריקה"""
        try:
            if self._is_closing:
                return

            self.labelStats.setText(self.labelStats.text() + " ✅ Done.")
            self.stopBtn.setEnabled(False)
            self.progressBar.setValue(self.progressBar.maximum())
            print("[Scan] Scan completed successfully")

        except Exception as e:
            print(f"[Scan Finished Error] {e}")

    def stopScan(self):
        """עצירת סריקה מהירה"""
        try:
            if self.thread and self.thread.isRunning():
                self.thread.stop()
                self.thread.wait(1000)
            self.labelStats.setText("Scan stopped by user.")
            self.stopBtn.setEnabled(False)
            print("[Scan] Scan stopped by user")

        except Exception as e:
            print(f"[Stop Scan Error] {e}")

    def markProblematicChannels(self):
        """סימון ערוצים בעייתיים במהירות שיא"""
        try:
            if not self.scan_results:
                QMessageBox.information(self, "No Results", "No scan results available.")
                return

            urls_to_mark = set()
            channel_statuses = {}
            duplicate_count = 0
            offline_count = 0

            # איסוף נתונים מהיר
            for name, status, reason, url in self.scan_results:
                if name not in channel_statuses:
                    channel_statuses[name] = []
                channel_statuses[name].append({
                    'status': status.lower(),
                    'url': url,
                    'is_offline': 'offline' in status.lower()
                })

            # עיבוד מהיר
            for name, entries in channel_statuses.items():
                offline_entries = [e for e in entries if e['is_offline']]
                online_entries = [e for e in entries if not e['is_offline']]

                # סימון אופליין
                for entry in offline_entries:
                    urls_to_mark.add(entry['url'])
                    offline_count += 1

                # סימון כפולים (רק אונליין נוספים)
                if len(online_entries) > 1:
                    for entry in online_entries[1:]:
                        urls_to_mark.add(entry['url'])
                        duplicate_count += 1

            total_marked = len(urls_to_mark)

            # סימון בפועל
            if self.parent() and hasattr(self.parent(), "selectChannelsByUrls"):
                self.parent().selectChannelsByUrls(urls_to_mark)
                QMessageBox.information(
                    self, "Marked Successfully",
                    f"✅ Found and marked:\n"
                    f"• {duplicate_count} duplicate channels\n"
                    f"• {offline_count} offline channels\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"Total: {total_marked} channels marked"
                )
                print(f"[Mark] Marked {total_marked} channels")
            else:
                QMessageBox.warning(self, "Error", "Parent method not found.")

        except Exception as e:
            print(f"[Mark Channels Error] {e}")
            QMessageBox.critical(self, "Error", f"Failed to mark channels: {str(e)}")

    def closeEvent(self, event):
        """סגירה מהירה ובטוחה"""
        try:
            self._is_closing = True
            if self.thread and self.thread.isRunning():
                self.thread.stop()
                self.thread.wait(2000)
            event.accept()
            print("[Close] Dialog closed")

        except Exception as e:
            print(f"[Close Event Error] {e}")
            event.accept()

    def reject(self):
        """דחייה מהירה"""
        try:
            self._is_closing = True
            if self.thread and self.thread.isRunning():
                self.thread.stop()
                self.thread.wait(1000)
            print("[Reject] Dialog rejected")

        except Exception as e:
            print(f"[Reject Error] {e}")
        finally:
            super().reject()


class M3UEditor(QWidget):
    logosFinished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.categories = {}
        # טוען את כל הלוגואים ל־cache בפעם אחת
        self.logo_cache = load_logo_cache()
        self.initUI()
        self.logo_cache = load_logo_cache()
        self.logosFinished.connect(self.onLogosFinished)

    @property
    def full_text(self) -> str:
        """
        מחזיר את כל תוכן ה־M3U שמוצג בעורך.
        """
        return self.textEdit.toPlainText()



    def merge_or_fix_epg(self):
        """
        מאחד או מתקן את שורת ה־EPG בראש הקובץ לפי ספקים מזוהים.
        שומר שורת EXTM3U אחת בלבד, עם כל קישורי ה־EPG התקפים שנמצאו.
        """
        import os
        import json
        import re
        from PyQt5.QtWidgets import QMessageBox

        # —————— שלב 1: אסוף קישורי EPG קיימים ——————
        all_epg_links = set()
        # אם נשמרו כותרות EPG בעבר
        if hasattr(self, 'epg_headers'):
            for hdr in self.epg_headers:
                # מוציא כל URL שמופיע ב- x-tvg-url="..."
                urls = re.findall(r'x-tvg-url="([^"]+)"', hdr)
                for u in urls:
                    all_epg_links.update(u.split(','))

        # —————— שלב 2: טען תוכן M3U הנוכחי ——————
        content = getattr(self, 'last_loaded_m3u', None) or self.textEdit.toPlainText()
        if not content:
            QMessageBox.warning(self, "EPG Error", "אין תוכן ל־M3U לטעינה או לעדכון.")
            return

        # —————— שלב 3: טען JSON של ספקי EPG ——————
        providers_path = os.path.join(os.path.dirname(__file__), "EPG_providers_full.json")
        try:
            with open(providers_path, "r", encoding="utf-8") as f:
                providers = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "EPG Error", f"שגיאה בקריאת קובץ ספקים:\n{e}")
            return

        # —————— שלב 4: זהה ספקים בתוכן לפי מילים או דומיינים ——————
        lower = content.lower()
        # כל כתובות URL בקובץ
        urls_in_file = [line.strip() for line in content.splitlines() if line.strip().startswith("http")]
        domains = {urlparse(u).netloc.lower().lstrip("www.") for u in urls_in_file}

        for provider, epg_list in providers.items():
            prov_l = provider.lower()
            # זיהוי לפי שם הספק בתוך התוכן
            if prov_l in lower:
                all_epg_links.update(epg_list)
                continue
            # זיהוי לפי דומיין של אחד מקישורי ה־EPG
            for epg_url in epg_list:
                dom = urlparse(epg_url).netloc.lower().lstrip("www.")
                if dom in domains:
                    all_epg_links.update(epg_list)
                    break

        # —————— שלב 5: בנייה וניקוי של התוכן החדש ——————
        cleaned = []
        for line in content.splitlines():
            # משמיט רק שורות שמתחילות ב־#EXTM3U
            if not line.startswith("#EXTM3U"):
                cleaned.append(line)
        # בנה שורת EXTM3U חדשה עם כל הקישורים
        if all_epg_links:
            links = ",".join(sorted(all_epg_links))
            new_header = f'#EXTM3U x-tvg-url="{links}"'
        else:
            new_header = "#EXTM3U"
        new_content = new_header + "\n" + "\n".join(cleaned)

        # —————— שלב 6: עדכון המערכת ותצוגה ——————
        self.epg_headers = [new_header]  # עדכון רשימת ה־EPG headers
        self.last_loaded_m3u = new_content  # שמירה פנימית
        self.loadM3UFromText(new_content)  # טעינה מחדש למערכת

        QMessageBox.information(self, "EPG Updated", "✅ שורת EPG עודכנה והוזנה מחדש.")

    def create_top_toolbar(self):
        from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton, QFrame as Line
        from PyQt5.QtGui import QIcon
        from PyQt5.QtCore import Qt

        bar = QFrame(self)
        bar.setObjectName("TopToolbar")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(8)

        # כפתור אחד מאוחד לטעינה/העלאה (עיצוב כחול)
        self.btnUploadTop = QPushButton("העלאת קובץ M3U", bar)
        self.btnUploadTop.setStyleSheet(
            "background:#2563eb; color:white; font-weight:bold; border-radius:8px; padding:6px 12px;"
        )
        if hasattr(self, "loadM3UFromDialog"):
            self.btnUploadTop.clicked.connect(self.loadM3UFromDialog)
        elif hasattr(self, "loadM3U"):
            self.btnUploadTop.clicked.connect(self.loadM3U)

        # יצוא כללי (עיצוב ירוק)
        self.btnExportTop = QPushButton("M3U ייצוא", bar)
        self.btnExportTop.setStyleSheet(
            "background:#16a34a; color:white; font-weight:bold; border-radius:8px; padding:6px 12px;"
        )
        if hasattr(self, "openExportDialog"):
            self.btnExportTop.clicked.connect(self.openExportDialog)
        elif hasattr(self, "exportVisibleM3U"):
            self.btnExportTop.clicked.connect(self.exportVisibleM3U)

        lay.addWidget(self.btnUploadTop)
        lay.addWidget(self.btnExportTop)

        # מפריד דק
        sep = Line(bar)
        sep.setFrameShape(Line.VLine)
        sep.setFrameShadow(Line.Sunken)
        sep.setStyleSheet("color:#e5e7eb;")
        lay.addWidget(sep)

        # הכפתורים שהיו למטה - עוברים למעלה באותו עיצוב ותפקוד
        self.topSaveButton = QPushButton("Save M3U", bar)
        self.topSaveButton.setStyleSheet("background-color: red; color: white;")
        if hasattr(self, "saveM3U"):
            self.topSaveButton.clicked.connect(self.saveM3U)

        self.topMergeButton = QPushButton("Merge M3Us", bar)
        self.topMergeButton.setStyleSheet("background-color: blue; color: white;")
        if hasattr(self, "mergeM3Us"):
            self.topMergeButton.clicked.connect(self.mergeM3Us)

        self.topExportTelegramButton = QPushButton(" Export to Telegram", bar)
        self.topExportTelegramButton.setIcon(QIcon("icons/telegram.png"))
        self.topExportTelegramButton.setStyleSheet("background-color: teal; color: white;")
        if hasattr(self, "exportToTelegram"):
            self.topExportTelegramButton.clicked.connect(self.exportToTelegram)

        lay.addWidget(self.topSaveButton)
        lay.addWidget(self.topMergeButton)
        lay.addWidget(self.topExportTelegramButton)

        lay.addStretch()

        # alias לשמות הישנים כדי שלא תישבר אף הפניה קיימת בקוד
        self.loadButton = self.btnUploadTop  # "load" הישן מצביע לכחול החדש
        self.saveButton = self.topSaveButton
        self.mergeButton = self.topMergeButton
        self.exportTelegramButton = self.topExportTelegramButton

        return bar

    def _attach_actions_to_channel_widget(self, widget, entry):
        from PyQt5.QtWidgets import QToolButton, QStyle, QWidget, QHBoxLayout
        from PyQt5.QtCore import Qt

        root = widget.layout()
        if root is None:
            return
        root.addStretch()

        bar = QWidget(widget)
        h = QHBoxLayout(bar);
        h.setContentsMargins(0, 0, 0, 0);
        h.setSpacing(2)

        def mk(icon_std, tip, handler):
            btn = QToolButton(bar)
            btn.setObjectName("ActionBtn")
            btn.setToolButtonStyle(btn.ToolButtonIconOnly)
            btn.setAutoRaise(True)
            btn.setIcon(widget.style().standardIcon(icon_std))
            btn.setToolTip(tip)
            btn.clicked.connect(handler)
            h.addWidget(btn)
            return btn

        def select_this():
            try:
                if not hasattr(self, "channelList"):
                    return
                for i in range(self.channelList.count()):
                    it = self.channelList.item(i)
                    it.setSelected(it.data(Qt.UserRole) == entry)
            except Exception:
                pass

        mk(QStyle.SP_TrashIcon, "Delete", lambda: (select_this(), self.deleteSelectedChannels()))
        mk(QStyle.SP_FileDialogDetailedView, "Edit", lambda: (select_this(), self.editSelectedChannel()))
        mk(QStyle.SP_ArrowUp, "Move Up", lambda: (select_this(), self.moveChannelUp()))
        mk(QStyle.SP_ArrowDown, "Move Down", lambda: (select_this(), self.moveChannelDown()))

        root.addWidget(bar, 0, Qt.AlignRight)

    def create_header_bar(self):
        """יוצר פס עליון עם כותרת וכפתורי עזרה/יצוא. לא מוחק כלום מהקיים."""
        from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
        from PyQt5.QtCore import Qt

        bar = QFrame(self)
        bar.setObjectName("HeaderBar")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(8)

        # כותרת
        title = QLabel("M3U Playlist Editor", bar)
        title.setObjectName("HeaderTitle")
        title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        lay.addWidget(title)
        lay.addStretch()

        # כפתור עזרה
        btn_help = QPushButton("Help", bar)
        btn_help.clicked.connect(self.showHelpDialog)
        lay.addWidget(btn_help)

        # כפתור יצוא מהיר - נשתמש במה שיש אצלך
        btn_export = QPushButton("Export", bar)
        if hasattr(self, "openExportDialog"):
            btn_export.clicked.connect(self.openExportDialog)
        elif hasattr(self, "exportVisibleM3U"):
            btn_export.clicked.connect(self.exportVisibleM3U)
        lay.addWidget(btn_export)

        return bar

    def show_toast(self, text: str, kind: str = "info", ms: int = 2000):
        """
        מציג הודעת Toast קצרה בפינה הימנית-עליונה של החלון.
        kind: "info", "success", "warn", "error"
        ms: זמן תצוגה במילישניות
        """
        from PyQt5.QtWidgets import QFrame, QLabel
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QFont

        colors = {
            "info": "#2563eb",
            "success": "#10b981",
            "warn": "#f59e0b",
            "error": "#ef4444",
        }
        bg = colors.get(kind, "#2563eb")

        toast = QFrame(self)
        toast.setObjectName("Toast")
        toast.setStyleSheet(
            f"background:{bg}; color:white; border-radius:8px; padding:8px 12px;"
            "border:1px solid rgba(0,0,0,0.1);"
        )
        toast.setAttribute(Qt.WA_StyledBackground, True)

        lbl = QLabel(text, toast)
        lbl.setStyleSheet("color:white;")
        f = QFont()
        f.setPointSize(9)
        f.setBold(True)
        lbl.setFont(f)
        lbl.adjustSize()

        # קביעת גודל ומיקום
        toast.resize(lbl.width() + 24, lbl.height() + 16)
        x = max(8, self.width() - toast.width() - 16)
        y = 16
        toast.move(x, y)

        toast.show()
        toast.raise_()

        QTimer.singleShot(ms, toast.deleteLater)

    def showHelpDialog(self):
        """חלון עזרה קצר עם קיצורים ומצב נוכחי."""
        from PyQt5.QtWidgets import QMessageBox

        # קיצורים
        tips = []
        tips.append("F1 - עזרה")
        if hasattr(self, "searchBox"):
            tips.append("Ctrl+F - חיפוש")
            tips.append("Ctrl+R - איפוס חיפוש")
        tips.append("Ctrl+A - בחר הכל ברשימת הערוצים")
        tips.append("Delete - מחיקת נבחרים")
        if hasattr(self, "_open_export_dialog_smart") or hasattr(self, "openExportDialog") or hasattr(self,
                                                                                                      "exportVisibleM3U"):
            tips.append("Ctrl+E - יצוא")
        if hasattr(self, "openURLCheckerDialog"):
            tips.append("Ctrl+L - URL Checker")

        # מצב נוכחי
        state = []
        if hasattr(self, "categoryList") and self.categoryList.currentItem():
            cat = self.categoryList.currentItem().text().split(" (")[0].strip()
            state.append(f"קטגוריה: {cat}")
        if hasattr(self, "statusFilter"):
            state.append(f"סטטוס: {self.statusFilter.currentText()}")
        if hasattr(self, "categoryFilter"):
            state.append(f"מסנן קטגוריה: {self.categoryFilter.currentText()}")
        if hasattr(self, "channelList"):
            state.append(f"ערוצים מוצגים: {self.channelList.count()}")
        if hasattr(self, "searchBox") and self.searchBox.text().strip():
            state.append(f"חיפוש: {self.searchBox.text().strip()}")

        msg = "\n".join(tips)
        if state:
            msg += "\n\nמצב נוכחי:\n" + "\n".join(state)

        QMessageBox.information(self, "Help", msg if tips else "No shortcuts defined.")

    def open_channel_context_menu(self, position):
        """
        תפריט קליק־ימני על ערוץ בודד: נגן אותו ב-VLC או preview לריבוי.
        """
        item = self.channelList.itemAt(position)
        if not item:
            return

        # שולפים את הערך מ-UserRole, ומגבים לטקסט אם זה לא מחרוזת
        raw = item.data(Qt.UserRole)
        entry = raw if isinstance(raw, str) else item.text().strip()

        menu = QMenu(self)

        # ▶ נגן את הערוץ ב-VLC
        play_action = QAction("▶ נגן ב־VLC", self)
        play_action.triggered.connect(lambda _, e=entry: self.play_channel_with_name(e))
        menu.addAction(play_action)

        # ▶ צפה בכל הנבחרים (preview)
        preview_action = QAction("▶ צפה בערוצים נבחרים", self)
        preview_action.triggered.connect(self.previewSelectedChannels)
        menu.addAction(preview_action)

        menu.exec_(self.channelList.viewport().mapToGlobal(position))

    def chooseFilterMethod(self):
        """בחירה ישירה בין סינון קלאסי למתקדם"""
        dialog = QDialog(self)
        dialog.setWindowTitle("🎯 בחר שיטת סינון")
        dialog.setFixedSize(400, 200)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 5px solid black;
            }
            QPushButton {
                font-size: 16px;
                padding: 15px;
                margin: 10px;
                font-weight: bold;
                border: 2px solid black;
                border-radius: 5px;
            }
        """)

        layout = QVBoxLayout(dialog)

        # כפתור סינון קלאסי
        classic_btn = QPushButton("📋 סינון קלאסי (ישראל בלבד)")
        classic_btn.setStyleSheet("background-color: black; color: white;")
        classic_btn.clicked.connect(lambda: [dialog.accept(), self.showLanguageChoice()])

        # כפתור סינון מתקדם
        advanced_btn = QPushButton("🚀 סינון מתקדם (ישראל + עולם)")
        advanced_btn.setStyleSheet("background-color: red; color: white;")
        advanced_btn.clicked.connect(lambda: [dialog.accept(), self.runAdvancedFilter()])

        layout.addWidget(classic_btn)
        layout.addWidget(advanced_btn)

        dialog.exec_()

    def showLanguageChoice(self):
        """בחירת שפה לסינון הקלאסי"""
        dialog = QDialog(self)
        dialog.setWindowTitle("בחר שפה")
        dialog.setFixedSize(350, 150)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 5px solid black;
            }
            QPushButton {
                font-size: 16px;
                padding: 12px;
                margin: 8px;
                font-weight: bold;
                border: 2px solid black;
                border-radius: 5px;
            }
        """)

        layout = QVBoxLayout(dialog)

        hebrew_btn = QPushButton(" עברית")
        hebrew_btn.setStyleSheet("background-color: black; color: white;")
        hebrew_btn.clicked.connect(lambda: [dialog.accept(), self.filterIsraelChannelsFromKeywords("he")])

        english_btn = QPushButton(" English")
        english_btn.setStyleSheet("background-color: red; color: white;")
        english_btn.clicked.connect(lambda: [dialog.accept(), self.filterIsraelChannelsFromKeywords("en")])

        layout.addWidget(hebrew_btn)
        layout.addWidget(english_btn)

        dialog.exec_()

    def runAdvancedFilter(self):
        if not self.categories:
            QMessageBox.warning(self, "אין נתונים", "אין ערוצים לסינון")
            return
        self.filter_system.chooseIsraelLanguageAndRunAdvanced()

    def filterIsraelChannelsFromKeywords(self, lang):
        """
        סינון ישראלי נקי ומדויק, בלי רדיו.
        זיהוי ישראלי:
        1) שם בעברית
        2) דפוסי IL בגבולות מילה: ' IL ', '(IL)', 'IL:', '-IL-', 'ISR'
        3) מותגים/ערוצים ישראליים ידועים
        """
        import re
        from channel_keywords import CATEGORY_KEYWORDS_EN, CATEGORY_KEYWORDS_HE

        keywords_map = CATEGORY_KEYWORDS_HE if lang == "he" else CATEGORY_KEYWORDS_EN

        il_provider_tokens = [
            'israel', 'kan', 'keshet', 'reshet', 'makan', 'i24', 'hidabroot', 'kabbalah',
            'yes', 'hot', 'partner', 'cellcom', 'sting',
            'sport 1', 'sport1', 'sport 2', 'sport2', 'sport 3', 'sport3', 'sport 4', 'sport4', 'sport 5', 'sport5',
            'one', 'channel 11', 'channel 12', 'channel 13', 'channel 14', 'channel 9', 'arutz'
        ]

        il_boundary_patterns = [
            r'\bIL\b', r'\(IL\)', r'\bIL:', r'-IL-', r'\bISR\b', r'\bisrael\b'
        ]

        def _has_hebrew(txt: str) -> bool:
            return any('\u0590' <= c <= '\u05EA' for c in txt)

        def _is_israeli_name(name: str) -> bool:
            if _has_hebrew(name):
                return True
            if any(re.search(pat, name, flags=re.IGNORECASE) for pat in il_boundary_patterns):
                return True
            low = name.lower()
            return any(tok in low for tok in il_provider_tokens)

        def _best_category(name: str) -> str:
            low = name.lower()
            best = None
            best_score = 0
            for cat, kws in keywords_map.items():
                score = 0
                for k in kws:
                    k = k.strip().lower()
                    if not k:
                        continue
                    if k in low:
                        score += 1
                if score > best_score:
                    best_score = score
                    best = cat
            return best if best_score >= 1 else 'Other'

        # נבנה מבנה קטגוריות
        filtered = {cat: [] for cat in keywords_map}
        if 'Other' not in filtered:
            filtered['Other'] = []

        # מעבר על כל הערוצים
        for _category, channels in self.categories.items():
            for entry in channels:
                # חילוץ שם הערוץ
                if isinstance(entry, str) and ' (' in entry and entry.endswith(')'):
                    name = entry.split(' (', 1)[0].strip()
                else:
                    name = str(entry).strip()

                if _is_israeli_name(name):
                    cat = _best_category(name)
                    filtered[cat].append(entry)

        # עדכון UI
        self.categories = filtered
        self.updateCategoryList()
        self.regenerateM3UTextOnly()
        self.categoryList.clear()
        for category, channels in self.categories.items():
            self.categoryList.addItem(f"{category} ({len(channels)})")

    def translate_category_names(self):
        from PyQt5.QtWidgets import QInputDialog, QMessageBox, QProgressDialog

        mode, ok = QInputDialog.getItem(
            self,
            "בחר סגנון תרגום",
            "בחר תצוגה:",
            ["English Only", "Hebrew Only", "English | Hebrew"],
            2,
            False
        )
        if not ok:
            return

        # התחלת סרגל התקדמות
        self.progressDialog = QProgressDialog("מתרגם קטגוריות...", "ביטול", 0, len(self.categories), self)
        self.progressDialog.setWindowTitle("מתרגם...")
        self.progressDialog.setWindowModality(Qt.WindowModal)
        self.progressDialog.setAutoClose(True)
        self.progressDialog.show()

        self.translation_thread = CategoryTranslateThread(self.categories.copy(), mode)
        self.translation_thread.progress.connect(lambda i, name: self.progressDialog.setValue(i))
        self.translation_thread.finished.connect(self.on_translation_finished)
        self.translation_thread.start()

    def on_translation_finished(self, updated_categories, mapping, mode):
        self.categories = updated_categories
        self.updateCategoryList()

        # עדכון EXTINF בקובץ הטקסט
        try:
            lines = self.textEdit.toPlainText().splitlines()
            new_lines = []
            for line in lines:
                if line.startswith("#EXTINF") and 'group-title="' in line:
                    for old, new in mapping.items():
                        if f'group-title="{old}"' in line:
                            line = line.replace(f'group-title="{old}"', f'group-title="{new}"')
                            break
                new_lines.append(line)
            self.safely_update_text_edit("\n".join(new_lines))
        except Exception as e:
            print(f"[EXTINF Update Error] {e}")

        self.regenerateM3UTextOnly()
        QMessageBox.information(self, "בוצע", f"שמות הקטגוריות תורגמו לפי: {mode}")

    def on_channels_translated(self, new_categories, mapping):
        # סגירת הפרוגרס
        try:
            self.chProgress.close()
        except:
            pass

        # 1. עדכון self.categories
        self.categories = new_categories

        # 2. עדכון QListWidget של קטגוריות
        self.updateCategoryList()

        # 3. בתיבת הטקסט (M3U Content) - נחליף שמות ב־EXTINF
        content = self.textEdit.toPlainText().splitlines()
        out = []
        for line in content:
            if line.startswith("#EXTINF"):
                # נחליף כל מיפוי שיש
                for old, new in mapping.items():
                    # old בפורמט "OldName (URL)" ⇒ שם ישן אחרי הפסיק
                    old_name = old.split(" (")[0]
                    new_name = new.split(" (")[0]
                    # מחליפים את after-last-comma
                    if f",{old_name}" in line:
                        parts = line.rsplit(",", 1)
                        line = f"{parts[0]},{new_name}"
                        break
            out.append(line)
        self.safely_update_text_edit("\n".join(out))

        # 4. רענון UI – נבחר קטגוריה ראשונה
        if self.categoryList.count():
            self.categoryList.setCurrentRow(0)
            self.display_channels(self.categoryList.currentItem())

        # 5. עדכון המחרוזות הלוגיות
        self.regenerateM3UTextOnly()

        QMessageBox.information(self, "תרגום ערוצים", "כל הערוצים תורגמו לאנגלית בהצלחה!")

    def translateChannels(self):
        """דיאלוג משופר עם 3 אפשרויות"""
        dlg = QDialog(self)
        dlg.setWindowTitle("תרגם ערוצים")
        dlg.setModal(True)
        dlg.setMinimumSize(400, 250)

        layout = QVBoxLayout(dlg)

        # כפתור לקטגוריה נוכחית
        btn_current = QPushButton("📝 תרגם קטגוריה נוכחית")
        btn_current.clicked.connect(lambda: [dlg.accept(), self._translateCategory()])

        # כפתור לבחירת קטגוריות מרובות - חדש!
        btn_selected = QPushButton("☑️ תרגם קטגוריות נבחרות")
        btn_selected.setStyleSheet("background-color: #9b59b6; color: white;")
        btn_selected.clicked.connect(lambda: [dlg.accept(), self._translateSelectedCategories()])

        # כפתור לכל הקטגוריות
        btn_all = QPushButton("🌐 תרגם את כל הערוצים")
        btn_all.clicked.connect(lambda: [dlg.accept(), self._translateAll()])

        layout.addWidget(btn_current)
        layout.addWidget(btn_selected)  # החדש!
        layout.addWidget(btn_all)

        dlg.exec_()

    def _translateSelectedCategories(self):
        """תרגום קטגוריות נבחרות בלבד"""
        dialog = QDialog(self)
        dialog.setWindowTitle("בחר קטגוריות לתרגום")
        dialog.setMinimumSize(400, 500)

        layout = QVBoxLayout(dialog)

        # רשימה עם checkboxes
        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.MultiSelection)

        for category in self.categories.keys():
            item = QListWidgetItem(f"{category} ({len(self.categories[category])} ערוצים)")
            item.setCheckState(Qt.Unchecked)
            list_widget.addItem(item)

        layout.addWidget(QLabel("סמן קטגוריות לתרגום:"))
        layout.addWidget(list_widget)

        # כפתורי פעולה
        btn_layout = QHBoxLayout()

        select_all_btn = QPushButton("בחר הכל")
        select_all_btn.clicked.connect(lambda: [
            list_widget.item(i).setCheckState(Qt.Checked)
            for i in range(list_widget.count())
        ])

        deselect_all_btn = QPushButton("בטל הכל")
        deselect_all_btn.clicked.connect(lambda: [
            list_widget.item(i).setCheckState(Qt.Unchecked)
            for i in range(list_widget.count())
        ])

        translate_btn = QPushButton("תרגם נבחרות")
        translate_btn.setStyleSheet("background-color: green; color: white;")

        btn_layout.addWidget(select_all_btn)
        btn_layout.addWidget(deselect_all_btn)
        btn_layout.addWidget(translate_btn)
        layout.addLayout(btn_layout)

        def start_translation():
            selected = {}
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                if item.checkState() == Qt.Checked:
                    cat_name = item.text().split(" (")[0]
                    selected[cat_name] = self.categories[cat_name]

            if selected:
                dialog.accept()
                self._startFastTranslation(selected, f"מתרגם {len(selected)} קטגוריות")
            else:
                QMessageBox.warning(dialog, "אזהרה", "לא נבחרו קטגוריות")

        translate_btn.clicked.connect(start_translation)
        dialog.exec_()

    def _translateAll(self):
        """תרגום כל הערוצים - עם אופטימיזציות מהירות"""
        if not self.categories:
            QMessageBox.information(self, "מידע", "אין קטגוריות לתרגום")
            return

        total_channels = sum(len(channels) for channels in self.categories.values())

        # אזהרה אם יש הרבה ערוצים
        if total_channels > 5000:
            reply = QMessageBox.question(
                self, "אזהרה",
                f"יש {total_channels:,} ערוצים לתרגום.\n"
                f"התהליך עלול לקחת זמן רב.\n"
                f"האם להמשיך?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        self._startFastTranslation(self.categories, "מתרגם את כל הערוצים")

    def _startFastTranslation(self, categories_to_translate, status_message):
        """התחלת תרגום מהיר עם אופטימיזציות"""
        from PyQt5.QtCore import QThread, pyqtSignal

        class FastChannelTranslateThread(QThread):
            """Thread מהיר לתרגום ערוצים עם batch processing"""
            progress = pyqtSignal(int, str, float)
            finished = pyqtSignal(dict, dict)
            error = pyqtSignal(str)

            def __init__(self, categories_dict):
                super().__init__()
                self.categories = categories_dict
                self._stop_requested = False

            def stop(self):
                self._stop_requested = True

            def run(self):
                import re
                from deep_translator import GoogleTranslator
                from concurrent.futures import ThreadPoolExecutor, as_completed
                import time

                def clean(text):
                    if not text:
                        return ""
                    return re.sub(r'[\r\n\t\x00-\x1F]', '', str(text)).strip()

                def is_english(text):
                    if not text:
                        return False
                    return all(ord(c) < 128 for c in str(text) if c.isalpha())

                def batch_translate(translator, texts, batch_size=20):
                    """תרגום בקבוצות למהירות מיטבית"""
                    results = {}

                    # חלוקה לקבוצות קטנות
                    text_batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]

                    for batch in text_batches:
                        if self._stop_requested:
                            break

                        try:
                            # ניסיון תרגום batch
                            translated_batch = translator.translate_batch(batch)
                            for original, translated in zip(batch, translated_batch):
                                results[original] = clean(translated) if translated else original
                        except:
                            # fallback לתרגום יחיד אם batch נכשל
                            for text in batch:
                                try:
                                    time.sleep(0.1)  # המתנה קצרה
                                    result = translator.translate(text)
                                    results[text] = clean(result) if result else text
                                except:
                                    results[text] = text  # שמירת המקור אם נכשל

                    return results

                try:
                    # אתחול מתרגם
                    translator_en = GoogleTranslator(source='auto', target='en')

                    # איסוף כל הטקסטים שצריך לתרגם
                    texts_to_translate = set()
                    channel_names = []

                    for channels in self.categories.values():
                        for channel in channels:
                            # חילוץ שם הערוץ
                            if " (" in channel and channel.endswith(")"):
                                name = channel.split(" (")[0].strip()
                            else:
                                name = channel.strip()

                            if name and not is_english(name):
                                texts_to_translate.add(name)

                            channel_names.append((channel, name))

                    self.progress.emit(0, "מכין רשימת תרגומים...", 0)

                    # תרגום batch של כל הטקסטים
                    if texts_to_translate:
                        translation_cache = batch_translate(translator_en, list(texts_to_translate))
                        self.progress.emit(50, "מיישם תרגומים...", 50)
                    else:
                        translation_cache = {}

                    # יישום התרגומים
                    updated_categories = {}
                    category_mapping = {}

                    total_categories = len(self.categories)

                    for i, (category_name, channels) in enumerate(self.categories.items()):
                        if self._stop_requested:
                            break

                        # תרגום שם הקטגוריה
                        translated_category = translation_cache.get(category_name, category_name)

                        # תרגום ערוצים
                        translated_channels = []
                        for channel in channels:
                            if " (" in channel and channel.endswith(")"):
                                name = channel.split(" (")[0].strip()
                                url_part = channel.split(" (", 1)[1]

                                # שימוש בcache לתרגום
                                translated_name = translation_cache.get(name, name)
                                translated_channel = f"{translated_name} ({url_part}"
                            else:
                                translated_name = translation_cache.get(channel.strip(), channel)
                                translated_channel = translated_name

                            translated_channels.append(translated_channel)

                        # איחוד קטגוריות זהות
                        if translated_category in updated_categories:
                            updated_categories[translated_category].extend(translated_channels)
                        else:
                            updated_categories[translated_category] = translated_channels

                        category_mapping[category_name] = translated_category

                        # עדכון progress
                        progress = ((i + 1) / total_categories) * 50 + 50
                        self.progress.emit(i + 1, f"מעבד: {category_name[:30]}...", progress)

                    self.finished.emit(updated_categories, category_mapping)

                except Exception as e:
                    self.error.emit(f"שגיאה בתרגום: {str(e)}")

        # יצירת והרצת Thread
        self.channel_translate_thread = FastChannelTranslateThread(categories_to_translate)

        # יצירת Progress Dialog
        progress_dialog = self._createTranslationProgressDialog(status_message)

        # חיבור סיגנלים
        self.channel_translate_thread.progress.connect(progress_dialog.update_progress)
        self.channel_translate_thread.finished.connect(lambda categories, mapping: [
            progress_dialog.accept(),
            self._applyChannelTranslation(categories, mapping)
        ])
        self.channel_translate_thread.error.connect(lambda error: [
            progress_dialog.reject(),
            QMessageBox.critical(self, "שגיאה", error)
        ])

        # הצגת Dialog והתחלת Thread
        progress_dialog.show()
        self.channel_translate_thread.start()

    def _createTranslationProgressDialog(self, title):
        """יצירת dialog התקדמות מודרני"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel
        from PyQt5.QtCore import Qt

        dialog = QDialog(self)
        dialog.setWindowTitle("תרגום ערוצים")
        dialog.setModal(True)
        dialog.setMinimumSize(400, 150)
        dialog.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)

        # תווית סטטוס
        status_label = QLabel(title)
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 15px;
            }
        """)

        # פס התקדמות
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                font-size: 12px;
                min-height: 25px;
                background: #ecf0f1;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 6px;
            }
        """)

        # תווית אחוזים ופרטים
        details_label = QLabel("מתחיל...")
        details_label.setAlignment(Qt.AlignCenter)
        details_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                margin-top: 10px;
            }
        """)

        layout.addWidget(status_label)
        layout.addWidget(progress_bar)
        layout.addWidget(details_label)

        # פונקציה לעדכון
        def update_progress(processed, current_item, percentage):
            progress_bar.setValue(int(percentage))
            details_label.setText(f"{percentage:.1f}% - {current_item}")

            if percentage >= 100:
                status_label.setText("✅ התרגום הושלם!")
                details_label.setText("סוגר...")

        dialog.update_progress = update_progress
        return dialog

    def _applyChannelTranslation(self, translated_categories, category_mapping):
        """יישום תוצאות התרגום - מעדכן רק את הקטגוריות שתורגמו"""

        # שמירת מצב לפני
        channels_before = sum(len(channels) for channels in self.categories.values())
        categories_before = len(self.categories)

        # במקום להחליף את כל self.categories, נעדכן רק את מה שתורגם
        for old_category, new_category in category_mapping.items():
            if old_category in self.categories:
                # אם השם השתנה
                if old_category != new_category:
                    # העבר את הערוצים לקטגוריה החדשה
                    if new_category in self.categories:
                        # אם הקטגוריה החדשה כבר קיימת - מזג
                        self.categories[new_category].extend(translated_categories[new_category])
                    else:
                        # צור קטגוריה חדשה
                        self.categories[new_category] = translated_categories[new_category]

                    # מחק את הקטגוריה הישנה
                    del self.categories[old_category]
                else:
                    # אם השם לא השתנה, רק עדכן את הערוצים
                    self.categories[old_category] = translated_categories[old_category]

        # עדכון התצוגה
        self.cleanEmptyCategories()
        self.updateCategoryList()
        self.regenerateM3UTextOnly()

        if self.categoryList.count() > 0:
            self.categoryList.setCurrentRow(0)
            self.display_channels(self.categoryList.currentItem())

        # הצגת תוצאות
        channels_after = sum(len(channels) for channels in self.categories.values())
        categories_after = len(self.categories)

        QMessageBox.information(
            self, "תרגום הושלם",
            f"✅ תורגמו {len(category_mapping)} קטגוריות\n"
            f"📊 סה\"כ ערוצים: {channels_after:,}"
        )

    def _translateCategory(self):
        # בוחר קטגוריה
        items = list(self.categories.keys())
        cat, ok = QInputDialog.getItem(self, "בחר קטגוריה", "תרגם קטגוריה:", items, 0, False)
        if not ok or not cat:
            return
        subset = {cat: self.categories[cat][:]}
        self._startTranslation(subset)

    def _translateAll(self):
        subset = {cat: lst[:] for cat, lst in self.categories.items()}
        self._startTranslation(subset)

    def _startTranslation(self, cats_dict):
        total = sum(len(lst) for lst in cats_dict.values())
        if total == 0:
            QMessageBox.information(self, "תרגום ערוצים", "אין ערוצים לתרגם.")
            return

        # 1. יוצרים ושומרים את הדיאלוג במשתנה של המופע
        self.chProgress = QProgressDialog(
            "מתרגם ערוצים...",  # טקסט ראשי
            "ביטול",  # טקסט כפתור ביטול
            0, total,  # טווח הערכים
            self  # parent
        )
        self.chProgress.setWindowModality(Qt.WindowModal)
        self.chProgress.setWindowTitle("תִרגוּם ערוצים")
        self.chProgress.setMinimumDuration(0)  # להציג מיד
        self.chProgress.setAutoClose(True)  # לסגור אוטומטית בהגעה למקסימום
        self.chProgress.setAutoReset(True)  # לאפס את הערך אם יופעל שוב
        self.chProgress.canceled.connect(lambda: getattr(self, 'chThread', None) and self.chThread.terminate())
        self.chProgress.show()

        # 2. אתחול ה-QThread
        self.chThread = ChannelTranslateThread(cats_dict)
        # הפרדת העדכון לרצף קריאות נקי יותר
        self.chThread.progress.connect(self._update_translation_progress)
        # כשהסתיים – נסגור את ה-QProgressDialog ואז נקרא לעדכון UI
        self.chThread.finished.connect(lambda new_cats, mapping: (
            self.chProgress.setValue(self.chProgress.maximum()),
            self.chProgress.close(),
            self._onTranslated(new_cats, mapping, cats_dict)
        ))
        self.chThread.start()

    def _update_translation_progress(self, idx: int, name: str):
        """
        מעדכן את הסרגל ואת התווית בכל אירוע פרוגרס
        """
        self.chProgress.setValue(idx)
        self.chProgress.setLabelText(f"מתרגם: {name} ({idx}/{self.chProgress.maximum()})")

    def _onTranslated(self, new_cats, mapping, orig_dict):
        # עדכון רק הקטגוריות שעובדו
        for cat in orig_dict:
            self.categories[cat] = new_cats.get(cat, [])

        self.updateCategoryList()
        cur = self.categoryList.currentItem()
        if cur:
            self.display_channels(cur)

        # עדכון שמות בתוך #EXTINF בתוכן הגלילי
        text = self.textEdit.toPlainText().splitlines()
        out = []
        for line in text:
            if line.startswith("#EXTINF"):
                for old, new in mapping.items():
                    old_nm = old.split(" (")[0]
                    new_nm = new.split(" (")[0]
                    if f",{old_nm}" in line:
                        props = line.rsplit(",", 1)[0]
                        line = f"{props},{new_nm}"
                        break
            out.append(line)
        self.safely_update_text_edit("\n".join(out))

        self.regenerateM3UTextOnly()
        QMessageBox.information(self, "תרגום ערוצים", "התרגום הסתיים בהצלחה.")

    def play_channel_with_name(self, entry):
        """
        מפעיל VLC רק על הערוץ היחיד שבחרנו (entry = "Name (URL)").
        הקוד ידאג לבנות קובץ M3U תקין עם #EXTM3U, שורת EXTINF נכונה ושורת URL.
        גרסה מתוקנת עם טיפול מלא בשגיאות.
        """
        try:
            # וידוא שזה מחרוזת
            if not isinstance(entry, str):
                entry = str(entry) if entry else ""

            if not entry.strip():
                QMessageBox.warning(self, "שגיאה", "לא נבחר ערוץ תקין להפעלה.")
                return

            # פענוח שם ו-URL עם בדיקות בטיחות
            name = ""
            url = ""

            if "(" in entry and entry.endswith(")"):
                try:
                    parts = entry.split(" (", 1)
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        url = parts[1].rstrip(")").strip()
                    else:
                        raise ValueError("Invalid format")
                except:
                    QMessageBox.warning(self, "שגיאה", f"פורמט ערוץ לא תקין:\n{entry}")
                    return
            else:
                QMessageBox.warning(self, "שגיאה", "לא ניתן לחלץ URL מתוך הפריט.")
                return

            # וידוא שיש שם וURL תקינים
            if not name or not url:
                QMessageBox.warning(self, "שגיאה", "שם ערוץ או URL חסרים או לא תקינים.")
                return

            # בדיקה בסיסית של URL
            if not any(url.lower().startswith(protocol) for protocol in
                       ['http://', 'https://', 'rtmp://', 'rtsp://', 'udp://']):
                reply = QMessageBox.question(
                    self, "URL לא תקין",
                    f"ה-URL נראה לא תקין:\n{url}\n\nהאם להמשיך בכל זאת?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return

            # נסיון לקבל את שורת ה-EXTINF המקורית מה-lookup
            extinf_line = ""
            try:
                if hasattr(self, 'extinf_lookup') and self.extinf_lookup:
                    extinf_line = self.extinf_lookup.get(entry, "")
            except:
                pass

            if not extinf_line:
                # אם אין, בונים אחת ידנית
                logo = ""
                try:
                    logo = get_saved_logo(name) or ""
                except:
                    pass

                logo_tag = f' tvg-logo="{logo}"' if logo else ""

                # מוצאים את הקטגוריה הנוכחית להצבה ב-group-title בצורה בטוחה
                grp = "Unknown"
                try:
                    cat_item = self.categoryList.currentItem()
                    if cat_item and hasattr(cat_item, 'text') and cat_item.text():
                        grp = cat_item.text().split(" (")[0].strip()
                except:
                    grp = "Unknown"

                extinf_line = (
                    f'#EXTINF:-1{logo_tag} '
                    f'tvg-name="{name}" group-title="{grp}",{name}'
                )

            # כותבים קובץ M3U זמני
            try:
                with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".m3u", delete=False, encoding="utf-8"
                ) as f:
                    f.write("#EXTM3U\n")
                    f.write(extinf_line + "\n")
                    f.write(url + "\n")
                    temp_path = f.name

            except Exception as e:
                QMessageBox.critical(
                    self, "שגיאה ביצירת קובץ זמני",
                    f"לא ניתן ליצור קובץ זמני:\n{e}"
                )
                return

            # בדיקת קיום VLC בנתיב
            vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
            if not os.path.exists(vlc_path):
                # ניסיון לחפש VLC במיקומים נוספים
                alternative_paths = [
                    r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
                    r"C:\Users\%USERNAME%\AppData\Local\Programs\VideoLAN\VLC\vlc.exe"
                ]

                vlc_found = False
                for alt_path in alternative_paths:
                    if os.path.exists(alt_path):
                        vlc_path = alt_path
                        vlc_found = True
                        break

                if not vlc_found:
                    QMessageBox.critical(
                        self, "VLC לא נמצא",
                        f"לא נמצא VLC באף אחד מהנתיבים הבאים:\n" +
                        "\n".join([vlc_path] + alternative_paths) +
                        "\n\nאנא התקן VLC או עדכן את הנתיב בקוד."
                    )
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                    return

            # הפעלת VLC
            try:
                process = subprocess.Popen([vlc_path, temp_path])

                # הודעת הצלחה קצרה
                QMessageBox.information(
                    self, "VLC הופעל",
                    f"ערוץ '{name}' הופעל ב-VLC בהצלחה!"
                )

            except Exception as e:
                QMessageBox.critical(
                    self, "שגיאה בהפעלת VLC",
                    f"לא ניתן להפעיל VLC:\n{e}"
                )
                try:
                    os.remove(temp_path)
                except:
                    pass

        except Exception as e:
            error_msg = f"שגיאה כללית בהפעלת ערוץ: {e}"
            print(f"[ERROR] {error_msg}")
            QMessageBox.critical(self, "שגיאה", error_msg)

    def getCurrentEntry(self):
        """
        מחזירה את ה-entry הנוכחי מרשימת הערוצים,
        כפי שנשמר ב-UserRole כ"Name (URL)".
        """
        item = self.channelList.currentItem()
        if not item:
            return ""
        raw = item.data(Qt.UserRole)
        return raw if isinstance(raw, str) else item.text().strip()

    def getUrl(self, channel_string):
        try:
            if '(' in channel_string and ')' in channel_string:
                url = channel_string.split(" (")[-1].rstrip(")")
                if url.startswith("http"):
                    return url
            return ""
        except Exception:
            return ""

    def onLogosFinished(self):
        QMessageBox.information(self, "Logo Scan", "✅ סריקת הלוגואים הושלמה בהצלחה!")

    def initUI(self):
        # כותרת החלון ומאפיינים כלליים
        self.setWindowTitle('M3U Playlist Editor')
        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowMinMaxButtonsHint |
                            Qt.WindowCloseButtonHint)

        self.setGeometry(100, 100, 1200, 800)
        QApplication.setFont(QFont('Arial', 12))

        self.setStyleSheet(APP_QSS + QSS_CHANNELS)
        self.setStyleSheet(self.styleSheet() + EXTRA_QSS_HEADER)
        self.setStyleSheet(self.styleSheet() + EXTRA_QSS_CARDS)
        self.setStyleSheet(self.styleSheet() + APP_QSS_LARGE)
        # הזרקת שכבת נראות נוספת
        self.setStyleSheet(self.styleSheet() + QSS_TAILWINDISH)

        # לייאאוט ראשי
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        main_layout.addWidget(self.create_top_toolbar())
        main_layout.setContentsMargins(8, 2, 8, 6)
        main_layout.setSpacing(4)


        # ─── שורת חיפוש ───
        self.searchBox = QLineEdit(self)
        self.searchBox.setPlaceholderText("🔍 חיפוש קטגוריה או ערוץ...")
        self.searchBox.textChanged.connect(self.handleSearchTextChanged)
        self.searchBox.textChanged.connect(self._on_filters_changed)  # הוספה

        reset_btn = QPushButton("🔄 איפוס", self)
        reset_btn.setStyleSheet("padding:3px; font-weight:bold;")
        reset_btn.clicked.connect(lambda: self.searchBox.setText(""))

        # חדשים
        self.categoryFilter = QComboBox(self)
        self.categoryFilter.addItem("כל הקטגוריות", "")
        self.categoryFilter.currentIndexChanged.connect(self._on_filters_changed)


        search_layout = QHBoxLayout()
        search_layout.addWidget(self.searchBox)
        search_layout.addWidget(self.categoryFilter)  # הוספה
        search_layout.addWidget(reset_btn)
        main_layout.addLayout(search_layout)


        # ─── מידע על קובץ וערוצים ───
        info_layout = QHBoxLayout()
        self.fileNameLabel = QLabel("No file loaded", self)
        self.fileNameLabel.setAlignment(Qt.AlignCenter)
        self.fileNameLabel.setStyleSheet("font-size:18px; font-weight:bold;")
        info_layout.addWidget(self.fileNameLabel)

        self.channelCountLabel = QLabel("Total Channels: 0", self)
        self.channelCountLabel.setAlignment(Qt.AlignRight)
        self.channelCountLabel.setStyleSheet("font-size:18px; font-weight:bold;")
        info_layout.addWidget(self.channelCountLabel)

        main_layout.addLayout(info_layout)

        #main_layout.addLayout(self.create_category_section(), 2)  # יותר גובה לקטגוריות
        #main_layout.addLayout(self.create_channel_section(), 5)  # הכי הרבה גובה לערוצים
        #main_layout.addLayout(self.create_m3u_content_section(), 2)

        self.mainSplitter = self.create_main_splitter()
        main_layout.addWidget(self.mainSplitter, 1)

        main_layout.addLayout(self.create_Tools(), 1)


        # ─── כפתורי VLC (Play & Preview) ───
        vlc_icon = QIcon("icons/vlc.png")

        vlc_layout = QHBoxLayout()

        # ▶ נגן ערוץ בודד
        self.playButton = QPushButton("▶ נגן ב־VLC", self)
        self.playButton.setIcon(vlc_icon)
        self.playButton.setIconSize(QSize(22, 22))
        self.playButton.setStyleSheet(
            "background-color: navy; color: white; font-weight: bold;"
        )
        self.playButton.clicked.connect(
            lambda: self.play_channel_with_name(self.getCurrentEntry())
        )
        vlc_layout.addWidget(self.playButton)

        # ▶ Preview לערוצים מרובים
        self.previewButton = QPushButton("▶ צפה בערוצים", self)
        self.previewButton.setIcon(vlc_icon)
        self.previewButton.setIconSize(QSize(22, 22))
        self.previewButton.setStyleSheet(
            "background-color: navy; color: white; font-weight: bold;"
        )
        self.previewButton.clicked.connect(self.previewSelectedChannels)
        vlc_layout.addWidget(self.previewButton)

        # ▶ Translate Channels ↔ כפתור תרגום ערוצים
        self.translateChannelsButton = QPushButton("🌐 תרגם ערוצים", self)
        self.translateChannelsButton.setStyleSheet(
            "background-color: navy; color: white; font-weight: bold;"
        )
        vlc_layout.addWidget(self.translateChannelsButton)
        # ברגע שלחיצה – נפתח דיאלוג פנימי עם 2 אפשרויות
        self.translateChannelsButton.clicked.connect(self.translateChannels)

        # בסוף, מוסיפים את vlc_layout ל־main_layout
        main_layout.addLayout(vlc_layout)

        # לחצן Checker וכדומה
        self.urlCheckButton = QPushButton('IPTV Checker', self)
        self.urlCheckButton.setStyleSheet("background-color: purple; color: white;")
        self.urlCheckButton.clicked.connect(self.openURLCheckerDialog)
        main_layout.addWidget(self.urlCheckButton)

        # ווידוא כותרת EXTM3U
        self.textEdit.textChanged.connect(self.ensure_extm3u_header)
        # קיצורי מקשים לכלל האפליקציה
        self._add_shortcuts()

    def create_main_splitter(self):
        from PyQt5.QtWidgets import QWidget, QSplitter
        from PyQt5.QtCore import Qt

        def wrap(layout_fn):
            w = QWidget()
            w.setLayout(layout_fn())
            return w

        top = wrap(self.create_category_section)
        middle = wrap(self.create_channel_section)
        bottom = wrap(self.create_m3u_content_section)

        sp = QSplitter(Qt.Vertical)
        sp.setChildrenCollapsible(False)
        sp.setHandleWidth(6)
        sp.addWidget(top)
        sp.addWidget(middle)
        sp.addWidget(bottom)

        # קטגוריות קטנות, ערוצים גדולים, תוכן בינוני
        sp.setStretchFactor(0, 1)
        sp.setStretchFactor(1, 6)
        sp.setStretchFactor(2, 2)
        sp.setSizes([120, 900, 240])

        return sp

    def create_channel_section(self):
        """
        בונה את ה־UI לטיפול בערוצים:
        - כותרת
        - ComboBox למיון
        - QListWidget להצגת הערוצים
        - כפתורים להוספה/מחיקה/העברה/עריכה/בדיקת כפילויות
        """
        # חשוב: ייבוא מוקדם כדי למנוע UnboundLocalError בשימוש ב-Qt לפני הייבוא
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QAbstractItemView, QListWidget

        layout = QVBoxLayout()

        # כותרת
        channel_title = QLabel("Channels", self)
        channel_title.setAlignment(Qt.AlignCenter)
        channel_title.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(channel_title)

        # ComboBox למיון
        self.sortingComboBox = QComboBox(self)
        self.sortingComboBox.addItems([
            "Sort by Name A-Z",
            "Sort by Name Z-A",
            "Sort by Stream Type",
            "Sort by Group Title",
            "Sort by URL Length",
            "Sort by Quality (4K → SD)"
        ])
        self.sortingComboBox.currentIndexChanged.connect(self.sortChannels)
        layout.addWidget(self.sortingComboBox)

        # רשימת הערוצים
        self.channelList = ChannelListWidget(self)
        from PyQt5.QtWidgets import QSizePolicy
        self.channelList.setMinimumHeight(1200)  # הגדלת חלון הערוצים
        self.channelList.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.channelList.setStyleSheet("font-size: 8pt;")

        # אפשר להשאיר גם את הייבוא כאן אם כתבת אותו לפני כן. לא חובה.
        # from PyQt5.QtWidgets import QAbstractItemView
        # from PyQt5.QtCore import Qt

        # בחירה מרובה ופוקוס חזק
        self.channelList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.channelList.setFocusPolicy(Qt.StrongFocus)

        self.channelList.setAlternatingRowColors(True)
        self.channelList.setUniformItemSizes(True)
        self.channelList.setSpacing(1)
        self.channelList.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.channelList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.channelList.setAlternatingRowColors(True)
        self.channelList.setUniformItemSizes(True)

        # שומר את ההגדרות שלך כמו שהיו
        self.channelList.setSelectionMode(QListWidget.MultiSelection)
        self.channelList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.channelList.customContextMenuRequested.connect(self.open_channel_context_menu)
        layout.addWidget(self.channelList)

        # כפתורי פעולה לערוצים
        button_layout = QHBoxLayout()
        self.addChannelButton = QPushButton('Add Channel')
        self.deleteChannelButton = QPushButton('Delete Selected')
        self.moveChannelUpButton = QPushButton('Move Up')
        self.moveChannelDownButton = QPushButton('Move Down')
        self.selectAllChannelsButton = QPushButton('Select All')
        self.clearChannelsSelectionButton = QPushButton('Deselect All')
        self.moveSelectedChannelButton = QPushButton('Move Selected')
        self.editSelectedChannelButton = QPushButton('Edit Selected')
        self.checkDoublesButton = QPushButton('Check Duplicate')
        self.checkDoublesButton.clicked.connect(self.checkDoubles)

        for btn in [
            self.addChannelButton, self.deleteChannelButton,
            self.moveChannelUpButton, self.moveChannelDownButton,
            self.selectAllChannelsButton, self.clearChannelsSelectionButton,
            self.moveSelectedChannelButton, self.editSelectedChannelButton,
            self.checkDoublesButton
        ]:
            button_layout.addWidget(btn)
            self.channelList.setMinimumHeight(400)  # חלון ערוצים גבוה
            self.channelList.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addLayout(button_layout)

        # חיבור אותות (Signals) למתודות
        self.addChannelButton.clicked.connect(self.addChannel)
        self.deleteChannelButton.clicked.connect(self.deleteSelectedChannels)
        self.moveChannelUpButton.clicked.connect(self.moveChannelUp)
        self.moveChannelDownButton.clicked.connect(self.moveChannelDown)
        self.selectAllChannelsButton.clicked.connect(self.selectAllChannels)
        self.clearChannelsSelectionButton.clicked.connect(self.deselectAllChannels)
        self.moveSelectedChannelButton.clicked.connect(self.moveSelectedChannel)
        self.editSelectedChannelButton.clicked.connect(self.editSelectedChannel)
        # self.checkDoublesButton חוברה כבר לעיל

        # חיזוק אחרון: להבטיח שהמצב הסופי הוא ExtendedSelection ופוקוס חזק
        self.channelList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.channelList.setFocusPolicy(Qt.StrongFocus)

        return layout

    def inject_logo(self, line, channel_name, logo_db=None):
        """
        Injects saved logo into a #EXTINF line if missing.
        logo_db - optional dictionary to speed up repeated calls
        """
        # אם כבר קיים תג tvg-logo בשורה, לא עושים כלום
        if 'tvg-logo="' in line:
            return line

        # שליפת לוגו מה-DB אם לא הועבר לוגו מבחוץ
        if logo_db is None:
            # שימוש בקריאה הנכונה: get_saved_logo מקבלת רק ארגומנט אחד
            logo = get_saved_logo(channel_name)
        else:
            logo = logo_db.get(channel_name)
            if isinstance(logo, list):
                logo = logo[0] if logo else None
            elif not isinstance(logo, str):
                logo = None

        # אם מצאנו URL לוגו תקין, משבצים אותו ב-EXTINF
        if logo and isinstance(logo, str) and logo.startswith("http"):
            return line.replace(
                "#EXTINF:-1",
                f'#EXTINF:-1 tvg-logo="{logo}"'
            )

        # אם לא מצאנו לוגו, מחזירים את השורה המקורית ללא שינוי
        return line

    def exportM3UWithFullData(self, output_path):
        """
        גרסה משופרת לשמירת קובץ M3U הכוללת:
        - EXTINF מלא כולל tvg-id, group-title, לוגו
        - שם ערוץ מלא
        - לינק מקורי
        - שימוש בטוח במפות lookup, ללא תלות בפורמט מחרוזת
        """
        try:
            with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                logo_db = json.load(f)
        except:
            logo_db = {}

        with open(output_path, "w", encoding="utf-8") as out:
            out.write("#EXTM3U\n")

            for category, channels in self.categories.items():
                for channel in channels:
                    name = channel.strip()

                    # שליפת שורת EXTINF מלאה
                    extinf_line = self.extinf_lookup.get(name)
                    if not extinf_line:
                        extinf_line = f"#EXTINF:-1,{name}"

                    # הזרקת לוגו לפי שם
                    extinf_line = self.inject_logo(extinf_line, name, logo_db)

                    # שליפת לינק מה־map אם נשמרה
                    url = self.urls.get(name)

                    # גיבוי - פענוח מתוך השם אם נדרש
                    if not url and " (" in name:
                        url = name.split(" (")[-1].strip(")")
                        name = name.split(" (")[0].strip()

                    if not url:
                        print(f"⚠️ ערוץ '{name}' לא כולל URL, דילוג.")
                        continue

                    out.write(extinf_line + "\n")
                    out.write(url + "\n")

    def openM3UConverterDialog(self):
        from PyQt5.QtCore import Qt
        # יוצרים את הדיאלוג ומוודאים שהוא יימחק אוטומטית בסגירה
        dlg = M3UUrlConverterDialog(self)
        dlg.setAttribute(Qt.WA_DeleteOnClose)
        dlg.finished.connect(dlg.deleteLater)
        dlg.exec_()

    def handle_download():
        import re
        from datetime import datetime
        import requests
        from PyQt5.QtWidgets import QMessageBox, QFileDialog

        url = url_input.text().strip()
        if not url:
            QMessageBox.warning(dialog, "Missing URL", "Please enter a valid M3U URL.")
            return

        if not (url.startswith("http://") or url.startswith("https://")):
            QMessageBox.warning(dialog, "Invalid URL", "URL must start with http:// or https://")
            return

        try:
            session = setup_session()
            resp = session.get(url, timeout=5)
            resp.raise_for_status()
            content = resp.text.strip()

            if not content.startswith("#EXTM3U"):
                QMessageBox.warning(dialog, "Invalid File", "Downloaded file is not a valid M3U playlist.")
                return

            choice = QMessageBox.question(
                dialog,
                "M3U Downloaded",
                "M3U file downloaded successfully.\n\nLoad into the system?",
                QMessageBox.Yes | QMessageBox.No
            )

            if choice == QMessageBox.Yes:
                self.loadM3UFromText(content)
            else:
                m = re.search(r"username=([\w]+)", url)
                default_name = f"{m.group(1)}.m3u" if m else f"m3u_{datetime.now():%Y%m%d_%H%M%S}.m3u"
                path, _ = QFileDialog.getSaveFileName(
                    dialog,
                    "Save M3U File",
                    default_name,
                    "M3U Files (*.m3u);;All Files (*)"
                )
                if path:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    QMessageBox.information(dialog, "Saved", "M3U file saved successfully.")

            # סוגרים דרך accept() כדי שה-deleteLater יעבוד
            dialog.accept()

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(dialog, "Network Error", f"Network error:\n{e}")
        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"Unexpected error:\n{e}")

    def openBatchDownloader(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Multi M3U Downloader")
        dialog.setGeometry(100, 100, 600, 500)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        dialog.setStyleSheet("""
            QDialog { border: 5px solid red; background-color: white; }
            QPushButton { font-weight: bold; height: 40px; }
        """)

        layout = QVBoxLayout(dialog)

        url_label = QLabel("Paste M3U URLs (one per line):", dialog)
        layout.addWidget(url_label)

        url_input = QTextEdit(dialog)
        url_input.setStyleSheet("font-size: 14px;")
        url_input.setPlaceholderText("Example:\nhttp://site1.com/playlist\nhttp://site2.com/playlist")
        layout.addWidget(url_input)

        # כפתור טעינת קבצים מקומיים וטעינה מיידית
        load_files_button = QPushButton("📂 UPLOAD FROM DRIVE", dialog)
        load_files_button.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(load_files_button)

        def handle_load_local_files():
            files, _ = QFileDialog.getOpenFileNames(dialog, "Select M3U Files", "",
                                                    "M3U Files (*.m3u *.m3u8);;All Files (*)")
            if not files:
                return

            combined_content = "#EXTM3U\n"
            for path in files:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if content.strip().startswith("#EXTM3U"):
                            lines = [line for line in content.splitlines() if
                                     line.strip() and not line.startswith("#EXTM3U")]
                            combined_content += "\n".join(lines) + "\n"
                except Exception as e:
                    QMessageBox.warning(dialog, "File Error", f"❌ Failed to load {path}:\n{str(e)}")

            self.loadM3UFromText(combined_content, append=False)
            QMessageBox.information(dialog, "Success", "All selected M3U files were loaded into the editor.")
            dialog.close()

        load_files_button.clicked.connect(handle_load_local_files)

        # הדבקה חכמה + מעבר שורה
        def on_url_text_changed():
            text = url_input.toPlainText()
            if "," in text:
                clean = "\n".join([x.strip() for x in text.split(",") if x.strip()])
                url_input.blockSignals(True)
                url_input.setPlainText(clean)
                url_input.blockSignals(False)
                return
            lines = text.splitlines()
            if lines and not text.endswith("\n"):
                url_input.blockSignals(True)
                url_input.setPlainText(text + "\n")
                cursor = url_input.textCursor()
                cursor.movePosition(cursor.End)
                url_input.setTextCursor(cursor)
                url_input.blockSignals(False)

        url_input.textChanged.connect(on_url_text_changed)

        url_input.setAcceptDrops(True)

        def dragEnterEvent(event):
            if event.mimeData().hasUrls():
                event.acceptProposedAction()

        def dropEvent(event):
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path.endswith(".txt"):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read()
                            url_input.append(content)
                    except Exception as e:
                        QMessageBox.warning(dialog, "Error", f"Failed to read dropped file:\n{str(e)}")

        url_input.dragEnterEvent = dragEnterEvent
        url_input.dropEvent = dropEvent

        # כפתור הורדת URL מרובים - נשאר למי שרוצה דרך URL
        download_button = QPushButton("C0nvert URL ", dialog)
        download_button.setStyleSheet("background-color: red; color: white;")
        layout.addWidget(download_button)

        # כפתור סגירה
        close_button = QPushButton("Close", dialog)
        close_button.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(close_button)
        close_button.clicked.connect(dialog.close)

        def start_batch_download():
            lines = url_input.toPlainText().strip().splitlines()
            urls = [line.strip() for line in lines if line.strip() and not line.startswith("#")]

            if not urls:
                QMessageBox.warning(dialog, "Error", "Please enter at least one valid URL or file.")
                return

            merged_content = "#EXTM3U\n"
            valid_count = 0
            url_data = []

            for url in urls:
                if not re.match(r'^https?://', url):
                    continue
                try:
                    session = setup_session()  # ← חדש
                    response = session.get(url, timeout=5)
                    response.raise_for_status()
                    content = response.text.strip()
                    if not content.startswith("#EXTM3U"):
                        continue
                    url_data.append((url, content))
                    merged_content += "\n".join(
                        line for line in content.splitlines() if line.strip() and not line.startswith("#EXTM3U")
                    ) + "\n"
                    valid_count += 1
                except Exception as e:
                    print(f"Failed to download: {url} — {e}")

            if valid_count == 0:
                QMessageBox.warning(dialog, "No Valid URLs", "None of the URLs were valid M3U files.")
                return

            choice = QMessageBox.question(
                dialog,
                "📥 Load All?",
                f"<b style='font-size:14px;'>✅ <u>{valid_count} M3U files</u> downloaded successfully.</b><br><br>"
                "<span style='font-size:13px;'>Do you want to load them all into the <b>editor</b>?</span>",
                QMessageBox.Yes | QMessageBox.No
            )

            if choice == QMessageBox.Yes:
                full_combined = "#EXTM3U\n"
                for (url, content) in url_data:
                    lines = [line for line in content.splitlines() if line.strip() and not line.startswith("#EXTM3U")]
                    full_combined += "\n".join(lines) + "\n"
                self.loadM3UFromText(full_combined, append=False)
                QMessageBox.information(dialog, "Loaded", "All M3U files were loaded into the editor.")
                dialog.close()
                return

            merge_choice = QMessageBox.question(
                dialog,
                "📦 Save Merged File?",
                f"<b style='font-size:14px;'>💾 Do you want to save all <u>{valid_count} files</u> as one merged M3U file?</b>",
                QMessageBox.Yes | QMessageBox.No
            )

            if merge_choice == QMessageBox.Yes:
                file_path, _ = QFileDialog.getSaveFileName(dialog, "Save Merged M3U File", "merged.m3u",
                                                           "M3U Files (*.m3u);;All Files (*)")
                if file_path:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(merged_content)
                    QMessageBox.information(dialog, "Saved", "Merged M3U file saved successfully.")
            else:
                save_dir = QFileDialog.getExistingDirectory(dialog, "Select Folder to Save Each M3U Separately")
                if save_dir:
                    for i, (url, content) in enumerate(url_data):
                        match = re.search(r'username=([a-zA-Z0-9]+)', url)
                        file_name = f"{match.group(1)}.m3u" if match else f"playlist_{i + 1}.m3u"
                        file_path = os.path.join(save_dir, file_name)

                        # ✅ כאן התיקון: נוסיף ניקוי שורות ריקות גם בשמירה נפרדת:
                        cleaned_content = "\n".join(
                            line for line in content.splitlines() if line.strip()
                        )

                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(cleaned_content)

                    QMessageBox.information(dialog, "Saved", "All M3U files saved individually.")

            dialog.close()

        download_button.clicked.connect(start_batch_download)
        dialog.exec_()

    def loadM3UFromText(self, content, append=False):
        """
        טוען טקסט M3U, דואג שתמיד תהיה שורת EXTM3U עם tvg-url,
        מנסה עברית תחילה, ומתעד מאיפה נאספו קישורי ה-EPG.
        """
        import threading

        # שמירה של התוכן האחרון עבור פונקציות משלימות
        self.last_loaded_m3u = content

        # אם לא append מנקים את הקטגוריות
        if not append:
            self.categories.clear()

        # ניהול meta למקורות EPG האחרונים
        if not hasattr(self, "last_epg_sources") or not append:
            self.last_epg_sources = []  # רשימת מחרוזות תיאור מקור ה-EPG

        # ----- 1) ניהול EPG headers -----
        # אתחול self.epg_headers בפעם הראשונה (או בכל load מחדש)
        if not hasattr(self, "epg_headers") or not append:
            self.epg_headers = []

        # שלב 1: אסוף את כל ה-EPG headers כפי שהם בקובץ
        detected_epg_headers = []
        for line in content.splitlines():  # splitlines() ללא strip
            if line.startswith("#EXTM3U") and ("url-tvg=" in line or "x-tvg-url=" in line or "tvg-url=" in line):
                detected_epg_headers.append(line.strip())

        # שלב 2: הוספת headers ייחודיים (איחוד)
        for header in detected_epg_headers:
            if header not in self.epg_headers:
                self.epg_headers.append(header)

        if detected_epg_headers:
            self.last_epg_sources.append("EPG מהכותרת בקובץ")

        # אם אין אף header זמין, ננסה 2 מסלולים לפני merge_or_fix_epg:
        #   א. קובץ sidecar עם אותו שם בסיס (xml או xml.gz) => נבנה tvg-url ממנו
        #   ב. אם גם זה לא קיים, נשתמש ב-merge_or_fix_epg כדי לאחד ספקים מוכרים
        if not self.epg_headers:
            sidecar_urls = self._try_load_sidecar_epg()
            if sidecar_urls:
                # בנה header חדש על בסיס sidecar
                new_hdr = '#EXTM3U tvg-url="' + ",".join(sidecar_urls) + '"'
                self.epg_headers.append(new_hdr)
                self.last_epg_sources.append("EPG מקובץ sidecar מקומי")
            else:
                # איחוד/זיהוי אוטומטי מתוך ספקים
                try:
                    self.merge_or_fix_epg(content=content, prefer_hebrew=True, update_only=True)
                    if self.epg_headers:
                        self.last_epg_sources.append("EPG מ-EPG_providers_full.json")
                except Exception:
                    # אם נכשל, נמשיך גם בלי EPG כדי לא לחסום טעינה
                    pass

        # ----- 3) ניקוי כל שורות EXTM3U המקוריות מהתוכן -----
        lines = [line for line in content.splitlines() if not line.startswith("#EXTM3U")]

        # ----- 4) בניית שורת EXTM3U אחידה עם עדיפות לעברית -----
        unified_header = self.buildUnifiedEPGHeader()

        # מיזוג לכדי טקסט סופי להצגה ולעיבוד
        content2 = unified_header + "\n\n" + "\n".join(lines)

        # ----- 5) פרס קובץ M3U -----
        self.parseM3UContentEnhanced(content2)
        self.updateCategoryList()
        self.buildSearchCompleter()

        # ----- 6) בחירת קטגוריה ראשונה -----
        if self.categoryList.count() > 0:
            self.categoryList.setCurrentRow(0)
            self.display_channels(self.categoryList.currentItem())

        # ----- 7) סריקת לוגואים ברקע -----
        threading.Thread(
            target=self.extract_and_save_logos_for_all_channels,
            args=(content2,),
            daemon=True
        ).start()

    def extract_and_save_logos_for_all_channels(self, content):
        """
        סריקה חכמה – שומרת לוגואים רק אם הם לא קיימים, שומרת פעם אחת בסוף.
        """
        try:
            logo_db = {}
            if os.path.exists(LOGO_DB_PATH):
                with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                    logo_db = json.load(f)

            seen = set()
            updated = False  # נדע אם בכלל נוספו לוגואים

            lines = content.strip().splitlines()
            for i in range(len(lines)):
                if lines[i].startswith("#EXTINF:"):
                    name_match = re.search(r",(.+)", lines[i])
                    channel_name = name_match.group(1).strip() if name_match else ""

                    logo_match = re.search(r'tvg-logo="([^"]+)"', lines[i])
                    logo_url = logo_match.group(1).strip() if logo_match else ""

                    if not channel_name or not logo_url:
                        continue

                    # ודא שאין כפילויות
                    if (channel_name, logo_url) in seen:
                        continue
                    seen.add((channel_name, logo_url))

                    existing = logo_db.get(channel_name, [])
                    if isinstance(existing, str):
                        existing = [existing]

                    if logo_url not in existing:
                        if channel_name not in logo_db:
                            logo_db[channel_name] = []
                        if isinstance(logo_db[channel_name], str):
                            logo_db[channel_name] = [logo_db[channel_name]]
                        logo_db[channel_name].append(logo_url)
                        updated = True
                        print(f"[LOGO] ✅ {channel_name} | {logo_url}")

            if updated:
                with open(LOGO_DB_PATH, "w", encoding="utf-8") as f:
                    json.dump(logo_db, f, indent=2, ensure_ascii=False)
                print("[LOGO] ✔ כל הלוגואים החדשים נשמרו.")

            else:
                print("[LOGO] ⏩ אין לוגואים חדשים לשמירה.")

        except Exception as e:
            print(f"[LOGO ERROR] Failed to extract logos: {e}")

    def open_logo_manager(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("ניהול לוגואים לערוצים מישראל")
        dialog.setGeometry(200, 200, 800, 500)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        dialog.setStyleSheet("""
            QDialog {
                border: 4px solid red;
                background-color: white;
            }
            QHeaderView::section {
                background-color: black;
                color: white;
                font-weight: bold;
                padding: 4px;
            }
        """)

        layout = QVBoxLayout(dialog)

        # 🔍 שורת חיפוש
        search_box = QLineEdit()
        search_box.setPlaceholderText("🔍 חפש לפי שם ערוץ או כתובת לוגו")
        layout.addWidget(search_box)

        table = QTableWidget(dialog)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["✔", "שם ערוץ", "לוגו (URL)"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSortingEnabled(True)
        layout.addWidget(table)

        # ✅ רענון נתונים לטבלה
        def load_table_data():
            table.setRowCount(0)
            seen = set()  # לא להציג כפולים

            try:
                with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except:
                data = {}

            row = 0
            for name, logos in data.items():
                if is_israeli_channel("", name):
                    # ודא שהערך הוא תמיד רשימה
                    if isinstance(logos, str):
                        logos = [logos]
                    for logo in logos:
                        if (name, logo) in seen:
                            continue
                        seen.add((name, logo))
                        table.insertRow(row)
                        checkbox_item = QTableWidgetItem()
                        checkbox_item.setCheckState(Qt.Unchecked)
                        table.setItem(row, 0, checkbox_item)
                        table.setItem(row, 1, QTableWidgetItem(name))
                        table.setItem(row, 2, QTableWidgetItem(logo))
                        row += 1

        load_table_data()  # טען פעם ראשונה

        def filter_table():
            text = search_box.text().lower()
            for row in range(table.rowCount()):
                show = False
                for col in range(1, 3):  # שם ולוגו
                    item = table.item(row, col)
                    if item and text in item.text().lower():
                        show = True
                        break
                table.setRowHidden(row, not show)

        search_box.textChanged.connect(filter_table)

        # 🔘 כפתורים
        button_layout = QHBoxLayout()
        style_black = """
            QPushButton {
                background-color: black;
                color: white;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """
        style_red = """
            QPushButton {
                background-color: red;
                color: white;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """

        select_all_btn = QPushButton("בחר הכל")
        deselect_all_btn = QPushButton("בטל בחירה")
        refresh_btn = QPushButton("🔃 רענן טבלה")
        delete_btn = QPushButton("🗑️ מחק ערוצים נבחרים")
        close_btn = QPushButton("סגור")

        for btn in [select_all_btn, deselect_all_btn, refresh_btn, close_btn]:
            btn.setStyleSheet(style_black)
        delete_btn.setStyleSheet(style_red)

        def select_all():
            for row in range(table.rowCount()):
                item = table.item(row, 0)
                if item:
                    item.setCheckState(Qt.Checked)

        def deselect_all():
            for row in range(table.rowCount()):
                item = table.item(row, 0)
                if item:
                    item.setCheckState(Qt.Unchecked)

        def delete_selected():
            try:
                with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                    logos_data = json.load(f)
            except:
                logos_data = {}

            to_remove = {}  # name → [logos to remove]

            for row in range(table.rowCount()):
                checkbox_item = table.item(row, 0)
                name_item = table.item(row, 1)
                logo_item = table.item(row, 2)
                if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                    name = name_item.text().strip()
                    logo = logo_item.text().strip()
                    to_remove.setdefault(name, []).append(logo)

            removed_count = 0
            for name, logos_to_remove in to_remove.items():
                if name in logos_data:
                    existing = logos_data[name]
                    if isinstance(existing, str):
                        existing = [existing]
                    updated = [logo for logo in existing if logo not in logos_to_remove]
                    if updated:
                        logos_data[name] = updated
                    else:
                        del logos_data[name]
                    removed_count += len(logos_to_remove)

            if removed_count > 0:
                with open(LOGO_DB_PATH, "w", encoding="utf-8") as f:
                    json.dump(logos_data, f, indent=2, ensure_ascii=False)
                QMessageBox.information(dialog, "בוצע", f"הוסרו {removed_count} פריטים.")
                load_table_data()

        select_all_btn.clicked.connect(select_all)
        deselect_all_btn.clicked.connect(deselect_all)
        refresh_btn.clicked.connect(load_table_data)
        delete_btn.clicked.connect(delete_selected)
        close_btn.clicked.connect(dialog.close)

        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(deselect_all_btn)
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        dialog.exec_()

    def onCategorySelected(self, item):
        selected_category = item.text().strip()
        if '(' in selected_category:
            selected_category = selected_category.split('(')[0].strip()
        self.loadChannelsForCategory(selected_category)

    def handleSearchTextChanged(self, text):
        try:
            text = text.strip().lower()

            # 🧹 איפוס – אם אין טקסט
            if not text:
                # איפוס מהיר עם batch updates
                self.categoryList.setUpdatesEnabled(False)
                self.channelList.setUpdatesEnabled(False)

                white_color = QColor("white")
                for i in range(self.categoryList.count()):
                    self.categoryList.item(i).setBackground(white_color)
                for i in range(self.channelList.count()):
                    ch_item = self.channelList.item(i)
                    ch_item.setBackground(white_color)
                    ch_item.setSelected(False)

                self.categoryList.setUpdatesEnabled(True)
                self.channelList.setUpdatesEnabled(True)
                return

            # צבעים מוכנים מראש
            yellow_color = QColor("#fff88a")
            white_color = QColor("white")
            green_color = QColor("#c0ffc0")

            # 🔍 חיפוש בקטגוריות - מהיר יותר עם caching
            category_found = False
            category_count = self.categoryList.count()

            # השבתת עדכונים למהירות
            self.categoryList.setUpdatesEnabled(False)

            for i in range(category_count):
                item = self.categoryList.item(i)
                item_text = item.text()

                # cache של הטקסט הנקי
                if not hasattr(item, '_cached_clean_text'):
                    item._cached_clean_text = item_text.split(" (")[0].lower()

                if text in item._cached_clean_text:
                    item.setBackground(yellow_color)
                    if not category_found:  # רק פעם אחת
                        self.categoryList.setCurrentItem(item)
                        category_found = True
                else:
                    item.setBackground(white_color)

            self.categoryList.setUpdatesEnabled(True)

            # אם נמצאה קטגוריה - הצג את הערוצים
            if category_found:
                current_item = self.categoryList.currentItem()
                if current_item:
                    self.display_channels(current_item)
                return

            # 🔍 אם לא נמצאה קטגוריה – חפש בערוצים (מהיר יותר)
            if not category_found:
                # יצירת מילון מהיר לחיפוש אם לא קיים
                if not hasattr(self, '_channel_lookup_cache'):
                    self._channel_lookup_cache = {}
                    for category, channels in self.categories.items():
                        for channel in channels:
                            channel_clean = channel.split(" (")[0].lower()
                            if channel_clean not in self._channel_lookup_cache:
                                self._channel_lookup_cache[channel_clean] = []
                            self._channel_lookup_cache[channel_clean].append((category, channel))

                # חיפוש מהיר במילון
                found_channel = None
                found_category = None

                # חיפוש ישיר במילון
                for cached_channel, category_channel_pairs in self._channel_lookup_cache.items():
                    if text in cached_channel:
                        found_category, found_channel = category_channel_pairs[0]
                        break

                if found_channel and found_category:
                    # השבתת עדכונים
                    self.categoryList.setUpdatesEnabled(False)
                    self.channelList.setUpdatesEnabled(False)

                    # איפוס קטגוריות
                    for i in range(category_count):
                        self.categoryList.item(i).setBackground(white_color)

                    # מציאת וסימון הקטגוריה הנכונה
                    for i in range(category_count):
                        item = self.categoryList.item(i)
                        if found_category in item.text():
                            item.setBackground(yellow_color)
                            self.categoryList.setCurrentItem(item)
                            self.display_channels(item)
                            break

                    # מציאת וסימון הערוץ
                    channel_count = self.channelList.count()
                    for j in range(channel_count):
                        ch_item = self.channelList.item(j)
                        ch_text = ch_item.text().lower()
                        if text in ch_text:
                            ch_item.setSelected(True)
                            ch_item.setBackground(green_color)
                            self.channelList.scrollToItem(ch_item)
                            break
                        else:
                            ch_item.setSelected(False)
                            ch_item.setBackground(white_color)

                    # הפעלת עדכונים
                    self.categoryList.setUpdatesEnabled(True)
                    self.channelList.setUpdatesEnabled(True)

        except Exception as e:
            print(f"[Search Error] {e}")
            # ודא שהעדכונים מופעלים במקרה של שגיאה
            if hasattr(self, 'categoryList'):
                self.categoryList.setUpdatesEnabled(True)
            if hasattr(self, 'channelList'):
                self.channelList.setUpdatesEnabled(True)

    def _on_filters_changed(self):
        # מרענן את רשימת הערוצים לפי המסננים החדשים
        current_item = self.categoryList.currentItem() if hasattr(self, "categoryList") else None
        self.display_channels(current_item)
        # מעדכן רק את מונה המוצגים בכותרת Channels (לא את הגלובלי)
        if hasattr(self, "channelsHeaderCount") and hasattr(self, "channelList"):
            self.channelsHeaderCount.setText(str(self.channelList.count()))
        # המונה הגלובלי תמיד גלובלי
        if hasattr(self, "displayTotalChannels"):
            self.displayTotalChannels()

    def buildSearchCompleter(self):
        search_terms = list(self.categories.keys())
        for ch_list in self.categories.values():
            for ch in ch_list:
                search_terms.append(ch.split(" (")[0])
        completer = QCompleter(sorted(set(search_terms)), self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)  # ← מאפשר חיפוש גם באמצע
        self.searchBox.setCompleter(completer)

    def setup_channel_context_menu(self):
        self.channelList.setContextMenuPolicy(Qt.ActionsContextMenu)
        addToCategoryAction = QAction('Add to Category', self)
        addToCategoryAction.triggered.connect(self.add_to_category)
        self.channelList.addAction(addToCategoryAction)

        newCategoryAction = QAction('Create New Category with Channel', self)
        newCategoryAction.triggered.connect(self.create_new_category_with_channel)
        self.channelList.addAction(newCategoryAction)

    def add_to_category(self):
        selected_channel = self.channelList.currentItem().text()
        category, ok = QInputDialog.getItem(self, "Select Category", "Choose a category:", self.categories.keys(), 0,
                                            False)
        if ok and category:
            self.categories[category].append(selected_channel)
            self.updateCategoryList()  # Update your category view if necessary

    def create_new_category_with_channel(self):
        selected_channel = self.channelList.currentItem().text()
        category_name, ok = QInputDialog.getText(self, "New Category", "Enter new category name:")
        if ok and category_name:
            self.categories[category_name] = [selected_channel]
            self.updateCategoryList()  # Update your category view if necessary

    def openURLCheckerDialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Choose scan type")
        dialog.setFixedSize(250, 130)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        dialog.setStyleSheet("""
            QDialog {
                border: 4px solid red;
                background-color: white;
            }
        """)

        layout = QVBoxLayout(dialog)

        label = QLabel("Choose scan type:")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        btn_scan_category = QPushButton("Scan Selected Category")
        btn_scan_category.setStyleSheet("background-color: purple; color: white; font-weight: bold; padding: 5px;")
        btn_scan_all = QPushButton("Scan All Channels")
        btn_scan_all.setStyleSheet("background-color: red; color: white; font-weight: bold; padding: 5px;")

        layout.addWidget(btn_scan_category)
        layout.addWidget(btn_scan_all)

        btn_scan_category.clicked.connect(lambda: [dialog.accept(), self.showCategoryPickerDialog()])
        btn_scan_all.clicked.connect(lambda: [dialog.accept(), self.startURLCheckAllChannels()])

        dialog.exec_()

    def ensure_epg_url_header(content):
        """
        מקבל את תוכן הקובץ כטקסט, מזהה את כל שורות ה־EPG ומחזיר אותן מסודרות בתחילת הקובץ,
        תוך שמירה על שורת ה־#EXTM3U בראש.
        """
        lines = content.strip().splitlines()

        # ודא שיש EXT_HEADER
        if not lines or not lines[0].startswith("#EXTM3U"):
            lines.insert(0, "#EXTM3U")

        # חילוץ שורות EPG
        epg_lines = [line for line in lines if line.startswith("#EXTM3U x-tvg-url=")]
        # הסרת שורות EPG ממיקומן המקורי
        cleaned_lines = [line for line in lines if
                         not line.startswith("#EXTM3U x-tvg-url=") and not line.startswith("#EXTM3U")]

        # בניית תוכן חדש
        result_lines = ["#EXTM3U"] + epg_lines + cleaned_lines
        return "\n".join(result_lines)

    # שימוש בפונקציה זו:
    # fixed_content = ensure_epg_url_header(original_content)
    # self.textEdit.setPlainText(fixed_content)

    def mergeM3Us(self):
        """מיזוג קובץ M3U נוסף לפלייליסט הקיים - גרסה מתוקנת"""

        # שמירת מצב הנוכחי לפני המיזוג
        channels_before = self.count_total_channels()

        # בחירת קובץ לצירוף
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Open Additional M3U File",
            "",
            "M3U Files (*.m3u *.m3u8);;All Files (*)",
            options=options
        )
        if not fileName:
            return

        # קריאה לתוכן הקובץ
        try:
            with open(fileName, 'r', encoding='utf-8') as f:
                new_content = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read file:\n{e}")
            return

        # עיבוד השורות
        lines = [l.strip() for l in new_content.strip().splitlines() if l.strip()]

        # טעינת בסיס הלוגואים
        logo_db = {}
        if os.path.exists(LOGO_DB_PATH):
            try:
                with open(LOGO_DB_PATH, 'r', encoding='utf-8') as lf:
                    logo_db = json.load(lf)
            except:
                pass

        # ספירת ערוצים חדשים שנוספו (רק ערוצים תקינים)
        channels_added = 0
        merged_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # בדיקה אם זו שורת EXTINF
            if line.startswith("#EXTINF:"):
                # וידוא שיש URL בשורה הבאה
                if i + 1 < len(lines) and not lines[i + 1].startswith("#"):
                    extinf_line = line
                    url_line = lines[i + 1]

                    # חילוץ שם הערוץ
                    name_match = re.search(r',(.+)', extinf_line)
                    channel_name = name_match.group(1).strip() if name_match else "Unknown Channel"

                    # הזרקת לוגו
                    extinf_line = self.inject_logo(extinf_line, channel_name, logo_db)

                    # הוספה לרשימה
                    merged_lines.extend([extinf_line, url_line])
                    channels_added += 1

                    i += 2  # דילוג על שתי השורות שעובדו
                else:
                    # EXTINF ללא URL - דילוג
                    i += 1
            else:
                # שורה אחרת - דילוג
                i += 1

        if channels_added == 0:
            QMessageBox.information(self, "M3U Merge", "לא נמצאו ערוצים תקינים לצירוף")
            return

        # מיזוג התוכן לתוכן הקיים
        current_content = self.textEdit.toPlainText()

        # בניית התוכן החדש
        if current_content.strip():
            # יש תוכן קיים - הוספה בסוף
            if not current_content.endswith('\n'):
                current_content += '\n'
            new_full_content = current_content + '\n'.join(merged_lines)
        else:
            # אין תוכן קיים - יצירת קובץ חדש
            unified_header = self.buildUnifiedEPGHeader()
            new_full_content = unified_header + '\n' + '\n'.join(merged_lines)

        # עדכון התוכן בעורך
        self.textEdit.blockSignals(True)
        self.textEdit.setPlainText(new_full_content)
        self.textEdit.blockSignals(False)

        # מיזוג התוכן לקטגוריות (כולל כפילויות)
        merged_content_for_categories = '\n'.join(merged_lines)
        self.mergeM3UContentToCategories(merged_content_for_categories, allow_duplicates=True)

        # עדכון תצוגה
        self.cleanEmptyCategories()
        self.updateCategoryList()
        self.regenerateM3UTextOnly()

        # חזרה לקטגוריה הראשונה אם קיימת
        if self.categoryList.count():
            self.categoryList.setCurrentRow(0)
            self.display_channels(self.categoryList.currentItem())

        # ספירת ערוצים אחרי המיזוג
        channels_after = self.count_total_channels()
        actual_added = channels_after - channels_before

        # עדכון תצוגת שם הקובץ
        current_file_text = self.fileNameLabel.text()
        if "Merged with:" not in current_file_text:
            self.fileNameLabel.setText(f"{current_file_text} | Merged with: {os.path.basename(fileName)}")
        else:
            self.fileNameLabel.setText(f"{current_file_text}, {os.path.basename(fileName)}")

        # הצגת הודעת הצלחה עם פירוט
        message = f"""המיזוג הושלם בהצלחה!

    📊 סיכום:
    • ערוצים שנוספו: {channels_added}
    • סה"כ ערוצים לפני: {channels_before:,}
    • סה"כ ערוצים אחרי: {channels_after:,}
    • הגידול בפועל: {actual_added:,}

    ✅ כל הערוצים והקטגוריות נוספו לפלייליסט"""

        QMessageBox.information(self, "M3U Merge Completed", message)

        # בדיקת עקביות (אופציונלי - להסרה בייצור)
        if actual_added != channels_added:
            print(f"Warning: Expected {channels_added} but actual increase was {actual_added}")

    def count_total_channels(self):
        """ספירת סה"כ ערוצים בכל הקטגוריות"""
        total = 0
        for category_channels in self.categories.values():
            total += len(category_channels)
        return total

    def loadM3UFromText(self, content, append=False):
        # אם לא append מנקים את הקטגוריות
        if not append:
            self.categories.clear()

        # ----- 1️⃣ ניהול EPG headers -----
        # אתחול self.epg_headers בפעם הראשונה (או בכל load מחדש)
        if not hasattr(self, "epg_headers") or not append:
            self.epg_headers = []

        # שלב 1: אסוף את כל ה־EPG headers (בלי strip על כל הקובץ)
        detected_epg_headers = []
        for line in content.splitlines():  # <-- splitlines() בלי strip()
            if line.startswith("#EXTM3U") and ("url-tvg=" in line or "x-tvg-url=" in line):
                detected_epg_headers.append(line.strip())

        # שלב 2: הוספת headers ייחודיים
        for header in detected_epg_headers:
            if header not in self.epg_headers:
                self.epg_headers.append(header)

        # שלב 3: ניקוי כל שורות EXTМ3U (בלי להסיר רווחים)
        lines = [
            line for line in content.splitlines()  # <-- שוב splitlines() בלי strip()
            if not line.startswith("#EXTM3U")
        ]

        # ----- 2️⃣ בניית שורת EXTМ3U אחידה -----
        unified_header = self.buildUnifiedEPGHeader()
        # מוסיפים שתי השורות הבאות: כותרת, שורה ריקה, ואז כל התוכן
        content2 = unified_header + "\n\n" + "\n".join(lines)

        # ----- 4️⃣ פרס קובץ M3U -----
        self.parseM3UContentEnhanced(content2)
        self.updateCategoryList()
        self.buildSearchCompleter()

        # ----- 5️⃣ בחירת קטגוריה ראשונה -----
        if self.categoryList.count() > 0:
            self.categoryList.setCurrentRow(0)
            self.display_channels(self.categoryList.currentItem())

        # ----- 6️⃣ סריקת לוגואים ברקע -----
        threading.Thread(
            target=self.extract_and_save_logos_for_all_channels,
            args=(content2,),
            daemon=True
        ).start()

    def mergeM3UContentToCategories(self, content, allow_duplicates=True):
        """
        ממזג תוכן M3U לתוך self.categories.
        אם allow_duplicates=True – מוסיף גם ערוצים שכבר קיימים באותה קטגוריה.
        גרסה מתוקנת עם טיפול משופר בשגיאות וספירה מדויקת.
        """
        if not content or not content.strip():
            return

        lines = [line.strip() for line in content.strip().splitlines() if line.strip()]

        # אתחול המטמון של EXTINF אם לא קיים
        if not hasattr(self, 'extinf_lookup'):
            self.extinf_lookup = {}

        # משתנים למעקב
        channels_processed = 0
        categories_created = 0

        i = 0
        while i < len(lines):
            line = lines[i]

            # בדיקה אם זו שורת EXTINF
            if line.startswith("#EXTINF:"):
                # וידוא שיש שורת URL אחריה
                if i + 1 >= len(lines) or lines[i + 1].startswith("#"):
                    print(f"Warning: EXTINF line without URL at index {i}: {line}")
                    i += 1
                    continue

                extinf_line = line
                url_line = lines[i + 1]

                # וידוא שה-URL תקין
                if not (url_line.startswith("http://") or url_line.startswith("https://") or
                        url_line.startswith("rtmp://") or url_line.startswith("rtsp://")):
                    print(f"Warning: Invalid URL format at index {i + 1}: {url_line}")
                    i += 2
                    continue

                # חילוץ שם הערוץ
                name_match = re.search(r',(.+)', extinf_line)
                if not name_match:
                    print(f"Warning: No channel name found in EXTINF: {extinf_line}")
                    i += 2
                    continue

                channel_name = name_match.group(1).strip()
                if not channel_name:
                    print(f"Warning: Empty channel name in EXTINF: {extinf_line}")
                    i += 2
                    continue

                # חילוץ קטגוריה
                group_match = re.search(r'group-title="([^"]*)"', extinf_line)
                category = group_match.group(1).strip() if group_match else "Uncategorized📺"

                # וידוא שהקטגוריה לא ריקה
                if not category:
                    category = "Uncategorized📺"

                # חילוץ לוגו (אופציונלי)
                logo_match = re.search(r'tvg-logo="([^"]*)"', extinf_line)
                logo = logo_match.group(1).strip() if logo_match else None

                # יצירת רשומת ערוץ
                channel_entry = f"{channel_name} ({url_line})"

                # הוספת לוגו לרשומה אם קיים
                if logo and logo.strip():
                    channel_entry += f' tvg-logo="{logo}"'

                # יצירת הקטגוריה אם לא קיימת
                if category not in self.categories:
                    self.categories[category] = []
                    categories_created += 1
                    print(f"Created new category: {category}")

                # בדיקת כפילויות
                should_add = True
                if not allow_duplicates:
                    # בדיקה מדויקת יותר - השוואה לפי שם וURL
                    existing_entries = self.categories[category]
                    for existing_entry in existing_entries:
                        existing_name = existing_entry.split(" (")[0].strip()
                        existing_url_match = re.search(r'\(([^)]+)\)', existing_entry)
                        existing_url = existing_url_match.group(1) if existing_url_match else ""

                        if existing_name == channel_name and existing_url == url_line:
                            should_add = False
                            print(f"Duplicate found in category '{category}': {channel_name}")
                            break

                # הוספת הערוץ
                if should_add:
                    self.categories[category].append(channel_entry)
                    channels_processed += 1

                    # שמירת EXTINF למעקב
                    self.extinf_lookup[channel_entry] = extinf_line

                    print(f"Added channel to '{category}': {channel_name}")

                i += 2  # דילוג על שתי השורות שעובדו

            else:
                # שורה שאינה EXTINF - דילוג
                i += 1

        print(f"Merge completed: {channels_processed} channels added, {categories_created} categories created")

    def cleanEmptyCategories(self):
        """
        מסיר קטגוריות ריקות מ-self.categories
        גרסה משופרת עם לוגים
        """
        empty_categories = []

        for category_name, channels in list(self.categories.items()):
            # בדיקה אם הקטגוריה ריקה או מכילה רק ערוצים לא תקינים
            valid_channels = []
            for channel in channels:
                # בדיקה שהערוץ מכיל שם ו-URL
                if " (" in channel and channel.endswith(")"):
                    name_part = channel.split(" (")[0].strip()
                    url_part = channel.split(" (")[1].rstrip(")").strip()

                    if name_part and url_part:
                        valid_channels.append(channel)

            if not valid_channels:
                empty_categories.append(category_name)
            else:
                # עדכון הקטגוריה עם ערוצים תקינים בלבד
                self.categories[category_name] = valid_channels

        # הסרת קטגוריות ריקות
        for empty_cat in empty_categories:
            print(f"Removing empty category: {empty_cat}")
            del self.categories[empty_cat]

        if empty_categories:
            print(f"Cleaned {len(empty_categories)} empty categories")

    def validateChannelEntry(self, channel_entry):
        """
        בודק אם רשומת ערוץ תקינה
        מחזיר: (is_valid: bool, channel_name: str, url: str, error_msg: str)
        """
        if not channel_entry or not isinstance(channel_entry, str):
            return False, "", "", "Empty or invalid entry type"

        channel_entry = channel_entry.strip()
        if not channel_entry:
            return False, "", "", "Empty entry after strip"

        # בדיקת פורמט בסיסי
        if " (" not in channel_entry or not channel_entry.endswith(")"):
            return False, "", "", "Invalid format - missing '(' or ')'"

        try:
            # חילוץ שם ו-URL
            name_part = channel_entry.split(" (")[0].strip()
            url_with_extras = channel_entry.split(" (", 1)[1].rstrip(")")

            # חילוץ URL (עד לרווח הראשון או סוף המחרוזת)
            url_part = url_with_extras.split()[0] if url_with_extras else ""

            # בדיקות תקינות
            if not name_part:
                return False, name_part, url_part, "Empty channel name"

            if not url_part:
                return False, name_part, url_part, "Empty URL"

            # בדיקת פורמט URL
            valid_protocols = ["http://", "https://", "rtmp://", "rtsp://"]
            if not any(url_part.startswith(protocol) for protocol in valid_protocols):
                return False, name_part, url_part, f"Invalid URL protocol: {url_part}"

            return True, name_part, url_part, ""

        except Exception as e:
            return False, "", "", f"Error parsing entry: {str(e)}"

    def getChannelStatistics(self):
        """
        מחזיר סטטיסטיקות מפורטות על הערוצים
        """
        stats = {
            'total_channels': 0,
            'total_categories': len(self.categories),
            'valid_channels': 0,
            'invalid_channels': 0,
            'categories_with_channels': {},
            'empty_categories': [],
            'duplicate_names': [],
            'protocol_distribution': {},
            'validation_errors': []
        }

        all_names = []

        for category_name, channels in self.categories.items():
            category_valid = 0
            category_invalid = 0

            if not channels:
                stats['empty_categories'].append(category_name)
                continue

            for channel in channels:
                stats['total_channels'] += 1

                is_valid, name, url, error = self.validateChannelEntry(channel)

                if is_valid:
                    stats['valid_channels'] += 1
                    category_valid += 1
                    all_names.append(name.lower())

                    # ספירת פרוטוקולים
                    if url.startswith('http://'):
                        stats['protocol_distribution']['HTTP'] = stats['protocol_distribution'].get('HTTP', 0) + 1
                    elif url.startswith('https://'):
                        stats['protocol_distribution']['HTTPS'] = stats['protocol_distribution'].get('HTTPS', 0) + 1
                    elif url.startswith('rtmp://'):
                        stats['protocol_distribution']['RTMP'] = stats['protocol_distribution'].get('RTMP', 0) + 1
                    elif url.startswith('rtsp://'):
                        stats['protocol_distribution']['RTSP'] = stats['protocol_distribution'].get('RTSP', 0) + 1
                else:
                    stats['invalid_channels'] += 1
                    category_invalid += 1
                    stats['validation_errors'].append(f"Category '{category_name}': {error}")

            if category_valid > 0:
                stats['categories_with_channels'][category_name] = {
                    'valid': category_valid,
                    'invalid': category_invalid,
                    'total': len(channels)
                }

        # זיהוי כפילויות
        name_counts = {}
        for name in all_names:
            name_counts[name] = name_counts.get(name, 0) + 1

        stats['duplicate_names'] = [name for name, count in name_counts.items() if count > 1]

        return stats

    def ensure_extm3u_header(self):
        """
        Ensure that the content starts with #EXTM3U.
        """
        content = self.textEdit.toPlainText()
        if not content.startswith("#EXTM3U"):
            self.textEdit.blockSignals(True)
            self.safely_update_text_edit("#EXTM3U\n" + content)
            self.textEdit.blockSignals(False)

    from PyQt5.QtWidgets import QAbstractItemView

    def create_category_section(self):
        layout = QVBoxLayout()

        # כותרת קטגוריות
        category_title = QLabel("Categories", self)
        category_title.setAlignment(Qt.AlignCenter)
        category_title.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(category_title)

        # קומבובוקס מיון קטגוריות
        self.categorySortComboBox = QComboBox(self)
        self.categorySortComboBox.addItems([
            "Sort Categories A-Z",
            "Sort Categories Z-A",
            "Sort by Channel Count (Most to Least)",
            "Sort by Channel Count (Least to Most)",
            "Sort Hebrew Categories A-Z",
            "Sort by Channel Name Length",
            "Sort by Online Channel Count (Descending)",
            "Sort by Country/Language in Category",
            "Sort by English Category Name"  # ✅ חדש
        ])

        self.categorySortComboBox.currentIndexChanged.connect(self.sortCategories)
        layout.addWidget(self.categorySortComboBox)

        # כפתורי פעולות
        button_layout = QHBoxLayout()

        self.addCategoryButton = QPushButton('Add Category')
        self.updateCategoryButton = QPushButton('Edit Category Name')
        self.deleteCategoryButton = QPushButton('Delete Selected')
        self.moveCategoryUpButton = QPushButton('Move Category Up')
        self.moveCategoryDownButton = QPushButton('Move Category Down')
        self.selectAllButton = QPushButton('Select All')
        self.deselectAllButton = QPushButton('Deselect All')
        self.translateCategoriesButton = QPushButton("🌍 Auto Translate")

        # צבעים לכפתורים
        self.selectAllButton.setStyleSheet("background-color: navy; color: white;")
        self.deselectAllButton.setStyleSheet("background-color: navy; color: white;")
        self.updateCategoryButton.setStyleSheet("background-color: red; color: white;")
        self.deleteCategoryButton.setStyleSheet("background-color: red; color: white;")
        self.addCategoryButton.setStyleSheet("background-color: green; color: white;")
        self.moveCategoryUpButton.setStyleSheet("background-color: green; color: white;")
        self.moveCategoryDownButton.setStyleSheet("background-color: green; color: white;")
        self.translateCategoriesButton.setStyleSheet("background-color: navy; color: white;")

        # הוספת הכפתורים לשורה
        button_layout.addWidget(self.addCategoryButton)
        button_layout.addWidget(self.updateCategoryButton)
        button_layout.addWidget(self.deleteCategoryButton)
        button_layout.addWidget(self.moveCategoryUpButton)
        button_layout.addWidget(self.moveCategoryDownButton)
        button_layout.addWidget(self.selectAllButton)
        button_layout.addWidget(self.deselectAllButton)
        button_layout.addWidget(self.translateCategoriesButton)

        layout.addLayout(button_layout)

        # רשימת קטגוריות
        self.categoryList = QListWidget(self)
        from PyQt5.QtWidgets import QSizePolicy
        self.categoryList.setMinimumHeight(300)  # הגדלת חלון הקטגוריות
        self.categoryList.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.categoryList.setStyleSheet("font-size: 12pt;")

        self.categoryList.setSelectionMode(QAbstractItemView.MultiSelection)  # בחירה מרובה
        layout.addWidget(self.categoryList)

        # חיבור פעולות
        self.addCategoryButton.clicked.connect(self.addCategory)
        self.updateCategoryButton.clicked.connect(self.updateCategoryName)
        self.deleteCategoryButton.clicked.connect(self.deleteSelectedCategories)
        self.moveCategoryUpButton.clicked.connect(self.moveCategoryUp)
        self.moveCategoryDownButton.clicked.connect(self.moveCategoryDown)
        self.selectAllButton.clicked.connect(self.selectAllCategories)
        self.deselectAllButton.clicked.connect(self.deselectAllCategories)
        self.categoryList.itemClicked.connect(self.display_channels)
        self.translateCategoriesButton.clicked.connect(self.translate_category_names)
        self.categoryList.setMinimumHeight(180)  # או 220 אם תרצה יותר

        return layout

    def create_Tools(self):
        layout = QVBoxLayout()
        tools_title = QLabel("Tools", self)
        tools_title.setAlignment(Qt.AlignCenter)
        tools_title.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(tools_title)

        # Create a horizontal layout for the buttons
        buttons_layout = QHBoxLayout()

        self.batchM3UDownloadButton = QPushButton('🔀 Smart M3U Loader', self)
        self.batchM3UDownloadButton.setStyleSheet("background-color: black; color: white;")
        self.batchM3UDownloadButton.clicked.connect(self.openBatchDownloader)
        buttons_layout.addWidget(self.batchM3UDownloadButton)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        # M3U URL Converter button
        self.m3uUrlConverterButton = QPushButton('🔐 Xtream Converter', self)
        self.m3uUrlConverterButton.setStyleSheet("background-color: black; color: white;")
        self.m3uUrlConverterButton.clicked.connect(self.openM3UConverterDialog)
        buttons_layout.addWidget(self.m3uUrlConverterButton)

        self.convertPortalButton = QPushButton('🌐 Advanced Portal Converter', self)
        self.convertPortalButton.setStyleSheet("background-color: black; color: white;")
        self.convertPortalButton.clicked.connect(self.convertStalkerToM3U)
        buttons_layout.addWidget(self.convertPortalButton)

        # Export Groups button
        self.exportGroupButton = QPushButton('📤 Export Groups', self)
        self.exportGroupButton.setStyleSheet("background-color: black; color: white;")
        self.exportGroupButton.clicked.connect(self.openExportDialog)
        buttons_layout.addWidget(self.exportGroupButton)

        self.filterIsraelChannelsButton = QPushButton('🎯 Filtered Export', self)
        self.filterIsraelChannelsButton.setStyleSheet("background-color: black; color: white;")
        self.filterIsraelChannelsButton.clicked.connect(self.chooseFilterMethod)  # רק פעם אחת!

        # יצירת המערכת המתקדמת
        self.filter_system = M3UFilterEnhanced(self)

        buttons_layout.addWidget(self.filterIsraelChannelsButton)

        self.smartScanButton = QPushButton('🔍 Smart Scan', self)
        self.smartScanButton.setStyleSheet("background-color: black; color: white; font-weight: ;")
        self.smartScanButton.clicked.connect(self.openSmartScanDialog)
        buttons_layout.addWidget(self.smartScanButton)

        self.mergeEPGButton = QPushButton('📺 Fix EPG', self)
        self.mergeEPGButton.setStyleSheet("background-color: black; color: white;")
        self.mergeEPGButton.clicked.connect(self.merge_or_fix_epg)
        buttons_layout.addWidget(self.mergeEPGButton)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        # Add the horizontal layout to the vertical layout
        layout.addLayout(buttons_layout)

        return layout

    def convertStalkerToM3U(self):
        """המרת Portal/Stalker ל-M3U - גרסה מתקדמת"""

        if not PORTAL_CONVERTER_AVAILABLE:
            QMessageBox.critical(
                self,
                "Feature Not Available",
                "Portal Converter module is not available.\n"
                "Please ensure portal_extensions.py is in the M3U_EDITOR folder."
            )
            return

        try:
            # יצירת חלון הממיר המתקדם
            converter = AdvancedPortalConverter(self)
            converter.exec_()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Portal Converter Error",
                f"Failed to open Portal Converter:\n\n{str(e)}"
            )
            print(f"Portal Converter Error: {e}")

    def displayTotalChannels(self, file_name: str = None):
        """
        מציג תמיד את הסיכום הגלובלי: סה"כ ערוצים + סה"כ קטגוריות.
        לא תלוי בסינון.
        אם file_name ניתן, יעדכן גם את שם הקובץ.
        """
        import os
        total_channels = sum(len(ch_list) for ch_list in self.categories.values())
        total_categories = len(self.categories)
        summary = f"📺 Total Channels: {total_channels}   |   🗂 Categories: {total_categories}"
        if hasattr(self, "channelCountLabel"):
            self.channelCountLabel.setText(summary)
            self.channelCountLabel.setToolTip(f"{total_channels} ערוצים בסך הכל ב-{total_categories} קטגוריות")
        if file_name and hasattr(self, "fileNameLabel"):
            self.fileNameLabel.setText(f"Loaded File: {os.path.basename(file_name)}")

    def sortChannels(self):
        """
        ממיין את self.categories[<קטגוריה נוכחית>] עפ״י האפשרות שב-sortingComboBox
        ואז מרענן את התצוגה וה-M3U.
        """
        # בודק שיש קטגוריה נבחרת
        cur_item = self.categoryList.currentItem()
        if not cur_item:
            return

        # שם הקטגוריה (ללא הספירה שבסוגריים)
        cur_cat = cur_item.text().split(" (")[0].strip()
        if cur_cat not in self.categories:
            return

        # אופציית המיון הנבחרת מה-ComboBox
        option = self.sortingComboBox.currentText()
        channels = self.categories[cur_cat]

        if option == "Sort by Name A-Z":
            channels.sort(key=lambda x: x.split(" (")[0].lower())

        elif option == "Sort by Name Z-A":
            channels.sort(key=lambda x: x.split(" (")[0].lower(), reverse=True)

        elif option == "Sort by Stream Type":
            channels.sort(key=lambda x: x.split(",")[-1])

        elif option == "Sort by Group Title":
            channels.sort(key=lambda x: x.split('group-title="')[-1].split('"')[0])

        elif option == "Sort by URL Length":
            channels.sort(key=lambda x: len(x.split(" (")[-1]))

        elif option == "Sort by Quality (4K → SD)":
            # משתמש בפונקציה detect_stream_quality המזהה איכות מתוך המחרוזת
            def quality_rank(entry: str) -> int:
                q = detect_stream_quality(entry)
                return {
                    "4K": 0,
                    "FHD": 1,
                    "HD": 2,
                    "SD": 3
                }.get(q, 4)

            channels.sort(key=quality_rank)

        # שמירת התוצאה בחזרה במילון
        self.categories[cur_cat] = channels

        # רענון התצוגה וכתיבת ה-M3U המעודכן
        self.display_channels(cur_item)
        self.regenerateM3UTextOnly()

    def create_m3u_content_section(self):
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QVBoxLayout, QLabel, QTextEdit, QSizePolicy

        layout = QVBoxLayout()

        title = QLabel("M3U Content", self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 12px; font-weight: bold; margin:0; padding:0;")
        layout.addWidget(title)

        self.textEdit = QTextEdit(self)
        self.textEdit.setMinimumHeight(0)
        self.textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.textEdit)

        return layout

    def addCategory(self):
        category, ok = QInputDialog.getText(self, 'Add Category', 'Enter category name:')
        if ok and category and category not in self.categories:
            self.categories[category] = []
            self.updateCategoryList()  # Update the category list

    def updateCategoryList(self):
        """
        עדכון רשימת הקטגוריות עם ספירה,
        כולל שימור הבחירה הנוכחית ומיקום הגלילה.
        ממלא גם את פילטר הקטגוריות אם קיים.
        """
        # שמירת מצב לפני רענון
        prev_row = self.categoryList.currentRow() if hasattr(self, "categoryList") else -1
        prev_text = None
        if hasattr(self, "categoryList") and self.categoryList.currentItem():
            prev_text = self.categoryList.currentItem().text().split(" (")[0].strip()
        prev_scroll = self.categoryList.verticalScrollBar().value() if hasattr(self, "categoryList") else 0

        # בניה מחדש
        self.categoryList.blockSignals(True)
        self.categoryList.clear()
        for category, channels in self.categories.items():
            display_text = f"{category} ({len(channels)})"
            self.categoryList.addItem(display_text)
        self.categoryList.blockSignals(False)

        # שיחזור בחירה לפי טקסט קודם אם אפשר, אחרת לפי prev_row, אחרת שורה 0 אם קיימת
        restored = False
        if prev_text is not None:
            for i in range(self.categoryList.count()):
                if self.categoryList.item(i).text().split(" (")[0].strip() == prev_text:
                    self.categoryList.setCurrentRow(i)
                    restored = True
                    break
        if not restored and prev_row >= 0 and prev_row < self.categoryList.count():
            self.categoryList.setCurrentRow(prev_row)
            restored = True
        if not restored and self.categoryList.count() > 0 and self.categoryList.currentRow() < 0:
            self.categoryList.setCurrentRow(0)

        # שיחזור גלילה
        if hasattr(self, "categoryList"):
            self.categoryList.verticalScrollBar().setValue(prev_scroll)

        # עדכון הספירה הכללית
        if hasattr(self, "displayTotalChannels"):
            self.displayTotalChannels()
        elif hasattr(self, "channelCountLabel"):
            total = sum(len(chs) for chs in self.categories.values())
            self.channelCountLabel.setText(f"Total Channels: {total}")

        # מילוי פילטר הקטגוריות
        if hasattr(self, "categoryFilter"):
            self.categoryFilter.blockSignals(True)
            self.categoryFilter.clear()
            self.categoryFilter.addItem("כל הקטגוריות", "")
            for cat_name in self.categories.keys():
                self.categoryFilter.addItem(cat_name, cat_name)
            self.categoryFilter.blockSignals(False)

    def cleanEmptyCategories(self):
        """
        מנקה קטגוריות ריקות מתוך self.categories
        """
        self.categories = {cat: ch_list for cat, ch_list in self.categories.items() if ch_list}

    def loadChannelsForCategory(self, category_name):
        try:
            category_name = category_name.strip()
            if category_name not in self.categories:
                raise KeyError(f"Category '{category_name}' not found in categories.")

            self.currentCategory = category_name
            self.channelList.clear()

            for channel in self.categories[category_name]:
                if isinstance(channel, dict):  # במבנה החדש
                    display_name = channel.get("name", "")
                else:
                    display_name = channel.split(" (")[0].strip()

                self.channelList.addItem(display_name)

        except KeyError as ke:
            QMessageBox.critical(self, "Error", f"Failed to load category: {ke}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load category channels: {str(e)}")

    def updateCategoryName(self):
        """
        Updates the name of a selected category and updates the M3U content accordingly.
        """
        selected_item = self.categoryList.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "No category selected for renaming.")
            return

        old_category_name = selected_item.text().split(" (")[0]
        new_category_name, ok = QInputDialog.getText(self, 'Edit Category', 'Enter new category name:',
                                                     text=old_category_name)
        if ok and new_category_name and new_category_name != old_category_name:
            if new_category_name in self.categories:
                QMessageBox.warning(self, "Warning", f"The category '{new_category_name}' already exists.")
                return

            # Update the category in the dictionary
            self.categories[new_category_name] = self.categories.pop(old_category_name)

            # Update the M3U content
            updated_lines = []
            for line in self.textEdit.toPlainText().splitlines():
                if f'group-title="{old_category_name}"' in line:
                    line = line.replace(f'group-title="{old_category_name}"', f'group-title="{new_category_name}"')
                updated_lines.append(line)

            # Update the UI
            self.safely_update_text_edit("\n".join(updated_lines))
            self.updateCategoryList()
            QMessageBox.information(self, "Success",
                                    f"Category '{old_category_name}' has been renamed to '{new_category_name}'.")

    def deleteSelectedCategories(self):
        """
        Deletes the selected categories and removes their associated channels and M3U records.
        """
        selected_items = self.categoryList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No categories selected for deletion.")
            return

        # Get a list of selected category names
        categories_to_delete = [item.text().split(" (")[0] for item in selected_items]

        try:
            # Remove selected categories from the dictionary
            for category in categories_to_delete:
                if category in self.categories:
                    del self.categories[category]

            # Update the M3U content to remove records associated with the deleted categories
            updated_lines = []
            skip_next_line = False  # Flag to skip URLs associated with a deleted category
            for line in self.textEdit.toPlainText().splitlines():
                if skip_next_line:
                    skip_next_line = False  # Reset the flag after skipping the URL line
                    continue

                # If the line contains a deleted category, mark the next line to be skipped
                if line.startswith("#EXTINF") and any(f'group-title="{cat}"' in line for cat in categories_to_delete):
                    skip_next_line = True
                    continue

                # Add the line to the updated content if it doesn't match a deleted category
                updated_lines.append(line)

            # Update the QTextEdit with the modified content
            self.safely_update_text_edit("\n".join(updated_lines))

            # Refresh the category list in the UI
            self.updateCategoryList()

            # Clear the channels list UI if the selected category is deleted
            self.channelList.clear()

            QMessageBox.information(self, "Success", "Selected categories and their records have been removed.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while deleting categories: {str(e)}")
            self.displayTotalChannels()

    def moveCategoryUp(self):
        try:
            current_row = self.categoryList.currentRow()
            if current_row <= 0:
                return

            # חסימת סיגנלים ועדכונים בזמן ההזזה
            self.categoryList.blockSignals(True)
            self.setUpdatesEnabled(False)

            # הזזת הפריט ברשימת ה-UI
            item = self.categoryList.takeItem(current_row)
            if item is None:
                # הגנה למקרה נדיר
                self.categoryList.blockSignals(False)
                self.setUpdatesEnabled(True)
                return

            self.categoryList.insertItem(current_row - 1, item)
            self.categoryList.setCurrentRow(current_row - 1)

            # עדכון סדר המילון במהירות וללא הקפצות
            keys = list(self.categories.keys())
            keys[current_row - 1], keys[current_row] = keys[current_row], keys[current_row - 1]

            # בנייה מחדש על בסיס הצילום הקיים כדי למנוע גישה תוך שינוי
            old_categories = self.categories
            self.categories = {k: old_categories[k] for k in keys}

        except Exception as e:
            try:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"moveCategoryUp failed: {e}")
            except Exception:
                pass
        finally:
            # שחרור חסימות ועדכונים
            self.categoryList.blockSignals(False)
            self.setUpdatesEnabled(True)

            # רענון מושהה לטיק הבא של לולאת האירועים למניעת קריסות Qt
            idx = max(0, current_row - 1)
            QTimer.singleShot(0, lambda: self.refreshCategoryListOnly(selected_index=idx))
            QTimer.singleShot(0, self.regenerateM3UTextOnly)

    def moveCategoryDown(self):
        try:
            current_row = self.categoryList.currentRow()
            last_index = self.categoryList.count() - 1
            if current_row < 0 or current_row >= last_index:
                return

            # חסימת סיגנלים ועדכונים בזמן ההזזה
            self.categoryList.blockSignals(True)
            self.setUpdatesEnabled(False)

            # הזזת הפריט ברשימת ה-UI
            item = self.categoryList.takeItem(current_row)
            if item is None:
                self.categoryList.blockSignals(False)
                self.setUpdatesEnabled(True)
                return

            self.categoryList.insertItem(current_row + 1, item)
            self.categoryList.setCurrentRow(current_row + 1)

            # עדכון סדר המילון במהירות וללא הקפצות
            keys = list(self.categories.keys())
            keys[current_row], keys[current_row + 1] = keys[current_row + 1], keys[current_row]

            old_categories = self.categories
            self.categories = {k: old_categories[k] for k in keys}

        except Exception as e:
            try:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"moveCategoryDown failed: {e}")
            except Exception:
                pass
        finally:
            # שחרור חסימות ועדכונים
            self.categoryList.blockSignals(False)
            self.setUpdatesEnabled(True)

            # רענון מושהה לטיק הבא של לולאת האירועים
            idx = min(self.categoryList.count() - 1, current_row + 1)
            QTimer.singleShot(0, lambda: self.refreshCategoryListOnly(selected_index=idx))
            QTimer.singleShot(0, self.regenerateM3UTextOnly)

    def sortCategories(self):
        sort_option = self.categorySortComboBox.currentText()

        if not self.categories:
            return

        def is_hebrew(text):
            return any('\u0590' <= c <= '\u05EA' for c in text)

        def get_english_name(cat_name):
            parts = cat_name.split('|')
            if len(parts) > 1:
                return parts[1].strip().lower()
            return cat_name.strip().lower()

        if sort_option == "Sort Categories A-Z":
            sorted_items = sorted(self.categories.items(), key=lambda x: x[0].lower())

        elif sort_option == "Sort Categories Z-A":
            sorted_items = sorted(self.categories.items(), key=lambda x: x[0].lower(), reverse=True)

        elif sort_option == "Sort by Channel Count (Most to Least)":
            sorted_items = sorted(self.categories.items(), key=lambda x: len(x[1]), reverse=True)

        elif sort_option == "Sort by Channel Count (Least to Most)":
            sorted_items = sorted(self.categories.items(), key=lambda x: len(x[1]))

        elif sort_option == "Sort Hebrew Categories A-Z":
            hebrew_categories = {k: v for k, v in self.categories.items() if is_hebrew(k)}
            non_hebrew_categories = {k: v for k, v in self.categories.items() if not is_hebrew(k)}
            sorted_hebrew = sorted(hebrew_categories.items(), key=lambda x: x[0])
            sorted_non_hebrew = sorted(non_hebrew_categories.items(), key=lambda x: x[0])
            sorted_items = sorted_hebrew + sorted_non_hebrew

        elif sort_option == "Sort by Channel Name Length":
            sorted_items = sorted(self.categories.items(),
                                  key=lambda x: sum(len(ch.split(' (')[0]) for ch in x[1]) / (len(x[1]) or 1))

        elif sort_option == "Sort by Online Channel Count (Descending)":
            sorted_items = sorted(self.categories.items(), key=lambda x: len(x[1]), reverse=True)

        elif sort_option == "Sort by Country/Language in Category":
            country_order = ['il', 'usa', 'uk', 'fr', 'es', 'de', 'ru', 'ar']  # דוגמה

            def get_country_index(name):
                for i, country in enumerate(country_order):
                    if country in name.lower():
                        return i
                return len(country_order) + 1

            sorted_items = sorted(self.categories.items(), key=lambda x: get_country_index(x[0]))

        elif sort_option == "Sort by English Category Name":
            sorted_items = sorted(self.categories.items(), key=lambda x: get_english_name(x[0]))

        else:
            return

        self.categories = dict(sorted_items)
        self.refreshCategoryListOnly()
        self.regenerateM3UTextOnly()

    def buildUnifiedEPGHeader(self):
        if hasattr(self, "epg_headers") and self.epg_headers:
            urls = []
            for header in self.epg_headers:
                matches = re.findall(r'(?:url-tvg|x-tvg-url|tvg-url)="([^"]+)"', header)
                for match in matches:
                    for url in match.split(","):
                        cleaned = url.strip()
                        if cleaned and cleaned not in urls:
                            urls.append(cleaned)
            if urls:
                return f'#EXTM3U tvg-url="{",".join(urls)}"'
        return "#EXTM3U"

    def regenerateM3UTextOnly(self, fast_mode=True):
        # מטמון סטטי לביצועים מקסימליים
        if not hasattr(self, '_logo_db_cache'):
            self._logo_db_cache = {}
            self._logo_db_timestamp = 0

        # בדיקת מטמון מאוד מהירה
        logo_db = self._logo_db_cache
        if fast_mode and os.path.exists(LOGO_DB_PATH):
            try:
                stat = os.stat(LOGO_DB_PATH)
                if stat.st_mtime > self._logo_db_timestamp:
                    with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                        self._logo_db_cache = json.load(f)
                        self._logo_db_timestamp = stat.st_mtime
                        logo_db = self._logo_db_cache
            except Exception as e:
                print(f"[LOGO] Failed to load logo DB: {e}")

        # EPG header - מהיר מאוד
        if hasattr(self, "epg_headers") and self.epg_headers:
            header = self.buildUnifiedEPGHeader()
        else:
            header = "#EXTM3U"

        # יצירת רשימה אחת גדולה במקום append מרובים - מהיר פי 50
        all_lines = [header]

        # אופטימיזציה מטורפת: list comprehension עם פעולה אחת
        for category, channels in self.categories.items():
            # פילטרינג וחיתוך מהיר במקום try/except איטי
            valid_channels = [
                (ch.split(" (", 1)[0].strip(), ch.split(" (", 1)[1].strip(") \n"))
                for ch in channels
                if " (" in ch and ch.count(" (") == 1
            ]

            # יצירת שורות M3U במקבץ - מהיר פי 100
            for name, url in valid_channels:
                # בדיקת logo מהירה
                logo_url = logo_db.get(name)
                if isinstance(logo_url, list) and logo_url:
                    logo_url = logo_url[0]

                # בנייה מהירה של EXTINF
                if logo_url:
                    extinf = f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="{category}",{name}'
                else:
                    extinf = f'#EXTINF:-1 group-title="{category}",{name}'

                all_lines.extend([extinf, url])

        # join אחד במקום הרבה - מהיר פי 1000
        self.safely_update_text_edit("\n".join(all_lines))

    def exportM3UWithLogos(self, path):
        """
        ייצוא קובץ M3U לאחר הזרקת לוגואים מתוך ה־DB.
        """
        if not self.full_text:
            print("⛔ אין תוכן לייצא.")
            return

        try:
            lines = self.full_text.strip().splitlines()
            result = []
            for line in lines:
                if line.startswith("#EXTINF:"):
                    name_match = re.search(r",(.+)", line)
                    channel_name = name_match.group(1).strip() if name_match else ""
                    if 'tvg-logo="' not in line:
                        logo = get_saved_logo(channel_name)
                        if logo and isinstance(logo, str) and logo.startswith("http"):
                            line = line.replace("#EXTINF:-1", f'#EXTINF:-1 tvg-logo="{logo}"')
                result.append(line)

            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(result))

            print(f"[LOGO] ✅ ייצוא עם לוגואים בוצע: {path}")

        except Exception as e:
            print(f"[LOGO] ❌ שגיאה בייצוא עם לוגואים: {e}")

    def get_saved_logo(channel_name):
        try:
            with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                logos = json.load(f)
                logo = logos.get(channel_name)
                if isinstance(logo, list):
                    return logo[0] if logo else None
                return logo
        except Exception as e:
            print(f"[LOGO] שגיאה בקריאת בסיס לוגואים: {e}")
            return None

    def refreshCategoryListOnly(self, selected_index=None):
        self.categoryList.clear()
        for category in self.categories:
            channel_count = len(self.categories[category])
            self.categoryList.addItem(f"{category} ({channel_count})")
        if selected_index is not None:
            self.categoryList.setCurrentRow(selected_index)

    def selectAllCategories(self):
        """Select all categories in the list."""
        for i in range(self.categoryList.count()):
            item = self.categoryList.item(i)
            item.setSelected(True)  # Ensure each item is selected

    def deselectAllCategories(self):
        """Deselect all categories in the list."""
        for i in range(self.categoryList.count()):
            item = self.categoryList.item(i)
            item.setSelected(False)  # Ensure each item is deselected

    def addChannel(self):
        name, ok1 = QInputDialog.getText(self, 'Add Channel', 'Enter channel name:')
        url, ok2 = QInputDialog.getText(self, 'Add Channel', 'Enter channel URL:')
        if ok1 and ok2:
            full_entry = f"{name} ({url})"
            channel_item = QListWidgetItem(name)
            # ← שמירה של המחרוזת המלאה במקום אחד בלבד
            channel_item.setData(Qt.UserRole, full_entry)
            self.channelList.addItem(channel_item)

            selected_category = self.categoryList.currentItem()
            if selected_category:
                cat = selected_category.text().split(" (")[0].strip()
                self.categories[cat].append(full_entry)
                self.updateM3UContent()
            # אחרי כל שינוי ב-self.categories כדאי גם
            self.display_channels(self.categoryList.currentItem())

    def deleteSelectedChannels(self):
        try:
            if not hasattr(self, "channelList") or not hasattr(self, "categoryList"):
                return

            # איסוף פריטים נבחרים מהרשימה הגרפית
            selected_items = [self.channelList.item(i)
                              for i in range(self.channelList.count())
                              if self.channelList.item(i) and self.channelList.item(i).isSelected()]

            if not selected_items:
                QMessageBox.information(self, "No Selection", "No channels selected for deletion.")
                return

            # אימות קטגוריה נוכחית
            selected_category_item = self.categoryList.currentItem()
            if not selected_category_item:
                QMessageBox.warning(self, "No Category", "Please select a category.")
                return

            category_name = selected_category_item.text().split(" (")[0].strip()
            if category_name not in self.categories:
                QMessageBox.warning(self, "Invalid Category", "Selected category not found.")
                return

            # בונים סט של הערכים המקוריים שנשמרו ב-UserRole כדי למחוק בדיוק
            entries_to_delete = set()
            for it in selected_items:
                val = it.data(Qt.UserRole)
                if isinstance(val, str) and val:
                    entries_to_delete.add(val)

            if not entries_to_delete:
                QMessageBox.information(self, "No Selection", "Could not resolve selected items.")
                return

            before = len(self.categories[category_name])
            self.categories[category_name] = [entry for entry in self.categories[category_name]
                                              if entry not in entries_to_delete]
            deleted = before - len(self.categories[category_name])

            # ניקוי קטגוריות ריקות אם יש לך פונקציה כזו
            if hasattr(self, "cleanEmptyCategories"):
                self.cleanEmptyCategories()

            # רענונים קיימים אצלך
            self.updateCategoryList()
            if hasattr(self, "regenerateM3UTextOnly"):
                self.regenerateM3UTextOnly()
            if self.categoryList.currentItem():
                self.display_channels(self.categoryList.currentItem())

            if hasattr(self, "channelCountLabel"):
                self.channelCountLabel.setText(f"Total Channels: {self.channelList.count()}")

            QMessageBox.information(self, "Success", f"Deleted {deleted} channel(s).")
            self.show_toast(f"נמחקו {deleted} ערוצים", "success")

            if hasattr(self, "displayTotalChannels"):
                self.displayTotalChannels()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Delete failed: {e}")

    def updateM3UContent(self):
        try:
            with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                logo_db = json.load(f)
        except:
            logo_db = {}

        skip_logos = getattr(self, 'skip_logo_scan', False)
        updated_lines = ["#EXTM3U"]

        # טען פעם אחת את הלוגואים
        for category, channels in self.categories.items():
            for channel in channels:
                try:
                    name, url = channel.split(" (", 1)
                    name = name.strip()
                    url = url.strip(") \n")
                except:
                    continue

                logo_url = ""

                if not skip_logos:
                    # בדוק אם קיים tvg-logo בשורה עצמה
                    match = re.search(r'tvg-logo="([^"]+)"', channel)
                    if match:
                        logo_url = match.group(1).strip()
                        existing = logo_db.get(name, [])
                        if isinstance(existing, str):
                            existing = [existing]

                        # אל תשמור שוב אם כבר קיים
                        if logo_url and logo_url not in existing:
                            logo_db.setdefault(name, []).append(logo_url)
                            save_logo_for_channel(name, logo_url)
                    else:
                        logo_url = get_saved_logo(name)
                else:
                    logo_url = get_saved_logo(name)

                # צור EXTINF עם או בלי לוגו
                if logo_url:
                    extinf = f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="{category}",{name}'
                else:
                    extinf = f'#EXTINF:-1 group-title="{category}",{name}'

                updated_lines.append(f"{extinf}\n{url}")

        # בדוק אם יש שינוי אמיתי בתוכן לפני setPlainText (מאוד איטי)
        new_content = "\n".join(updated_lines)
        if self.textEdit.toPlainText().strip() != new_content.strip():
            self.safely_update_text_edit(new_content)

        print("[LOG] 🔄 עדכון M3U בוצע", "כולל סריקת לוגואים" if not skip_logos else "ללא סריקת לוגואים")

    def moveChannelUp(self):
        """
        מעביר ערוץ אחד למעלה הן ב-UI והן ב-metadata של self.categories.
        """
        current_row = self.channelList.currentRow()
        if current_row <= 0:
            return

        # מוציאים את ה־entry המלא
        current_item = self.channelList.item(current_row)
        full_entry = current_item.data(Qt.UserRole)

        # מוצאים את הקטגוריה הפעילה
        category = self.categoryList.currentItem().text().split(" (")[0].strip()
        real_category = {k.strip(): k for k in self.categories.keys()}.get(category, category)
        channels = self.categories.get(real_category, [])

        # החלפת מיקומים ברשימת הפונלים
        channels[current_row], channels[current_row - 1] = channels[current_row - 1], channels[current_row]
        self.categories[real_category] = channels

        # בעדכון ה-UI מוחקים ומוסיפים עם הנתונים המעודכנים
        self.channelList.takeItem(current_row)
        new_item = QListWidgetItem(full_entry.split(" (")[0].strip())
        new_item.setData(Qt.UserRole, full_entry)
        self.channelList.insertItem(current_row - 1, new_item)
        self.channelList.setCurrentRow(current_row - 1)

        # רענון המחרוזת ל־M3U
        self.regenerateM3UTextOnly()

    def moveChannelDown(self):
        """
        מעביר ערוץ אחד למטה הן ב-UI והן ב-metadata של self.categories.
        """
        current_row = self.channelList.currentRow()
        if current_row < 0 or current_row >= self.channelList.count() - 1:
            return

        current_item = self.channelList.item(current_row)
        full_entry = current_item.data(Qt.UserRole)

        category = self.categoryList.currentItem().text().split(" (")[0].strip()
        real_category = {k.strip(): k for k in self.categories.keys()}.get(category, category)
        channels = self.categories.get(real_category, [])

        channels[current_row], channels[current_row + 1] = channels[current_row + 1], channels[current_row]
        self.categories[real_category] = channels

        self.channelList.takeItem(current_row)
        new_item = QListWidgetItem(full_entry.split(" (")[0].strip())
        new_item.setData(Qt.UserRole, full_entry)
        self.channelList.insertItem(current_row + 1, new_item)
        self.channelList.setCurrentRow(current_row + 1)

        self.regenerateM3UTextOnly()

    def saveToFile(self, file_path):
        try:
            with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                logo_db = json.load(f)
        except:
            logo_db = {}

        content = self.textEdit.toPlainText()
        self.extract_and_save_logos_for_all_channels(content)

        lines = content.strip().splitlines()
        fixed_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("#EXTINF:"):
                extinf_line = line
                url_line = lines[i + 1] if i + 1 < len(lines) else ""
                name_match = re.search(r",(.+)", extinf_line)
                channel_name = name_match.group(1).strip() if name_match else ""
                extinf_line = inject_logo(extinf_line, channel_name, logo_db)
                fixed_lines.append(extinf_line)
                fixed_lines.append(url_line)
                i += 2
            else:
                fixed_lines.append(line)
                i += 1

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))

        QMessageBox.information(self, "Success", "File saved successfully.")

    def selectAllChannels(self):
        try:
            if hasattr(self, "channelList"):
                self.channelList.setFocus()
            # הלולאה הקיימת שלך:
            for i in range(self.channelList.count()):
                self.channelList.item(i).setSelected(True)
        except Exception:
            pass

    def deselectAllChannels(self):
        for i in range(self.channelList.count()):
            self.channelList.item(i).setSelected(False)

    def moveSelectedChannel(self):
        """
        מעביר את הערוצים המסומנים לקטגוריה שנבחרה בדיאלוג, מציג הודעת סיכום,
        ומוחק קטגוריה ריקה אם העברנו את כל הערוצים ממנה.
        """
        try:
            # 1. שליפת הערוצים המסומנים
            items = self.channelList.selectedItems()
            if not items:
                QMessageBox.warning(self, "Warning", "No channels selected for moving.")
                return

            # 2. המרת פריטים למחרוזות מלאות "Name (URL)"
            selected_entries = []
            for item in items:
                raw = item.data(Qt.UserRole)
                entry = raw if isinstance(raw, str) else item.text().strip()
                selected_entries.append(entry)
            selected_names = [e.split(" (")[0].strip() for e in selected_entries]

            # 3. דיאלוג בחירת קטגוריה חדשה/קיימת
            dialog = MoveChannelsDialog(self, list(self.categories.keys()))
            if dialog.exec_() != QDialog.Accepted:
                return
            target = dialog.getSelectedCategory().strip()
            if not target:
                QMessageBox.warning(self, "Warning", "No target category specified.")
                return

            # 4. הוספת קטגוריה חדשה אם צריך
            if target not in self.categories:
                self.categories[target] = []

            # 5. שם הקטגוריה הנוכחית
            current_item = self.categoryList.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Warning", "No source category selected.")
                return
            source = current_item.text().split(" (")[0].strip()
            if source not in self.categories:
                QMessageBox.warning(self, "Warning", f"Category '{source}' does not exist.")
                return

            # 6. פילוח הערוצים למועברים ולשאריים
            original = self.categories[source]
            moved = [entry for entry in original if entry.split(" (")[0].strip() in selected_names]
            remaining = [entry for entry in original if entry.split(" (")[0].strip() not in selected_names]

            # 7. ביצוע המעבר במבנה הנתונים
            self.categories[source] = remaining
            self.categories[target].extend(moved)

            # 8. מחיקת קטגוריה ריקה
            if not self.categories[source]:
                del self.categories[source]

            # 9. ריענון התצוגה
            self.regenerateM3UTextOnly()
            self.updateCategoryList()
            # בחירת הקטגוריה היעדית והצגת הערוצים שלה
            for i in range(self.categoryList.count()):
                if self.categoryList.item(i).text().split(" (")[0].strip() == target:
                    self.categoryList.setCurrentRow(i)
                    self.display_channels(self.categoryList.item(i))
                    break

            # 10. ניקוי בחירות והצגת הודעת סיכום
            self.deselectAllChannels()
            QMessageBox.information(
                self, "Success",
                f"{len(moved)} channels moved to '{target}'."
            )

        except Exception as e:
            print(f"[ERROR] moveSelectedChannel: {e}")
            QMessageBox.critical(self, "Critical Error",
                                 f"Error in moveSelectedChannel:\n{e}")

    def previewSelectedChannels(self):
        """
        פותח ב-VLC את כל הערוצים המסומנים (ריבוי בחירה).
        יוצר קובץ M3U זמני עם #EXTM3U ושורה לכל EXTINF+URL.
        מציג את שם הערוץ ב-VLC כי משתמש בפורמט הנכון.
        גרסה מתוקנת עם טיפול מלא בשגיאות.
        """
        items = self.channelList.selectedItems()
        if not items:
            QMessageBox.warning(self, "אין ערוצים נבחרים", "בחר לפחות ערוץ אחד לצפייה.")
            return

        # בדיקת קיום VLC
        vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
        if not os.path.exists(vlc_path):
            QMessageBox.critical(self, "VLC לא נמצא", f"לא נמצא VLC בנתיב:\n{vlc_path}")
            return

        # בדיקת מספר הערוצים הנבחרים
        valid_channels = 0

        try:
            # בונים קובץ M3U זמני
            with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".m3u", delete=False, encoding="utf-8"
            ) as f:
                f.write("#EXTM3U\n")

                for item in items:
                    try:
                        # טיפול בטוח ב-UserRole data
                        raw = item.data(Qt.UserRole) if item else None
                        entry = raw if isinstance(raw, str) else (item.text().strip() if item else "")

                        if not entry:
                            continue

                        # מפרקים ל־name ו־url עם בדיקות בטיחות
                        if "(" in entry and entry.endswith(")"):
                            parts = entry.split(" (", 1)  # מגביל לפיצול יחיד
                            if len(parts) >= 2:
                                name = parts[0].strip()
                                url = parts[1].rstrip(")").strip()
                            else:
                                continue
                        else:
                            # אם הפורמט שבור, דילוג על הפריט
                            print(f"[WARNING] Invalid channel format: {entry}")
                            continue

                        # וידוא שיש שם וURL
                        if not name or not url:
                            continue

                        # מנסים להשיג #EXTINF מקורי אם יש
                        extinf = None
                        if hasattr(self, 'extinf_lookup') and self.extinf_lookup:
                            extinf = self.extinf_lookup.get(entry)

                        if not extinf:
                            # יוצרים EXTINF תקני עם שם הערוץ אחרי הפסיק
                            logo = ""
                            try:
                                logo = get_saved_logo(name) or ""
                            except:
                                pass

                            logo_tag = f' tvg-logo="{logo}"' if logo else ""

                            # group-title נלקח מ-categoryList בצורה בטוחה
                            grp = "Unknown"
                            try:
                                current_cat_item = self.categoryList.currentItem()
                                if current_cat_item and current_cat_item.text():
                                    grp = current_cat_item.text().split(" (")[0].strip()
                            except:
                                grp = "Unknown"

                            extinf = (
                                f'#EXTINF:-1{logo_tag} tvg-name="{name}" '
                                f'group-title="{grp}",{name}'
                            )

                        f.write(extinf + "\n")
                        f.write(url + "\n")
                        valid_channels += 1

                    except Exception as e:
                        print(f"[ERROR] Failed to process channel item: {e}")
                        continue

                temp_path = f.name

            # בדיקה שיש ערוצים תקינים
            if valid_channels == 0:
                QMessageBox.warning(
                    self, "אין ערוצים תקינים",
                    "לא נמצאו ערוצים תקינים לצפייה.\nבדוק את פורמט הערוצים הנבחרים."
                )
                try:
                    os.remove(temp_path)
                except:
                    pass
                return

            # הודעה מידעית על מספר הערוצים
            if valid_channels > 1:
                reply = QMessageBox.question(
                    self, "פתיחת מספר ערוצים",
                    f"האם לפתוח {valid_channels} ערוצים ב-VLC?\n\nזה עלול לצרוך הרבה משאבי מערכת.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                    return

            # מריצים את VLC על כל הקובץ
            process = subprocess.Popen([vlc_path, temp_path])

            # הודעת הצלחה
            QMessageBox.information(
                self, "VLC הופעל",
                f"VLC הופעל בהצלחה עם {valid_channels} ערוצים.\n\nהקובץ הזמני יימחק אוטומטית כשתסגור את VLC."
            )

        except Exception as e:
            error_msg = f"שגיאה כללית בהרצת VLC: {e}"
            print(f"[ERROR] {error_msg}")
            QMessageBox.critical(self, "שגיאה בהרצת VLC", error_msg)

    def editSelectedChannel(self):
        """
        Renames a selected channel and updates the M3U content accordingly.
        """
        selected_items = self.channelList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No channels selected for editing.")
            return

        for item in selected_items:
            widget = self.channelList.itemWidget(item)
            label = widget.findChild(QLabel, "channel_label") if widget else None
            if not label:
                continue

            old_channel_name = label.text().strip()

            new_channel_name, ok = QInputDialog.getText(self, 'Edit Channel', 'Enter new channel name:',
                                                        text=old_channel_name)
            if ok and new_channel_name and new_channel_name != old_channel_name:
                # Update the channel name in the categories dictionary
                current_category = self.categoryList.currentItem().text().split(" (")[0]
                if current_category in self.categories:
                    for i, channel in enumerate(self.categories[current_category]):
                        if channel.split(" (")[0] == old_channel_name:
                            self.categories[current_category][i] = channel.replace(old_channel_name, new_channel_name)
                            break

                # Update the M3U content
                updated_lines = []
                for line in self.textEdit.toPlainText().splitlines():
                    if old_channel_name in line:
                        line = line.replace(old_channel_name, new_channel_name)
                    updated_lines.append(line)

                self.safely_update_text_edit("\n".join(updated_lines))
                self.display_channels(self.categoryList.currentItem())
                QMessageBox.information(self, "Success",
                                        f"Channel '{old_channel_name}' has been renamed to '{new_channel_name}'.")

    def display_channels(self, item):
        """
        מציג את הערוצים באופן גרפי עם תג איכות, כולל סינון לפי חיפוש, קטגוריה וסטטוס.
        המונה הגלובלי לא מתעדכן כאן לפי סינון.
        """
        from PyQt5.QtWidgets import QListWidgetItem
        from PyQt5.QtGui import QColor
        from PyQt5.QtCore import Qt

        self.channelList.clear()
        # אם אין פריט – רק נקה את מונה המוצגים
        if item is None:
            if hasattr(self, "channelsHeaderCount"):
                self.channelsHeaderCount.setText("0")
            # גלובלי נשאר גלובלי
            if hasattr(self, "displayTotalChannels"):
                self.displayTotalChannels()
            return

        cat = item.text().split(" (")[0].strip()
        real = {k.strip(): k for k in self.categories}.get(cat)
        if not real:
            if hasattr(self, "channelsHeaderCount"):
                self.channelsHeaderCount.setText("0")
            if hasattr(self, "displayTotalChannels"):
                self.displayTotalChannels()
            return

        term = self.searchBox.text().lower().strip() if hasattr(self, "searchBox") else ""
        cat_filter_value = ""
        if hasattr(self, "categoryFilter") and self.categoryFilter.currentIndex() >= 0:
            data = self.categoryFilter.currentData()
            if isinstance(data, str):
                cat_filter_value = data
        status_text = self.statusFilter.currentText() if hasattr(self, "statusFilter") else "כל הערוצים"

        for entry in self.categories[real]:
            name = entry.split(" (")[0].strip()
            quality = detect_stream_quality(entry)
            url = self.getUrl(entry) if hasattr(self, "getUrl") else ""

            # לוגו אם יש cache
            logo_url = ""
            if hasattr(self, "logo_cache"):
                v = self.logo_cache.get(name)
                if isinstance(v, list) and v:
                    logo_url = v[0]
                elif isinstance(v, str):
                    logo_url = v

            is_hidden = False  # החלף אם יש לך דגל אמיתי

            # סינון
            if term and term not in name.lower():
                continue
            if cat_filter_value and real != cat_filter_value:
                continue
            if status_text == "מוסתרים" and not is_hidden:
                continue
            if status_text == "פעילים" and is_hidden:
                continue

            widget = create_channel_widget(name, quality, logo_url, real, is_hidden)
            lw_item = QListWidgetItem()
            lw_item.setSizeHint(widget.sizeHint())
            lw_item.setData(Qt.UserRole, entry)
            lw_item.setForeground(QColor("#111827"))
            self.channelList.addItem(lw_item)
            self.channelList.setItemWidget(lw_item, widget)

        # מונה מוצגים מקומי
        if hasattr(self, "channelsHeaderCount"):
            self.channelsHeaderCount.setText(str(self.channelList.count()))
        # גלובלי נשאר גלובלי
        if hasattr(self, "displayTotalChannels"):
            self.displayTotalChannels()

    def checkDoubles(self):
        """
        Check for duplicate channel names in the current category.
        Select only *one* of each duplicate pair (the second occurrence), so one channel always remains.
        """
        current_category_item = self.categoryList.currentItem()
        if not current_category_item:
            QMessageBox.warning(self, "Warning", "No category selected.")
            return

        current_category = current_category_item.text().split(" (")[0]
        if current_category not in self.categories:
            QMessageBox.warning(self, "Warning", "Category not found.")
            return

        # Clear all current selections first
        self.channelList.clearSelection()

        # Track channel occurrences by name
        channel_names = {}
        channels = self.categories[current_category]

        # Track which indexes to select (the duplicate copies, not the first)
        duplicate_indexes = set()

        for i, channel in enumerate(channels):
            channel_name = channel.split(" (")[0].strip()

            if channel_name in channel_names:
                # Found a duplicate - mark the second occurrence (i.e., this one)
                duplicate_indexes.add(i)
            else:
                # First occurrence - remember its index
                channel_names[channel_name] = i

        # Select only the duplicate channels (leaving the first copy unselected)
        for index in duplicate_indexes:
            self.channelList.item(index).setSelected(True)

        QMessageBox.information(self, "Check Complete",
                                f"Found {len(duplicate_indexes)} duplicate channels (one copy kept).")

    def _add_shortcuts(self):
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        from PyQt5.QtCore import Qt

        def make_shortcut(seq, slot):
            sc = QShortcut(QKeySequence(seq), self)
            sc.setContext(Qt.ApplicationShortcut)  # עובד בכל החלון
            sc.activated.connect(slot)
            return sc

        # חיפוש
        make_shortcut("Ctrl+F", self._focus_search)
        make_shortcut("Ctrl+R", self._clear_search)

        # בחירה ומחיקה ברשימת הערוצים
        make_shortcut("Ctrl+A", self.selectAllChannels)
        make_shortcut("Delete", self.deleteSelectedChannels)

        # יצוא
        make_shortcut("Ctrl+E", self._open_export_dialog_smart)

        # URL Checker רק אם יש
        if hasattr(self, "openURLCheckerDialog"):
            make_shortcut("Ctrl+L", self.openURLCheckerDialog)

        # עזרה תמיד, לא תלוי בשום דבר
        make_shortcut("F1", self.showHelpDialog if hasattr(self, "showHelpDialog") else lambda: None)

    def _focus_search(self):
        try:
            if hasattr(self, "searchBox"):
                self.searchBox.setFocus()
                self.searchBox.selectAll()
        except Exception:
            pass

    def _clear_search(self):
        try:
            if hasattr(self, "searchBox"):
                self.searchBox.clear()
        except Exception:
            pass

    def _open_export_dialog_smart(self):
        try:
            if hasattr(self, "openExportDialog"):
                self.openExportDialog()
                return
            if hasattr(self, "exportVisibleM3U"):
                self.exportVisibleM3U()
                return
        except Exception:
            pass

    def showURLScanChoiceDialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("URL Scan Options")

        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        # Apply red border and white background to dialog
        dialog.setStyleSheet("""
            QDialog {
                border: 5px solid red;
                background-color: white;
            }
        """)

        layout = QVBoxLayout(dialog)

        label = QLabel("Choose what to scan:")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        category_btn = QPushButton("Choose Category")
        category_btn.setStyleSheet("background-color: black; color: white; font-weight: bold;")

        all_btn = QPushButton("Scan All Channels")
        all_btn.setStyleSheet("background-color: red; color: white; font-weight: bold;")

        layout.addWidget(category_btn)
        layout.addWidget(all_btn)

        category_btn.clicked.connect(lambda: [dialog.accept(), self.showCategoryPickerDialog()])
        all_btn.clicked.connect(lambda: self.runURLChecker(False, dialog))

        dialog.setLayout(layout)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        dialog.exec_()

    def runURLCheckerFromCategory(self, category_name, dialog=None):
        if dialog:
            dialog.accept()

        # ניקוי השם מהשוואות לא תקינות (רווחים, תווים מוסתרים)
        normalized_input = category_name.strip()

        # יצירת מפה של קטגוריות מנורמלות → מקור
        normalized_map = {k.strip(): k for k in self.categories.keys()}

        # בדיקה האם הקטגוריה קיימת
        if normalized_input not in normalized_map:
            QMessageBox.warning(self, "Warning", f"Category '{normalized_input}' not found in categories.")
            return

        # שלוף את הקטגוריה המקורית מהמערכת
        real_category = normalized_map[normalized_input]

        channels = []
        for ch in self.categories[real_category]:
            name = ch.split(" (")[0]
            url = self.getUrl(ch)
            channels.append((name, url))

        if channels:
            dialog = URLCheckerDialog(channels, self)
            dialog.exec_()
        else:
            QMessageBox.information(self, "Info", "No channels found in this category.")

    def runURLChecker(self, scan_current_category, dialog):
        dialog.close()
        channels = []

        if scan_current_category:
            category_item = self.categoryList.currentItem()
            if not category_item:
                QMessageBox.warning(self, "Warning", "Please select a category.")
                return
            category_name = category_item.text().split(" (")[0]
            for ch in self.categories.get(category_name, []):
                name = ch.split(" (")[0]
                url = self.getUrl(ch)
                channels.append((name, url))
        else:
            for channel_list in self.categories.values():
                for ch in channel_list:
                    name = ch.split(" (")[0]
                    url = self.getUrl(ch)
                    channels.append((name, url))

        if channels:
            dialog = URLCheckerDialog(channels, self)
            dialog.exec_()
        else:
            QMessageBox.information(self, "Info", "No channels found to scan.")

    def showCategoryPickerDialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Category")
        dialog.setFixedSize(250, 120)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        dialog.setStyleSheet("""
            QDialog {
                border: 3px solid purple;
                background-color: white;
            }
        """)

        layout = QVBoxLayout(dialog)

        combo = QComboBox()
        combo.addItems(list(self.categories.keys()))
        layout.addWidget(combo)

        btn_ok = QPushButton("Start Scan")
        btn_ok.setStyleSheet("background-color: purple; color: white; font-weight: bold; padding: 5px;")
        layout.addWidget(btn_ok)

        btn_ok.clicked.connect(lambda: [dialog.accept(), self.startURLCheckForCategory(combo.currentText())])
        dialog.exec_()

    def startURLCheckForCategory(self, category_name):
        channels = []
        channel_category_mapping = {}

        for ch in self.categories.get(category_name, []):
            name = ch.split(" (")[0].strip()
            url = self.getUrl(ch)
            if url:
                channels.append((name, url))
                channel_category_mapping[name.lower()] = category_name

        if not channels:
            QMessageBox.warning(self, "No Channels", "No valid channels found in the selected category.")
            return

        dialog = URLCheckerDialog(channels, channel_category_mapping, self)
        dialog.exec_()

    def startURLCheckAllChannels(self):
        channels = []
        channel_category_mapping = {}

        for category, ch_list in self.categories.items():
            for ch in ch_list:
                name = ch.split(" (")[0].strip()
                url = self.getUrl(ch)
                if url:
                    channels.append((name, url))
                    channel_category_mapping[name.lower()] = category

        if not channels:
            QMessageBox.warning(self, "No Channels", "No channels with valid URLs were found.")
            return

        dialog = URLCheckerDialog(channels, channel_category_mapping, self)
        dialog.exec_()

    def openSmartScanDialog(self):
        from PyQt5.QtCore import Qt

        # מכינים רשימת ערוצים ומיפוי לקטגוריות
        channels = []
        category_map = {}
        for cat, lst in self.categories.items():
            for ch in lst:
                name = ch.split(" (")[0].strip()
                url = self.getUrl(ch)
                if url:
                    channels.append((name, url))
                    category_map[name.lower()] = cat

        # יוצרים את הדיאלוג ומוודאים שהוא יימחק אוטומטית
        dlg = SmartScanStatusDialog(channels, category_map, self)
        dlg.setAttribute(Qt.WA_DeleteOnClose)
        dlg.finished.connect(dlg.deleteLater)
        dlg.exec_()

    def performSmartScan(self, category_only, dialog):
        dialog.close()

        if category_only:
            category_item = self.categoryList.currentItem()
            if not category_item:
                QMessageBox.warning(self, "Warning", "Please select a category.")
                return

            category_name = category_item.text().split(" (")[0]
            if category_name not in self.categories:
                QMessageBox.warning(self, "Warning", "Category not found.")
                return

            self.checkDoubles()  # Already selects duplicates in category

            # Check URLs in current category
            channels = []
            for ch in self.categories[category_name]:
                name = ch.split(" (")[0]
                url = self.getUrl(ch)
                channels.append((name, url))

            dialog = URLCheckerDialog(channels, self)
            dialog.exec_()

        else:
            # Run checkDoublesAll
            duplicate_names = set()
            seen_names = set()

            for category in self.categories:
                for ch in self.categories[category]:
                    name = ch.split(" (")[0].strip()
                    if name in seen_names:
                        duplicate_names.add(name)
                    else:
                        seen_names.add(name)

            # Clear selection first
            self.channelList.clearSelection()

            # Collect all channels (name + url)
            all_channels = []
            for category, ch_list in self.categories.items():
                for ch in ch_list:
                    name = ch.split(" (")[0]
                    url = self.getUrl(ch)
                    all_channels.append((name, url))

            # Show URL check dialog
            dialog = URLCheckerDialog(all_channels, self)
            dialog.exec_()

            # Try to highlight duplicates in current list
            for index in range(self.channelList.count()):
                item = self.channelList.item(index)
                if item.text() in duplicate_names:
                    item.setSelected(True)

            QMessageBox.information(self, "Duplicates", f"Found {len(duplicate_names)} duplicate names.")

    def startSmartScan(self, all_categories=False, category=None):
        # Build full channel list
        channels = []
        seen_names = set()
        duplicate_names = set()

        if all_categories:
            for ch_list in self.categories.values():
                for ch in ch_list:
                    name = ch.split(" (")[0].strip()
                    url = self.getUrl(ch)
                    channels.append((name, url))

                    if name in seen_names:
                        duplicate_names.add(name)
                    else:
                        seen_names.add(name)
        else:
            if not category:
                QMessageBox.warning(self, "Error", "No category selected.")
                return

            for ch in self.categories.get(category, []):
                name = ch.split(" (")[0].strip()
                url = self.getUrl(ch)
                channels.append((name, url))

                if name in seen_names:
                    duplicate_names.add(name)
                else:
                    seen_names.add(name)

        if not channels:
            QMessageBox.information(self, "Info", "No channels to scan.")
            return

        # Show the scan dialog
        dialog = SmartScanStatusDialog(channels, duplicate_names, self)
        dialog.exec_()

    def showSmartScanCategoryPicker(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Category to Scan")
        dialog.setStyleSheet("QDialog { border: 5px solid purple; background-color: white; }")
        layout = QVBoxLayout(dialog)

        label = QLabel("Pick a category:")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        combo = QComboBox()
        combo.addItems(self.categories.keys())
        layout.addWidget(combo)

        start_btn = QPushButton("Start Scan")
        start_btn.setStyleSheet("background-color: black; color: white; font-weight: bold;")
        layout.addWidget(start_btn)

        start_btn.clicked.connect(lambda: [dialog.accept(), self.startSmartScan(category=combo.currentText())])

        dialog.setLayout(layout)  # ← חובה
        dialog.exec_()  # ← חובה

    def safely_update_text_edit(self, new_text):
        current_text = self.textEdit.toPlainText()
        if current_text.strip() != new_text.strip():
            self.textEdit.blockSignals(True)
            self.textEdit.setPlainText(new_text)
            self.textEdit.blockSignals(False)

    def selectChannelsByUrls(self, urls_set):
        self.channelList.clearSelection()
        SmartScanStatusDialog
        selected_category_item = self.categoryList.currentItem()
        if not selected_category_item:
            return

        category_name = selected_category_item.text().split(" (")[0]
        channels_in_category = self.categories.get(category_name, [])

        for idx, channel in enumerate(channels_in_category):
            url = self.getUrl(channel).strip()
            if url in urls_set:
                self.channelList.item(idx).setSelected(True)

    def removeChannelsByUrls(self, urls_set):
        removed_count = 0
        for category in self.categories.keys():
            original_channels = self.categories[category]
            new_channels = []

            for channel in original_channels:
                url = self.getUrl(channel).strip()
                if url in urls_set:
                    removed_count += 1  # ערוץ יימחק
                else:
                    new_channels.append(channel)

            self.categories[category] = new_channels

        self.updateM3UContent()
        self.display_channels(self.categoryList.currentItem())  # רענון התצוגה לאחר המחיקה
        return removed_count

    def selectChannelsByNames(self, channel_names):
        self.channelList.clearSelection()

        # Make sure a category is selected
        current_category_item = self.categoryList.currentItem()
        if not current_category_item:
            QMessageBox.warning(self, "Warning", "No category selected.")
            return

        current_category = current_category_item.text().split(" (")[0]
        if current_category not in self.categories:
            QMessageBox.warning(self, "Warning", "Category not found.")
            return

        # Select channels in the current category matching offline names
        count_selected = 0
        for index in range(self.channelList.count()):
            item = self.channelList.item(index)
            if item.text() in channel_names:
                item.setSelected(True)
                count_selected += 1

        if count_selected == 0:
            QMessageBox.information(self, "Channels Not Found",
                                    "None of the offline channels were found in the current category.")

    def deleteChannelsByNames(self, names_to_delete, urls_to_delete):
        removed = 0
        targets = set(zip(names_to_delete, urls_to_delete))  # הפוך לרשימה של זוגות מדויקים

        for category, ch_list in self.categories.items():
            original_len = len(ch_list)

            self.categories[category] = [
                ch for ch in ch_list
                if (ch.split(" (")[0].strip(), self.getUrl(ch).strip()) not in targets
            ]

            removed += original_len - len(self.categories[category])

        self.updateCategoryList()
        self.regenerateM3UTextOnly()
        if self.categoryList.currentItem():
            self.display_channels(self.categoryList.currentItem())

        return removed

    def selectChannelsByNameAndUrl(self, name_url_set):
        self.channelList.clearSelection()

        selected_category_item = self.categoryList.currentItem()
        if not selected_category_item:
            return

        category_name = selected_category_item.text().split(" (")[0]
        channels_in_category = self.categories.get(category_name, [])

        for idx, channel in enumerate(channels_in_category):
            name = channel.split(" (")[0].strip()
            url = self.getUrl(channel).strip()

            if (name, url) in name_url_set:
                self.channelList.item(idx).setSelected(True)

    def getUrl(self, channel_info):
        """
        Extracts the URL part from the channel string.
        Example: "Channel Name (http://...)" → returns http://...
        """
        try:
            if '(' in channel_info and ')' in channel_info:
                url = channel_info.split(" (")[-1].rstrip(")").strip()
                if url.startswith("http"):
                    return url
            return ""
        except Exception as e:
            print(f"[getUrl] Error: {e}")
            return ""

    def findFullM3UEntry(self, channel_name, category):
        for channel in self.categories.get(category, []):
            if channel.startswith(channel_name):
                return channel
        return None

    import xml.etree.ElementTree as ET

    def loadM3U(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Open M3U File",
            "",
            "M3U Files (*.m3u *.m3u8);;All Files (*)", options=options
        )
        if fileName:
            try:
                with open(fileName, 'r', encoding='utf-8') as file:
                    content = file.read()

                # טען M3U דרך המתודה הראשית
                self.loadM3UFromText(content, append=False)

                # ✅ עדכון תצוגה
                total_channels = sum(len(channels) for channels in self.categories.values())
                total_categories = len(self.categories)
                summary = f"📺 Total Channels: {total_channels}   |   🗂 Categories: {total_categories}"
                self.channelCountLabel.setText(summary)
                self.channelCountLabel.setToolTip(f"{total_channels} ערוצים בסך הכל ב-{total_categories} קטגוריות")
                self.fileNameLabel.setText(f"Loaded File: {os.path.basename(fileName)}")

                # 🧠 טעינת קובץ EPG אוטומטית אם קיים
                epg_base = os.path.splitext(fileName)[0]
                for ext in [".xml", ".xml.gz"]:
                    epg_candidate = epg_base + ext
                    if os.path.exists(epg_candidate):
                        try:
                            self.loadEPG(epg_candidate)
                            break  # נטען רק את הראשון שנמצא
                        except Exception as e:
                            print(f"EPG Load Failed for {epg_candidate}: {e}")


            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")

    def loadEPG(self, epg_path):
        try:
            tree = ET.parse(epg_path)
            root = tree.getroot()

            if not hasattr(self, 'epg_data'):
                self.epg_data = {}

            count = 0
            for programme in root.findall('programme'):
                channel_id = programme.attrib.get('channel', '').strip()
                title = (programme.findtext('title') or '').strip()
                desc = (programme.findtext('desc') or '').strip()
                start = programme.attrib.get('start', '').strip()
                stop = programme.attrib.get('stop', '').strip()

                if channel_id:
                    entry = {
                        'title': title or 'No Title',
                        'desc': desc or '',
                        'start': start,
                        'stop': stop
                    }
                    self.epg_data.setdefault(channel_id, []).append(entry)
                    count += 1

            # 🧠 מיון לפי זמן התחלה
            for programmes in self.epg_data.values():
                programmes.sort(key=lambda p: p.get('start', ''))

            QMessageBox.information(self, "EPG Loaded", f"📅 EPG data loaded successfully.\nEntries parsed: {count}")

        except Exception as e:
            QMessageBox.critical(self, "EPG Error", f"Failed to load EPG file:\n{str(e)}")

    def openEPGViewer(self, tvg_id):
        from PyQt5.QtWidgets import QScrollArea, QCheckBox
        from datetime import datetime

        if not hasattr(self, 'epg_data') or tvg_id not in self.epg_data:
            QMessageBox.information(self, "EPG Viewer", "No EPG data available.")
            return

        # === יצירת דיאלוג ===
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📺 לוח שידורים: {tvg_id}")
        dialog.resize(600, 700)
        main_layout = QVBoxLayout(dialog)

        # === שורת חיפוש ===
        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 חפש תוכנית לפי שם או תיאור...")
        main_layout.addWidget(search_input)

        # === תיבת סימון - רק עכשיו ===
        now_only_checkbox = QCheckBox("📡 הצג רק תוכניות שמשודרות עכשיו")
        main_layout.addWidget(now_only_checkbox)

        # === אזור גלילה ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        # === פונקציית רענון (פנימית) ===
        def refresh_epg_view():
            # ניקוי תצוגה קודמת
            for i in reversed(range(scroll_layout.count())):
                widget = scroll_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            entries = self.getRecentEPG(tvg_id)
            now = datetime.now()
            keyword = search_input.text().lower()
            show_now_only = now_only_checkbox.isChecked()

            for entry in sorted(entries, key=lambda e: e.get('start', '')):
                title = entry.get('title', 'No Title').strip()
                desc = entry.get('desc', '').strip()
                start = entry.get('start', '')
                stop = entry.get('stop', '')
                play_url = entry.get('play_url') or entry.get('catchup-url')

                # סינון לפי חיפוש
                if keyword and keyword not in title.lower() and keyword not in desc.lower():
                    continue

                # סינון לפי זמן נוכחי
                try:
                    start_dt = datetime.strptime(start[:12], '%Y%m%d%H%M')
                    stop_dt = datetime.strptime(stop[:12], '%Y%m%d%H%M')
                    if show_now_only and not (start_dt <= now <= stop_dt):
                        continue
                except:
                    pass  # מקרה של פורמט תאריך שגוי

                # תרגום תאריכים
                def format_time(ts):
                    try:
                        return datetime.strptime(ts[:12], '%Y%m%d%H%M').strftime('%d/%m/%Y %H:%M')
                    except:
                        return ts

                # תצוגת תוכנית
                label = QLabel(f"""
                    <b style="font-size:14px;">{title}</b><br>
                    <span style="color:gray;">{desc}</span><br>
                    <span style="color:blue;">{format_time(start)} → {format_time(stop)}</span>
                """)
                label.setWordWrap(True)

                program_box = QVBoxLayout()
                program_box.addWidget(label)

                if play_url:
                    play_button = QPushButton("▶ הפעל")
                    play_button.setStyleSheet("background-color: green; color: white; font-weight: bold;")
                    play_button.clicked.connect(lambda _, url=play_url: self.playCatchupStream(url))
                    program_box.addWidget(play_button)

                # עטיפה ב־QWidget
                program_widget = QWidget()
                program_widget.setLayout(program_box)
                scroll_layout.addWidget(program_widget)

            if scroll_layout.count() == 0:
                scroll_layout.addWidget(QLabel("❌ לא נמצאו תוכניות תואמות."))

        # === הפעלת רענון ===
        search_input.textChanged.connect(refresh_epg_view)
        now_only_checkbox.stateChanged.connect(refresh_epg_view)

        # רענון ראשון
        refresh_epg_view()

        dialog.setLayout(main_layout)
        dialog.exec_()

    def openEPGViewerForSelectedChannel(self):
        selected_items = self.channelList.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "EPG Viewer", "Please select a channel.")
            return

        selected_name = selected_items[0].text()
        current_category_item = self.categoryList.currentItem()
        if not current_category_item:
            QMessageBox.warning(self, "No Category", "No category selected.")
            return

        category = current_category_item.text().split(" (")[0]
        channels = self.categories.get(category, [])

        for ch in channels:
            ch_name = ch.split(" (")[0].strip()
            if ch_name == selected_name:
                match = re.search(r'tvg-id="([^"]+)"', ch)
                if match:
                    tvg_id = match.group(1)
                    self.openEPGViewer(tvg_id)
                else:
                    QMessageBox.information(self, "No EPG", "No tvg-id found for this channel.")
                return

    def getRecentEPG(self, tvg_id):
        now = datetime.now()
        week_ago = now - timedelta(days=7)

        entries = self.epg_data.get(tvg_id, [])
        filtered_entries = []

        for entry in entries:
            try:
                start_raw = entry.get("start", "")[:14]
                stop_raw = entry.get("stop", "")[:14]
                start_time = datetime.strptime(start_raw, "%Y%m%d%H%M%S")
                stop_time = datetime.strptime(stop_raw, "%Y%m%d%H%M%S")

                if week_ago <= start_time <= now:
                    filtered_entries.append({
                        "title": entry.get("title", ""),
                        "desc": entry.get("desc", ""),
                        "start": start_time.strftime("%d/%m %H:%M"),
                        "stop": stop_time.strftime("%H:%M"),
                        "play_url": entry.get("play_url")
                    })
            except Exception:
                continue

    def saveM3U(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save M3U File", "", "M3U Files (*.m3u);;All Files (*)",
                                                  options=options)
        if fileName:
            with open(fileName, 'w', encoding='utf-8') as file:
                file.write(self.textEdit.toPlainText())

    def exportToTelegram(self):
        """
        כותבת את התוכן המלא של ה-M3U לקובץ זמני ושולחת לטלגרם,
        עם יצירת שמות קבצים אוטומטיים וחכמים.
        """

        # יצירת שם קובץ אוטומטי
        today = datetime.now()
        date_str = today.strftime("%d-%m-%Y")

        # בדיקת כמה קבצים נשלחו היום
        cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "telegram_exports.json")
        today_key = today.strftime("%Y-%m-%d")

        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    exports_data = json.load(f)
            else:
                exports_data = {}
        except:
            exports_data = {}

        # ספירת ייצואים מוצלחים היום
        today_exports = exports_data.get(today_key, [])
        successful_today = [exp for exp in today_exports if exp.get('success', False)]
        count = len(successful_today)

        # יצירת שם הקובץ
        if count == 0:
            auto_name = f"EGTV_{date_str}.m3u"
        else:
            auto_name = f"EGTV_{date_str}_({count}).m3u"

        # שאלת שם קובץ עם הצעה אוטומטית
        name, ok = QInputDialog.getText(
            self, "ייצוא לטלגרם",
            f"שם קובץ מוצע: {auto_name}\n\nהשתמש בשם המוצע או הכנס שם אחר:",
            text=auto_name
        )

        if not ok or not name.strip():
            return
        if not name.lower().endswith(".m3u"):
            name += ".m3u"

        # כותב לקובץ זמני עם tempfile.NamedTemporaryFile
        try:
            with tempfile.NamedTemporaryFile(
                    mode="w", delete=False, suffix=".m3u", encoding="utf-8"
            ) as tmp:
                content = self.textEdit.toPlainText()
                # וידוא שהתוכן מתחיל ב-EXTM3U
                if not content.startswith("#EXTM3U"):
                    content = "#EXTM3U\n" + content
                tmp.write(content)
                tmp_path = tmp.name
        except Exception as e:
            QMessageBox.critical(
                self, "שגיאה בכתיבת קובץ",
                f"לא ניתן לכתוב את הקובץ הזמני:\n{e}"
            )
            return

        # שולח לטלגרם
        try:
            success = send_to_telegram(tmp_path, filename=name)
        except Exception as e:
            # רישום כישלון
            try:
                if today_key not in exports_data:
                    exports_data[today_key] = []
                exports_data[today_key].append({
                    "filename": name,
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                    "error": str(e)
                })
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(exports_data, f, ensure_ascii=False, indent=2)
            except:
                pass

            QMessageBox.critical(
                self, "שגיאה ב-Telegram",
                f"קריסה בעת שליחה לטלגרם:\n{e}"
            )
            return

        # רישום התוצאה
        try:
            if today_key not in exports_data:
                exports_data[today_key] = []
            exports_data[today_key].append({
                "filename": name,
                "timestamp": datetime.now().isoformat(),
                "success": success
            })

            # ניקוי נתונים ישנים (שמירה של 7 ימים)
            cutoff_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            exports_data = {k: v for k, v in exports_data.items() if k >= cutoff_date}

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(exports_data, f, ensure_ascii=False, indent=2)
        except:
            pass  # לא קריטי אם הרישום נכשל

        # מציג תוצאה למשתמש
        if success:
            # חישוב סטטיסטיקות פשוטות
            total_today = len(exports_data.get(today_key, []))
            successful_today_updated = len(
                [exp for exp in exports_data.get(today_key, []) if exp.get('success', False)])

            QMessageBox.information(
                self, "Telegram",
                f"הקובץ '{name}' נשלח בהצלחה!\n\nסטטיסטיקות היום:\nייצואים מוצלחים: {successful_today_updated}\nסה\"כ ניסיונות: {total_today}"
            )
        else:
            QMessageBox.warning(
                self, "Telegram", f"שליחה של '{name}' נכשלה."
            )

        # (אופציונלי) מחיקת הקובץ הזמני
        try:
            os.remove(tmp_path)
        except:
            pass

    def openExportDialog(self):
        try:
            dialog = ExportGroupsDialog(self.categories, self)
            dialog.exec_()
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{error_message}")
            print(error_message)  # Print the full traceback to the console

    def parseM3UContentEnhanced(self, content):
        """
        Parse M3U content, handling group-title, #EXTGRP, and tvg-logo robustly.
        לא סורק לוגואים – רק בונה קטגוריות ותוכן.
        """
        self.categories.clear()
        self.extinf_lookup = {}  # ← ← ← ✅ מוסיפים יצירה של המילון הזה
        updated_lines = []
        current_group = None
        lines = content.splitlines()

        for line in lines:
            if line.startswith("#EXTGRP:"):
                current_group = line.split(":", 1)[1].strip()
                continue

            if line.startswith("#EXTINF:"):
                if "group-title=" not in line and current_group:
                    line = re.sub(r'(#EXTINF:[^\n]*?),', f'\\1 group-title="{current_group}",', line)
                current_group = None  # Always reset group

            updated_lines.append(line)

        updated_content = "\n".join(updated_lines)

        # פרס קטגוריות וערוצים
        category_pattern = re.compile(r'#EXTINF.*group-title="([^"]+)".*,(.*)\n(.*)')
        for match in category_pattern.findall(updated_content):
            group_title, channel_name, channel_url = match
            if group_title not in self.categories:
                self.categories[group_title] = []
            self.categories[group_title].append(f"{channel_name.strip()} ({channel_url.strip()})")

        self.safely_update_text_edit(updated_content)
        self.categoryList.clear()
        for category, channels in self.categories.items():
            item = QListWidgetItem(f"{category} ({len(channels)})")
            self.categoryList.addItem(item)

        self.searchBox.setText("")
        self.buildSearchCompleter()

    def chooseLanguageAndFilterIsraelChannels(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("בחר שפה לסינון ערוצים")
        dialog.setMinimumWidth(300)
        dialog.setMinimumHeight(180)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 5px solid black;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: black;
            }
            QPushButton {
                font-size: 16px;
                padding: 10px;
                margin: 8px;
                font-weight: bold;
                border: 2px solid black;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:focus {
                outline: none;
                border: 2px solid red;
            }
            QPushButton:disabled {
                color: gray;
            }
        """)

        layout = QVBoxLayout(dialog)

        label = QLabel("בחר שפה לסינון ערוצים:")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        hebrew_btn = QPushButton("🇮🇱 עברית")
        hebrew_btn.setStyleSheet("background-color: black; color: white;")
        english_btn = QPushButton("English 🇬🇧")
        english_btn.setStyleSheet("background-color: red; color: white;")

        layout.addWidget(hebrew_btn)
        layout.addWidget(english_btn)

        hebrew_btn.clicked.connect(lambda: [dialog.accept(), self.filterIsraelChannelsFromKeywords("he")])
        english_btn.clicked.connect(lambda: [dialog.accept(), self.filterIsraelChannelsFromKeywords("en")])

        dialog.setLayout(layout)
        dialog.exec_()

        def apply_filter(lang):
            dialog.accept()
            self.filterIsraelChannelsFromKeywords(lang)

        hebrew_btn.clicked.connect(lambda: apply_filter("he"))
        english_btn.clicked.connect(lambda: apply_filter("en"))

    def _apply_filter_and_close(self, dialog, lang):
        dialog.accept()
        self.filterIsraelChannelsFromKeywords(lang)

    def getFilteredCategory(self, channel):
        if 'חדשות' in channel or 'News' in channel:
            return 'News'
        elif 'סרטים' in channel or 'Movies' in channel:
            return 'Movies'
        elif 'kids' in channel or 'Kids' in channel:
            return 'Kids'
        elif 'ספורט' in channel or 'Sports' in channel:
            return 'Sports'
        elif 'תיעוד' in channel or 'Documentaries' in channel:
            return 'Documentaries'
        elif 'Yes' in channel or 'Yes' in channel:
            return 'Yes'
        elif 'Hot' in channel or 'hot' in channel:
            return 'Hot'
        elif 'מוזיקה' in channel or 'Music' in channel:
            return 'Music'
        elif 'entertainment' in channel or 'Entertainment' in channel:
            return 'Entertainment'
        elif 'nature' in channel or 'Nature' in channel:
            return 'Nature'
        elif 'partner' in channel or 'Partner' in channel:
            return 'Partner'
        elif 'cellcom' in channel or 'Cellcom' in channel:
            return 'Cellcom'
        elif 'free Tv' in channel or 'Free Tv' in channel:
            return 'Free Tv'
        elif 'world series' in channel or 'world series' in channel:
            return 'world series'
        else:
            return 'Other'


def main():
    app = QApplication(sys.argv)
    editor = M3UEditor()
    editor.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()