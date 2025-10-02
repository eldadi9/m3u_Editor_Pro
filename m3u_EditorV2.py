from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFileDialog, QTextEdit, QInputDialog,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView,
    QHBoxLayout, QLabel, QMessageBox, QLineEdit, QAbstractItemView, QAction,
    QCompleter, QProgressBar, QDialog, QComboBox, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QColor, QIcon

import sys
import os
import re
import traceback
import pyperclip
import json
import threading
import requests
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import subprocess
import time
import shutil  # ודא שמופיע בתחילת הקובץ שלך
import tempfile
from tempfile import NamedTemporaryFile
from PyQt5.QtWidgets import QMenu, QAction
from datetime import datetime, timedelta

from telegram_uploader import send_to_telegram
from deep_translator import GoogleTranslator

# משתנים גלובליים
LOGO_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logos_db.json")
new_logos_counter = 0
existing_logos_counter = 0


def playCatchupStream(self, url):
    try:
        if not url.startswith("http"):
            QMessageBox.warning(self, "Invalid URL", "כתובת הזרמה לא תקינה.")
            return
        vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
        if not os.path.exists(vlc_path):
            QMessageBox.critical(self, "VLC לא נמצא", "עדכן את הנתיב ל־VLC במערכת.")
            return
        subprocess.Popen([vlc_path, url])
    except Exception as e:
        QMessageBox.critical(self, "שגיאה", str(e))


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

            updated_categories[final_base] = channels
            category_mapping[old_name] = final_base
            self.progress.emit(i + 1, old_name)

        self.finished.emit(updated_categories, category_mapping, self.mode)


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


def save_logo_for_channel(channel_name, logo_url):
    try:
        with threading.Lock():  # ננעל את הגישה במקרה של ריבוי תהליכים
            # טען את המסד אם קיים
            if os.path.exists(LOGO_DB_PATH):
                with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                    logos_db = json.load(f)
            else:
                logos_db = {}

            # ודא שהערוץ נמצא ושהערך הוא רשימה
            if channel_name not in logos_db:
                logos_db[channel_name] = [logo_url]
                added = True
            else:
                existing_logos = logos_db[channel_name]
                if isinstance(existing_logos, str):
                    existing_logos = [existing_logos]
                if logo_url not in existing_logos:
                    existing_logos.append(logo_url)
                    logos_db[channel_name] = existing_logos
                    added = True
                else:
                    added = False

            if added:
                # כתיבה לקובץ זמני ואז העתקה לקובץ המקורי
                temp_path = LOGO_DB_PATH + ".tmp"
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(logos_db, f, indent=2, ensure_ascii=False)
                os.replace(temp_path, LOGO_DB_PATH)
                print(f"[LOGO] ✅ IL: {channel_name} | {logo_url}")
            else:
                print(f"[LOGO] ⚠️ Already exists: {channel_name} | {logo_url}")

    except Exception as e:
        print(f"[LOGO ERROR] Failed to save logo for {channel_name}: {e}")


def detect_stream_quality(name_or_url):
    text = name_or_url.lower()
    if "4k" in text or "2160" in text:
        return "4K"
    elif "1080" in text or "hd" in text:
        return "HD"
    elif "720" in text:
        return "HD"
    elif "sd" in text or "480" in text or "360" in text:
        return "SD"
    else:
        return "Unknown"


def create_channel_widget(name, quality):
    def quality_color(q):
        if q == "4K":
            return "#66cc66"  # ירוק
        elif q == "HD":
            return "#ffff66"  # צהוב
        elif q == "SD":
            return "#ff9999"  # אדום
        elif q == "Unknown":
            return "#cccccc"  # אפור בהיר ל־Unknown
        else:
            return "#e0e0e0"  # גיבוי – אפור ניטרלי

    widget = QWidget()
    layout = QHBoxLayout()
    layout.setContentsMargins(4, 2, 4, 2)
    layout.setSpacing(10)

    name_label = QLabel(name)
    name_label.setObjectName("channel_label")
    name_label.setStyleSheet("color: black; font-weight: normal;")
    layout.addWidget(name_label)

    quality_label = QLabel(quality)
    quality_label.setAlignment(Qt.AlignCenter)
    quality_label.setStyleSheet(f"""
        background-color: {quality_color(quality)};
        color: black;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
    """)
    layout.addWidget(quality_label)

    layout.addStretch()
    widget.setLayout(layout)
    return widget

    # הזרקת לוגו תקני
    if logo and isinstance(logo, str) and logo.startswith("http"):
        return line.replace("#EXTINF:-1", f'#EXTINF:-1 tvg-logo="{logo}"')

    # לא מצאנו לוגו – מחזירים את השורה המקורית
    return line


def save_israeli_logos_background(self, parsed_channels):
    for channel_name, category, line in parsed_channels:
        if is_israeli_channel(category, channel_name):
            match = re.search(r'tvg-logo="([^"]+)"', line)
            if match:
                logo_url = match.group(1)
                save_logo_for_channel(channel_name, logo_url)
                print(f"[LOGO] Saved logo for {channel_name}: {logo_url}")


def is_israeli_channel(category, name):
    keywords = [
        'ישראל', 'israel', 'israel vip', 'israel hd',
        'ערוץ', 'עברי', 'hot', 'yes', 'kan', 'keshet', 'reshet',
        'i24', 'channel 9', 'iptv israel', 'Израиль', 'Израиль | ישראלי'
    ]
    text = f"{category} {name}".lower()
    # בודק אם אחת ממילות המפתח מופיעה בטקסט (קטגוריה + שם ערוץ)
    return any(word in text for word in keywords)


class ExportGroupsDialog(QDialog):
    def __init__(self, categories, parent=None):
        super(ExportGroupsDialog, self).__init__(parent)
        self.categories = categories
        self.parent = parent
        self.setupUI()

    def setupUI(self):
        self.setGeometry(100, 100, 500, 300)  # Adjust size as needed
        self.setWindowTitle("Export Groups")
        layout = QVBoxLayout(self)
        layout.setSpacing(10)  # Adjust spacing between widgets

        # Styling the dialog frame and background
        self.setStyleSheet("QDialog { border: 8px solid red; background-color: white;}")

        # Option to export selected groups
        self.exportSelectedButton = QPushButton("Export Selected Groups", self)
        self.exportSelectedButton.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.exportSelectedButton.clicked.connect(self.exportSelected)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        layout.addWidget(self.exportSelectedButton)

        # Option to export all groups
        self.exportAllButton = QPushButton("Export All Groups", self)
        self.exportAllButton.setStyleSheet("background-color: black; color: white; font-weight: bold;")
        self.exportAllButton.clicked.connect(self.exportAll)
        layout.addWidget(self.exportAllButton)

        self.setLayout(layout)

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
                    # ✅ שימוש בשורת EXTINF המקורית אם קיימת
                    extinf_line = self.parent.extinf_lookup.get(channel)

                    # אם אין שורת EXTINF מקורית — ניצור אחת עם group-title
                    if not extinf_line:
                        channel_name = channel.split(" (")[0].strip()
                        extinf_line = f'#EXTINF:-1 group-title="{category}",{channel_name}'
                    else:
                        # אם יש EXTINF אבל חסר group-title — נוסיף group-title
                        if 'group-title="' not in extinf_line:
                            parts = extinf_line.split(",", 1)
                            if len(parts) == 2:
                                props, name = parts
                                extinf_line = f'{props} group-title="{category}",{name}'

                    url = self.parent.getUrl(channel)
                    channel_name = channel.split(" (")[0].strip()
                    url = self.parent.append_channel_name_to_url(url, channel_name)
                    file.write(f"{extinf_line}\n{url}\n")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export {category}: {str(e)}")


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
        self.downloadButton.clicked.connect(self.downloadM3U)
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
        username = self.usernameInput.text().strip()
        password = self.passwordInput.text().strip()
        host = self.hostInput.text().strip()

        if not username or not password or not host:
            self.resultLabel.setText("❌ Please fill all fields")
            return

        # הסרה של http/https אם יש
        if host.startswith("http://") or host.startswith("https://"):
            host = host.split("://")[1]

        # בנה את שתי הגרסאות האפשריות
        urls_to_try = [
            f"https://{host}/get.php?username={username}&password={password}&type=m3u_plus",
            f"http://{host}/get.php?username={username}&password={password}&type=m3u_plus"
        ]

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*"
        }

        for url in urls_to_try:
            try:
                response = requests.head(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    self.m3uURL = url
                    self.resultLabel.setText(f"✅ {self.m3uURL}")
                    self.copyButton.show()
                    self.downloadButton.show()
                    return
            except:
                continue

        # אם לא הצליח – תוצאה שקטה
        self.resultLabel.setText("❌ Could not find a working M3U URL")
        self.copyButton.hide()
        self.downloadButton.hide()

    def copyResultToClipboard(self):
        resultText = self.resultLabel.text()
        pyperclip.copy(resultText)
        QMessageBox.information(self, "Success", "Result copied to clipboard!")
        pass

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
    progress = pyqtSignal(int, int, int, tuple)  # checked, offline, duplicate, (name, url, status, reason)
    finished = pyqtSignal()

    def __init__(self, channels, duplicate_names):
        super().__init__()
        self.channels = channels
        self.duplicate_names = duplicate_names
        self.stop_requested = False

    def run(self):
        checked = offline = duplicate = 0
        duplicates_count = {}

        headers = {
            "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko)",
            "Accept": "*/*",
            "Connection": "close"
        }

        for name, url in self.channels:
            if self.stop_requested:
                break

                time.sleep(0.05)  # האטה כדי לא להציף את הרשת

            status = "Online"
            reason = ""

            # בדיקת דופליקייטים
            duplicates_count[name] = duplicates_count.get(name, 0) + 1
            is_duplicate = duplicates_count[name] > 1

            # בדיקת כתובת URL בפועל
            try:
                res = requests.get(url, headers=headers, stream=True, timeout=4)

                if res.status_code >= 400:
                    status = "Offline"
                    reason = f"HTTP {res.status_code}"
                elif not any(x in res.text.lower() for x in ["#extm3u", "http", ".ts", ".m3u8", ".mp4", ".aac"]):
                    status = "Offline"
                    reason = "Invalid Content"

            except requests.exceptions.Timeout:
                status = "Offline"
                reason = "Timeout"
            except requests.exceptions.ConnectionError:
                status = "Offline"
                reason = "Connection Error"
            except Exception as e:
                status = "Offline"
                reason = str(e)

            # עדכון מונים
            if status == "Offline":
                offline += 1
            if is_duplicate:
                duplicate += 1
                reason = (reason + " & Duplicate") if reason else "Duplicate"

            checked += 1
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
        self.setWindowTitle("Smart Scan In Progress")
        self.resize(800, 400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setStyleSheet("QDialog { border: 5px solid red; background-color: white; }")

        self.channels = channels
        self.duplicates = duplicates
        self.scan_results = []  # To support filtering

        layout = QVBoxLayout(self)

        # Label
        self.labelStats = QLabel("Starting scan...")
        self.labelStats.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.labelStats)

        # Progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(len(channels))
        self.progressBar.setValue(0)
        layout.addWidget(self.progressBar)

        # Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Channel", "Status", "Reason", "URL"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Buttons
        btnLayout = QHBoxLayout()
        self.stopBtn = QPushButton("Stop Scan")
        self.stopBtn.setStyleSheet("background-color: purple; color: white;")
        self.stopBtn.clicked.connect(self.stopScan)
        btnLayout.addWidget(self.stopBtn)

        self.markBtn = QPushButton("Mark Channels (Duplicates + Offline)")
        self.markBtn.setStyleSheet("background-color: purple; color: white; font-weight: bold;")
        self.markBtn.clicked.connect(self.markProblematicChannels)
        btnLayout.addWidget(self.markBtn)

        layout.addLayout(btnLayout)

        # Filter
        # Filter (dropdown) – reposition to top right with smaller size
        filter_layout = QHBoxLayout()
        filter_layout.setAlignment(Qt.AlignRight)  # Align to right

        filter_label = QLabel("Show:")
        filter_label.setStyleSheet("font-size: 10px;")

        self.filterCombo = QComboBox()
        self.filterCombo.setFixedWidth(120)  # Small width
        self.filterCombo.addItems(["All", "Online", "Offline", "Duplicate"])
        self.filterCombo.currentIndexChanged.connect(self.applyFilter)
        self.filterCombo.setStyleSheet("font-size: 10px; padding: 2px;")

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filterCombo)

        # Insert filter layout at the top (just under the progress bar)
        layout.insertLayout(2, filter_layout)  # Adjust index if needed

        # Thread must be created **after all setup**
        self.thread = SmartScanThread(channels, duplicates)
        self.thread.progress.connect(self.updateProgress)
        self.thread.finished.connect(self.scanFinished)
        self.thread.start()

    def updateProgress(self, checked, offline, duplicate, data):
        name, url, status, reason = data
        total = self.progressBar.maximum()
        problematic = offline + duplicate
        self.labelStats.setText(
            f"Scanned: {checked}/{total} | Offline: {offline} | Duplicates: {duplicate} | ❌ Total Not Good: {problematic}")
        self.progressBar.setValue(checked)
        self.scan_results.append((name, status, reason, url))
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(name))
        status_item = QTableWidgetItem(status)
        if "offline" in status.lower():
            status_item.setBackground(QColor("#ffcccc"))  # red
        elif "duplicate" in reason.lower():
            status_item.setBackground(QColor("#ffffcc"))  # yellow
        else:
            status_item.setBackground(QColor("#ccffcc"))  # green

        self.table.setItem(row, 1, status_item)
        self.table.setItem(row, 2, QTableWidgetItem(reason))
        self.table.setItem(row, 3, QTableWidgetItem(url))

    def refreshTable(self):
        self.table.setRowCount(0)
        selected_filter = self.filterCombo.currentText().lower()

        for name, status, reason, url in self.scan_results:
            if selected_filter != "all":
                if selected_filter == "offline" and "offline" not in status.lower():
                    continue
                elif selected_filter == "online" and "online" not in status.lower():
                    continue
                elif selected_filter == "duplicate" and "duplicate" not in reason.lower():
                    continue

            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(name))

            status_item = QTableWidgetItem(status)
            if "offline" in status.lower():
                status_item.setBackground(QColor("#ffcccc"))
            elif "duplicate" in reason.lower():
                status_item.setBackground(QColor("#ffffcc"))
            else:
                status_item.setBackground(QColor("#ccffcc"))

            self.table.setItem(row, 1, status_item)
            self.table.setItem(row, 2, QTableWidgetItem(reason))
            self.table.setItem(row, 3, QTableWidgetItem(url))

    def applyFilter(self):
        self.refreshTable()

    def scanFinished(self):
        self.labelStats.setText(self.labelStats.text() + " ✅ Done.")
        self.stopBtn.setEnabled(False)
        self.progressBar.setValue(self.progressBar.maximum())
        self.progressBar.setStyleSheet("QProgressBar::chunk { background-color: green; }")

    def stopScan(self):
        self.thread.stop()
        self.labelStats.setText("Scan stopped by user.")
        self.stopBtn.setEnabled(False)

    def markProblematicChannels(self):
        urls_to_mark = set()
        channel_statuses = {}
        duplicate_count = 0
        offline_count = 0

        # שלב ראשון: אסוף נתונים
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text().strip()
            status = self.table.item(row, 1).text().lower().strip()
            url = self.table.item(row, 3).text().strip()

            if name not in channel_statuses:
                channel_statuses[name] = []

            channel_statuses[name].append({'status': status, 'url': url})

        # שלב שני: סמן לפי החוקים
        for name, entries in channel_statuses.items():
            offline_entries = [e for e in entries if e['status'] == 'offline']
            online_entries = [e for e in entries if e['status'] != 'offline']

            # אם יש אופליין, תמיד לסמן אותם
            for entry in offline_entries:
                urls_to_mark.add(entry['url'])
                offline_count += 1

            # אם יותר מערוץ אחד (כפולים), נסמן רק את הכפולים שאינם כבר מסומנים (אונליין בלבד)
            if len(entries) > 1:
                duplicate_entries_to_mark = []
                if len(online_entries) > 1:
                    # יש יותר מאונליין אחד, נסמן את השני והלאה
                    duplicate_entries_to_mark.extend(online_entries[1:])
                elif len(online_entries) == 1 and offline_entries:
                    # אחד אונליין ויתר אופליין - לא לסמן אונליין, כבר סימנו אופליין
                    pass
                elif len(offline_entries) > 1 and not online_entries:
                    # כל הכפולים אופליין וכבר סומנו, אין צורך לעשות משהו נוסף
                    pass

                for entry in duplicate_entries_to_mark:
                    urls_to_mark.add(entry['url'])
                    duplicate_count += 1

        total_marked = len(urls_to_mark)

        # שלב שלישי: סימון בפועל
        if hasattr(self.parent(), "selectChannelsByUrls"):
            self.parent().selectChannelsByUrls(urls_to_mark)
            QMessageBox.information(
                self, "Marked",
                f"נמצאו {duplicate_count} כפולים וגם {offline_count} לא תקינים.\n"
                f"סה\"כ סומנו {total_marked} ערוצים."
            )
        else:
            QMessageBox.warning(
                self, "Error",
                "Method selectChannelsByUrls not found."
            )


def setup_session():
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


class M3UEditor(QWidget):
    logosFinished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.categories = {}
        self.logo_cache = {}  # ← שורה חדשה שפותחת את המטמון של הלוגואים
        self.initUI()
        self.load_logos_once()  # ← טעינה מיידית של קובץ logos_db.json (אם קיים)
        self.logosFinished.connect(self.onLogosFinished)

    def merge_or_fix_epg(self):
        """
        מאחד או מתקן את שורת ה־EPG בראש הקובץ לפי ספקים מזוהים.
        שומר שורת EXTמ3U אחת בלבד, עם כל קישורי ה־EPG התקפים שנמצאו.
        """

        # שלב 1: אסוף את כל הקישורים שהוזנו ידנית או מזוהים מהטעינה
        all_epg_links = set(self.epg_headers if hasattr(self, 'epg_headers') else [])

        # שלב 2: אם יש תוכן נטען, נזהה ספקים
        if hasattr(self, 'last_loaded_m3u') and self.last_loaded_m3u:
            try:
                with open("EPG_providers_full.json", "r", encoding="utf-8") as f:
                    providers = json.load(f)
            except Exception as e:
                QMessageBox.critical(self, "EPG Error", f"שגיאה בקריאת קובץ EPG:\n{e}")
                return

            # זיהוי ספקים לפי מילים מתוך JSON
            content_lower = self.last_loaded_m3u.lower()
            for provider, epg_list in providers.items():
                for keyword in [provider] + provider.split():
                    if keyword.lower() in content_lower:
                        all_epg_links.update(epg_list)

        # שלב 3: ניקוי השורות הקודמות והוספת אחת חדשה
        cleaned_lines = []
        added_header = False

        for line in self.last_loaded_m3u.splitlines():
            if not line.startswith("#EXTM3U"):
                cleaned_lines.append(line)
            elif not added_header:
                added_header = True  # רק שורה אחת תיכנס

        # בניית שורת EXTמ3U חדשה
        final_epg_links = ",".join(sorted(all_epg_links))
        new_header = f'#EXTM3U x-tvg-url="{final_epg_links}"' if final_epg_links else "#EXTM3U"

        cleaned_content = new_header + "\n" + "\n".join(cleaned_lines)
        self.last_loaded_m3u = cleaned_content  # שמירה לעתיד

        # טעינה מחדש למערכת
        self.loadM3UFromText(cleaned_content)

        QMessageBox.information(self, "EPG Updated", "✅ שורת EPG עודכנה והוזנה מחדש.")

    def open_channel_context_menu(self, position):
        try:
            item = self.channelList.itemAt(position)
            if not item:
                print("[ContextMenu] No channel selected - skipping menu")
                return

            channel_name = item.text().strip()
            if not channel_name:
                print("[ContextMenu] Empty channel name - aborting")
                return

            menu = QMenu(self)
            play_action = QAction("▶ נגן ב־VLC", self)
            play_action.triggered.connect(lambda: self.play_channel_with_name(channel_name))
            menu.addAction(play_action)

            menu.exec_(self.channelList.viewport().mapToGlobal(position))

        except Exception as e:
            print(f"[ContextMenu Error] {e}")
            QMessageBox.critical(self, "שגיאה", f"שגיאה בתפריט קליק ימני:\n{e}")

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

    def play_channel_with_name(self, entry):
        """
        מנגן ערוץ עם VLC ומוודא ששם הערוץ יוצג תקין ע"י שימוש בשורת EXTINF עם שם ולוגו.
        """
        try:
            print(f"[Play] מפעיל ערוץ לפי טקסט: {entry}")

            if "(" in entry and entry.endswith(")"):
                name = entry.split(" (")[0].strip()
                url = entry.split(" (")[-1].strip(")")
            else:
                name = "Unknown"
                url = entry.strip()

            extinf_line = self.extinf_lookup.get(entry)

            if not extinf_line:
                logo = self.get_saved_logo(name)
                logo_tag = f' tvg-logo="{logo}"' if logo else ''
                extinf_line = f'#EXTINF:-1{logo_tag} tvg-name="{name}" group-title="Live",{name}'

            with tempfile.NamedTemporaryFile(mode="w", suffix=".m3u", delete=False, encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                f.write(extinf_line + "\n")
                f.write(url + "\n")
                temp_path = f.name

            # בדיקה אם VLC קיים
            if not os.path.exists(r"C:\Program Files\VideoLAN\VLC\vlc.exe"):
                QMessageBox.critical(self, "VLC Error",
                                     "VLC לא נמצא בנתיב הקבוע.\nעדכן נתיב או ודא שהותקן.")
                return

            subprocess.Popen([r"C:\Program Files\VideoLAN\VLC\vlc.exe", temp_path])

        except Exception as e:
            print(f"[ERROR] VLC Play Error: {e}")
            QMessageBox.critical(self, "שגיאה", f"שגיאה בהרצת VLC:\n{e}")

    def append_channel_name_to_url(self, url, channel_name):
        """
        Appends the channel name to the URL as a parameter for debugging or tracking.
        Example: http://example.com → http://example.com?channel=Sport5_HD
        """
        try:
            if not url or not channel_name:
                return url

            clean_name = channel_name.strip().replace(" ", "_")
            if "?" in url:
                return f"{url}&channel={clean_name}"
            else:
                return f"{url}?channel={clean_name}"
        except Exception as e:
            print(f"[append_channel_name_to_url] Error: {e}")
            return url

    def getUrl(self, channel_string):
        try:
            if '(' in channel_string and ')' in channel_string:
                url = channel_string.split(" (")[-1].rstrip(")")
                if url.startswith("http"):
                    return url
            return ""
        except Exception:
            return ""

    def getUrlFromTextByChannelName(self, channel_name):
        lines = self.textEdit.toPlainText().splitlines()
        for i in range(len(lines) - 1):
            if lines[i].startswith("#EXTINF") and channel_name in lines[i]:
                url_line = lines[i + 1]
                if url_line.startswith("http"):
                    return url_line
        return ""

    def onLogosFinished(self):
        QMessageBox.information(self, "Logo Scan", "✅ סריקת הלוגואים הושלמה בהצלחה!")

    def initUI(self):
        self.setWindowTitle('M3U Playlist Editor')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        # Set a global font
        font = QFont('Arial', 10)
        QApplication.setFont(font)

        # Main layout
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # 🔲 לוגו עליון במסגרת שחורה
        logo_frame = QFrame(self)
        logo_frame.setStyleSheet("background-color: black;")
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(0, 0, 0, 0)

        logo_label = QLabel(self)
        image_path = r'C:\Users\Master_PC\Desktop\IPtv_projects\Projects Eldad\M3u_Editor_EldadV1\Main Logo.jpg'

        if os.path.exists(image_path):
            logo_pixmap = QPixmap(image_path)
            if not logo_pixmap.isNull():
                logo_pixmap = logo_pixmap.scaledToHeight(80, Qt.SmoothTransformation)
                logo_label.setPixmap(logo_pixmap)
                logo_label.setAlignment(Qt.AlignCenter)
            else:
                logo_label.setText("Failed to load image.")
                logo_label.setAlignment(Qt.AlignCenter)
        else:
            logo_label.setText("Image not found.")
            logo_label.setAlignment(Qt.AlignCenter)

        logo_layout.addWidget(logo_label)
        main_layout.addWidget(logo_frame)

        # 🔍 שורת חיפוש חכמה
        self.searchBox = QLineEdit()
        self.searchBox.setPlaceholderText("🔍 חיפוש קטגוריה או ערוץ...")
        self.searchBox.textChanged.connect(self.handleSearchTextChanged)

        reset_button = QPushButton("🔄 איפוס")
        reset_button.setStyleSheet("padding: 3px; font-weight: bold;")
        reset_button.clicked.connect(lambda: self.searchBox.setText(""))

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.searchBox)
        search_layout.addWidget(reset_button)
        main_layout.addLayout(search_layout)

        # 🧾 כותרת ראשית
        title = QLabel("M3U Playlist Editor", self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 25px; font-weight: bold; background-color: black; color: white;")
        main_layout.addWidget(title)

        # 🗂️ מידע על הקובץ וערוצים
        file_info_layout = QHBoxLayout()
        self.fileNameLabel = QLabel("No file loaded", self)
        self.fileNameLabel.setAlignment(Qt.AlignCenter)
        self.fileNameLabel.setStyleSheet("font-size: 18px; font-weight: bold;")
        file_info_layout.addWidget(self.fileNameLabel)

        self.channelCountLabel = QLabel("Total Channels: 0", self)
        self.channelCountLabel.setAlignment(Qt.AlignRight)
        self.channelCountLabel.setStyleSheet("font-size: 18px; font-weight: bold;")
        file_info_layout.addWidget(self.channelCountLabel)

        main_layout.addLayout(file_info_layout)

        # 🧩 אזורים אחרים
        main_layout.addLayout(self.create_category_section())
        main_layout.addLayout(self.create_channel_section())
        main_layout.addLayout(self.create_m3u_content_section())
        main_layout.addLayout(self.create_Tools())

        self.urlCheckButton = QPushButton('IPTV Checker', self)
        self.urlCheckButton.setStyleSheet("background-color: purple; color: white;")
        self.urlCheckButton.clicked.connect(self.openURLCheckerDialog)
        main_layout.addWidget(self.urlCheckButton)

        # ✅ וידוא EXT header
        self.textEdit.textChanged.connect(self.ensure_extm3u_header)

    def create_channel_section(self):
        layout = QVBoxLayout()

        # כותרת
        channel_title = QLabel("Channels", self)
        channel_title.setAlignment(Qt.AlignCenter)
        channel_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(channel_title)

        # שורת חיפוש חכמה - לא נדרשת פה אם כבר קיימת ב-initUI
        # לכן נוותר עליה כאן לחלוטין כדי למנוע כפילות!

        # קומבובוקס למיון
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

        # כפתורים לערוצים
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

        self.previewButton = QPushButton("▶ צפה בערוץ")
        self.previewButton.setIcon(QIcon("icons/vlc.png"))  # ← וודא שיש לך את הקובץ הזה בתיקייה
        self.previewButton.setStyleSheet("background-color: navy; color: white; font-weight: bold;")
        self.previewButton.clicked.connect(self.previewSelectedChannel)
        button_layout.addWidget(self.previewButton)

        for btn in [self.addChannelButton, self.deleteChannelButton, self.moveChannelUpButton,
                    self.moveChannelDownButton, self.selectAllChannelsButton, self.clearChannelsSelectionButton,
                    self.moveSelectedChannelButton, self.editSelectedChannelButton, self.checkDoublesButton]:
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        # חיבורים
        self.addChannelButton.clicked.connect(self.addChannel)
        self.deleteChannelButton.clicked.connect(self.deleteSelectedChannels)
        self.moveChannelUpButton.clicked.connect(self.moveChannelUp)
        self.moveChannelDownButton.clicked.connect(self.moveChannelDown)
        self.selectAllChannelsButton.clicked.connect(self.selectAllChannels)
        self.clearChannelsSelectionButton.clicked.connect(self.deselectAllChannels)
        self.moveSelectedChannelButton.clicked.connect(self.moveSelectedChannel)
        self.editSelectedChannelButton.clicked.connect(self.editSelectedChannel)

        # רשימת ערוצים
        self.channelList = QListWidget(self)
        self.channelList.setSelectionMode(QListWidget.MultiSelection)
        # הוספת תפריט קליק ימני
        self.channelList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.channelList.customContextMenuRequested.connect(self.open_channel_context_menu)
        layout.addWidget(self.channelList)

        return layout

    def load_logos_once(self):
        self.logo_cache = {}
        if os.path.exists(LOGO_DB_PATH):
            with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                self.logo_cache = json.load(f)

    def get_saved_logo(self, channel_name):
        logo = self.logo_cache.get(channel_name)
        if isinstance(logo, list):
            return logo[0] if logo else None
        elif isinstance(logo, str):
            return logo
        return None

    def inject_logo(self, line, channel_name, logo_db=None):
        """
        Injects saved logo into a #EXTINF line if missing.
        logo_db - optional dictionary to speed up repeated calls
        """
        if 'tvg-logo="' in line:
            return line  # יש כבר לוגו, לא עושים כלום

        # שלוף לוגו מה־DB (אם לא הועבר מבחוץ)
        if logo_db is None:
            logo = self.get_saved_logo(channel_name)
        else:
            logo = logo_db.get(channel_name)
            if isinstance(logo, list):
                logo = logo[0] if logo else None
            elif not isinstance(logo, str):
                logo = None

        # הזרקת לוגו תקני
        if logo and isinstance(logo, str) and logo.startswith("http"):
            return line.replace("#EXTINF:-1", f'#EXTINF:-1 tvg-logo="{logo}"')

        # לא מצאנו לוגו – מחזירים את השורה המקורית
        return line

    def exportM3UWithLogos(self, output_path):
        """
        כותב קובץ M3U תקני עם שמות ערוצים תקינים (EXTINF) ולוגואים אם קיימים.
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
                    extinf_line = self.extinf_lookup.get(channel, f'#EXTINF:-1,{channel.split(" (")[0].strip()}')
                    url_line = channel.split(" (")[-1].strip(")")

                    name = channel.split(" (")[0].strip()
                    extinf_with_logo = self.inject_logo(extinf_line, name, logo_db)

                    out.write(extinf_with_logo + "\n")
                    out.write(url_line + "\n")

    def openM3UConverterDialog(self):
        dialog = M3UUrlConverterDialog(self)
        dialog.exec_()

        def handle_download():
            url = url_input.text().strip()
            if not url:
                QMessageBox.warning(dialog, "Missing URL", "Please enter a valid M3U URL.")
                return

            if not re.match(r'^https?://', url):
                QMessageBox.warning(dialog, "Invalid URL", "Please enter a valid URL starting with http:// or https://")
                return

            try:
                session = setup_session()  # ← חדש
                response = session.get(url, timeout=5)
                response.raise_for_status()
                content = response.text.strip()

                if not content.startswith("#EXTM3U"):
                    QMessageBox.warning(dialog, "Invalid File", "The downloaded file is not a valid M3U playlist.")
                    return

                # שואל אם לטעון
                choice = QMessageBox.question(
                    dialog, "M3U Downloaded",
                    "M3U file downloaded successfully.\n\nDo you want to load it into the system?",
                    QMessageBox.Yes | QMessageBox.No
                )

                if choice == QMessageBox.Yes:
                    self.loadM3UFromText(content)
                else:
                    # קובע שם ברירת מחדל
                    match = re.search(r'username=([a-zA-Z0-9]+)', url)
                    if match:
                        default_name = f"{match.group(1)}.m3u"
                    else:
                        from datetime import datetime
                        default_name = f"m3u_{datetime.now().strftime('%Y%m%d_%H%M%S')}.m3u"

                    file_path, _ = QFileDialog.getSaveFileName(dialog, "Save M3U File", default_name,
                                                               "M3U Files (*.m3u);;All Files (*)")
                    if file_path:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        QMessageBox.information(dialog, "Saved", "M3U file saved successfully.")

                dialog.close()

            except Exception as e:
                QMessageBox.critical(dialog, "Download Error", f"Failed to download or parse M3U:\n{str(e)}")

        download_button.clicked.connect(handle_download)

        dialog.exec_()

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
        load_files_button = QPushButton("📂 Load Files.M3U", dialog)
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
        download_button = QPushButton("Download URL", dialog)
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
        if not append:
            self.categories.clear()

        # ----- 1️⃣ ניהול EPG headers -----
        if not hasattr(self, "epg_headers") or not append:
            self.epg_headers = []

        # שלב 1: אסוף את כל ה־EPG headers
        detected_epg_headers = []
        for line in content.strip().splitlines():
            if line.startswith("#EXTM3U") and ("url-tvg=" in line or "x-tvg-url=" in line):
                detected_epg_headers.append(line.strip())

        # שלב 2: הוספת headers ייחודיים
        for header in detected_epg_headers:
            if header not in self.epg_headers:
                self.epg_headers.append(header)

        # שלב 3: ניקוי כל שורות EXTМ3U (גם רגיל וגם עם tvg)
        content = "\n".join([
            line for line in content.strip().splitlines()
            if not line.startswith("#EXTM3U")
        ])

        # ----- 2️⃣ בניית שורת EXTМ3U אחידה -----
        unified_header = self.buildUnifiedEPGHeader()
        content = unified_header + "\n" + content

        # ----- 3️⃣ טעינת לוגואים -----
        self.load_logos_once()

        # ----- 4️⃣ פרס קובץ M3U -----
        self.parseM3UContentEnhanced(content)
        self.updateCategoryList()
        self.buildSearchCompleter()

        # ----- 5️⃣ בחירת קטגוריה ראשונה -----
        if self.categoryList.count() > 0:
            self.categoryList.setCurrentRow(0)
            self.display_channels(self.categoryList.currentItem())

        # ----- 6️⃣ סריקת לוגואים ברקע -----
        threading.Thread(
            target=self.extract_and_save_logos_for_all_channels,
            args=(content,),
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
                for i in range(self.categoryList.count()):
                    item = self.categoryList.item(i)
                    item.setBackground(QColor("white"))
                for i in range(self.channelList.count()):
                    ch_item = self.channelList.item(i)
                    ch_item.setBackground(QColor("white"))
                    ch_item.setSelected(False)
                return

            # 🔍 חיפוש בקטגוריות
            category_found = False
            for i in range(self.categoryList.count()):
                item = self.categoryList.item(i)
                category_name = item.text().split(" (")[0].lower()

                if text in category_name:
                    item.setBackground(QColor("#fff88a"))  # צהוב רך
                    self.categoryList.setCurrentItem(item)
                    self.display_channels(item)
                    category_found = True
                else:
                    item.setBackground(QColor("white"))

            # 🔍 אם לא נמצאה קטגוריה – חפש בערוצים
            if not category_found:
                for category, channels in self.categories.items():
                    for channel in channels:
                        channel_name = channel.split(" (")[0].lower()
                        if text in channel_name:
                            # טען את הקטגוריה התואמת
                            for i in range(self.categoryList.count()):
                                item = self.categoryList.item(i)
                                if category in item.text():
                                    item.setBackground(QColor("#fff88a"))  # צהוב
                                    self.categoryList.setCurrentItem(item)
                                    self.display_channels(item)
                                    break

                            # סמן את הערוץ התואם
                            for j in range(self.channelList.count()):
                                ch_item = self.channelList.item(j)
                                widget = self.channelList.itemWidget(ch_item)
                                if widget:
                                    label = widget.findChild(QLabel, "channel_label")
                                    if label and text in label.text().lower():
                                        ch_item.setSelected(True)
                                        ch_item.setBackground(QColor("#c0ffc0"))  # ירוק
                                        self.channelList.scrollToItem(ch_item)
                                        return

        except Exception as e:
            print(f"[Search Error] {e}")

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
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Open Additional M3U File", "",
            "M3U Files (*.m3u *.m3u8);;All Files (*)", options=options
        )
        if not fileName:
            return

        try:
            with open(fileName, 'r', encoding='utf-8') as file:
                new_content = file.read()

            # Extract EPG URLs from the EXT line
            for line in new_content.strip().splitlines():
                if line.startswith("#EXTM3U"):
                    matches = re.findall(r'(url-tvg|x-tvg-url)="([^"]+)"', line)
                    if not hasattr(self, "epg_headers"):
                        self.epg_headers = []
                    if matches:
                        urls = [match[1] for match in matches]
                        joined = ",".join(urls)
                        self.epg_headers.append(f'#EXTM3U url-tvg="{joined}"')

            # ✅ Clean and split new file
            new_lines = [line for line in new_content.strip().splitlines() if
                         line.strip() and not line.startswith("#EXTM3U")]

            try:
                with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                    logo_db = json.load(f)
            except:
                logo_db = {}

            merged_lines = []
            merged_channel_count = 0  # ✅ מונה חדש לערוצים
            i = 0
            while i < len(new_lines):
                line = new_lines[i]
                if line.startswith("#EXTINF:"):
                    extinf_line = line
                    url_line = new_lines[i + 1] if i + 1 < len(new_lines) else ""
                    name_match = re.search(r",(.+)", extinf_line)
                    channel_name = name_match.group(1).strip() if name_match else ""
                    extinf_line = self.inject_logo(extinf_line, channel_name, logo_db)  # ← תיקון!
                    merged_lines.append(extinf_line)
                    if url_line:
                        merged_lines.append(url_line)
                    merged_channel_count += 1  # ✅ עדכון מונה
                    i += 2
                else:
                    i += 1

            # Add to text editor
            current_content = self.textEdit.toPlainText().strip()
            current_lines = current_content.splitlines() if current_content else []

            # Remove old EPG headers
            current_lines = [line for line in current_lines if
                             not line.startswith("#EXTM3U")]

            # Build unified header
            header = self.buildUnifiedEPGHeader()
            final_lines = [header] + current_lines + merged_lines

            self.safely_update_text_edit("\n".join(final_lines))

            self.mergeM3UContentToCategories("\n".join(merged_lines), allow_duplicates=True)

            # ✅ הוספת השורה כאן:
            self.cleanEmptyCategories()

            self.updateCategoryList()
            self.regenerateM3UTextOnly()

            if self.categoryList.count() > 0:
                self.categoryList.setCurrentRow(0)
                self.display_channels(self.categoryList.currentItem())

            self.fileNameLabel.setText(f"Loaded File: {fileName.split('/')[-1]} (Merged)")

            # ✅ נוסיף הודעה עם מספר ערוצים:
            QMessageBox.information(
                self,
                "Merge Complete",
                f"The M3U files have been merged successfully.\nChannels added: {merged_channel_count}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", "Failed to merge M3U files: " + str(e))

    def loadM3UFromText(self, content, append=False):
        if not append:
            self.categories.clear()

        if not hasattr(self, "epg_headers") or not append:
            self.epg_headers = []

        for line in content.strip().splitlines():
            if line.startswith("#EXTM3U"):
                matches = re.findall(r'(url-tvg|x-tvg-url)="([^"]+)"', line)
                if matches:
                    urls = [match[1] for match in matches]
                    joined = ",".join(urls)
                    self.epg_headers.append(f'#EXTM3U url-tvg="{joined}"')

        # הסרה מוחלטת של כל שורות EXTМ3U
        content = "\n".join([line for line in content.strip().splitlines()
                             if not line.startswith("#EXTM3U")])

        unified_header = self.buildUnifiedEPGHeader()
        content = unified_header + "\n" + content

        self.load_logos_once()
        self.parseM3UContentEnhanced(content)
        self.updateCategoryList()
        self.buildSearchCompleter()
        self.logosFinished.connect(self.onLogosFinished)

        if self.categoryList.count() > 0:
            self.categoryList.setCurrentRow(0)
            self.display_channels(self.categoryList.currentItem())

        threading.Thread(
            target=self.extract_and_save_logos_for_all_channels,
            args=(content,),
            daemon=True
        ).start()

    def mergeM3UContentToCategories(self, content):
        lines = content.strip().splitlines()
        current_name = ""
        current_category = "Uncategorized📺"
        current_logo = None

        for i in range(len(lines)):
            line = lines[i].strip()

            if line.startswith("#EXTINF:"):
                name_match = re.search(r",(.+)", line)
                current_name = name_match.group(1).strip() if name_match else ""

                group_match = re.search(r'group-title="([^"]+)"', line)
                current_category = group_match.group(1).strip() if group_match else "Uncategorized📺"

                logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                current_logo = logo_match.group(1).strip() if logo_match else None

            elif line.startswith("http") and current_name:
                channel_entry = f"{current_name} ({line})"
                if current_logo:
                    channel_entry += f' tvg-logo="{current_logo}"'

                # 🟢 תמיד הוסף את הערוץ לקטגוריה – גם אם כפול
                if current_category not in self.categories:
                    self.categories[current_category] = []

                self.categories[current_category].append(channel_entry)

                current_name = ""
                current_logo = None

    def mergeM3UContentToCategories(self, content, allow_duplicates=True):
        """
        ממזג תוכן M3U לתוך self.categories.
        אם allow_duplicates=True – מוסיף גם ערוצים שכבר קיימים באותה קטגוריה.
        """
        lines = content.strip().splitlines()
        current_name = ""
        current_category = "Uncategorized📺"
        current_logo = None

        for i in range(len(lines)):
            line = lines[i].strip()

            if line.startswith("#EXTINF:"):
                name_match = re.search(r",(.+)", line)
                current_name = name_match.group(1).strip() if name_match else ""

                group_match = re.search(r'group-title="([^"]+)"', line)
                current_category = group_match.group(1).strip() if group_match else "Uncategorized📺"

                logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                current_logo = logo_match.group(1).strip() if logo_match else None

            elif line.startswith("http") and current_name:
                # צור רשומת ערוץ
                channel_entry = f"{current_name} ({line})"
                if current_logo:
                    channel_entry += f' tvg-logo="{current_logo}"'

                # הכן את הקטגוריה אם לא קיימת
                if current_category not in self.categories:
                    self.categories[current_category] = []

                # בדוק כפילות רק אם לא מאפשרים כפולים
                if allow_duplicates or channel_entry not in self.categories[current_category]:
                    self.categories[current_category].append(channel_entry)

                # שמירת EXTINF למעקב (אם קיים)
                if not hasattr(self, 'extinf_lookup'):
                    self.extinf_lookup = {}
                if channel_entry not in self.extinf_lookup:
                    self.extinf_lookup[channel_entry] = lines[i - 1]  # שורת EXTINF המקורית

                current_name = ""
                current_logo = None

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
        category_title.setStyleSheet("font-size: 18px; font-weight: bold;")
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

        return layout

    def create_Tools(self):
        layout = QVBoxLayout()
        tools_title = QLabel("Tools", self)
        tools_title.setAlignment(Qt.AlignCenter)
        tools_title.setStyleSheet("font-size: 18px; font-weight: bold;")
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

        self.convertPortalButton = QPushButton('🔄 Stalker MAC to M3U', self)
        self.convertPortalButton.setStyleSheet("background-color: black; color: white;")
        self.convertPortalButton.clicked.connect(self.convertPortalToM3U)
        buttons_layout.addWidget(self.convertPortalButton)

        # Export Groups button
        self.exportGroupButton = QPushButton('📤 Export Groups', self)
        self.exportGroupButton.setStyleSheet("background-color: black; color: white;")
        self.exportGroupButton.clicked.connect(self.openExportDialog)
        buttons_layout.addWidget(self.exportGroupButton)

        self.filterIsraelChannelsButton = QPushButton('🇮🇱 IsraelX Export', self)
        self.filterIsraelChannelsButton.setStyleSheet("background-color: black; color: white;")
        self.filterIsraelChannelsButton.clicked.connect(self.chooseLanguageAndFilterIsraelChannels)

        buttons_layout.addWidget(self.filterIsraelChannelsButton)

        self.smartScanButton = QPushButton('🔍 Smart Scan', self)
        self.smartScanButton.setStyleSheet("background-color: black; color: white; font-weight: ;")
        self.smartScanButton.clicked.connect(self.openSmartScanDialog)
        buttons_layout.addWidget(self.smartScanButton)

        self.manageLogosButton = QPushButton('🖼️ Logo Manager', self)
        self.manageLogosButton.setStyleSheet("background-color: black; color: red;")
        self.manageLogosButton.clicked.connect(self.open_logo_manager)
        buttons_layout.addWidget(self.manageLogosButton)

        self.mergeEPGButton = QPushButton('📺 Fix EPG', self)
        self.mergeEPGButton.setStyleSheet("background-color: black; color: white;")
        self.mergeEPGButton.clicked.connect(self.merge_or_fix_epg)
        buttons_layout.addWidget(self.mergeEPGButton)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        # Add the horizontal layout to the vertical layout
        layout.addLayout(buttons_layout)

        return layout

    def convertPortalToM3U(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Portal to M3U Converter")
        dialog.setGeometry(300, 300, 600, 300)
        dialog.setStyleSheet("""
            QDialog { background-color: white; border: 5px solid red; }
            QPushButton { font-weight: bold; height: 40px; }
            QLineEdit { font-size: 14px; padding: 6px; }
        """)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Enter your Portal URL:"))
        portal_input = QLineEdit()
        portal_input.setPlaceholderText("http://example.com/stalker_portal/")
        layout.addWidget(portal_input)

        layout.addWidget(QLabel("Enter your MAC Address:"))
        mac_input = QLineEdit()
        mac_input.setPlaceholderText("00:1A:79:XX:XX:XX")
        layout.addWidget(mac_input)

        convert_button = QPushButton("Convert & Download")
        convert_button.setStyleSheet("background-color: red; color: white;")
        layout.addWidget(convert_button)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(close_button)

        close_button.clicked.connect(dialog.close)

        def handle_conversion():
            portal_url = portal_input.text().strip()
            mac_address = mac_input.text().strip()

            if not portal_url or not mac_address:
                QMessageBox.warning(dialog, "Missing Input", "Please enter both Portal URL and MAC address.")
                return

            if not portal_url.endswith('/'):
                portal_url += '/'

            session = setup_session()

            headers = {
                "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko)",
                "Referer": portal_url,
                "X-User-Agent": "Model: MAG254; Link: Ethernet"
            }

            try:
                handshake_url = f"{portal_url}server/load.php"
                handshake_data = {"type": "stb", "action": "handshake", "token": "", "mac": mac_address}
                response = session.post(handshake_url, headers=headers, json=handshake_data, timeout=10)

                if response.status_code != 200 or not response.text.strip():
                    QMessageBox.critical(dialog, "Error", "Failed to connect to portal. Check the Portal URL.")
                    return

                token = response.json().get("js", {}).get("token", None)
                if not token:
                    QMessageBox.critical(dialog, "Error", "Authentication failed. Check your MAC and Portal URL.")
                    return

                channels_url = f"{portal_url}stalker_portal/server/load.php?type=itv&action=get_all_channels&mac={mac_address}&token={token}"
                channels_response = session.get(channels_url, headers=headers, timeout=10)

                if channels_response.status_code != 200 or not channels_response.text.strip():
                    QMessageBox.critical(dialog, "Error", "Failed to retrieve channel list.")
                    return

                channels = channels_response.json().get("js", {}).get("data", [])
                if not channels:
                    QMessageBox.critical(dialog, "Error", "No channels found.")
                    return

                m3u_content = "#EXTM3U\n"
                for channel in channels:
                    name = channel.get("name", "Unknown Channel")
                    stream_url = channel.get("cmd", "")
                    m3u_content += f"#EXTINF:-1,{name}\n{stream_url}\n"

                file_path, _ = QFileDialog.getSaveFileName(dialog, "Save M3U File", "playlist.m3u",
                                                           "M3U Files (*.m3u);;All Files (*)")
                if file_path:
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(m3u_content)
                    QMessageBox.information(dialog, "Success", "M3U file successfully created!")

                dialog.close()

            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to convert Portal MAC to M3U:\n{str(e)}")

        convert_button.clicked.connect(handle_conversion)
        dialog.exec_()

    def displayTotalChannels(self):
        total_channels = sum(len(channels) for channels in self.categories.values())
        total_categories = len(self.categories)
        text = f"📺 Total Channels: {total_channels}   |   🗂 Categories: {total_categories}"
        self.channelCountLabel.setText(text)
        self.channelCountLabel.setToolTip(f"{total_channels} ערוצים בסך הכל ב-{total_categories} קטגוריות")

    def sortChannels(self):
        sort_option = self.sortingComboBox.currentText()
        current_category = self.categoryList.currentItem().text().split(" (")[
            0] if self.categoryList.currentItem() else None

        if current_category and current_category in self.categories:
            if sort_option == "Sort by Name A-Z":
                self.categories[current_category].sort(key=lambda x: x.split(" (")[0])
            elif sort_option == "Sort by Name Z-A":
                self.categories[current_category].sort(key=lambda x: x.split(" (")[0], reverse=True)
            elif sort_option == "Sort by Stream Type":
                self.categories[current_category].sort(key=lambda x: x.split(",")[-1])
            elif sort_option == "Sort by Group Title":
                self.categories[current_category].sort(key=lambda x: x.split("group-title=")[-1].split(",")[0])
            elif sort_option == "Sort by URL Length":
                self.categories[current_category].sort(key=lambda x: len(x.split(",")[-1]))
            elif sort_option == "Sort by Quality (4K → SD)":
                def quality_rank(channel):
                    quality = detect_stream_quality(channel)
                    if quality == "4K":
                        return 0
                    elif quality == "HD":
                        return 1
                    elif quality == "SD":
                        return 2
                    else:
                        return 3

                self.categories[current_category].sort(key=quality_rank)

            self.display_channels(self.categoryList.currentItem())
            self.regenerateM3UTextOnly()  # <-- Add this line

    def create_m3u_content_section(self):
        layout = QVBoxLayout()

        m3u_title = QLabel("M3U Content", self)
        m3u_title.setAlignment(Qt.AlignCenter)
        m3u_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(m3u_title)

        self.textEdit = QTextEdit(self)
        layout.addWidget(self.textEdit)

        button_layout = QHBoxLayout()

        self.loadButton = QPushButton('Load M3U')
        self.saveButton = QPushButton('Save M3U')
        self.mergeButton = QPushButton('Merge M3Us')
        self.exportTelegramButton = QPushButton(" Export to Telegram")  # ← כפתור חדש
        self.exportTelegramButton.setIcon(QIcon("icons/telegram.png"))

        self.loadButton.setStyleSheet("background-color: green; color: white;")
        self.saveButton.setStyleSheet("background-color: red; color: white;")
        self.mergeButton.setStyleSheet("background-color: blue; color: white;")
        self.exportTelegramButton.setStyleSheet("background-color: teal; color: white;")

        self.loadButton.clicked.connect(self.loadM3U)
        self.saveButton.clicked.connect(self.saveM3U)
        self.mergeButton.clicked.connect(self.mergeM3Us)
        self.exportTelegramButton.clicked.connect(self.exportToTelegram)  # ← חיבור לפונקציה

        # הוספה ללייאאוט
        button_layout.addWidget(self.loadButton)
        button_layout.addWidget(self.saveButton)
        button_layout.addWidget(self.mergeButton)
        button_layout.addWidget(self.exportTelegramButton)  # ← בסוף מימין

        layout.addLayout(button_layout)

        return layout

    def addCategory(self):
        category, ok = QInputDialog.getText(self, 'Add Category', 'Enter category name:')
        if ok and category and category not in self.categories:
            self.categories[category] = []
            self.updateCategoryList()  # Update the category list

    def updateCategoryList(self):
        """
        Updates the category list dynamically to reflect the current channel counts.
        """
        self.categoryList.clear()
        for category, channels in self.categories.items():
            display_text = f"{category} ({len(channels)})"
            self.categoryList.addItem(display_text)

            # עדכון הספירה הכללית של ערוצים + קטגוריות
            self.displayTotalChannels()

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
        current_row = self.categoryList.currentRow()
        if current_row > 0:
            current_item = self.categoryList.takeItem(current_row)
            self.categoryList.insertItem(current_row - 1, current_item)
            self.categoryList.setCurrentRow(current_row - 1)

            category_keys = list(self.categories.keys())
            category_keys[current_row], category_keys[current_row - 1] = category_keys[current_row - 1], category_keys[
                current_row]
            reordered_categories = {key: self.categories[key] for key in category_keys}
            self.categories = reordered_categories

            self.refreshCategoryListOnly(selected_index=current_row - 1)
            self.regenerateM3UTextOnly()

    def moveCategoryDown(self):
        current_row = self.categoryList.currentRow()
        if current_row < self.categoryList.count() - 1:
            current_item = self.categoryList.takeItem(current_row)
            self.categoryList.insertItem(current_row + 1, current_item)
            self.categoryList.setCurrentRow(current_row + 1)

            category_keys = list(self.categories.keys())
            category_keys[current_row], category_keys[current_row + 1] = category_keys[current_row + 1], category_keys[
                current_row]
            reordered_categories = {key: self.categories[key] for key in category_keys}
            self.categories = reordered_categories

            self.refreshCategoryListOnly(selected_index=current_row + 1)
            self.regenerateM3UTextOnly()

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
        updated_lines = []

        # הוספת שורת EPG בראש
        if hasattr(self, "epg_headers") and self.epg_headers:
            updated_lines.append(self.buildUnifiedEPGHeader())
        else:
            updated_lines.append("#EXTM3U")

        logo_db = {}
        if fast_mode and os.path.exists(LOGO_DB_PATH):
            try:
                with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                    logo_db = json.load(f)
            except Exception as e:
                print(f"[LOGO] Failed to load logo DB: {e}")

        for category, channels in self.categories.items():
            for channel in channels:
                try:
                    name, url = channel.split(" (", 1)
                    name = name.strip()
                    url = url.strip(") \n")
                except:
                    continue

                logo_url = logo_db.get(name)
                if isinstance(logo_url, list):
                    logo_url = logo_url[0] if logo_url else None

                extinf = f'#EXTINF:-1'
                if logo_url:
                    extinf += f' tvg-logo="{logo_url}"'
                extinf += f' group-title="{category}",{name}'

                updated_lines.append(f"{extinf}\n{url}")

        self.safely_update_text_edit("\n".join(updated_lines))

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
            channel_item = QListWidgetItem(name)
            self.channelList.addItem(channel_item)
            selected_category = self.categoryList.currentItem()
            if selected_category:
                category_name = selected_category.text()
                self.categories[category_name].append(f"{name} ({url})")
                self.updateM3UContent()

    def deleteSelectedChannels(self):
        selected_indexes = []
        for i in range(self.channelList.count()):
            if self.channelList.item(i).isSelected():
                selected_indexes.append(i)

        if not selected_indexes:
            QMessageBox.information(self, "No Selection", "No channels selected for deletion.")
            return

        selected_category_item = self.categoryList.currentItem()
        if not selected_category_item:
            QMessageBox.warning(self, "No Category", "Please select a category.")
            return

        category_name = selected_category_item.text().split(" (")[0]
        if category_name not in self.categories:
            QMessageBox.warning(self, "Invalid Category", "Selected category not found.")
            return

        channels_in_category = self.categories[category_name]
        original_len = len(channels_in_category)

        self.categories[category_name] = [
            ch for i, ch in enumerate(channels_in_category)
            if i not in selected_indexes
        ]

        deleted = original_len - len(self.categories[category_name])

        # ← הוספה כאן — בדיוק אחרי שינוי ה־categories:
        self.cleanEmptyCategories()

        self.updateCategoryList()
        self.regenerateM3UTextOnly()
        if self.categoryList.currentItem():
            self.display_channels(self.categoryList.currentItem())

        QMessageBox.information(self, "Success", f"Deleted {deleted} channel(s).")
        self.displayTotalChannels()

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

    def getCategoryName(self, channel):
        """
        Placeholder method to extract the category from a channel string.
        """
        # Implement logic based on your channel data structure
        return "Default Category"

    def getUrl(self, channel):
        """
        Extracts the URL from a channel string.
        """
        return channel.split(' (')[1].strip(')')

    def moveChannelUp(self):
        current_row = self.channelList.currentRow()
        if current_row <= 0:
            return

        # שלוף את שם הערוץ ששמרנו מראש
        current_item = self.channelList.item(current_row)
        channel_name = current_item.data(Qt.UserRole)

        # הסר את הפריט הישן
        self.channelList.takeItem(current_row)

        # שלוף את quality מהתוכן המקורי
        current_category = self.categoryList.currentItem().text().split(" (")[0].strip()
        real_category = {k.strip(): k for k in self.categories.keys()}.get(current_category, current_category)
        channels = self.categories.get(real_category, [])
        channel_full_line = channels[current_row]
        quality = detect_stream_quality(channel_full_line)

        # צור ווידג'ט חדש
        new_widget = create_channel_widget(channel_name, quality)
        new_item = QListWidgetItem()
        new_item.setSizeHint(new_widget.sizeHint())
        new_item.setData(Qt.UserRole, channel_name)

        # הכנס שורה למעלה
        self.channelList.insertItem(current_row - 1, new_item)
        self.channelList.setItemWidget(new_item, new_widget)
        self.channelList.setCurrentRow(current_row - 1)

        # עדכון רשימת הערוצים הלוגית
        channels[current_row], channels[current_row - 1] = channels[current_row - 1], channels[current_row]
        self.categories[real_category] = channels
        self.regenerateM3UTextOnly()

    def moveChannelDown(self):
        current_row = self.channelList.currentRow()
        if current_row < 0 or current_row >= self.channelList.count() - 1:
            return

        current_item = self.channelList.item(current_row)
        channel_name = current_item.data(Qt.UserRole)

        # הסר את הפריט מהשורה הנוכחית
        self.channelList.takeItem(current_row)

        # שלוף את quality מתוך התוכן המקורי
        current_category = self.categoryList.currentItem().text().split(" (")[0].strip()
        real_category = {k.strip(): k for k in self.categories.keys()}.get(current_category, current_category)
        channels = self.categories.get(real_category, [])
        channel_full_line = channels[current_row]
        quality = detect_stream_quality(channel_full_line)

        # צור ווידג'ט חדש
        new_widget = create_channel_widget(channel_name, quality)
        new_item = QListWidgetItem()
        new_item.setSizeHint(new_widget.sizeHint())
        new_item.setData(Qt.UserRole, channel_name)

        # הכנס למקום החדש (שורה אחת למטה)
        self.channelList.insertItem(current_row + 1, new_item)
        self.channelList.setItemWidget(new_item, new_widget)
        self.channelList.setCurrentRow(current_row + 1)

        # עדכון רשימת הערוצים הלוגית
        channels[current_row], channels[current_row + 1] = channels[current_row + 1], channels[current_row]
        self.categories[real_category] = channels
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
        for i in range(self.channelList.count()):
            self.channelList.item(i).setSelected(True)

    def deselectAllChannels(self):
        for i in range(self.channelList.count()):
            self.channelList.item(i).setSelected(False)

    def moveSelectedChannel(self):
        try:
            print("[DEBUG] Starting moveSelectedChannel...")

            selected_items = self.channelList.selectedItems()
            if not selected_items:
                print("[DEBUG] No channels selected.")
                QMessageBox.warning(self, "Warning", "No channels selected for moving.")
                return

            # נשלוף את השמות דרך ה־QLabel בתוך ה־QWidget
            selected_names = []
            for item in selected_items:
                widget = self.channelList.itemWidget(item)
                if widget:
                    label = widget.findChild(QLabel, "channel_label")  # השם חייב להיות מוגדר
                    if label:
                        selected_names.append(label.text().strip())

            print(f"[DEBUG] Selected channel names: {selected_names}")

            dialog = MoveChannelsDialog(self, list(self.categories.keys()))
            if not dialog.exec_():
                print("[DEBUG] MoveChannelsDialog canceled by user.")
                return

            target_category = dialog.getSelectedCategory().strip()
            print(f"[DEBUG] Target category selected: {target_category}")

            if not target_category:
                QMessageBox.warning(self, "Warning", "No target category specified.")
                return

            if target_category not in self.categories:
                self.categories[target_category] = []
                print(f"[DEBUG] Target category '{target_category}' created.")

            current_item = self.categoryList.currentItem()
            if not current_item:
                print("[DEBUG] No current category selected.")
                QMessageBox.warning(self, "Warning", "No category selected.")
                return

            current_category = current_item.text().split(" (")[0].strip()
            print(f"[DEBUG] Current category: {current_category}")

            if current_category not in self.categories:
                QMessageBox.warning(self, "Warning", f"Category '{current_category}' does not exist.")
                return

            moved_channels = []
            remaining_channels = []

            original_list = self.categories[current_category]
            print(f"[DEBUG] Original list size: {len(original_list)}")

            for channel in original_list:
                channel_name = channel.split(" (")[0].strip()
                if channel_name in selected_names:
                    moved_channels.append(channel)
                else:
                    remaining_channels.append(channel)

            print(f"[DEBUG] Channels to move: {len(moved_channels)}")
            print(f"[DEBUG] Channels remaining: {len(remaining_channels)}")

            if moved_channels:
                self.categories[current_category] = remaining_channels
                self.categories[target_category].extend(moved_channels)

                # ✅ הוספת השורה כאן:
                self.cleanEmptyCategories()

                self.regenerateM3UTextOnly()
                self.updateCategoryList()

                for i in range(self.categoryList.count()):
                    if self.categoryList.item(i).text().startswith(target_category):
                        self.categoryList.setCurrentRow(i)
                        self.display_channels(self.categoryList.item(i))
                        break

                self.deselectAllChannels()

                QMessageBox.information(self, "Success",
                                        f"{len(moved_channels)} channels moved to '{target_category}'.")

            else:
                print("[DEBUG] No channels matched for moving.")

            print("[DEBUG] moveSelectedChannel finished successfully.")

        except Exception as e:
            print(f"[ERROR] moveSelectedChannel crashed: {str(e)}")
            QMessageBox.critical(self, "Critical Error", f"Error in moveSelectedChannel:\n{str(e)}")

    def previewSelectedChannel(self):
        selected_items = self.channelList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "אין ערוץ נבחר", "בחר ערוץ אחד לפחות לצפייה.")
            return

        vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
        if not os.path.exists(vlc_path):
            QMessageBox.critical(self, "VLC לא נמצא", f"VLC לא נמצא בנתיב:\n{vlc_path}")
            return

        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".m3u", delete=False, encoding="utf-8") as f:
                f.write("#EXTM3U\n")

                for item in selected_items:
                    widget = self.channelList.itemWidget(item)
                    if widget:
                        label = widget.findChild(QLabel, "channel_label")
                        if not label:
                            continue
                        channel_name = label.text().strip()

                        url = self.getUrl(channel_name) or self.getUrlFromTextByChannelName(channel_name)
                        if not url or not url.startswith("http"):
                            continue

                        extinf_line = self.extinf_lookup.get(f"{channel_name} ({url})")

                        if not extinf_line:
                            logo = self.get_saved_logo(channel_name)
                            logo_tag = f' tvg-logo="{logo}"' if logo else ''
                            extinf_line = f'#EXTINF:-1{logo_tag} tvg-name="{channel_name}" group-title="Preview",{channel_name}'

                        f.write(extinf_line + "\n")
                        f.write(url + "\n")

                temp_path = f.name

            subprocess.Popen([vlc_path, temp_path])

        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בהרצת VLC:\n{str(e)}")

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
        מציג את הערוצים עם טקסט שחור רגיל + תגית איכות צבעונית מימין (באמצעות create_channel_widget).
        """
        self.channelList.clear()

        if item is None:
            self.channelCountLabel.setText("Total Channels: 0")
            return

        category = item.text().split(" (")[0].strip()
        normalized_categories = {k.strip(): k for k in self.categories.keys()}

        if category not in normalized_categories:
            QMessageBox.critical(self, "Error", f"Category '{category}' not found in categories.")
            return

        real_category = normalized_categories[category]
        channels = self.categories.get(real_category, [])

        for channel in channels:
            channel_name = channel.split(" (")[0].strip()
            if not channel_name:
                continue

            # איכות
            quality = detect_stream_quality(channel)

            # יצירת ווידג'ט מעוצב
            widget = create_channel_widget(channel_name, quality)

            # יצירת פריט חדש
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            item.setData(Qt.UserRole, channel_name)  # 🟢 כאן! שמור את שם הערוץ עבור moveUp/Down

            # הוספה לרשימה והצמדת ווידג'ט
            self.channelList.addItem(item)
            self.channelList.setItemWidget(item, widget)

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
        dialog = QDialog(self)
        dialog.setWindowTitle("Smart Scan")
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        dialog.setStyleSheet("""
            QDialog {
                border: 6px solid red;
                background-color: white;
            }
        """)

        layout = QVBoxLayout(dialog)
        label = QLabel("Choose scan type:")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        category_btn = QPushButton("Scan Selected Category")
        all_btn = QPushButton("Scan All Channels")

        category_btn.setStyleSheet("background-color: black; color: white; font-weight: bold;")
        all_btn.setStyleSheet("background-color: red; color: white; font-weight: bold;")

        layout.addWidget(category_btn)
        layout.addWidget(all_btn)

        category_btn.clicked.connect(lambda: [dialog.accept(), self.showSmartScanCategoryPicker()])
        all_btn.clicked.connect(lambda: [dialog.accept(), self.startSmartScan(all_categories=True)])

        dialog.setLayout(layout)
        dialog.exec_()

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
                        self.loadEPG(epg_candidate)
                        break  # נטען רק את הראשון שנמצא

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

    def playCatchupIfExists(self, epg_entry):
        # בעתיד: אם יש catchup-url מובנה בתוך epg_entry
        QMessageBox.information(self, "Play", f"Trying to play:\n{epg_entry.get('title')}")

    def saveM3U(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save M3U File", "", "M3U Files (*.m3u);;All Files (*)",
                                                  options=options)
        if fileName:
            with open(fileName, 'w', encoding='utf-8') as file:
                file.write(self.textEdit.toPlainText())

    def exportToTelegram(self):
        name, ok = QInputDialog.getText(self, "ייצוא לטלגרם", "איך לקרוא לקובץ (למשל playlist.m3u)?")
        if not ok or not name.strip():
            return

        if not name.lower().endswith(".m3u"):
            name += ".m3u"

        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(mode="w", delete=False, suffix=".m3u", encoding="utf-8") as tmp:
            tmp.write(self.textEdit.toPlainText())
            tmp_path = tmp.name

        success = send_to_telegram(tmp_path, filename=name)
        if success:
            QMessageBox.information(self, "Telegram", f"✅ הקובץ '{name}' נשלח לטלגרם.")
        else:
            QMessageBox.warning(self, "Telegram", f"❌ שליחה נכשלה.")

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

    def filterIsraelChannelsFromKeywords(self, lang):
        from channel_keywords import CATEGORY_KEYWORDS_EN, CATEGORY_KEYWORDS_HE

        keywords_map = CATEGORY_KEYWORDS_HE if lang == "he" else CATEGORY_KEYWORDS_EN
        israel_keywords = ['Israel', 'IL', 'ISRAEL', 'Hebrew', 'hebrew', 'israeli', 'Israeli', '"IL"', 'Il',
                           'IL HD', 'TV', 'MUSIC', 'ישראלי', 'MTV', 'USA', 'mtv', 'Music Hits+', 'WWE ', 'nba tv',
                           'music', 'IL:', 'Hebrew']

        filtered_channels = {cat: [] for cat in keywords_map}
        filtered_channels['Other'] = []
        filtered_channels['Israel Radio📻'] = []
        filtered_channels['World Radio🌍'] = []

        for category, channels in self.categories.items():
            for channel in channels:
                if any(keyword in channel for keyword in israel_keywords):
                    placed = False
                    for cat_name, keyword_list in keywords_map.items():
                        if any(k.lower() in channel.lower() for k in keyword_list):
                            filtered_channels[cat_name].append(channel)
                            placed = True
                            break
                    if not placed:
                        filtered_channels['Other'].append(channel)

        # טעינת תחנות רדיו
        self.loadRadioChannels(filtered_channels, 'Israel Radio📻',
                               r"C:\Users\Master_PC\Desktop\IPtv_projects\Projects Eldad\M3u_Editor_EldadV1\IsraeliRadios.m3u")

        self.loadRadioChannels(filtered_channels, 'World Radio🌍',
                               r"C:\Users\Master_PC\Desktop\IPtv_projects\Projects Eldad\M3u_Editor_EldadV1\RADIO World.m3u")

        # עדכון UI
        self.categories = filtered_channels
        self.updateCategoryList()
        self.regenerateM3UTextOnly()
        self.categoryList.clear()
        for category, channels in self.categories.items():
            self.categoryList.addItem(f"{category} ({len(channels)})")

    def loadRadioCategories(self, filtered_channels, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            current_name, current_logo, current_group = None, None, "Uncategorized📻"

            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF:"):
                    logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                    group_match = re.search(r'group-title="([^"]+)"', line)
                    current_logo = logo_match.group(1) if logo_match else None
                    current_group = group_match.group(1) if group_match else "Uncategorized📻"
                    current_name = line.split(",")[-1].strip()
                elif line.startswith("http") and current_name:
                    channel_entry = f"{current_name} ({line})"
                    if current_logo:
                        channel_entry += f' tvg-logo="{current_logo}"'

                    if current_group not in filtered_channels:
                        filtered_channels[current_group] = []

                    filtered_channels[current_group].append(channel_entry)

                    current_name, current_logo, current_group = None, None, "Uncategorized📻"

        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"The file {file_path} was not found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while loading the M3U file: {str(e)}")

    def loadRadioChannels(self, filtered_channels, category, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            current_name = None
            current_logo = None
            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF:"):
                    logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                    current_logo = logo_match.group(1) if logo_match else None
                    current_name = line.split(",")[-1].strip()
                elif line.startswith("http") and current_name:
                    channel_entry = f"{current_name} ({line})"
                    if current_logo:
                        channel_entry += f' tvg-logo="{current_logo}"'
                    filtered_channels[category].append(channel_entry)
                    current_name = None
                    current_logo = None

        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"The file {file_path} was not found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while loading the M3U file: {str(e)}")

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