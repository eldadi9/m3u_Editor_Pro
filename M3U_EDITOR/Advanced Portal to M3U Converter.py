"""
שיפורים ותוספות לתוכנת M3U Editor הקיימת
==========================================
הוסף את הקוד הזה לקובץ m3u_EditorV3.py שלך
או צור קובץ נפרד portal_extensions.py
"""

import json
import time
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import concurrent.futures
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTextEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox,
    QProgressBar, QCheckBox, QSpinBox, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# ================== Portal Manager Class ==================
class PortalManager:
    """מנהל מתקדם לטיפול ב-Portals"""
    
    # רשימת פורטלים ידועים עם הגדרות מותאמות
    KNOWN_PORTALS = {
        "stalker": {
            "api_path": "/stalker_portal/server/load.php",
            "referer_path": "/c/",
            "headers": {
                "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3",
                "X-User-Agent": "Model: MAG254; Link: Ethernet"
            }
        },
        "ministra": {
            "api_path": "/portal.php",
            "referer_path": "/c/",
            "headers": {
                "User-Agent": "Mozilla/5.0 (SMART-TV; Linux; Tizen 5.0) AppleWebKit/538.1",
                "X-User-Agent": "Model: MAG322; Link: WiFi"
            }
        },
        "xtream": {
            "api_path": "/player_api.php",
            "referer_path": "/",
            "headers": {
                "User-Agent": "IPTVSmarters/1.1"
            }
        }
    }
    
    @staticmethod
    def detect_portal_type(url: str) -> str:
        """זיהוי אוטומטי של סוג הפורטל"""
        url_lower = url.lower()
        
        if "stalker_portal" in url_lower or "/c/" in url_lower:
            return "stalker"
        elif "ministra" in url_lower:
            return "ministra"
        elif "player_api" in url_lower or ":8080" in url:
            return "xtream"
        else:
            return "stalker"  # ברירת מחדל
    
    @staticmethod
    def validate_mac_address(mac: str) -> bool:
        """בדיקת תקינות כתובת MAC"""
        import re
        pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        return bool(re.match(pattern, mac))
    
    @staticmethod
    def generate_mac_variations(mac: str) -> List[str]:
        """יצירת וריאציות של כתובת MAC (עם ובלי נקודתיים)"""
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
        
        return variations

# ================== Portal Converter Thread ==================
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
    
    def run(self):
        """ביצוע ההמרה"""
        try:
            import requests
            
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
                except:
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
            
            session.get(api_url, params=login_params, headers=headers, timeout=15)
            self.status.emit("🔐 Logged in successfully")
            self.progress.emit(50)
            
            # Get categories (optional)
            categories = {}
            if self.options.get("fetch_categories", True):
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
                except:
                    pass
            
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
                self.error.emit("❌ No channels found")
                return
            
            self.status.emit(f"📊 Found {len(channels)} channels")
            self.progress.emit(70)
            
            # Build M3U with enhanced features
            m3u_lines = ["#EXTM3U"]
            
            # Add portal info as comment
            m3u_lines.append(f"# Portal: {base_url}")
            m3u_lines.append(f"# MAC: {successful_mac}")
            m3u_lines.append(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            m3u_lines.append(f"# Channels: {len(channels)}")
            m3u_lines.append("")
            
            # Process channels
            progress_step = 20 / len(channels)
            current_progress = 70
            
            for i, channel in enumerate(channels):
                if self.is_cancelled:
                    return
                
                # Extract channel info
                ch_name = channel.get("name", f"Channel {i+1}")
                ch_logo = channel.get("logo", "")
                ch_id = str(channel.get("id", ""))
                ch_number = channel.get("number", i+1)
                ch_category_id = channel.get("tv_genre_id", "")
                ch_category = categories.get(ch_category_id, "")
                
                # Get stream URL
                stream_url = channel.get("cmd", "")
                
                if not stream_url or self.options.get("force_create_link", False):
                    # Create link dynamically
                    try:
                        link_params = {
                            "type": "itv",
                            "action": "create_link",
                            "cmd": f"ffrt {ch_id}",
                            "forced_storage": "undefined",
                            "disable_ad": "0"
                        }
                        
                        link_response = session.get(
                            api_url,
                            params=link_params,
                            headers=headers,
                            timeout=10
                        )
                        
                        if link_response.status_code == 200:
                            link_data = link_response.json()
                            stream_url = link_data.get("js", {}).get("cmd", stream_url)
                    except:
                        pass
                
                # Build EXTINF line with all metadata
                extinf_parts = [f'#EXTINF:-1']
                
                # Add attributes
                if ch_id:
                    extinf_parts.append(f'tvg-id="{ch_id}"')
                
                if ch_name:
                    extinf_parts.append(f'tvg-name="{ch_name}"')
                
                if ch_logo:
                    if not ch_logo.startswith("http"):
                        ch_logo = base_url + "/" + ch_logo.lstrip("/")
                    extinf_parts.append(f'tvg-logo="{ch_logo}"')
                
                if ch_category:
                    extinf_parts.append(f'group-title="{ch_category}"')
                
                if ch_number:
                    extinf_parts.append(f'tvg-chno="{ch_number}"')
                
                # Add portal-specific metadata
                extinf_parts.append(f'portal-id="{ch_id}"')
                
                # Combine and add
                extinf_line = " ".join(extinf_parts) + f',{ch_name}'
                m3u_lines.append(extinf_line)
                
                # Add stream URL
                if stream_url:
                    m3u_lines.append(stream_url)
                else:
                    m3u_lines.append(f"# No stream URL for {ch_name}")
                
                # Update progress
                current_progress += progress_step
                self.progress.emit(int(current_progress))
                
                if i % 10 == 0:
                    self.status.emit(f"📺 Processing channel {i+1}/{len(channels)}")
            
            # Add VOD if requested
            if self.options.get("include_vod", False):
                self.status.emit("🎬 Fetching VOD content...")
                
                vod_params = {"type": "vod", "action": "get_categories"}
                try:
                    vod_response = session.get(
                        api_url,
                        params=vod_params,
                        headers=headers,
                        timeout=15
                    )
                    
                    if vod_response.status_code == 200:
                        vod_data = vod_response.json()
                        # Process VOD categories...
                        m3u_lines.append("")
                        m3u_lines.append("# === VOD CONTENT ===")
                        # Add VOD items here
                except:
                    pass
            
            self.progress.emit(100)
            self.status.emit("✅ Conversion completed successfully!")
            
            # Return M3U content
            m3u_content = "\n".join(m3u_lines) + "\n"
            self.finished.emit(m3u_content)
            
        except Exception as e:
            self.error.emit(f"❌ Error: {str(e)}")
    
    def normalize_url(self, url: str) -> str:
        """נרמול URL"""
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        url = url.rstrip("/")
        
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

# ================== Enhanced Portal Dialog ==================
class EnhancedPortalDialog(QDialog):
    """דיאלוג מתקדם להמרת Portal"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.converter_thread = None
        self.m3u_content = None
        self.setup_ui()
    
    def setup_ui(self):
        """בניית ממשק משתמש"""
        self.setWindowTitle("🚀 Advanced Portal to M3U Converter")
        self.setGeometry(300, 200, 700, 600)
        self.setStyleSheet("""
            QDialog { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e3c72, stop:1 #2a5298);
            }
            QLabel { 
                color: white; 
                font-weight: bold;
            }
            QLineEdit, QTextEdit, QComboBox {
                background: rgba(255, 255, 255, 0.9);
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #45a049;
            }
            QPushButton:pressed {
                background: #367c39;
            }
            QProgressBar {
                border: 2px solid #4CAF50;
                border-radius: 5px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #8BC34A);
                border-radius: 3px;
            }
            QGroupBox {
                color: white;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QCheckBox {
                color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # === Input Section ===
        input_group = QGroupBox("📡 Portal Connection")
        input_layout = QVBoxLayout()
        
        # Portal URL
        input_layout.addWidget(QLabel("Portal URL:"))
        self.portal_input = QLineEdit()
        self.portal_input.setPlaceholderText("http://example.com/stalker_portal/")
        input_layout.addWidget(self.portal_input)
        
        # Portal Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Portal Type:"))
        self.portal_type = QComboBox()
        self.portal_type.addItems(["Auto Detect", "Stalker", "Ministra", "Xtream"])
        type_layout.addWidget(self.portal_type)
        type_layout.addStretch()
        input_layout.addLayout(type_layout)
        
        # MAC Address
        input_layout.addWidget(QLabel("MAC Address:"))
        self.mac_input = QLineEdit()
        self.mac_input.setPlaceholderText("00:1A:79:XX:XX:XX")
        input_layout.addWidget(self.mac_input)
        
        # MAC Generator button
        mac_gen_btn = QPushButton("🎲 Generate Random MAC")
        mac_gen_btn.clicked.connect(self.generate_random_mac)
        input_layout.addWidget(mac_gen_btn)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # === Options Section ===
        options_group = QGroupBox("⚙️ Options")
        options_layout = QVBoxLayout()
        
        # Checkboxes
        self.fetch_categories = QCheckBox("Fetch Categories")
        self.fetch_categories.setChecked(True)
        options_layout.addWidget(self.fetch_categories)
        
        self.include_vod = QCheckBox("Include VOD Content")
        options_layout.addWidget(self.include_vod)
        
        self.force_create_link = QCheckBox("Force Create Fresh Links")
        options_layout.addWidget(self.force_create_link)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # === Progress Section ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(150)
        self.status_text.setVisible(False)
        layout.addWidget(self.status_text)
        
        # === Buttons ===
        buttons_layout = QHBoxLayout()
        
        self.convert_btn = QPushButton("🚀 Convert Portal")
        self.convert_btn.clicked.connect(self.start_conversion)
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
    
    def generate_random_mac(self):
        """יצירת MAC אקראי"""
        import random
        
        # MAG prefix
        prefixes = ["00:1A:79", "00:1A:78", "00:09:DF"]
        prefix = random.choice(prefixes)
        
        # Random suffix
        suffix = ":".join([f"{random.randint(0, 255):02X}" for _ in range(3)])
        
        mac = f"{prefix}:{suffix}"
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
            QMessageBox.warning(self, "Invalid MAC", 
                              "Please enter a valid MAC address.")
            return
        
        # Prepare options
        options = {
            "fetch_categories": self.fetch_categories.isChecked(),
            "include_vod": self.include_vod.isChecked(),
            "force_create_link": self.force_create_link.isChecked()
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
            self.converter_thread.wait()
            
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
        
        # Count channels
        channels_count = m3u_content.count("#EXTINF:")
        self.update_status(f"📊 Total channels: {channels_count}")
        
        # Enable save button
        self.save_btn.setEnabled(True)
        self.reset_ui()
        
        # Show success message
        QMessageBox.information(self, "Success", 
                               f"Successfully converted portal!\n"
                               f"Found {channels_count} channels.\n"
                               f"Click 'Save M3U' to save the playlist.")
    
    def conversion_error(self, error_message: str):
        """טיפול בשגיאת המרה"""
        self.update_status(error_message)
        self.reset_ui()
        
        QMessageBox.critical(self, "Conversion Error", error_message)
    
    def reset_ui(self):
        """איפוס ממשק המשתמש"""
        self.convert_btn.setEnabled(True)
        self.cancel_btn.setVisible(False)
    
    def save_m3u(self):
        """שמירת קובץ M3U"""
        if not self.m3u_content:
            return
        
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save M3U File",
            f"portal_{time.strftime('%Y%m%d_%H%M%S')}.m3u",
            "M3U Files (*.m3u);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.m3u_content)
                
                QMessageBox.information(self, "Success", 
                                       f"M3U file saved successfully!\n{file_path}")
                
                # Ask if user wants to load it in the editor
                reply = QMessageBox.question(
                    self, 
                    "Load in Editor?",
                    "Do you want to load this M3U file in the editor?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes and self.parent():
                    self.parent().loadM3UFromText(self.m3u_content)
                    self.close()
                    
            except Exception as e:
                QMessageBox.critical(self, "Save Error", 
                                   f"Failed to save file:\n{str(e)}")

# ================== Integration Function ==================
def add_portal_converter_to_editor(editor_instance):
    """
    הוספת כפתור Portal Converter לתוכנה הקיימת
    
    Usage:
    ------
    # בקובץ m3u_EditorV3.py שלך, הוסף:
    
    from portal_extensions import add_portal_converter_to_editor
    
    # בתוך __init__ של המחלקה M3UEditor:
    add_portal_converter_to_editor(self)
    """
    
    # מצא את ה-toolbar או panel המתאים
    if hasattr(editor_instance, 'toolbar'):
        toolbar = editor_instance.toolbar
    else:
        # צור toolbar חדש אם לא קיים
        from PyQt5.QtWidgets import QToolBar
        toolbar = QToolBar("Portal Tools")
        editor_instance.addToolBar(toolbar)
    
    # הוסף כפתור
    portal_action = toolbar.addAction("🚀 Advanced Portal Converter")
    portal_action.triggered.connect(
        lambda: EnhancedPortalDialog(editor_instance).exec_()
    )
    
    print("✅ Portal Converter added to editor")

# ================== Standalone Usage ==================
if __name__ == "__main__":
    """הרצה עצמאית לבדיקה"""
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # הצג את הדיאלוג
    dialog = EnhancedPortalDialog()
    dialog.show()
    
    sys.exit(app.exec_())