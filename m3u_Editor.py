from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFileDialog,
    QTextEdit, QInputDialog, QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView,
    QHBoxLayout, QLabel, QMessageBox, QLineEdit, QAbstractItemView, QAction)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QColor  # Add this line
import sys
import os
import re
import traceback
import pyperclip
import json
import threading
from PyQt5.QtWidgets import QCompleter
import requests  # You need to import requests to handle downloading
from urllib.parse import urlparse
from PyQt5.QtWidgets import QProgressBar
import xml.etree.ElementTree as ET
from PyQt5.QtCore import pyqtSignal
from datetime import datetime, timedelta
LOGO_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logos_db.json")
new_logos_counter = 0
existing_logos_counter = 0

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QHBoxLayout


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
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        buttonBox.addWidget(self.okButton)
        buttonBox.addWidget(self.cancelButton)
        layout.addLayout(buttonBox)

        self.setLayout(layout)

    def getSelectedCategory(self):
        return self.newCategoryInput.text().strip() if self.newCategoryInput.text().strip() else self.categoryCombo.currentText()


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



def get_saved_logo(channel_name):
    if not os.path.exists(LOGO_DB_PATH):
        return None

    try:
        with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        logo = data.get(channel_name)

        # תמיכה בלוגו ישן (מחרוזת) או חדש (רשימה)
        if isinstance(logo, list):
            return logo[0] if logo else None
        elif isinstance(logo, str):
            return logo
        else:
            return None

    except Exception as e:
        print(f"[ERROR] Error loading logo DB: {e}")
        return None



def inject_logo(line, channel_name, logo_db=None):
    """
    Injects saved logo into a #EXTINF line if missing.
    logo_db - optional dictionary to speed up repeated calls
    """
    if 'tvg-logo="' in line:
        return line

    if logo_db is None:
        logo = get_saved_logo(channel_name)
    else:
        logo = logo_db.get(channel_name)
        if isinstance(logo, list):
            logo = logo[0] if logo else None
        elif not isinstance(logo, str):
            logo = None

    if logo and isinstance(logo, str) and logo.startswith("http"):
        return line.replace("#EXTINF:-1", f'#EXTINF:-1 tvg-logo="{logo}"')
    return line

    with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
        logo_db = json.load(f)

    for line in m3u_lines:
        new_line = inject_logo(line, channel_name, logo_db)

def exportM3UWithLogos(self, output_path):
    try:
        with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
            logo_db = json.load(f)
    except:
        logo_db = {}

    with open(output_path, "w", encoding="utf-8") as out:
        for category, channels in self.categories.items():
            for channel in channels:
                # נניח channel זה EXTINF + URL
                extinf_line, url_line = channel.splitlines()

                name = channel.split(" (")[0].strip()
                extinf_with_logo = inject_logo(extinf_line, name, logo_db)

                out.write(extinf_with_logo + "\n")
                out.write(url_line.strip() + "\n")


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
        'ישראל', 'israel', 'il', 'is', 'israel vip', 'israel hd',
        'ערוץ', 'עברי', 'hot', 'yes', 'kan', 'keshet', 'reshet',
        'i24', 'channel 9', 'iptv israel', 'Израиль', 'Израиль | ישראלי'
    ]
    text = f"{category} {name}".lower()
    return any(word in text for word in keywords)


    def getSelectedCategory(self):
        return self.newCategoryInput.text() if self.newCategoryInput.text() else self.categoryCombo.currentText()

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

    def getUrl(self, channel):
        if self.parent:
            return self.parent.getUrl(channel)  # Call getUrl of M3UEditor
        return ""  # Default or error handling

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
                    extinf_line = self.getFullExtInfLine(channel, category)
                    url = self.getUrl(channel)  # Correctly extracts URL
                    file.write(f"{extinf_line}\n{url}\n")  # Newline between properties and URL
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export {category}: {str(e)}")

    def getFullExtInfLine(self, channel, category="Default Category"):
        """
        Constructs the full EXTINF line from channel information,
        preserving all properties such as tvg-logo, tvg-id, catchup-days, etc.
        The category parameter is optional and will default to 'Default Category' if not provided.
        """
        # Assume the channel format includes the full EXTINF line with properties followed by URL in parentheses
        properties_part = channel.split(' (')[0]  # Separate properties from URL
        channel_name = properties_part.split(',')[
            -1] if ',' in properties_part else properties_part  # Get last part after comma as channel name

        # Check if "group-title" is included and add it if missing
        if "group-title=" not in properties_part:
            properties_part = f"#EXTINF:-1, group-title=\"{category}\", {channel_name}"
        else:
            properties_part = f"#EXTINF:-1, {properties_part}"

        return properties_part

    def parseChannelInfo(self, channel):
        # Regex to extract name, url and optional tvg-logo
        match = re.search(r'^(.+) \((http.+)\)$', channel)
        if match:
            name = match.group(1)
            url = match.group(2)
            return name, url
        return "", ""


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

            response = requests.get(self.m3uURL, headers=headers, timeout=10)
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
                offline_channels.append(channel_name)
                self.channelTable.selectRow(row)

        if not offline_channels:
            QMessageBox.information(
                self, "No Offline Channels",
                "There are no offline channels to select."
            )
            return

        # Call parent method to select these offline channels in main list
        if hasattr(self.parent(), 'selectChannelsByNames'):
            self.parent().selectChannelsByNames(offline_channels)
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

    def selectProblematic(self):
        urls_to_mark = set()
        duplicate_tracker = {}

        for row in range(self.table.rowCount()):
            channel_name = self.table.item(row, 0).text()
            status = self.table.item(row, 1).text().lower()
            url = self.table.item(row, 3).text()

            if "offline" in status:
                urls_to_mark.add(url)
            else:
                # במקרה של כפולים נסמן רק את השני והלאה
                if channel_name not in duplicate_tracker:
                    duplicate_tracker[channel_name] = url
                else:
                    urls_to_mark.add(url)

        # סימון סופי לפי URL ייחודי, לא לפי שם בלבד
        if hasattr(self.parent(), "selectChannelsByUrls"):
            self.parent().selectChannelsByUrls(urls_to_mark)
            QMessageBox.information(
                self, "Marked",
                f"{len(urls_to_mark)} problematic channels marked in your channel list."
            )
        else:
            QMessageBox.warning(
                self, "Error",
                "Method selectChannelsByUrls not found."
            )


def setup_session() -> requests.Session:
    """
    Configures a requests Session with retry logic.
    """
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[502, 503, 504, 500],
        allowed_methods=["HEAD", "GET", "POST"]
    )
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session


class M3UEditor(QWidget):
    logosFinished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.categories = {}  # ← הוסף שורה זו ממש בתחילת הפונקציה!
        self.initUI()
        self.logosFinished.connect(self.onLogosFinished)


    def onLogosFinished(self):
        QMessageBox.information(self, "Logo Scan", "✅ סריקת הלוגואים הושלמה בהצלחה!")


    def initUI(self):
        self.setWindowTitle('M3U Playlist Editor')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        # Setup the horizontal layout for top buttons
        top_buttons_layout = QHBoxLayout()

        # Set a global font
        font = QFont('Arial', 10)  # Change 'Arial' to your preferred font and '12' to your desired size
        QApplication.setFont(font)

        # Main layout
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # Add image at the top
        logo_label = QLabel(self)
        logo_label.setAlignment(Qt.AlignCenter)  # Center the logo
        image_path = r'C:\Users\Master_PC\Desktop\IPtv_projects\Projects Eldad\M3u_Editor_EldadV1\Main Logo.jpg'

        # Check if the image exists and load it
        if os.path.exists(image_path):
            logo_pixmap = QPixmap(image_path)
            if not logo_pixmap.isNull():  # Check if the pixmap was loaded successfully
                logo_pixmap = logo_pixmap.scaled(150, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(logo_pixmap)
            else:
                logo_label.setText("Failed to load image.")  # Fallback text
                logo_label.setAlignment(Qt.AlignCenter)
        else:
            logo_label.setText("Image not found.")
            logo_label.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(logo_label)

        # Setup title
        title = QLabel("M3U Playlist Editor", self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 25px; font-weight: bold; background-color: black; color: white;")
        main_layout.addWidget(title)

        # File info layout
        file_info_layout = QHBoxLayout()
        self.fileNameLabel = QLabel("No file loaded", self)
        self.fileNameLabel.setAlignment(Qt.AlignCenter)
        self.fileNameLabel.setStyleSheet("font-size: 18px; font-weight: bold;")
        file_info_layout.addWidget(self.fileNameLabel)

        self.channelCountLabel = QLabel("Total Channels: 0", self)
        self.channelCountLabel.setAlignment(Qt.AlignRight)


        # Change font size of 'Total Channels'
        self.channelCountLabel.setStyleSheet("font-size: 18px; font-weight: bold;")
        file_info_layout.addWidget(self.channelCountLabel)
        main_layout.addLayout(file_info_layout)

        # 🔍 תיבת חיפוש חכמה
        self.searchBox = QLineEdit()
        self.searchBox.setPlaceholderText("🔍 חיפוש קטגוריה או ערוץ...")
        self.searchBox.textChanged.connect(self.handleSearchTextChanged)

        # כפתור איפוס 🧹
        reset_button = QPushButton("🔄 איפוס")
        reset_button.setStyleSheet("padding: 3px; font-weight: bold;")
        reset_button.clicked.connect(lambda: self.searchBox.setText(""))

        # סידור אופקי של חיפוש + איפוס
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.searchBox)
        search_layout.addWidget(reset_button)
        main_layout.insertLayout(1, search_layout)  # מוסיף את שורת החיפוש מתחת לכותרת

        # Add other sections
        main_layout.addLayout(self.create_category_section())
        main_layout.addLayout(self.create_channel_section())
        main_layout.addLayout(self.create_m3u_content_section())
        main_layout.addLayout(self.create_Tools())

        self.urlCheckButton = QPushButton('IPTV Checker', self)
        self.urlCheckButton.setStyleSheet("background-color: purple; color: white;")
        self.urlCheckButton.clicked.connect(self.openURLCheckerDialog)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        main_layout.addWidget(self.urlCheckButton)

        # Ensure EXTM3U header
        self.textEdit.textChanged.connect(self.ensure_extm3u_header)
        # Ensure everything is added to main_layout
        self.setLayout(main_layout)

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
            "Sort by URL Length"
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

        for btn in [self.addChannelButton, self.deleteChannelButton, self.moveChannelUpButton,
                    self.moveChannelDownButton, self.selectAllChannelsButton, self.clearChannelsSelectionButton,
                    self.moveSelectedChannelButton, self.editSelectedChannelButton, self.checkDoublesButton]:
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        # רשימת ערוצים
        self.channelList = QListWidget(self)
        self.channelList.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.channelList)

        # חיבורים
        self.addChannelButton.clicked.connect(self.addChannel)
        self.deleteChannelButton.clicked.connect(self.deleteSelectedChannels)
        self.moveChannelUpButton.clicked.connect(self.moveChannelUp)
        self.moveChannelDownButton.clicked.connect(self.moveChannelDown)
        self.selectAllChannelsButton.clicked.connect(self.selectAllChannels)
        self.clearChannelsSelectionButton.clicked.connect(self.deselectAllChannels)
        self.moveSelectedChannelButton.clicked.connect(self.moveSelectedChannel)
        self.editSelectedChannelButton.clicked.connect(self.editSelectedChannel)

        return layout

    def load_logos_once(self):
        self.logo_cache = {}
        if os.path.exists(LOGO_DB_PATH):
            with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                self.logo_cache = json.load(f)

    def get_saved_logo(self, channel_name):
        return self.logo_cache.get(channel_name)

    def openM3UConverterDialog(self):
        dialog = M3UUrlConverterDialog(self)
        dialog.exec_()

    def downloadDirectM3U(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Direct M3U Downloader")
        dialog.setGeometry(300, 300, 600, 300)

        # ✅ כאן להוסיף את השורה שלך על dialog
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        dialog.setStyleSheet("""
            QDialog { background-color: white; border: 5px solid red; }
            QPushButton { font-weight: bold; height: 40px; }
            QLineEdit { font-size: 14px; padding: 6px; }
        """)

        layout = QVBoxLayout(dialog)

        label = QLabel("Paste your M3U URL:")
        layout.addWidget(label)

        url_input = QLineEdit()
        url_input.setPlaceholderText("http://example.com/get.php?username=...&password=...")
        layout.addWidget(url_input)

        download_button = QPushButton("Download M3U")
        download_button.setStyleSheet("background-color: red; color: white;")
        layout.addWidget(download_button)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(close_button)

        close_button.clicked.connect(dialog.close)

        def handle_download():
            url = url_input.text().strip()
            if not url:
                QMessageBox.warning(dialog, "Missing URL", "Please enter a valid M3U URL.")
                return

            if not re.match(r'^https?://', url):
                QMessageBox.warning(dialog, "Invalid URL", "Please enter a valid URL starting with http:// or https://")
                return

            try:
                response = requests.get(url)
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

        # כפתור סגירה
        close_button = QPushButton("Close", dialog)
        close_button.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(close_button)
        close_button.clicked.connect(dialog.close)

        # כפתור הורדת URL מרובים - נשאר למי שרוצה דרך URL
        download_button = QPushButton("Download All", dialog)
        download_button.setStyleSheet("background-color: red; color: white;")
        layout.addWidget(download_button)

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
                    response = requests.get(url)
                    response.raise_for_status()
                    content = response.text.strip()
                    if not content.startswith("#EXTM3U"):
                        continue
                    url_data.append((url, content))
                    merged_content += "\n".join(
                        line for line in content.splitlines() if line.strip() and not line.startswith("#EXTM3U")) + "\n"
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
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                    QMessageBox.information(dialog, "Saved", "All M3U files saved individually.")

            dialog.close()

        download_button.clicked.connect(start_batch_download)
        dialog.exec_()

    def loadM3UFromText(self, content, append=False):
        if not append:
            self.categories.clear()

        self.load_logos_once()  # בדיקת קובץ json אם כבר נטען

        self.parseM3UContentEnhanced(content)  # ← מציג מיד את הקטגוריות

        self.updateCategoryList()
        self.buildSearchCompleter()
        self.logosFinished.connect(self.onLogosFinished)

        # טען את הערוצים הראשונים
        if self.categoryList.count() > 0:
            self.categoryList.setCurrentRow(0)
            self.display_channels(self.categoryList.currentItem())

        # סריקת לוגואים ברקע בלבד
        threading.Thread(
            target=self.extract_and_save_logos_for_all_channels,
            args=(content,),
            daemon=True
        ).start()

    def extract_and_save_logos_for_all_channels(self, content):
        """
        Scans all channels in the M3U content and saves unique logos only if not already present.
        """
        try:
            with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                logo_db = json.load(f)
        except:
            logo_db = {}

        seen = set()
        lines = content.strip().splitlines()

        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF:"):
                name_match = re.search(r",(.+)", lines[i])
                channel_name = name_match.group(1).strip() if name_match else ""

                logo_match = re.search(r'tvg-logo="([^"]+)"', lines[i])
                logo_url = logo_match.group(1).strip() if logo_match else ""

                if channel_name and logo_url:
                    existing = logo_db.get(channel_name, [])
                    if isinstance(existing, str):
                        existing = [existing]

                    if logo_url not in existing and (channel_name, logo_url) not in seen:
                        if channel_name not in logo_db:
                            logo_db[channel_name] = []
                        if isinstance(logo_db[channel_name], str):
                            logo_db[channel_name] = [logo_db[channel_name]]
                        logo_db[channel_name].append(logo_url)
                        seen.add((channel_name, logo_url))
                        print(f"[LOGO] ✅ {channel_name} | {logo_url}")

        with open(LOGO_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(logo_db, f, indent=2, ensure_ascii=False)

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
        text = text.strip().lower()
        if not text:
            return

        # חיפוש קטגוריה קודם
        found_category = False
        for i in range(self.categoryList.count()):
            item = self.categoryList.item(i)
            category_name = item.text().split(" (")[0].lower()
            if text in category_name:
                item.setBackground(QColor("yellow"))
                self.categoryList.setCurrentItem(item)
                self.display_channels(item)
                found_category = True
            else:
                item.setBackground(QColor("white"))

        # חיפוש ערוץ בתוך כל הקטגוריות
        for category, channels in self.categories.items():
            for channel in channels:
                name = channel.split(" (")[0].lower()
                if text in name:
                    for i in range(self.categoryList.count()):
                        item = self.categoryList.item(i)
                        if category in item.text():
                            item.setBackground(QColor("yellow"))
                            self.categoryList.setCurrentItem(item)
                            self.display_channels(item)
                            break

                    for j in range(self.channelList.count()):
                        ch_item = self.channelList.item(j)
                        if text in ch_item.text().lower():
                            ch_item.setSelected(True)
                            self.channelList.scrollToItem(ch_item)
                            return

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

    def mergeM3Us(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Additional M3U File", "",
                                                  "M3U Files (*.m3u *.m3u8);;All Files (*)", options=options)
        if fileName:
            try:
                with open(fileName, 'r', encoding='utf-8') as file:
                    additional_content = file.read().strip().splitlines()

                # טען לוגואים לזיכרון לשימוש מהיר
                try:
                    with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                        logo_db = json.load(f)
                except:
                    logo_db = {}

                merged_lines = []
                i = 0
                while i < len(additional_content):
                    line = additional_content[i]
                    if line.startswith("#EXTINF:"):
                        extinf_line = line
                        url_line = additional_content[i + 1] if i + 1 < len(additional_content) else ""

                        name_match = re.search(r",(.+)", extinf_line)
                        channel_name = name_match.group(1).strip() if name_match else ""

                        extinf_line = inject_logo(extinf_line, channel_name, logo_db)
                        merged_lines.append(extinf_line)
                        merged_lines.append(url_line)
                        i += 2
                    else:
                        i += 1

                # מיזוג לשדה הטקסט
                current_content = self.textEdit.toPlainText()
                if not current_content.endswith('\n'):
                    current_content += '\n'
                merged_text = current_content + '\n'.join(merged_lines)
                self.textEdit.setPlainText(merged_text)

                self.fileNameLabel.setText(f"Loaded File: {fileName.split('/')[-1]} (Merged)")
                QMessageBox.information(self, "Merge Complete", "The M3U files have been merged successfully.")

                # סריקה מחדש
                self.parseM3UContentEnhanced(self.textEdit.toPlainText())

            except Exception as e:
                QMessageBox.critical(self, "Error", "Failed to merge M3U files: " + str(e))

    def ensure_extm3u_header(self):
        """
        Ensure that the content starts with #EXTM3U.
        """
        content = self.textEdit.toPlainText()
        if not content.startswith("#EXTM3U"):
            self.textEdit.blockSignals(True)
            self.textEdit.setPlainText("#EXTM3U\n" + content)
            self.textEdit.blockSignals(False)

    from PyQt5.QtWidgets import QAbstractItemView

    def create_category_section(self):
        layout = QVBoxLayout()
        category_title = QLabel("Categories", self)
        category_title.setAlignment(Qt.AlignCenter)
        category_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(category_title)

        button_layout = QHBoxLayout()

        # Create buttons
        self.addCategoryButton = QPushButton('Add Category')
        self.updateCategoryButton = QPushButton('Edit Category Name')
        self.deleteCategoryButton = QPushButton('Delete Selected')
        self.moveCategoryUpButton = QPushButton('Move Category Up')
        self.moveCategoryDownButton = QPushButton('Move Category Down')
        self.selectAllButton = QPushButton('Select All')
        self.deselectAllButton = QPushButton('Deselect All')

        # New button to show total channels
        self.showTotalChannelsButton = QPushButton('Show Total Channels')
        self.showTotalChannelsButton.clicked.connect(self.displayTotalChannels)

        # Apply button colors
        self.selectAllButton.setStyleSheet("background-color: blue; color: white;")
        self.deselectAllButton.setStyleSheet("background-color: blue; color: white;")

        self.updateCategoryButton.setStyleSheet("background-color: red; color: white;")
        self.deleteCategoryButton.setStyleSheet("background-color:red; color: white;")

        self.addCategoryButton.setStyleSheet("background-color: green; color: white;")
        self.moveCategoryUpButton.setStyleSheet("background-color: green; color: white;")
        self.moveCategoryDownButton.setStyleSheet("background-color:green; color: white;")
        self.showTotalChannelsButton.setStyleSheet("background-color:black; color: white;")

        # Add buttons to layout
        button_layout.addWidget(self.addCategoryButton)
        button_layout.addWidget(self.updateCategoryButton)
        button_layout.addWidget(self.deleteCategoryButton)
        button_layout.addWidget(self.moveCategoryUpButton)
        button_layout.addWidget(self.moveCategoryDownButton)
        button_layout.addWidget(self.selectAllButton)
        button_layout.addWidget(self.deselectAllButton)
        button_layout.addWidget(self.showTotalChannelsButton)  # Add the new button

        layout.addLayout(button_layout)

        # Create category list widget
        self.categoryList = QListWidget(self)
        self.categoryList.itemClicked.connect(self.onCategorySelected)
        self.categoryList.setSelectionMode(QAbstractItemView.MultiSelection)  # Ensure multiple selection is enabled
        layout.addWidget(self.categoryList)

        # Connect buttons to their respective functions
        self.addCategoryButton.clicked.connect(self.addCategory)
        self.updateCategoryButton.clicked.connect(self.updateCategoryName)
        self.deleteCategoryButton.clicked.connect(self.deleteSelectedCategories)
        self.moveCategoryUpButton.clicked.connect(self.moveCategoryUp)
        self.moveCategoryDownButton.clicked.connect(self.moveCategoryDown)
        self.selectAllButton.clicked.connect(self.selectAllCategories)  # Assign to select all function
        self.deselectAllButton.clicked.connect(self.deselectAllCategories)  # Assign to deselect all function
        self.categoryList.itemClicked.connect(self.display_channels)
        return layout

    def create_Tools(self):
        layout = QVBoxLayout()
        tools_title = QLabel("Tools", self)
        tools_title.setAlignment(Qt.AlignCenter)
        tools_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(tools_title)

        # Create a horizontal layout for the buttons
        buttons_layout = QHBoxLayout()

        self.directM3UDownloadButton = QPushButton('🌐 M3U Direct', self)
        self.directM3UDownloadButton.setStyleSheet("background-color: black; color: white;")
        self.directM3UDownloadButton.clicked.connect(self.downloadDirectM3U)
        buttons_layout.addWidget(self.directM3UDownloadButton)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

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

        # Filter Israeli Channels button
        self.filterIsraelChannelsButton = QPushButton('🇮🇱 IsraelX Export', self)
        self.filterIsraelChannelsButton.setStyleSheet("background-color: black; color: white;")
        self.filterIsraelChannelsButton.clicked.connect(self.filterIsraelChannels)
        buttons_layout.addWidget(self.filterIsraelChannelsButton)

        self.smartScanButton = QPushButton('🔍 Scan Master', self)
        self.smartScanButton.setStyleSheet("background-color: black; color: white; font-weight: ;")
        self.smartScanButton.clicked.connect(self.openSmartScanDialog)
        buttons_layout.addWidget(self.smartScanButton)

        self.manageLogosButton = QPushButton('🖼️ Logo Manager', self)
        self.manageLogosButton.setStyleSheet("background-color: black; color: red;")
        self.manageLogosButton.clicked.connect(self.open_logo_manager)
        buttons_layout.addWidget(self.manageLogosButton)



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
        self.channelCountLabel.setText(f"Total Channels: {total_channels}")


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
        button_layout.addWidget(self.loadButton)
        button_layout.addWidget(self.saveButton)
        button_layout.addWidget(self.mergeButton)
        layout.addLayout(button_layout)
        self.loadButton.clicked.connect(self.loadM3U)
        self.saveButton.clicked.connect(self.saveM3U)
        self.mergeButton.clicked.connect(self.mergeM3Us)
        self.loadButton.setStyleSheet("background-color: green; color: white;")
        self.saveButton.setStyleSheet("background-color: red; color: white;")
        self.mergeButton.setStyleSheet("background-color: blue; color: white;")

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
            self.textEdit.setPlainText("\n".join(updated_lines))
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
            self.textEdit.setPlainText("\n".join(updated_lines))

            # Refresh the category list in the UI
            self.updateCategoryList()

            # Clear the channels list UI if the selected category is deleted
            self.channelList.clear()

            QMessageBox.information(self, "Success", "Selected categories and their records have been removed.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while deleting categories: {str(e)}")

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

    def regenerateM3UTextOnly(self, fast_mode=True):
        updated_lines = ["#EXTM3U"]
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

        self.textEdit.setPlainText("\n".join(updated_lines))

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

        # מחיקה לפי אינדקסים מסומנים בלבד
        self.categories[category_name] = [
            ch for i, ch in enumerate(channels_in_category)
            if i not in selected_indexes
        ]

        deleted = original_len - len(self.categories[category_name])

        self.updateCategoryList()
        self.regenerateM3UTextOnly()
        if self.categoryList.currentItem():
            self.display_channels(self.categoryList.currentItem())

        QMessageBox.information(self, "Success", f"Deleted {deleted} channel(s).")

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
            self.textEdit.setPlainText(new_content)

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

        current_item = self.channelList.takeItem(current_row)
        self.channelList.insertItem(current_row - 1, current_item)
        self.channelList.setCurrentRow(current_row - 1)

        current_category_item = self.categoryList.currentItem()
        if not current_category_item:
            QMessageBox.warning(self, "Warning", "No category selected.")
            return

        current_category = current_category_item.text().split(" (")[0]
        channels = self.categories[current_category]
        channels[current_row], channels[current_row - 1] = channels[current_row - 1], channels[current_row]

        self.categories[current_category] = channels
        self.regenerateM3UTextOnly()

    def moveChannelDown(self):
        current_row = self.channelList.currentRow()
        if current_row < 0 or current_row >= self.channelList.count() - 1:
            return

        current_item = self.channelList.takeItem(current_row)
        self.channelList.insertItem(current_row + 1, current_item)
        self.channelList.setCurrentRow(current_row + 1)

        current_category_item = self.categoryList.currentItem()
        if not current_category_item:
            return

        current_category = current_category_item.text().split(" (")[0]
        channels = self.categories[current_category]
        channels[current_row], channels[current_row + 1] = channels[current_row + 1], channels[current_row]

        self.categories[current_category] = channels
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
        """
        Move selected channels to a new or existing category safely and FAST.
        """
        selected_items = self.channelList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No channels selected for moving.")
            return

        dialog = MoveChannelsDialog(self, list(self.categories.keys()))
        if dialog.exec_():
            target_category = dialog.getSelectedCategory().strip()
            if not target_category:
                QMessageBox.warning(self, "Warning", "No target category specified.")
                return

            if target_category not in self.categories:
                self.categories[target_category] = []

            current_item = self.categoryList.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Warning", "No category selected.")
                return

            current_category = current_item.text().split(" (")[0].strip()
            if current_category not in self.categories:
                QMessageBox.warning(self, "Warning", f"Category '{current_category}' does not exist.")
                return

            moved_channels = []
            selected_names = [item.text().strip() for item in selected_items]
            original_list = self.categories[current_category]
            remaining_channels = []

            for channel in original_list:
                match = re.match(r"^(.*?) \((.*?)\)$", channel.strip())
                if not match:
                    remaining_channels.append(channel)
                    continue

                name = match.group(1).strip()
                if name in selected_names:
                    moved_channels.append(channel)
                    selected_names.remove(name)
                else:
                    remaining_channels.append(channel)

            if moved_channels:
                self.categories[current_category] = remaining_channels
                self.categories[target_category].extend(moved_channels)

                self.regenerateM3UTextOnly()
                self.updateCategoryList()

                for i in range(self.categoryList.count()):
                    if self.categoryList.item(i).text().startswith(target_category):
                        self.categoryList.setCurrentRow(i)
                        self.display_channels(self.categoryList.item(i))
                        break

                QMessageBox.information(
                    self,
                    "Success",
                    f"{len(moved_channels)} channels moved to '{target_category}'."
                )

    def editSelectedChannel(self):
        """
        Renames a selected channel and updates the M3U content accordingly.
        """
        selected_items = self.channelList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No channels selected for moving.")
            return

        for item in selected_items:
            old_channel_name = item.text()
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

                self.textEdit.setPlainText("\n".join(updated_lines))
                self.display_channels(self.categoryList.currentItem())
                QMessageBox.information(self, "Success",
                                        f"Channel '{old_channel_name}' has been renamed to '{new_channel_name}'.")

    def display_channels(self, item):
        """
        Display channels for the selected category and update the total count label.
        """
        if item is None:  # Check if item is None
            self.channelList.clear()
            self.channelCountLabel.setText("Total Channels: 0")
            return

        category = item.text().split(" (")[0]  # Extract the category name
        self.channelList.clear()

        # Get channels in the selected category
        channels = self.categories.get(category, [])
        for channel in channels:
            channel_name = channel.split(" (")[0]
            if not channel_name:  # Skip empty or invalid channel names
                continue
            channel_item = QListWidgetItem(channel_name)
            self.channelList.addItem(channel_item)

        # Update the total channel count label
        self.channelCountLabel.setText(f"Channels in '{category}': {len(channels)}")

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

        if category_name not in self.categories:
            QMessageBox.warning(self, "Warning", "Selected category not found.")
            return

        channels = []
        for ch in self.categories[category_name]:
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

        # ✅ כאן להוסיף את השורה שלך על dialog
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        dialog.setStyleSheet("""
            QDialog {
                border: 6px solid red;
                background-color: white;
            }
        """)


        layout = QVBoxLayout(dialog)
        label = QLabel("Choose scan type:")
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)


        category_btn = QPushButton("Scan Selected Category")
        all_btn = QPushButton("Scan All Channels")
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

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

        dialog.setLayout(layout)
        dialog.exec_()

    def selectChannelsByUrls(self, urls_set):
        self.channelList.clearSelection()

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
        try:
            if '(' in channel_info and ')' in channel_info:
                return channel_info.split(" (")[-1].rstrip(")")
            return ""
        except Exception:
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
            "M3U Files (*.m3u *.m3u8);;All Files (*)",
            options=options
        )
        if fileName:
            try:
                with open(fileName, 'r', encoding='utf-8') as file:
                    content = file.read()

                self.textEdit.setPlainText(content)

                # מציג את התוכן ומעדכן קטגוריות
                self.parseM3UContentEnhanced(content)

                # סריקת לוגואים של כל הערוצים, לא רק ישראל
                threading.Thread(
                    target=self.extract_and_save_logos_for_all_channels,
                    args=(content,),
                    daemon=True
                ).start()

                total_channels = sum(len(channels) for channels in self.categories.values())
                self.channelCountLabel.setText(f"Total Channels: {total_channels}")
                self.fileNameLabel.setText(f"Loaded File: {os.path.basename(fileName)}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")

    def loadEPG(self, epg_path):
        try:
            tree = ET.parse(epg_path)
            root = tree.getroot()

            if not hasattr(self, 'epg_data'):
                self.epg_data = {}

            for programme in root.findall('programme'):
                channel_id = programme.attrib.get('channel')
                title = programme.findtext('title')
                desc = programme.findtext('desc')
                start = programme.attrib.get('start')
                stop = programme.attrib.get('stop')

                if channel_id:
                    self.epg_data.setdefault(channel_id, []).append({
                        'title': title,
                        'desc': desc,
                        'start': start,
                        'stop': stop
                    })

        except Exception as e:
            QMessageBox.critical(self, "EPG Error", f"Failed to load EPG file:\n{str(e)}")

    from datetime import datetime, timedelta

    def openEPGViewer(self, tvg_id):
        if not hasattr(self, 'epg_data') or tvg_id not in self.epg_data:
            QMessageBox.information(self, "EPG Viewer", "No EPG data available.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"EPG for {tvg_id}")
        dialog.resize(500, 600)
        layout = QVBoxLayout(dialog)

        entries = self.getRecentEPG(tvg_id)
        if not entries:
            layout.addWidget(QLabel("No recent programs"))
        else:
            for entry in entries:
                label = QLabel(f"<b>{entry['title']}</b><br>{entry['desc']}<br>{entry['start']} → {entry['stop']}")
                layout.addWidget(label)

        dialog.setLayout(layout)
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

        self.textEdit.setPlainText(updated_content)
        self.categoryList.clear()
        for category, channels in self.categories.items():
            item = QListWidgetItem(f"{category} ({len(channels)})")
            self.categoryList.addItem(item)

        self.searchBox.setText("")
        self.buildSearchCompleter()

    def save_israeli_logos_background(self, content):
        def run():
            lines = content.strip().splitlines()
            for i in range(len(lines)):
                line = lines[i].strip()
                if line.startswith("#EXTINF:"):
                    name_match = re.search(r',(.+)', line)
                    logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                    if name_match and logo_match:
                        name = name_match.group(1).strip()
                        logo = logo_match.group(1).strip()
                        if is_israeli_channel("", name):
                            save_logo_for_channel(name, logo)
                            print(f"[LOGO] Saved logo for {name}: {logo}")

        threading.Thread(target=run, daemon=True).start()

    def filterIsraelChannels(self):
        israel_keywords = ['Israel', 'IL', 'ISRAEL', 'Hebrew', 'hebrew', 'israeli', 'Israeli', '"IL"', 'Il', 'IL HD',
                           'TV', 'MUSIC', 'ישראלי', 'MTV', 'USA', 'mtv', 'Music Hits+', 'WWE ', 'nba tv',
                           'music', 'IL:', 'Hebrew']
        category_keywords = {

            'News📺': ['Keshet 12 IL', 'Channel 9 HD IL', '9 Channel IL', 'CHANNEL 9 HD IL', 'KAN 11 IL', '12 Keshet IL',
                      'C13 Keshet IL', 'KAN 14 IL', 'Channel 9 IL', 'Kan 11 IL', 'Knesset Channel IL',
                      'MAKAN HD IL', 'i24 IL', 'Channel 14', 'Kan Educational HD IL', 'Reshet 13 IL', 'KHAN 11','CBS reality [IL]',
                      'Channel 9 HD', 'Channel 11', 'Channel 12', 'Channel 13',  'Reshet 13 [IL]', 'Knesset [IL]', 'I24 News [IL]','Keshet 12 HD [IL]','Keshet 12 [IL]','Reshet 13 HD [IL]','13 Keshet IL','KAN 11 HD [IL]','KAN 11 [IL]','Makan 33 HD', 'Reshet 13 IL',
                      'Kan Chinuchit 23', 'i24 News', 'Channel 9','Now 14 HD [IL]','Mikan 33 [IL]','Kabbalah channel [IL]', 'Channel 11','KAN23 [IL]','Kan Educational HD [IL]', 'Channel 12', 'Channel 13',
                      'Channel 24', 'Channel 14', 'ערוץ 14', 'ערוץ 24', 'Channel 98 IL', 'CHANNEL 12 HD IL',
                      'CHANNEL 13 HD'],
            'Hot🔥': ['HOT', 'HOT CINEMA', 'HOT Cinema 1 HD IL', 'HOT CINEMA 1', 'HOT CINEMA 3', 'HOT CINEMA 4',
                     'HOT3 HD', 'HOT 8 HD', 'Hot HBO', 'HOT cinema 1', 'HOT cinema 2', 'HOT cinema 3', 'HOT8 HD',
                     'HOT COMEDY CENTRAL', 'HOT CINEMA 4', 'HOT CINEMA 3', 'hot-IL', 'HoT'],
            'Yes👑': ['yes', 'Yes', 'YES', 'Yes_IL', 'YES_IL', 'yes Israeli Cinema HD', 'Yes E', 'YES_IL',
                     'Yes TV Drama HD', 'YES_IL', 'YES_IL', 'Sport-IL', 'YES HD IL', 'YES TV', 'yes tv'],
            'Partner🌈': ['Partner Yladim', 'Partner Sratim', 'Partner Sdarot'],
            'Cellcom🐶': ['Cellcom Israel', 'Cellcom Rus', 'Cellcom Sratim', 'Cellcom Yeladim', 'Cellcom HBO HD',
                         'Cellcom Doco HD', 'YES HD IL', 'YES TV', 'yes tv'],
            'Free Tv🌞': ['Free Tv Drama HD', 'Free Tv Comedy HD', 'Free Tv Lifestyle HD', 'Free Israeli Movies HD',
                         'Free Movies Family HD', 'Free Movies Horror HD', 'Free Movies Romantic HD',
                         'Free Movies Comedy HD', 'Free Movies Drama HD', 'Free Series Global HD',
                         'Free Movies Action HD', 'Free Tv Cooking HD', 'Free Tv Doco HD', 'Free Tv Hatuna HD',
                         'Free Tv Karaoke HD', 'Free Tv Kohav Haba HD', 'Free Tv Feel Good'],
            'Sports🏀': ['Sport 1', 'Sport 2', 'Sport 3', 'Sport 4', 'Sport 5', 'Sport-IL', 'Sport_il', 'Sport', 'ONE ',
                        'ONE HD', 'Eurosport 2', 'ONE HD', 'Sport 1 HD', 'EXTREME IL', 'Sport 5+ Live HD IL',
                        'ONE 2 HD IL', 'Sport 3 HD IL', 'Sport 5 HD IL ', 'SPORT 2 HD IL', 'Sport 1 HD IL',
                        'Sport 2 HD', 'Sport 3 HD', 'Sport 4 HD','5 Live IL','ONE1 HD IL','ONE2 HD IL','ONE2 HD [IL]','ONE2  [IL]','Sport 4 HD','Sport 4 HD',
                        'Sport 5 HD', 'Sport 5 Live HD', 'Eurosport 1 HD', 'ESPN 2 HD USA', 'ESPN USA',
                        'Eurosport 1 HD', 'Red Bull TV HD',
                        'WWE Russian', 'Red Bull TV', 'MMA-TV.com HD', 'MMA-TV.com', 'MMA-TV.com orig', 'NHL', 'nba',
                        'NBA', 'wwe', 'WWE Network HD', 'Eurosport 2',
                        'Eurosport 2', 'EXTREME', 'SPORT'],
            'Kids🍦': ['Hop!', 'Israelit', 'Baby IL', 'Yaldut IL', 'BABY TV IL', 'hop', 'HOT A+ Kids', 'Nick Jr',
                      'Nickelodeon', 'Disney Junior', 'Luli', 'Junior', 'Disney HD', 'Baby', 'Hop! Childhood', 'Yaldut','Disney Jr [IL]',
                      'ZOOM', 'Disney Channel H', 'YoYo', 'NICK JR HD IL', 'Nick Jr IL', 'NICK HD IL','FOMO [IL]','HOP [IL]','Yoyo [IL]','Disney [IL]',
                      'Junior IL', 'hop IL', 'HOP HD IL', 'JUNIOR IL', 'Zoom', 'Zoom Toon HD', 'Wiz', 'Yalduti',
                      'TeenNick', 'Nick HD', 'Nick Jr HD', 'Luli', 'Logi', 'Junior', 'Jim Jam', 'Disney Jr.', 'LULI IL',
                      'Disney Jr IL', 'Baby TV', 'DISNEY JR IL', 'TeenNick IL',
                      'ZOOM IL', 'HOP CHILDHOOD IL', 'KIDS HD IL', 'Hop', 'Hop Israeli Childhood', 'Hop Pele HD',
                      'Kids IL', 'DISNEY CHANNEL', 'WIZ IL'],
            'Entertainment🧸': ['Home Plus IL', 'Good Life', 'FOOD CHANNE IL', '5Stars HD IL', 'Polsat HD', 'Home Plus',
                               'Food Channel', 'Ego Total', 'Health', 'EGO TOTAL HD IL', 'STARS IL',
                               'CANAL+ FAMILY HD PL', 'HISTORY HD IL', 'Star Channel', 'Reality HD', 'Savri HD',
                               'A+ HD IL', 'LIFETIME HD IL', 'STARS HD IL',
                               'Ego Total', 'Food Network', 'Game Show Channel HD IL', 'Health', 'E!',
                               'Horse and Country TV', 'ZONE HD', 'Good Life', 'TLC HD', 'Horse and Country TV',
                               'Home Plus', 'Love Island', 'History HD', 'Humor Channel', 'Fomo', 'Fashion','Holiday channel [IL]',
                               'Food Channel HD', 'Foody HD', 'Erez Nehederet HD', 'Big', 'CBS Reality', 'Boomerang',
                               'Entertainment IL', 'HEALTH CHANNEL', 'HUMOR CHANNEL', 'E! IL'],
            'Music🎵': ['music', 'MUSIC', 'MUSIC 24', 'MTV Hits', 'MTV Base HD', 'Stingray ', 'MTV Hits',
                       'Stingray Hot Country HD', 'Stingray Pop Adult HD', 'Stingray Hit List HD', 'MTV Hits',
                       'MTV Club', 'Clubbing TV HD', 'IL: MTV HD', 'MTV 80s', 'MTV', 'MTV Pulse HD', 'IT: MTV HD',
                       'MTV Idol HD', 'VH1 Classic', 'Rock Classics', 'Europa Plus TV HD', 'Music Box Gold', 'music 24',
                       'MTV Hits orig', 'Music Channel [IL]',
                       'Club MTV', 'Bridge Deluxe HD', 'Now 90s HD UK', 'Now 80s HD UK', 'NOW 70s UK', 'Bridge TV',
                       'Bridge Deluxe HD orig', 'Bridge Hits',
                       'Bridge Rock', 'Europa Plus TV', 'Europa Plus TV orig', 'MTV Live HD', 'MTV Live HD orig',
                       'MTV 90s', 'MUSIC 24', 'Yosso TV Music Hits', 'Fresh Concerts', 'Fresh Dance',
                       'Sky High Concert HD', 'Movistar Musica HD', 'MTV' '1HD Music Television orig',
                       '4ever Music HD UA', '4ever Music UA', 'B4U Music IN', 'BOX Music 4K HDR', 'Backus TV Music HD',
                       'Baraza Music HD', 'Biz Music HD UZ', 'CHANNEL 24 MUSIC HD IL', 'Classic Music',
                       'Classic Music HD', 'Disco Polo Music PL', 'EU Music HD UA', 'EU Music UA', 'FRESH Sad Music HD',
                       'HMTV IN', 'KLI Music HD', "MTV 00's PT", 'MTV 00s RO', 'MTV 80s RO', 'MTV 90s',
                       'MTV Aitio HD SE', 'MTV Base UK', 'MTV Classic', 'MTV Classic USA', 'MTV Club', 'MTV HD CA',
                       'MTV Hits', 'MTV Hits RO', 'MTV India IN', 'MTV Live HD', 'MTV Live HD orig', 'MTV MUSIC IL',
                       'MTV Music UK', 'MTV POLSKA PL', 'MTV RO', 'MTV SE', 'MTV Viihde HD FI', 'MTV Viihde HD SE',
                       'MUSIC 24 IL', 'Music Box Gold', 'Music Box Russia', 'Music Box Russia HD',
                       'Music Box Russia orig', 'Music Channel RO', 'MusicBox GE', 'Prokop TV Music', 'Public Music IN',
                       'Retro Music TV HD CZ', 'SUN Music IN', 'Sochi Music HD', 'VB MTV Old Россия HD', 'VF Music',
                       'Vox Music TV PL', 'Yosso TV Music Hits', 'Z!Music HD', 'ТНТ Music', 'ТНТ Music HD',
                       'ТНТ Music orig'],
            'Nature🌴': ['Discovery', 'Travel Channel', 'DISCOVERY CHANNEL HD IL', 'Travel Channel',
                        'DISCOVERY CHANNEL HD IL', 'Nat Geo HD', 'Nat Geo Wild', 'Animal Planet HD',
                        'National Geographic [IL]', 'NET GEO_WILD HD IL', 'Sky Select 5 HD', 'NAT GEO WILD IL','History [IL]','IETV [IL]','ZEE TV [IL]',
                        'TRAVEL CHANNEL IL','Animal Planet [IL]','National Geographic HD [IL]',
                        'NATIONAL GEOGRAPHICS HD IL'],
            'world series🌍': ['Viva Premium HD IL', 'Turkish Dramas 3 HD IL', 'Turkish Dramas 2 HD IL',
                              'Turkish Dramas Plus HD IL', 'Viva', 'Turkish Dramas 3 HD IL', 'Yam Tihoni 25',
                              'Viva plus', 'Aruch Sdarot Hahodiot', 'Aruch Sdarot Hahodiot 2', 'Yam Tihoni Plus',
                              'Vamos HD', 'Yam Tihoni HD', 'Yam Tihoni 2', 'Viva+ IL', 'Viva+', 'Viva Vintage','Star channel [IL]','Mediterranean [IL]','Bollywood [IL]','Turkish Dramas Plus HD [IL]',
                              'Viva Premium HD', 'VIVA IL', 'Yamtihoni IL', 'VIVA HD IL', 'VIVA+ IL','The Mediterranean HD [IL]','The Mediterranean [IL]','The Mediterranean+ HD [IL]','The Mediterranean+ [IL]',
                              'YAM TIHONI HD IL', 'HALA TV IL', 'BOLLYWOOD HD IL', 'BOLLYSHOW HD IL', 'Bollywood HD','Turkish Dramas Plus [IL]','Turkish Dramas 2 HD [IL]','Turkish Dramas 2 [IL]','Turkish Dramas 3 HD [IL]',
                              'Turkish Drama Plus', 'Turkish Drama 2', 'Turkish Drama 3', 'Viva'],

        }

        filtered_channels = {category: [] for category in category_keywords.keys()}
        filtered_channels['Other'] = []
        filtered_channels['Israel Radio📻'] = []
        filtered_channels['World Radio🌍'] = []

        for category, channels in self.categories.items():
            for channel in channels:
                if any(keyword in channel for keyword in israel_keywords):
                    placed = False
                    for key, keywords in category_keywords.items():
                        if any(keyword in channel for keyword in keywords):
                            filtered_channels[key].append(channel)
                            placed = True
                            break
                    if not placed:
                        filtered_channels['Other'].append(channel)

        # טוען רק את תחנות הרדיו מישראל ומעולם, ללא Radio by Category
        self.loadRadioChannels(filtered_channels, 'Israel Radio📻',
                               r"C:\Users\Master_PC\Desktop\IPtv_projects\Projects Eldad\M3u_Editor_EldadV1\IsraeliRadios.m3u")

        self.loadRadioChannels(filtered_channels, 'World Radio🌍',
                               r"C:\Users\Master_PC\Desktop\IPtv_projects\Projects Eldad\M3u_Editor_EldadV1\RADIO World.m3u")

        # Update categories and regenerate M3U content
        self.categories = filtered_channels
        self.updateCategoryList()
        self.regenerateM3UTextOnly()

        # Refresh the UI category list
        self.categoryList.clear()
        for category, channels in self.categories.items():
            display_text = f"{category} ({len(channels)})"
            self.categoryList.addItem(QListWidgetItem(display_text))

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