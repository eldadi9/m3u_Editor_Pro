from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTextEdit, QInputDialog, QListWidget, QListWidgetItem, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QHBoxLayout, QLabel, QMessageBox, QDialog, QLineEdit, QAbstractItemView, QAction
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont  # Add this line
import sys
import os
import re
import traceback
import pyperclip
import requests  # You need to import requests to handle downloading
from urllib.parse import urlparse


class MoveChannelsDialog(QDialog):
    def __init__(self, parent=None, categories=None):
        super().__init__(parent)
        self.categories = categories or []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Move Channels')
        layout = QVBoxLayout(self)
        self.categoryCombo = QComboBox(self)
        self.categoryCombo.addItems(self.categories)
        layout.addWidget(QLabel("Select category to move to:"))
        layout.addWidget(self.categoryCombo)
        self.newCategoryInput = QLineEdit(self)
        layout.addWidget(QLabel("Or create a new category:"))
        layout.addWidget(self.newCategoryInput)
        buttonBox = QHBoxLayout()
        self.okButton = QPushButton('OK', self)
        self.cancelButton = QPushButton('Cancel', self)
        buttonBox.addWidget(self.okButton)
        buttonBox.addWidget(self.cancelButton)
        layout.addLayout(buttonBox)
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        # Add a search bar and search button to the layout
        self.search_input = QLineEdit(self)
        self.search_button = QPushButton('Search', self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

    def getSelectedCategory(self):
        return self.newCategoryInput.text() if self.newCategoryInput.text() else self.categoryCombo.currentText()


class URLCheckThread(QThread):
    progress_signal = pyqtSignal(int, int, int, tuple)
    finished_signal = pyqtSignal()

    def __init__(self, channels):
        super().__init__()
        self.channels = channels
        self.stop_requested = False

    def run(self):
        online, offline, checked = 0, 0, 0
        total = len(self.channels)

        for name, url in self.channels:
            if self.stop_requested:
                break

            try:
                res = requests.head(url, timeout=3)
                status = "Online" if res.status_code < 400 else "Offline"
            except:
                status = "Offline"

            parsed_url = urlparse(url)
            server = parsed_url.hostname or "Unknown"

            if status == "Online":
                online += 1
            else:
                offline += 1

            checked += 1
            self.progress_signal.emit(checked, online, offline, (name, status, server, url))

        self.finished_signal.emit()

    def stop(self):
        self.stop_requested = True


class URLCheckerDialog(QDialog):
    def __init__(self, channels, parent=None):
        super().__init__(parent)
        self.channels = channels
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
        self.channelTable.setColumnCount(4)
        self.channelTable.setHorizontalHeaderLabels(["Channel Name", "Status", "Server", "URL"])
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
            status_item = self.channelTable.item(row, 1)
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

    def addChannelToTable(self, name, status, server, url):
        row_position = self.channelTable.rowCount()
        self.channelTable.insertRow(row_position)

        for col, data in enumerate([name, status, server, url]):
            item = QTableWidgetItem(data)
            if col == 1:
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
        self.usernameInput = QLineEdit(self)
        self.passwordInput = QLineEdit(self)
        self.hostInput = QLineEdit(self)

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

        layout.addWidget(usernameLabel)
        layout.addWidget(self.usernameInput)
        layout.addWidget(passwordLabel)
        layout.addWidget(self.passwordInput)
        layout.addWidget(hostLabel)
        layout.addWidget(self.hostInput)

        self.setLayout(layout)

    def convertToM3U(self):
        username = self.usernameInput.text()
        password = self.passwordInput.text()
        host = self.hostInput.text()
        self.m3uURL = f"{host}/get.php?username={username}&password={password}&type=m3u_plus"
        self.resultLabel.setText(self.m3uURL)
        self.copyButton.show()
        self.downloadButton.show()  # Show the download button once URL is generated
        pass

    def copyResultToClipboard(self):
        resultText = self.resultLabel.text()
        pyperclip.copy(resultText)
        QMessageBox.information(self, "Success", "Result copied to clipboard!")
        pass

    def downloadM3U(self):
        try:
            response = requests.get(self.m3uURL)
            response.raise_for_status()  # Raises stored HTTPError, if one occurred

            # Prompt to save file
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getSaveFileName(self,
                                                      "Save M3U File",
                                                      "",
                                                      "M3U Files (*.m3u);;All Files (*)",
                                                      options=options)
            if fileName:
                with open(fileName, 'wb') as f:
                    f.write(response.content)
                QMessageBox.information(self, "Download Successful", "The M3U file has been downloaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download M3U file: {str(e)}")
            pass


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
    progress = pyqtSignal(int, int, int, tuple)  # checked, offline, duplicates, (name, url, status, reason)
    finished = pyqtSignal()

    def __init__(self, channels, duplicate_names):
        super().__init__()
        self.channels = channels
        self.duplicate_names = duplicate_names
        self.stop_requested = False

    def run(self):
        checked = offline = duplicate = 0

        for name, url in self.channels:
            if self.stop_requested:
                break

            status = "Online"
            reason = ""

            try:
                res = requests.head(url, timeout=2)
                if res.status_code >= 400:
                    status = "Offline"
                    reason = "Bad Response"
                    offline += 1
            except:
                status = "Offline"
                reason = "Connection Error"
                offline += 1

            if name in self.duplicate_names:
                reason = "Duplicate" if not reason else reason + " & Duplicate"
                duplicate += 1

            checked += 1
            self.progress.emit(checked, offline, duplicate, (name, url, status, reason))

        self.finished.emit()

    def stop(self):
        self.stop_requested = True
class SmartScanStatusDialog(QDialog):
    def __init__(self, channels, duplicates, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Scan In Progress")
        self.setGeometry(200, 200, 1000, 600)

        self.setStyleSheet("QDialog { border: 5px solid red; background-color: white; }")
        self.channels = channels
        self.duplicates = duplicates

        layout = QVBoxLayout(self)

        # Top Stats
        self.labelStats = QLabel("Starting scan...")
        self.labelStats.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.labelStats)

        # Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Channel", "Status", "Reason", "URL"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Buttons
        # Buttons
        btnLayout = QHBoxLayout()

        self.deleteOfflineBtn = QPushButton("Delete Offline")
        self.deleteOfflineBtn.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.deleteOfflineBtn.clicked.connect(self.deleteOffline)

        self.deleteDuplicatesBtn = QPushButton("Delete Duplicates")
        self.deleteDuplicatesBtn.setStyleSheet("background-color: black; color: white; font-weight: bold;")
        self.deleteDuplicatesBtn.clicked.connect(self.deleteDuplicates)

        self.stopBtn = QPushButton("Stop Scan")
        self.stopBtn.setStyleSheet("background-color: purple; color: white; font-weight: bold;")
        self.stopBtn.clicked.connect(self.stopScan)

        btnLayout.addWidget(self.deleteOfflineBtn)
        btnLayout.addWidget(self.deleteDuplicatesBtn)
        btnLayout.addWidget(self.stopBtn)
        layout.addLayout(btnLayout)

        self.stopBtn.setStyleSheet("background-color: black; color: white; font-weight: bold;")
        self.stopBtn.clicked.connect(self.stopScan)
        btnLayout.addWidget(self.stopBtn)

        layout.addLayout(btnLayout)

        # Thread
        self.thread = SmartScanThread(channels, duplicates)
        self.thread.progress.connect(self.updateProgress)
        self.thread.finished.connect(self.scanFinished)
        self.thread.start()

    def deleteOffline(self):
        self.deleteByReason(match_offline=True, match_duplicate=False)

    def deleteDuplicates(self):
        self.deleteByReason(match_offline=False, match_duplicate=True)

    def deleteByReason(self, match_offline=False, match_duplicate=False):
        names_to_delete = []
        urls_to_delete = []

        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text()
            url = self.table.item(row, 3).text()
            reason = self.table.item(row, 2).text().lower()

            if (match_offline and "offline" in reason) or (match_duplicate and "duplicate" in reason):
                names_to_delete.append(name)
                urls_to_delete.append(url)

        if hasattr(self.parent(), "deleteChannelsByNames"):
            removed_count = self.parent().deleteChannelsByNames(names_to_delete, urls_to_delete)
            QMessageBox.information(self, "Deleted", f"{removed_count} channels deleted.")

    def scanFinished(self):
        self.labelStats.setText(self.labelStats.text() + " ✅ Done.")
        self.stopBtn.setEnabled(False)

        # Collect duplicate/offline names from table
        to_select_names = set()
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text()
            status = self.table.item(row, 1).text()
            reason = self.table.item(row, 2).text().lower()

            if "offline" in status.lower() or "duplicate" in reason:
                to_select_names.add(name)

        # Call parent to select them in channelList
        if hasattr(self.parent(), "selectChannelsByNames"):
            self.parent().selectChannelsByNames(to_select_names)
            QMessageBox.information(self, "Selected in List", f"{len(to_select_names)} problematic channels selected.")

    def updateProgress(self, checked, offline, duplicate, data):
        name, url, status, reason = data
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem(status))
        self.table.setItem(row, 2, QTableWidgetItem(reason))
        self.table.setItem(row, 3, QTableWidgetItem(url))

        self.labelStats.setText(f"Scanned: {checked} | Offline: {offline} | Duplicates: {duplicate}")

    def stopScan(self):
        self.thread.stop()
        self.labelStats.setText("Scan stopped by user.")
        self.stopBtn.setEnabled(False)

    def scanFinished(self):
        self.labelStats.setText(self.labelStats.text() + " ✅ Done.")
        self.stopBtn.setEnabled(False)


class M3UEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.categories = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle('M3U Playlist Editor')
        self.setGeometry(100, 100, 800, 600)

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

    def openM3UConverterDialog(self):
        dialog = M3UUrlConverterDialog(self)
        dialog.exec_()

    def search_channels(self, query, filter_options):
        results = []
        for category, channels in self.categories.items():
            for channel in channels:
                if query.lower() in channel.lower():
                    results.append(channel)
        return results

    def perform_search(self):
        query = self.search_input.text().strip()
        if query:  # Check if the query is not empty
            results = self.search_channels(query, {})
            self.display_search_results(results)
        else:
            self.display_search_results([])  # Clear results if query is empty

    def display_search_results(self, results):
        self.channelList.clear()  # Clears the current list
        self.textEdit.clear()  # Assuming 'textEdit' is your QTextEdit for M3U content
        for channel in results:
            self.channelList.addItem(channel)  # Adds channel to the list
            self.textEdit.append(channel)  # Also append the full channel info to the M3U content area

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
        self.showURLScanChoiceDialog()


    def mergeM3Us(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Additional M3U File", "",
                                                  "M3U Files (*.m3u *.m3u8);;All Files (*)", options=options)
        if fileName:
            try:
                with open(fileName, 'r', encoding='utf-8') as file:
                    additional_content = file.read()
                    current_content = self.textEdit.toPlainText()
                    if not current_content.endswith('\n'):
                        current_content += '\n'
                    self.textEdit.setPlainText(current_content + additional_content)

                    # Update the label to show that a file was merged
                    self.fileNameLabel.setText(f"Loaded File: {fileName.split('/')[-1]} (Merged)")
                    QMessageBox.information(self, "Merge Complete", "The M3U files have been merged successfully.")

                    # Parse the merged content to update categories and channels display
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

        # M3U URL Converter button
        self.m3uUrlConverterButton = QPushButton('M3U URL Converter', self)
        self.m3uUrlConverterButton.setStyleSheet("background-color: black; color: white;")
        self.m3uUrlConverterButton.clicked.connect(self.openM3UConverterDialog)
        buttons_layout.addWidget(self.m3uUrlConverterButton)

        self.convertPortalButton = QPushButton('Convert Portal MAC to M3U', self)
        self.convertPortalButton.setStyleSheet("background-color: green; color: white;")
        self.convertPortalButton.clicked.connect(self.convertPortalToM3U)
        buttons_layout.addWidget(self.convertPortalButton)

        # Export Groups button
        self.exportGroupButton = QPushButton('Export Groups', self)
        self.exportGroupButton.setStyleSheet("background-color: black; color: white;")
        self.exportGroupButton.clicked.connect(self.openExportDialog)
        buttons_layout.addWidget(self.exportGroupButton)

        # Filter Israeli Channels button
        self.filterIsraelChannelsButton = QPushButton('Filter Israeli Channels', self)
        self.filterIsraelChannelsButton.setStyleSheet("background-color: black; color: white;")
        self.filterIsraelChannelsButton.clicked.connect(self.filterIsraelChannels)
        buttons_layout.addWidget(self.filterIsraelChannelsButton)

        self.smartScanButton = QPushButton('Smart Scan', self)
        self.smartScanButton.setStyleSheet("background-color: purple; color: white; font-size: 16px;")
        self.smartScanButton.clicked.connect(self.openSmartScanDialog)
        buttons_layout.addWidget(self.smartScanButton)

        # Add the horizontal layout to the vertical layout
        layout.addLayout(buttons_layout)

        return layout

    def convertPortalToM3U(self):
        mac_address, ok_mac = QInputDialog.getText(self, 'Enter MAC Address', 'Enter your MAC Address:')
        portal_url, ok_portal = QInputDialog.getText(self, 'Enter Portal URL', 'Enter your Portal URL:')

        if ok_mac and ok_portal and mac_address and portal_url:
            headers = {
                "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko)",
                "Referer": portal_url,
                "X-User-Agent": "Model: MAG254; Link: Ethernet"
            }

            try:
                # Step 1: Authentication (Handshake)
                handshake_url = f"{portal_url}server/load.php"
                handshake_data = {"type": "stb", "action": "handshake", "token": "", "mac": mac_address}
                response = requests.post(handshake_url, headers=headers, json=handshake_data)

                # Debugging print
                print("Handshake Response:", response.text)

                # Validate JSON response
                if response.status_code != 200 or not response.text.strip():
                    QMessageBox.critical(self, "Error", "Failed to connect to portal. Check the Portal URL.")
                    return

                token = response.json().get("js", {}).get("token", None)

                if not token:
                    QMessageBox.critical(self, "Error", "Authentication failed. Check your MAC address and Portal URL.")
                    return

                # Step 2: Fetch Channels
                channels_url = f"{portal_url}stalker_portal/server/load.php?type=itv&action=get_all_channels&mac={mac_address}&token={token}"
                channels_response = requests.get(channels_url, headers=headers)

                # Debugging print
                print("Channels Response:", channels_response.text)

                # Validate JSON response
                if channels_response.status_code != 200 or not channels_response.text.strip():
                    QMessageBox.critical(self, "Error", "Failed to retrieve channel list. Check your Portal URL.")
                    return

                channels = channels_response.json().get("js", {}).get("data", [])

                if not channels:
                    QMessageBox.critical(self, "Error", "No channels found. Check your MAC and Portal URL.")
                    return

                # Step 3: Generate M3U File
                m3u_content = "#EXTM3U\n"
                for channel in channels:
                    name = channel.get("name", "Unknown Channel")
                    stream_url = channel.get("cmd", "")
                    m3u_content += f"#EXTINF:-1,{name}\n{stream_url}\n"

                file_path, _ = QFileDialog.getSaveFileName(self, "Save M3U File", "playlist.m3u",
                                                           "M3U Files (*.m3u);;All Files (*)")
                if file_path:
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(m3u_content)
                    QMessageBox.information(self, "Success", "M3U file successfully created!")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to convert Portal MAC to M3U: {str(e)}")

    def displayTotalChannels(self):
        total_channels = sum(len(channels) for channels in self.categories.values())
        self.channelCountLabel.setText(f"Total Channels: {total_channels}")

    def create_channel_section(self):
        layout = QVBoxLayout()
        channel_title = QLabel("Channels", self)
        channel_title.setAlignment(Qt.AlignCenter)
        channel_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(channel_title)

        # Search components added here for channels
        self.search_input = QLineEdit(self)
        self.search_button = QPushButton('Search', self)
        self.search_button.clicked.connect(
            self.perform_search)  # Ensure this connects to a proper channel search method
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)

        # Create the sorting combo box and add additional sorting options
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
        button_layout.addWidget(self.addChannelButton)
        button_layout.addWidget(self.deleteChannelButton)
        button_layout.addWidget(self.moveChannelUpButton)
        button_layout.addWidget(self.moveChannelDownButton)
        button_layout.addWidget(self.selectAllChannelsButton)
        button_layout.addWidget(self.clearChannelsSelectionButton)
        button_layout.addWidget(self.moveSelectedChannelButton)
        button_layout.addWidget(self.editSelectedChannelButton)
        button_layout.addWidget(self.checkDoublesButton)  # Add it to the button row
        layout.addLayout(button_layout)

        self.channelList = QListWidget(self)
        self.channelList.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.channelList)
        self.addChannelButton.clicked.connect(self.addChannel)
        self.deleteChannelButton.clicked.connect(self.deleteSelectedChannels)
        self.moveChannelUpButton.clicked.connect(self.moveChannelUp)
        self.moveChannelDownButton.clicked.connect(self.moveChannelDown)
        self.selectAllChannelsButton.clicked.connect(self.selectAllChannels)
        self.clearChannelsSelectionButton.clicked.connect(self.deselectAllChannels)
        self.moveSelectedChannelButton.clicked.connect(self.moveSelectedChannel)
        self.editSelectedChannelButton.clicked.connect(self.editSelectedChannel)
        return layout

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
            self.updateM3UContent()  # <-- Add this line

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

            # Update the self.categories dictionary
            category_keys = list(self.categories.keys())
            category_keys[current_row], category_keys[current_row - 1] = category_keys[current_row - 1], category_keys[
                current_row]

            # Reorder the dictionary
            reordered_categories = {key: self.categories[key] for key in category_keys}
            self.categories = reordered_categories

            # Regenerate the M3U content
            self.updateM3UContent()

    def moveCategoryDown(self):
        current_row = self.categoryList.currentRow()
        if current_row < self.categoryList.count() - 1:
            current_item = self.categoryList.takeItem(current_row)
            self.categoryList.insertItem(current_row + 1, current_item)
            self.categoryList.setCurrentRow(current_row + 1)

            # Update the self.categories dictionary
            category_keys = list(self.categories.keys())
            category_keys[current_row], category_keys[current_row + 1] = category_keys[current_row + 1], category_keys[
                current_row]

            # Reorder the dictionary
            reordered_categories = {key: self.categories[key] for key in category_keys}
            self.categories = reordered_categories

            # Regenerate the M3U content
            self.updateM3UContent()

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
        """
        Deletes only the channels that are explicitly selected in the channel list.
        Works with the exact position (index) in the current category.
        Shows a message at the end with the count of deleted channels.
        """
        current_category_item = self.categoryList.currentItem()
        if not current_category_item:
            QMessageBox.warning(self, "Warning", "No category selected.")
            return

        current_category = current_category_item.text().split(" (")[0]
        if current_category not in self.categories:
            QMessageBox.warning(self, "Warning", "Category not found.")
            return

        selected_items = self.channelList.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Info", "No channels selected for deletion.")
            return

        # We need to find the actual index positions of selected channels
        selected_indexes = [self.channelList.row(item) for item in selected_items]

        # Delete by index — reverse so deletion does not shift indexes
        selected_indexes.sort(reverse=True)

        deleted_count = 0

        for index in selected_indexes:
            if 0 <= index < len(self.categories[current_category]):
                del self.categories[current_category][index]
                deleted_count += 1

        # Update the UI and M3U content
        self.updateM3UContent()
        self.display_channels(self.categoryList.currentItem())

        QMessageBox.information(self, "Success", f"Deleted {deleted_count} channel(s).")

    def updateM3UContent(self):
        """
        Regenerates the M3U content based on the current state of self.categories,
        preserving all channel attributes.
        """
        updated_lines = ["#EXTM3U"]
        for category, channels in self.categories.items():
            for channel in channels:
                extinf_line = self.getFullExtInfLine(channel)
                url = self.getUrl(channel)
                updated_lines.append(f"{extinf_line}\n{url}")

        self.textEdit.setPlainText("\n".join(updated_lines))

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
        """
        Moves the selected channel up in the list and updates the M3U content.
        """
        current_row = self.channelList.currentRow()
        if current_row <= 0:
            return  # Can't move the first item up

        current_item = self.channelList.takeItem(current_row)
        self.channelList.insertItem(current_row - 1, current_item)
        self.channelList.setCurrentRow(current_row - 1)

        # Update the self.categories dictionary
        current_category_item = self.categoryList.currentItem()
        if not current_category_item:
            QMessageBox.warning(self, "Warning", "No category selected.")
            return

        current_category = current_category_item.text().split(" (")[0]
        channels = self.categories[current_category]
        if 0 <= current_row < len(channels):
            # Swap the current channel with the one above it
            channels[current_row], channels[current_row - 1] = channels[current_row - 1], channels[current_row]
            self.categories[current_category] = channels

        # Update the M3U content
        self.updateM3UContent()

    def moveChannelDown(self):
        """
        Moves the selected channel down in the list and updates the M3U content.
        """
        current_row = self.channelList.currentRow()
        if current_row < 0 or current_row >= self.channelList.count() - 1:
            return  # Can't move the last item down

        current_item = self.channelList.takeItem(current_row)
        self.channelList.insertItem(current_row + 1, current_item)
        self.channelList.setCurrentRow(current_row + 1)

        # Update the self.categories dictionary
        current_category_item = self.categoryList.currentItem()
        if not current_category_item:
            return  # No category selected

        current_category = current_category_item.text().split(" (")[0]
        channels = self.categories[current_category]
        if 0 <= current_row < len(channels) - 1:
            # Swap the current channel with the one below it
            channels[current_row], channels[current_row + 1] = channels[current_row + 1], channels[current_row]
            self.categories[current_category] = channels

        # Update the M3U content
        self.updateM3UContent()

    def updateM3UContent(self):
        """
        Regenerates the M3U content based on the current state of self.categories.
        """
        updated_lines = []
        for category, channels in self.categories.items():
            for channel in channels:
                # Add EXTINF line
                updated_lines.append(f"#EXTINF:-1 group-title=\"{category}\",{channel.split(' (')[0]}")
                # Add URL line
                updated_lines.append(channel.split(' (')[-1].strip(')'))

        self.textEdit.setPlainText("\n".join(updated_lines))

    def selectAllChannels(self):
        for i in range(self.channelList.count()):
            self.channelList.item(i).setSelected(True)

    def deselectAllChannels(self):
        for i in range(self.channelList.count()):
            self.channelList.item(i).setSelected(False)

    def moveSelectedChannel(self):
        """
        Moves selected channels to a new or existing category and updates the M3U content.
        """
        # Validate the selected channels
        selected_items = self.channelList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No channels selected for moving.")
            return

        # Open the dialog to select the target category or create a new one
        dialog = MoveChannelsDialog(self, list(self.categories.keys()))
        if dialog.exec_():
            # Get the target category from the dialog
            target_category = dialog.getSelectedCategory()
            if not target_category:
                QMessageBox.warning(self, "Warning", "No target category specified.")
                return

            # Ensure the target category exists
            if target_category not in self.categories:
                # Dynamically create the new category
                self.categories[target_category] = []
                self.updateCategoryList()  # Refresh the UI with the new category

            # Validate the current category
            current_category_item = self.categoryList.currentItem()
            if current_category_item is None:
                QMessageBox.warning(self, "Warning", "No category selected.")
                return

            current_category = current_category_item.text().split(" (")[0]
            if current_category not in self.categories:
                QMessageBox.warning(self, "Warning", "The current category does not exist.")
                return

            moved_channels = []

            # Move the selected channels
            for item in selected_items:
                if item is None:
                    continue
                channel_name = item.text()
                if not channel_name:
                    continue
                # Check if the channel exists in the current category
                for channel in self.categories[current_category]:
                    if channel.split(" (")[0] == channel_name:
                        moved_channels.append(channel)
                        self.categories[current_category].remove(channel)
                        break

            # Add the moved channels to the target category
            self.categories[target_category].extend(moved_channels)

            # Update the M3U content to reflect the changes
            self.updateM3UContent()

            # Refresh the UI
            self.updateCategoryList()  # Update category list counts
            self.display_channels(self.categoryList.currentItem())  # Update channel list for the current category

            # Show success message with the count of moved channels
            QMessageBox.information(self, "Success",
                                    f"{len(moved_channels)} channels have been successfully moved to '{target_category}'.")
            current_category_item = self.categoryList.currentItem()
            if current_category_item and hasattr(current_category_item, 'text') and current_category_item.text():
                current_category = current_category_item.text().split(" (")[0]
            else:
                current_category = None  # Fallback

                return

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
        dialog.setWindowTitle("Select Category to Scan")

        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        dialog.setStyleSheet("""
            QDialog {
                border: 5px solid red;
                background-color: white;
            }
        """)

        layout = QVBoxLayout(dialog)

        label = QLabel("Choose a category to scan:")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        combo = QComboBox(dialog)
        combo.addItems(self.categories.keys())
        layout.addWidget(combo)

        scan_button = QPushButton("Start Scan")
        scan_button.setStyleSheet("background-color: black; color: white; font-weight: bold;")
        layout.addWidget(scan_button)

        scan_button.clicked.connect(lambda: self.runURLCheckerFromCategory(combo.currentText(), dialog))

        dialog.setLayout(layout)
        dialog.exec_()

    def openSmartScanDialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Smart Scan")
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        dialog.setStyleSheet("""
            QDialog {
                border: 5px solid red;
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
        dialog.setStyleSheet("QDialog { border: 5px solid red; background-color: white; }")
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

    def smartScan(self, category_only=True, dialog=None):
        if dialog:
            dialog.close()

        duplicate_names = set()
        seen_names = set()
        channels_to_check = []

        if category_only:
            item = self.categoryList.currentItem()
            if not item:
                QMessageBox.warning(self, "Warning", "Please select a category.")
                return
            category = item.text().split(" (")[0]
            source = self.categories.get(category, [])
        else:
            # כל הערוצים מכל הקטגוריות
            source = []
            for ch_list in self.categories.values():
                source.extend(ch_list)

        # מציאת כפולים ואיסוף קישורים לבדיקה
        for ch in source:
            name = ch.split(" (")[0].strip()
            url = self.getUrl(ch)
            channels_to_check.append((name, url))

            if name in seen_names:
                duplicate_names.add(name)
            else:
                seen_names.add(name)

        # בדיקת תקינות URL
        offline_names = []
        for name, url in channels_to_check:
            try:
                res = requests.head(url, timeout=2)
                if res.status_code >= 400:
                    offline_names.append(name)
            except:
                offline_names.append(name)

        # איחוד רשימת שמות כפולים ולא תקינים
        final_selection = set(offline_names).union(duplicate_names)

        # סימון ברשימת הערוצים
        self.channelList.clearSelection()
        for i in range(self.channelList.count()):
            item = self.channelList.item(i)
            if item.text() in final_selection:
                item.setSelected(True)

        QMessageBox.information(self, "Smart Scan Complete",
                                f"✔️ Duplicate channels: {len(duplicate_names)}\n❌ Offline channels: {len(offline_names)}\n🎯 Total marked: {len(final_selection)}")

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
        for category, ch_list in self.categories.items():
            original_len = len(ch_list)

            self.categories[category] = [
                ch for ch in ch_list
                if not any(
                    ch.startswith(name) and self.getUrl(ch) == url
                    for name, url in zip(names_to_delete, urls_to_delete)
                )
            ]

            removed += original_len - len(self.categories[category])

        self.updateCategoryList()
        self.updateM3UContent()
        if self.categoryList.currentItem():
            self.display_channels(self.categoryList.currentItem())

        return removed

    def getUrl(self, channel_info):
        try:
            return channel_info.split(" (")[1][:-1]
        except IndexError:
            return ""

    def findFullM3UEntry(self, channel_name, category):
        for channel in self.categories.get(category, []):
            if channel.startswith(channel_name):
                return channel
        return None

    def loadM3U(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open M3U File", "", "M3U Files (*.m3u *.m3u8);;All Files (*)",
                                                  options=options)
        if fileName:
            try:
                with open(fileName, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.textEdit.setPlainText(content)
                self.parseM3UContentEnhanced(content)
                # Display the file name and total channels in the label
                total_channels = sum(len(channels) for channels in self.categories.values())
                self.channelCountLabel.setText(f"Total Channels: {total_channels}")
                self.fileNameLabel.setText(f"Loaded File: {fileName.split('/')[-1]}")  # Only show the file name
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")

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
        - Use #EXTGRP to set group-title if missing and reset appropriately.
        - Always preserve the tvg-logo attribute if it exists.
        - Reset current_group after each #EXTINF to prevent misapplication.
        """
        self.categories.clear()
        updated_lines = []
        current_group = None  # To track the group name from #EXTGRP

        lines = content.splitlines()

        for line in lines:
            if line.startswith("#EXTGRP:"):
                # Extract the group name from the #EXTGRP line
                current_group = line.split(":", 1)[1].strip()
                continue  # Skip the #EXTGRP line itself

            if line.startswith("#EXTINF:"):
                # Handle group-title, adding it if missing and current_group is set
                if "group-title=" not in line and current_group:
                    line = re.sub(r'(#EXTINF:[^\n]*?),', f'\\1 group-title="{current_group}",', line)
                current_group = None  # Reset after usage to prevent misapplication

                # Ensure the tvg-logo attribute remains intact
                match = re.search(r'tvg-logo="([^"]+)"', line)
                if match:
                    logo_url = match.group(1)  # Extract the tvg-logo URL
                    if 'tvg-logo' not in line:
                        line += f' tvg-logo="{logo_url}"'

            updated_lines.append(line)

        # Combine updated lines into a modified M3U content
        updated_content = "\n".join(updated_lines)
        # Parse categories and channels from the updated content
        category_pattern = re.compile(r'#EXTINF.*group-title="([^"]+)".*,(.*)\n(.*)')
        for match in category_pattern.findall(updated_content):
            group_title, channel_name, channel_url = match
            if group_title not in self.categories:
                self.categories[group_title] = []
            self.categories[group_title].append(f"{channel_name.strip()} ({channel_url.strip()})")

        # Update the QTextEdit and the category list
        self.textEdit.setPlainText(updated_content)
        self.categoryList.clear()
        for category, channels in self.categories.items():
            item = QListWidgetItem(f"{category} ({len(channels)})")  # Add count of channels to the category name
            self.categoryList.addItem(item)

    def filterIsraelChannels(self):
        israel_keywords = ['Israel', 'IL', 'ISRAEL', 'Hebrew', 'hebrew', 'israeli', 'Israeli', '"IL"', 'Il', 'IL HD',
                           'TV', 'MUSIC', 'ישראלי', 'MTV', 'USA', 'mtv', 'Music Hits+', 'WWE ', 'nba tv',
                           'music', 'IL:', 'Hebrew']
        category_keywords = {

            'News📺': ['Keshet 12 IL', 'Channel 9 HD IL', '9 Channel IL', 'CHANNEL 9 HD IL', 'KAN 11 IL', '12 Keshet IL',
                      'C13 Keshet IL', 'KAN 14 IL', 'Channel 9 IL', 'Kan 11 IL', 'Knesset Channel IL',
                      'MAKAN HD IL', 'i24 IL', 'Channel 14', 'Kan Educational HD IL', 'Reshet 13 IL', 'KHAN 11',
                      'Channel 9 HD', 'Channel 11', 'Channel 12', 'Channel 13', 'Makan 33 HD', 'Reshet 13 IL',
                      'Kan Chinuchit 23', 'i24 News', 'Channel 9', 'Channel 11', 'Channel 12', 'Channel 13',
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
                        'Sport 2 HD', 'Sport 3 HD', 'Sport 4 HD',
                        'Sport 5 HD', 'Sport 5 Live HD', 'Eurosport 1 HD', 'ESPN 2 HD USA', 'ESPN USA',
                        'Eurosport 1 HD', 'Red Bull TV HD',
                        'WWE Russian', 'Red Bull TV', 'MMA-TV.com HD', 'MMA-TV.com', 'MMA-TV.com orig', 'NHL', 'nba',
                        'NBA', 'wwe', 'WWE Network HD', 'Eurosport 2',
                        'Eurosport 2', 'EXTREME', 'SPORT'],
            'Kids🍦': ['Hop!', 'Israelit', 'Baby IL', 'Yaldut IL', 'BABY TV IL', 'hop', 'HOT A+ Kids', 'Nick Jr',
                      'Nickelodeon', 'Disney Junior', 'Luli', 'Junior', 'Disney HD', 'Baby', 'Hop! Childhood', 'Yaldut',
                      'ZOOM', 'Disney Channel H', 'YoYo', 'NICK JR HD IL', 'Nick Jr IL', 'NICK HD IL',
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
                               'Home Plus', 'Love Island', 'History HD', 'Humor Channel', 'Fomo', 'Fashion',
                               'Food Channel HD', 'Foody HD', 'Erez Nehederet HD', 'Big', 'CBS Reality', 'Boomerang',
                               'Entertainment IL', 'HEALTH CHANNEL', 'HUMOR CHANNEL', 'E! IL'],
            'Music🎵': ['music', 'MUSIC', 'MUSIC 24', 'MTV Hits', 'MTV Base HD', 'Stingray ', 'MTV Hits',
                       'Stingray Hot Country HD', 'Stingray Pop Adult HD', 'Stingray Hit List HD', 'MTV Hits',
                       'MTV Club', 'Clubbing TV HD', 'IL: MTV HD', 'MTV 80s', 'MTV', 'MTV Pulse HD', 'IT: MTV HD',
                       'MTV Idol HD', 'VH1 Classic', 'Rock Classics', 'Europa Plus TV HD', 'Music Box Gold', 'music 24',
                       'MTV Hits orig',
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
                        'DISCOVERY CHANNEL HD IL', 'NET GEO_WILD HD IL', 'Sky Select 5 HD', 'NAT GEO WILD IL',
                        'TRAVEL CHANNEL IL',
                        'NATIONAL GEOGRAPHICS HD IL'],
            'world series🌍': ['Viva Premium HD IL', 'Turkish Dramas 3 HD IL', 'Turkish Dramas 2 HD IL',
                              'Turkish Dramas Plus HD IL', 'Viva', 'Turkish Dramas 3 HD IL', 'Yam Tihoni 25',
                              'Viva plus', 'Aruch Sdarot Hahodiot', 'Aruch Sdarot Hahodiot 2', 'Yam Tihoni Plus',
                              'Vamos HD', 'Yam Tihoni HD', 'Yam Tihoni 2', 'Viva+ IL', 'Viva+', 'Viva Vintage',
                              'Viva Premium HD', 'VIVA IL', 'Yamtihoni IL', 'VIVA HD IL', 'VIVA+ IL',
                              'YAM TIHONI HD IL', 'HALA TV IL', 'BOLLYWOOD HD IL', 'BOLLYSHOW HD IL', 'Bollywood HD',
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

        # Load Israeli and World Radios as usual
        self.loadRadioChannels(filtered_channels, 'Israel Radio📻',
                               r"C:\Users\Master_PC\Desktop\IPtv_projects\Projects Eldad\M3u_Editor_EldadV1\IsraeliRadios.m3u")

        self.loadRadioChannels(filtered_channels, 'World Radio🌍',
                               r"C:\Users\Master_PC\Desktop\IPtv_projects\Projects Eldad\M3u_Editor_EldadV1\RADIO World.m3u")

        # Ask user whether to load radio channels together or separately
        user_reply = QMessageBox.question(self, 'Load Radio by Category',
                                          'Do you want to upload all channels together (Radio_By_Category.m3u)?',
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if user_reply == QMessageBox.Yes:
            # Load all channels together into one category
            filtered_channels['Radio by Category📡'] = []
            self.loadRadioChannels(filtered_channels, 'Radio by Category📡',
                                   r"C:\Users\Master_PC\Desktop\IPtv_projects\Projects Eldad\M3u_Editor_EldadV1\Radio_By_Category.m3u")
        else:
            # Load channels separated by categories dynamically
            self.loadRadioCategories(filtered_channels,
                                     r"C:\Users\Master_PC\Desktop\IPtv_projects\Projects Eldad\M3u_Editor_EldadV1\Radio_By_Category.m3u")

        # Update categories and regenerate M3U content
        self.categories = filtered_channels
        self.updateCategoryList()
        self.updateM3UContent()

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