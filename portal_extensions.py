#!/usr/bin/env python3
"""
Portal Extensions for M3U Editor
===============================
Advanced Portal to M3U converter with enhanced features
Compatible with m3u_EditorV3.py

Usage: Add to M3U_EDITOR folder and import in m3u_EditorV3.py
"""

import json
import time
import requests
import random
import re
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, urljoin
import concurrent.futures
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QComboBox,
    QMessageBox, QProgressBar, QCheckBox, QSpinBox,
    QGroupBox, QGridLayout, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from datetime import datetime



# ===== THEME: Portal converter UI styles =====
PORTAL_QSS = """
QDialog {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1e3c72, stop:1 #2a5298);
}
QLabel {
    color: white;
    font-weight: bold;
}
QLineEdit, QTextEdit, QComboBox {
    background: rgba(255, 255, 255, 0.92);
    border: 2px solid #4CAF50;
    border-radius: 6px;
    padding: 6px;
    font-size: 12px;
}
QPushButton {
    background: #4CAF50;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    font-weight: 600;
    font-size: 14px;
}
QPushButton:hover {
    background: #45a049;
}
QPushButton:pressed {
    background: #367c39;
}
QPushButton:disabled {
    background: #9E9E9E;
}
QProgressBar {
    border: 2px solid #4CAF50;
    border-radius: 6px;
    text-align: center;
    color: white;
    font-weight: bold;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4CAF50, stop:1 #8BC34A);
    border-radius: 6px;
}
QGroupBox {
    color: white;
    border: 2px solid #4CAF50;
    border-radius: 8px;
    margin-top: 10px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
}
QCheckBox {
    color: white;
}
"""


class PortalManager:
    """מנהל מתקדם לטיפול בPortals"""

    # רשימת פורטלים ידועים עם הגדרות מותאמות
    KNOWN_PORTALS = {
        "stalker": {
            "api_path": "/stalker_portal/server/load.php",
            "referer_path": "/c/",
            "headers": {
                "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3",
                "X-User-Agent": "Model: MAG254; Link: Ethernet"
            },
            "login_params": {
                "type": "stb",
                "action": "login"
            }
        },
        "ministra": {
            "api_path": "/portal.php",
            "referer_path": "/c/",
            "headers": {
                "User-Agent": "Mozilla/5.0 (SMART-TV; Linux; Tizen 5.0) AppleWebKit/538.1",
                "X-User-Agent": "Model: MAG322; Link: WiFi"
            },
            "login_params": {
                "type": "stb",
                "action": "handshake"
            }
        },
        "xtream": {
            "api_path": "/player_api.php",
            "referer_path": "/",
            "headers": {
                "User-Agent": "IPTVSmarters/1.1"
            },
            "login_params": {
                "action": "get_live_categories"
            }
        }
    }

    @staticmethod
    def detect_portal_type(url: str) -> str:
        """זיהוי אוטומטי של סוג הפורטל"""
        url_lower = url.lower()

        if "stalker_portal" in url_lower or "/c/" in url_lower:
            return "stalker"
        elif "ministra" in url_lower or "portal.php" in url_lower:
            return "ministra"
        elif "player_api" in url_lower or ":8080" in url:
            return "xtream"
        elif "get.php" in url_lower:
            return "stalker"
        else:
            return "stalker"  # ברירת מחדל

    @staticmethod
    def validate_mac_address(mac: str) -> bool:
        """בדיקת תקינות כתובת MAC"""
        pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        return bool(re.match(pattern, mac))

    @staticmethod
    def generate_mac_variations(mac: str) -> List[str]:
        """יצירת וריאציות של כתובת MAC"""
        clean_mac = mac.replace(":", "").replace("-", "").upper()

        if len(clean_mac) != 12:
            return [mac]

        variations = [
            # 00:1A:79:XX:XX:XX
            ":".join([clean_mac[i:i+2] for i in range(0, 12, 2)]),
            # 00-1A-79-XX-XX-XX
            "-".join([clean_mac[i:i+2] for i in range(0, 12, 2)]),
            # 001A79XXXXXX
            clean_mac
        ]

        return list(set(variations))  # הסרת כפילויות

    @staticmethod
    def generate_random_mac() -> str:
        """יצירת MAC אקראי"""
        # MAG prefixes
        prefixes = ["00:1A:79", "00:1A:78", "00:09:DF", "00:1A:7A"]
        prefix = random.choice(prefixes)

        # Random suffix
        suffix = ":".join([f"{random.randint(0, 255):02X}" for _ in range(3)])

        return f"{prefix}:{suffix}"


class PortalConverterThread(QThread):
    """Thread לביצוע המרת Portal ברקע"""

    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(str)  # M3U content
    error = pyqtSignal(str)

    def __init__(self, portal_url: str, mac_address: str,
                 portal_type: str = "auto", options: Dict = None):
        super().__init__()
        self.portal_url = portal_url
        self.mac_address = mac_address
        self.portal_type = portal_type
        self.options = options or {}
        self.is_cancelled = False

    def cancel(self):
        """ביטול התהליך"""
        self.is_cancelled = True

    def normalize_url(self, url: str) -> str:
        """נרמול URL"""
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        return url.rstrip('/')

    def run(self):
        """ביצוע ההמרה"""
        try:
            # זיהוי סוג הפורטל
            if self.portal_type == "auto":
                portal_type = PortalManager.detect_portal_type(self.portal_url)
                self.status.emit(f"🔍 Detected portal type: {portal_type}")
            else:
                portal_type = self.portal_type

            self.progress.emit(10)

            # בחירת הגדרות לפי סוג הפורטל
            portal_config = PortalManager.KNOWN_PORTALS.get(
                portal_type,
                PortalManager.KNOWN_PORTALS["stalker"]
            )

            # נרמול URL
            base_url = self.normalize_url(self.portal_url)
            api_url = base_url + portal_config["api_path"]
            referer = base_url + portal_config["referer_path"]

            self.status.emit(f"🔗 Connecting to: {base_url}")
            self.progress.emit(20)

            # הכנת session
            session = requests.Session()
            headers = portal_config["headers"].copy()
            headers["Referer"] = referer
            headers["Origin"] = base_url

            # ניסיון התחברות עם וריאציות MAC
            mac_variations = PortalManager.generate_mac_variations(self.mac_address)
            token = None
            successful_mac = None

            for mac in mac_variations:
                if self.is_cancelled:
                    return

                self.status.emit(f"🔑 Trying MAC: {mac}")

                # Handshake
                hs_params = {
                    "type": "stb",
                    "action": "handshake",
                    "token": "",
                    "mac": mac
                }

                try:
                    response = session.get(
                        api_url,
                        params=hs_params,
                        headers=headers,
                        timeout=15
                    )

                    if response.status_code == 200:
                        data = response.json()
                        token = data.get("js", {}).get("token") or data.get("token")

                        if token:
                            successful_mac = mac
                            self.status.emit(f"✅ Connected with MAC: {mac}")
                            break

                except Exception as e:
                    self.status.emit(f"⚠️ MAC {mac} failed: {str(e)[:50]}")
                    continue

            if not token:
                self.error.emit("❌ Failed to authenticate with any MAC variation")
                return

            self.progress.emit(40)

            # Login
            headers["Authorization"] = f"Bearer {token}"
            login_params = {
                "type": "stb",
                "action": "login",
                "device_id": successful_mac,
                "device_id2": successful_mac,
                "mac": successful_mac
            }

            try:
                session.get(api_url, params=login_params, headers=headers, timeout=15)
                self.status.emit("📝 Logged in successfully")
                self.progress.emit(50)
            except Exception as e:
                self.status.emit(f"⚠️ Login warning: {str(e)[:50]}")

            # Get categories (optional)
            categories = {}
            if self.options.get("fetch_categories", True):
                self.status.emit("📂 Fetching categories...")
                cat_params = {"type": "itv", "action": "get_genres"}
                try:
                    cat_response = session.get(
                        api_url,
                        params=cat_params,
                        headers=headers,
                        timeout=10
                    )
                    if cat_response.status_code == 200:
                        cat_data = cat_response.json()
                        for cat in cat_data.get("js", []):
                            categories[cat.get("id")] = cat.get("title", "Unknown")
                        self.status.emit(f"📂 Found {len(categories)} categories")
                except Exception as e:
                    self.status.emit(f"⚠️ Categories fetch failed: {str(e)[:50]}")

            # Get channels
            self.status.emit("📺 Fetching channels...")
            self.progress.emit(60)

            channels_params = {"type": "itv", "action": "get_all_channels"}
            ch_response = session.get(
                api_url,
                params=channels_params,
                headers=headers,
                timeout=30
            )

            if ch_response.status_code != 200:
                self.error.emit("❌ Failed to fetch channels")
                return

            channels_data = ch_response.json()
            channels = (channels_data.get("js") or {}).get("data", [])

            if not channels:
                self.error.emit("❌ No channels found in response")
                return

            self.status.emit(f"📊 Found {len(channels)} channels")
            self.progress.emit(70)

            # Build M3U with enhanced features
            m3u_lines = ["#EXTM3U"]

            # Add portal info as comments
            m3u_lines.append(f"# Portal: {base_url}")
            m3u_lines.append(f"# MAC: {successful_mac}")
            m3u_lines.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            m3u_lines.append(f"# Total Channels: {len(channels)}")
            m3u_lines.append("")

            processed_channels = 0

            for channel in channels:
                if self.is_cancelled:
                    return

                name = channel.get("name", "Unknown Channel").strip()
                logo = channel.get("logo", "")
                tvg_id = str(channel.get("id", ""))
                genre_id = channel.get("tv_genre_id", "")
                genre_name = categories.get(genre_id, "General")

                # Get stream URL
                stream_url = channel.get("cmd", "").strip()

                # Try to create fresh link if needed
                if not stream_url or self.options.get("force_create_link", False):
                    try:
                        link_params = {
                            "type": "itv",
                            "action": "create_link",
                            "cmd": f"ffrt {channel.get('id')}",
                            "mac": successful_mac,
                            "token": token
                        }
                        link_resp = session.get(api_url, params=link_params, headers=headers, timeout=10)
                        if link_resp.status_code == 200:
                            link_data = link_resp.json()
                            stream_url = link_data.get("js", {}).get("cmd", stream_url)
                    except:
                        pass

                if stream_url:
                    # Build EXTINF line
                    extinf = f'#EXTINF:-1 tvg-id="{tvg_id}"'

                    if logo:
                        extinf += f' tvg-logo="{logo}"'

                    if genre_name:
                        extinf += f' group-title="{genre_name}"'

                    extinf += f',{name}'

                    m3u_lines.append(extinf)
                    m3u_lines.append(stream_url)
                    m3u_lines.append("")  # Empty line for readability

                    processed_channels += 1

                # Update progress
                if processed_channels % 10 == 0:
                    progress = 70 + int((processed_channels / len(channels)) * 25)
                    self.progress.emit(progress)
                    self.status.emit(f"📺 Processed {processed_channels}/{len(channels)} channels")

            self.progress.emit(95)
            self.status.emit(f"✨ Finalizing M3U with {processed_channels} channels...")

            # Join lines and emit result
            m3u_content = "\n".join(m3u_lines)

            self.progress.emit(100)
            self.status.emit(f"🎉 Conversion completed! {processed_channels} channels ready")
            self.finished.emit(m3u_content)

        except Exception as e:
            self.error.emit(f"❌ Conversion failed: {str(e)}")


class AdvancedPortalConverter(QDialog):
    """חלון המרת Portal מתקדם"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🌐 Advanced Portal to M3U Converter")
        self.setModal(True)
        self.setMinimumSize(600, 500)

        self.m3u_content = ""
        self.converter_thread = None

        self.init_ui()

    def init_ui(self):
        """יצירת ממשק המשתמש"""
        layout = QVBoxLayout(self)

        # === Input Section ===
        input_group = QGroupBox("📡 Portal Connection")
        input_layout = QGridLayout()

        # Portal URL
        input_layout.addWidget(QLabel("Portal URL:"), 0, 0)
        self.portal_input = QLineEdit()
        self.portal_input.setPlaceholderText("http://example.com:8080/c/ or https://portal.example.com")
        input_layout.addWidget(self.portal_input, 0, 1)

        # Portal Type
        input_layout.addWidget(QLabel("Portal Type:"), 1, 0)
        self.portal_type = QComboBox()
        self.portal_type.addItems(["Auto Detect", "Stalker", "Ministra", "Xtream"])
        input_layout.addWidget(self.portal_type, 1, 1)

        # MAC Address
        input_layout.addWidget(QLabel("MAC Address:"), 2, 0)
        mac_layout = QHBoxLayout()
        self.mac_input = QLineEdit()
        self.mac_input.setPlaceholderText("00:1A:79:XX:XX:XX")
        mac_layout.addWidget(self.mac_input)

        mac_gen_btn = QPushButton("🎲 Random")
        mac_gen_btn.clicked.connect(self.generate_random_mac)
        mac_gen_btn.setMaximumWidth(80)
        mac_layout.addWidget(mac_gen_btn)

        mac_widget = QWidget()
        mac_widget.setLayout(mac_layout)
        input_layout.addWidget(mac_widget, 2, 1)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # === Options Section ===
        options_group = QGroupBox("⚙️ Conversion Options")
        options_layout = QGridLayout()

        self.fetch_categories = QCheckBox("Fetch Categories")
        self.fetch_categories.setChecked(True)
        options_layout.addWidget(self.fetch_categories, 0, 0)

        self.include_vod = QCheckBox("Include VOD Content")
        options_layout.addWidget(self.include_vod, 0, 1)

        self.force_create_link = QCheckBox("Force Create Fresh Links")
        self.force_create_link.setToolTip("May take longer but ensures working links")
        options_layout.addWidget(self.force_create_link, 1, 0)

        self.auto_logo = QCheckBox("Auto-inject Logos")
        self.auto_logo.setChecked(True)
        options_layout.addWidget(self.auto_logo, 1, 1)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # === Progress Section ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(120)
        self.status_text.setVisible(False)
        layout.addWidget(self.status_text)

        # === Buttons ===
        buttons_layout = QHBoxLayout()

        self.convert_btn = QPushButton("🚀 Convert Portal")
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        buttons_layout.addWidget(self.convert_btn)

        self.save_btn = QPushButton("💾 Save M3U")
        self.save_btn.clicked.connect(self.save_m3u)
        self.save_btn.setEnabled(False)
        buttons_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.cancel_conversion)
        self.cancel_btn.setVisible(False)
        buttons_layout.addWidget(self.cancel_btn)

        self.close_btn = QPushButton("🚪 Close")
        self.close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(self.close_btn)

        layout.addLayout(buttons_layout)
        self.apply_portal_theme()

    def apply_portal_theme(self):
        """החלת ערכת עיצוב אחידה על הדיאלוג"""
        try:
            self.setStyleSheet(PORTAL_QSS)
            # שיפורי UX קטנים שלא משנים לוגיקה:
            self.progress_bar.setTextVisible(True)
            self.progress_bar.setFormat("%p%")
            # מגדיר רוחבים מינימליים לשדות כדי לשמור פרופורציות יפות
            self.portal_input.setMinimumWidth(380)
            self.mac_input.setMinimumWidth(240)
        except Exception:
            # אם מכל סיבה ה-QSS נכשל, ממשיכים בלי לעצור את החלון
            pass

    def generate_random_mac(self):
        """יצירת MAC אקראי"""
        mac = PortalManager.generate_random_mac()
        self.mac_input.setText(mac)

    def start_conversion(self):
        """התחלת תהליך ההמרה"""
        portal_url = self.portal_input.text().strip()
        mac_address = self.mac_input.text().strip()

        if not portal_url or not mac_address:
            QMessageBox.warning(self, "Missing Input",
                              "Please enter both Portal URL and MAC address.")
            return

        if not PortalManager.validate_mac_address(mac_address):
            reply = QMessageBox.question(
                self, "Invalid MAC Format",
                "MAC address format seems incorrect. Continue anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # Prepare option
        options = {
            "fetch_categories": self.fetch_categories.isChecked(),
            "include_vod": self.include_vod.isChecked(),
            "force_create_link": self.force_create_link.isChecked(),
            "auto_logo": self.auto_logo.isChecked()
        }

        # Get portal type
        portal_type = "auto"
        if self.portal_type.currentIndex() > 0:
            portal_type = self.portal_type.currentText().lower()

        # Show progress elements
        self.progress_bar.setVisible(True)
        self.status_text.setVisible(True)
        self.convert_btn.setEnabled(False)
        self.cancel_btn.setVisible(True)
        self.save_btn.setEnabled(False)

        # Clear previous status
        self.status_text.clear()
        self.progress_bar.setValue(0)

        # Create and start converter thread
        self.converter_thread = PortalConverterThread(
            portal_url, mac_address, portal_type, options
        )

        self.converter_thread.progress.connect(self.update_progress)
        self.converter_thread.status.connect(self.update_status)
        self.converter_thread.finished.connect(self.conversion_finished)
        self.converter_thread.error.connect(self.conversion_error)

        self.converter_thread.start()

    def cancel_conversion(self):
        """ביטול ההמרה"""
        if self.converter_thread and self.converter_thread.isRunning():
            self.converter_thread.cancel()
            self.converter_thread.wait(3000)  # Wait max 3 seconds

            self.update_status("❌ Conversion cancelled")
            self.reset_ui()

    def update_progress(self, value: int):
        """עדכון progress bar"""
        self.progress_bar.setValue(value)

    def update_status(self, message: str):
        """עדכון הודעת סטטוס"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")

        # Auto scroll to bottom
        scrollbar = self.status_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def conversion_finished(self, m3u_content: str):
        """סיום המרה מוצלח"""
        self.m3u_content = m3u_content
        self.update_status("🎉 Conversion completed successfully!")

        # Enable save button
        self.save_btn.setEnabled(True)

        # Show channel count
        channel_count = m3u_content.count('#EXTINF:')
        self.update_status(f"📺 Total channels in playlist: {channel_count}")

        self.reset_ui()

        # Ask if user wants to load into editor
        reply = QMessageBox.question(
            self, "Conversion Complete",
            f"Successfully converted portal to M3U with {channel_count} channels.\n\n"
            "Would you like to load this playlist into the M3U Editor?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes and hasattr(self.parent(), 'loadM3UFromText'):
            self.parent().loadM3UFromText(self.m3u_content)
            self.close()

    def conversion_error(self, error_message: str):
        """שגיאה בהמרה"""
        self.update_status(error_message)
        self.reset_ui()

        QMessageBox.critical(self, "Conversion Failed",
                           f"Failed to convert portal:\n\n{error_message}")

    def reset_ui(self):
        """איפוס ממשק המשתמש"""
        self.convert_btn.setEnabled(True)
        self.cancel_btn.setVisible(False)

    def save_m3u(self):
        """שמירת קובץ M3U"""
        if not self.m3u_content:
            QMessageBox.warning(self, "No Content", "No M3U content to save.")
            return

        from PyQt5.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save M3U Playlist",
            f"portal_playlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.m3u",
            "M3U Files (*.m3u);;All Files (*)"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.m3u_content)

                QMessageBox.information(self, "Success", f"M3U playlist saved successfully!\n\n{filename}")

                # Open file location
                import os
                import subprocess
                try:
                    subprocess.Popen(f'explorer /select,"{filename}"')
                except:
                    pass

            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save file:\n{str(e)}")


# פונקציה להוספה למודול הראשי
def show_portal_converter(parent=None):
    """הצגת חלון המרת Portal"""
    dialog = AdvancedPortalConverter(parent)
    dialog.exec_()


# פונקציה לשילוב ישיר בm3u_EditorV3.py
def convert_portal_to_m3u(portal_url: str, mac_address: str, portal_type: str = "auto") -> str:
    """המרת Portal ל-M3U באופן ישיר (ללא GUI)"""

    import requests
    from urllib.parse import urljoin

    try:
        # Validate inputs
        if not portal_url or not mac_address:
            raise ValueError("Portal URL and MAC address are required")

        # Detect portal type
        if portal_type == "auto":
            portal_type = PortalManager.detect_portal_type(portal_url)

        # Get portal config
        portal_config = PortalManager.KNOWN_PORTALS.get(
            portal_type,
            PortalManager.KNOWN_PORTALS["stalker"]
        )

        # Normalize URL
        if not portal_url.startswith(('http://', 'https://')):
            portal_url = 'http://' + portal_url
        base_url = portal_url.rstrip('/')

        api_url = base_url + portal_config["api_path"]

        # Setup session
        session = requests.Session()
        headers = portal_config["headers"].copy()
        headers["Referer"] = base_url + portal_config["referer_path"]

        # Try MAC variations
        mac_variations = PortalManager.generate_mac_variations(mac_address)
        token = None
        successful_mac = None

        for mac in mac_variations:
            try:
                # Handshake
                hs_params = {
                    "type": "stb",
                    "action": "handshake",
                    "token": "",
                    "mac": mac
                }

                response = session.get(api_url, params=hs_params, headers=headers, timeout=15)

                if response.status_code == 200:
                    data = response.json()
                    token = data.get("js", {}).get("token") or data.get("token")

                    if token:
                        successful_mac = mac
                        break

            except:
                continue

        if not token:
            raise Exception("Failed to authenticate with portal")

        # Login
        login_params = {
            "type": "stb",
            "action": "login",
            "device_id": successful_mac,
            "device_id2": successful_mac,
            "mac": successful_mac
        }

        session.get(api_url, params=login_params, headers=headers, timeout=15)

        # Get channels
        channels_params = {"type": "itv", "action": "get_all_channels"}
        ch_response = session.get(api_url, params=channels_params, headers=headers, timeout=30)

        if ch_response.status_code != 200:
            raise Exception("Failed to fetch channels")

        channels_data = ch_response.json()
        channels = (channels_data.get("js") or {}).get("data", [])

        if not channels:
            raise Exception("No channels found")

        # Build M3U
        m3u_lines = ["#EXTM3U"]
        m3u_lines.append(f"# Portal: {base_url}")
        m3u_lines.append(f"# MAC: {successful_mac}")
        m3u_lines.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        m3u_lines.append("")

        for channel in channels:
            name = channel.get("name", "Unknown").strip()
            logo = channel.get("logo", "")
            tvg_id = str(channel.get("id", ""))
            cmd = channel.get("cmd", "").strip()

            if cmd and name:
                extinf = f'#EXTINF:-1 tvg-id="{tvg_id}"'
                if logo:
                    extinf += f' tvg-logo="{logo}"'
                extinf += f',{name}'

                m3u_lines.append(extinf)
                m3u_lines.append(cmd)

        return "\n".join(m3u_lines)

    except Exception as e:
        raise Exception(f"Portal conversion failed: {str(e)}")


if __name__ == "__main__":
    # Test the converter
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    converter = AdvancedPortalConverter()
    converter.show()
    sys.exit(app.exec_())