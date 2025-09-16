#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ðŸŽ¨ M3U Playlist Editor V3 - ULTRA MODERN EDITION ðŸŽ¨

A revolutionary, beautifully designed M3U IPTV playlist editor with:
âœ¨ Stunning Material Design interface with gradients and glassmorphism
ðŸŽ¯ Advanced tabbed navigation for better organization
ðŸŽ¨ Modern icons and typography
âš¡ Smooth animations and hover effects
ðŸ›¡ï¸ All original functionality preserved and enhanced

Created with â¤ï¸ for the ultimate user experience
Version: 3.0 Modern Edition
"""

import os
import sys
# Add current directory to sys.path for logo.py imports
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
from logo import get_saved_logo
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QTextEdit, QInputDialog, QAbstractItemView, QMenu, QAction, QCompleter,
    QProgressBar, QDialog, QComboBox, QPushButton, QFrame, QTabWidget,
    QMessageBox, QLineEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from m3u_filter_enhanced import M3UFilterEnhanced

# Import all original modules and dependencies


import os
import sys
# Ã—ÂªÃ—Â•Ã—Â¡Ã—Â™Ã—Â£ Ã—ÂÃ—Âª Ã—Â”Ã—ÂªÃ—Â™Ã—Â§Ã—Â™Ã—Â™Ã—Â” Ã—Â”Ã—Â Ã—Â•Ã—Â›Ã—Â—Ã—Â™Ã—Âª Ã—ÂœÃ–Â¾sys.path Ã—Â›Ã—Â“Ã—Â™ Ã—Â©Ã—Â¤Ã—Â™Ã—Â™Ã—ÂªÃ—Â•Ã—ÂŸ Ã—Â™Ã—ÂžÃ—Â¦Ã—Â Ã—ÂÃ—Âª logo.py

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


import os
print("Portal file exists:", os.path.exists("portal_extensions.py"))

try:
    from portal_extensions import AdvancedPortalConverter, convert_portal_to_m3u
    PORTAL_CONVERTER_AVAILABLE = True
except ImportError as e:
    PORTAL_CONVERTER_AVAILABLE = False




import shutil
from datetime import datetime, timedelta
from urllib.parse import urlparse




"""
ðŸŽ¨ Ultra-Modern Material Design Stylesheet for M3U Editor V3
Created with advanced CSS-like styling for PyQt5
"""

def get_modern_stylesheet():
    return """
    /* Main Application Window */
    QWidget {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
        color: #ffffff;
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 12px;
        border-radius: 8px;
    }

    /* Modern Tabbed Interface */
    QTabWidget {
        background: transparent;
        border: none;
    }

    QTabWidget::pane {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255,255,255,0.1), stop:1 rgba(255,255,255,0.05));
        border: 2px solid rgba(255,255,255,0.2);
        border-radius: 12px;
        margin-top: -1px;
        padding: 15px;
    }

    QTabBar::tab {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255,255,255,0.2), stop:1 rgba(255,255,255,0.1));
        color: #ffffff;
        border: 2px solid rgba(255,255,255,0.3);
        border-bottom: none;
        border-radius: 8px 8px 0 0;
        padding: 12px 20px;
        margin-right: 2px;
        font-weight: bold;
        font-size: 13px;
    }

    QTabBar::tab:selected {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4facfe, stop:1 #00f2fe);
        border-color: #00f2fe;
        color: #000000;
    }

    QTabBar::tab:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255,255,255,0.3), stop:1 rgba(255,255,255,0.2));
        transform: translateY(-2px);
    }

    /* Modern Buttons with Stunning Effects */
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        font-size: 13px;
        padding: 10px 20px;
        margin: 3px;
        min-height: 35px;
    }

    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4facfe, stop:1 #00f2fe);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.4);
    }

    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
        transform: translateY(1px);
    }

    /* Primary Action Buttons */
    QPushButton[class="primary"] {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #11998e, stop:1 #38ef7d);
        font-size: 14px;
        min-height: 40px;
    }

    QPushButton[class="primary"]:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #06d6a0, stop:1 #54e346);
        box-shadow: 0 10px 30px rgba(17, 153, 142, 0.4);
    }

    /* Warning/Delete Buttons */
    QPushButton[class="danger"] {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff6b6b, stop:1 #ee5a24);
    }

    QPushButton[class="danger"]:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff5252, stop:1 #ff1744);
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
    }

    /* List Widgets with Modern Glass Effect */
    QListWidget {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 10px;
        alternate-background-color: rgba(255, 255, 255, 0.05);
        selection-background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 #4facfe, stop:1 #00f2fe);
        font-size: 13px;
    }

    QListWidget::item {
        background: transparent;
        border: none;
        border-radius: 6px;
        padding: 8px;
        margin: 2px;
    }

    QListWidget::item:selected {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(79, 172, 254, 0.8), stop:1 rgba(0, 242, 254, 0.8));
        color: #000000;
        font-weight: bold;
    }

    QListWidget::item:hover {
        background: rgba(255, 255, 255, 0.2);
    }

    /* Text Editing Areas */
    QTextEdit, QLineEdit {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        padding: 10px;
        color: #ffffff;
        font-size: 13px;
        selection-background-color: #4facfe;
    }

    QTextEdit:focus, QLineEdit:focus {
        border-color: #4facfe;
        box-shadow: 0 0 15px rgba(79, 172, 254, 0.3);
    }

    /* Combo Boxes */
    QComboBox {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        padding: 8px 15px;
        color: #ffffff;
        font-size: 13px;
        min-height: 30px;
    }

    QComboBox:hover {
        border-color: #4facfe;
        background: rgba(255, 255, 255, 0.2);
    }

    QComboBox::drop-down {
        border: none;
        width: 30px;
    }

    QComboBox::down-arrow {
        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQgNkw4IDEwTDEyIDYiIHN0cm9rZT0iI2ZmZmZmZiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
        width: 16px;
        height: 16px;
    }

    /* Table Widgets */
    QTableWidget {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        gridline-color: rgba(255, 255, 255, 0.1);
        selection-background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 #4facfe, stop:1 #00f2fe);
        alternate-background-color: rgba(255, 255, 255, 0.02);
    }

    QHeaderView::section {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
        color: white;
        border: none;
        padding: 10px;
        font-weight: bold;
        font-size: 13px;
    }

    /* Progress Bars */
    QProgressBar {
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.1);
        text-align: center;
        font-weight: bold;
        color: #ffffff;
        min-height: 20px;
    }

    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #11998e, stop:1 #38ef7d);
        border-radius: 6px;
    }

    /* Labels */
    QLabel {
        color: #ffffff;
        font-size: 13px;
        background: transparent;
    }

    QLabel[class="title"] {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(79, 172, 254, 0.3), stop:1 rgba(0, 242, 254, 0.3));
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
    }

    QLabel[class="section"] {
        font-size: 16px;
        font-weight: bold;
        color: #4facfe;
        margin: 8px 0 4px 0;
    }

    /* Scroll Bars */
    QScrollBar:vertical {
        background: rgba(255, 255, 255, 0.1);
        width: 12px;
        border-radius: 6px;
        margin: 0;
    }

    QScrollBar::handle:vertical {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
        border-radius: 6px;
        min-height: 30px;
    }

    QScrollBar::handle:vertical:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4facfe, stop:1 #00f2fe);
    }

    /* Dialog Specific Styling */
    QDialog {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
        border: 3px solid rgba(79, 172, 254, 0.5);
        border-radius: 15px;
    }

    /* Frame Styling */
    QFrame {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
    }
    """



def create_icon_button(text, icon="", button_class="default", tooltip=""):
    """Create a modern styled button with icon and advanced effects"""
    from PyQt5.QtWidgets import QPushButton
    from PyQt5.QtCore import Qt

    # Combine icon with text
    display_text = f"{icon} {text}" if icon else text
    button = QPushButton(display_text)

    # Set button class for styling
    if button_class == "primary":
        button.setProperty("class", "primary")
    elif button_class == "danger":
        button.setProperty("class", "danger")

    # Add tooltip
    if tooltip:
        button.setToolTip(tooltip)

    # Set minimum size for better appearance
    button.setMinimumHeight(40)

    return button

def create_section_label(text, icon=""):
    """Create a styled section header label"""
    from PyQt5.QtWidgets import QLabel

    display_text = f"{icon} {text}" if icon else text
    label = QLabel(display_text)
    label.setProperty("class", "section")
    return label

def create_title_label(text, icon=""):
    """Create a main title label"""
    from PyQt5.QtWidgets import QLabel

    display_text = f"{icon} {text}" if icon else text
    label = QLabel(display_text)
    label.setProperty("class", "title")
    return label


# Modern Icon Mapping
ICON_MAP = {'Load M3U': 'ðŸ“', 'Save M3U': 'ðŸ’¾', 'Merge M3Us': 'ðŸ”„', 'Export to Telegram': 'ðŸ“¤', 'Add Category': 'âž•', 'Edit Category Name': 'âœï¸', 'Delete Selected': 'ðŸ—‘ï¸', 'Move Category Up': 'â¬†ï¸', 'Move Category Down': 'â¬‡ï¸', 'Select All': 'â˜‘ï¸', 'Deselect All': 'â˜', 'ðŸŒ Auto Translate': 'ðŸŒ', 'Add Channel': 'ðŸ“º', 'Move Up': 'â¬†ï¸', 'Move Down': 'â¬‡ï¸', 'Move Selected': 'ðŸ“‹', 'Edit Selected': 'âœï¸', 'Check Duplicate': 'ðŸ”', 'ðŸ”€ Smart M3U Loader': 'ðŸ”€', 'ðŸ” Xtream Converter': 'ðŸ”', 'ðŸŒ Advanced Portal Converter': 'ðŸŒ', 'ðŸ“¤ Export Groups': 'ðŸ“¤', 'ðŸŽ¯ Filtered Export': 'ðŸŽ¯', 'ðŸ” Smart Scan': 'ðŸ”', 'ðŸ“º Fix EPG': 'ðŸ“º', 'â–¶ × ×’×Ÿ ×‘Ö¾VLC': 'â–¶ï¸', 'â–¶ ×¦×¤×” ×‘×¢×¨×•×¦×™×': 'ðŸ‘ï¸', 'ðŸŒ ×ª×¨×’× ×¢×¨×•×¦×™×': 'ðŸŒ', 'âœ” OK': 'âœ…', 'âœ– ×‘×™×˜×•×œ': 'âŒ', 'Copy Result': 'ðŸ“‹', 'Download M3U': 'â¬‡ï¸', 'Convert to M3U URL': 'ðŸ”„', 'Export Selected Groups': 'ðŸ“¤', 'Export All Groups': 'ðŸ“¦', 'Check URLs': 'ðŸ”—', 'Stop Checking': 'â¹ï¸', 'Select Offline Channels': 'ðŸ“¡', 'Stop Scan': 'â¹ï¸', 'Mark Channels': 'ðŸ·ï¸', 'Search': 'ðŸ”', 'Reset': 'ðŸ”„', 'Filter': 'ðŸŽ›ï¸', 'Settings': 'âš™ï¸', 'Help': 'â“', 'Info': 'â„¹ï¸'}

def get_icon(text):
    """Get the appropriate icon for a button text"""
    return ICON_MAP.get(text, "")


def create_modern_tabbed_interface(self):
    """Create a beautiful tabbed interface to replace the long scrolling layout"""
    from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QHBoxLayout
    from PyQt5.QtCore import Qt

    # Main tab widget
    tab_widget = QTabWidget()

    # === TAB 1: File & Categories ===
    file_categories_tab = QWidget()
    file_categories_layout = QVBoxLayout(file_categories_tab)

    # File operations section
    file_section_label = create_section_label("File Operations", "ðŸ“")
    file_categories_layout.addWidget(file_section_label)

    # File buttons in a nice grid
    file_buttons_layout = QHBoxLayout()

    load_btn = create_icon_button("Load M3U", "ðŸ“", "primary", "Load M3U playlist file")
    save_btn = create_icon_button("Save M3U", "ðŸ’¾", "primary", "Save current playlist")
    merge_btn = create_icon_button("Merge M3Us", "ðŸ”„", "default", "Merge multiple playlists")

    file_buttons_layout.addWidget(load_btn)
    file_buttons_layout.addWidget(save_btn)
    file_buttons_layout.addWidget(merge_btn)
    file_categories_layout.addLayout(file_buttons_layout)

    # Category management
    category_section_label = create_section_label("Category Management", "ðŸ“‚")
    file_categories_layout.addWidget(category_section_label)

    # Add category list and controls here
    # (This will be expanded with the actual category widgets)

    tab_widget.addTab(file_categories_tab, "ðŸ“ Files & Categories")

    # === TAB 2: Channels ===
    channels_tab = QWidget()
    channels_layout = QVBoxLayout(channels_tab)

    channels_section_label = create_section_label("Channel Management", "ðŸ“º")
    channels_layout.addWidget(channels_section_label)

    # Channel buttons
    channel_buttons_layout = QHBoxLayout()

    add_channel_btn = create_icon_button("Add Channel", "ðŸ“º", "primary")
    edit_channel_btn = create_icon_button("Edit Selected", "âœï¸")
    delete_channel_btn = create_icon_button("Delete Selected", "ðŸ—‘ï¸", "danger")

    channel_buttons_layout.addWidget(add_channel_btn)
    channel_buttons_layout.addWidget(edit_channel_btn)
    channel_buttons_layout.addWidget(delete_channel_btn)
    channels_layout.addLayout(channel_buttons_layout)

    tab_widget.addTab(channels_tab, "ðŸ“º Channels")

    # === TAB 3: Tools & Export ===
    tools_tab = QWidget()
    tools_layout = QVBoxLayout(tools_tab)

    tools_section_label = create_section_label("Advanced Tools", "ðŸ› ï¸")
    tools_layout.addWidget(tools_section_label)

    # Tools in a grid layout
    tools_grid_1 = QHBoxLayout()

    smart_loader_btn = create_icon_button("Smart M3U Loader", "ðŸ”€", "primary")
    xtream_converter_btn = create_icon_button("Xtream Converter", "ðŸ”")
    portal_converter_btn = create_icon_button("Portal Converter", "ðŸŒ")

    tools_grid_1.addWidget(smart_loader_btn)
    tools_grid_1.addWidget(xtream_converter_btn)
    tools_grid_1.addWidget(portal_converter_btn)
    tools_layout.addLayout(tools_grid_1)

    tools_grid_2 = QHBoxLayout()

    export_groups_btn = create_icon_button("Export Groups", "ðŸ“¤")
    smart_scan_btn = create_icon_button("Smart Scan", "ðŸ”")
    fix_epg_btn = create_icon_button("Fix EPG", "ðŸ“º")

    tools_grid_2.addWidget(export_groups_btn)
    tools_grid_2.addWidget(smart_scan_btn)
    tools_grid_2.addWidget(fix_epg_btn)
    tools_layout.addLayout(tools_grid_2)

    tab_widget.addTab(tools_tab, "ðŸ› ï¸ Tools & Export")

    # === TAB 4: M3U Content ===
    content_tab = QWidget()
    content_layout = QVBoxLayout(content_tab)

    content_section_label = create_section_label("M3U Content Editor", "ðŸ“")
    content_layout.addWidget(content_section_label)

    # Text editor will be added here

    tab_widget.addTab(content_tab, "ðŸ“ M3U Content")

    # === TAB 5: Settings & VLC ===
    settings_tab = QWidget()
    settings_layout = QVBoxLayout(settings_tab)

    settings_section_label = create_section_label("Settings & Media Player", "âš™ï¸")
    settings_layout.addWidget(settings_section_label)

    # VLC controls
    vlc_section_label = create_section_label("VLC Integration", "â–¶ï¸")
    settings_layout.addWidget(vlc_section_label)

    vlc_buttons_layout = QHBoxLayout()

    vlc_play_btn = create_icon_button("Play in VLC", "â–¶ï¸", "primary")
    vlc_preview_btn = create_icon_button("Preview Channels", "ðŸ‘ï¸")
    translate_btn = create_icon_button("Translate Channels", "ðŸŒ")

    vlc_buttons_layout.addWidget(vlc_play_btn)
    vlc_buttons_layout.addWidget(vlc_preview_btn)
    vlc_buttons_layout.addWidget(translate_btn)
    settings_layout.addLayout(vlc_buttons_layout)

    tab_widget.addTab(settings_tab, "âš™ï¸ Settings & VLC")

    return tab_widget


# Modern Animation Effects (placeholder for future enhancement)
def add_hover_animation(widget):
    """Add hover animation effects to widgets"""
    # This can be expanded with QPropertyAnimation in the future
    pass

def apply_glassmorphism_effect(widget):
    """Apply glassmorphism visual effects"""
    # Future enhancement for advanced visual effects
    pass


# ============================================================================
# ORIGINAL UTILITY FUNCTIONS (Preserved)
# ============================================================================

def create_channel_widget(name: str, quality: str) -> QWidget:
    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(5, 2, 5, 2)

    # 1. Ã—Â”Ã—Â©Ã—Â
    lbl = QLabel(name)
    h.addWidget(lbl)

    # 2. Ã—ÂªÃ—Â•Ã—Â•Ã—Â™Ã—Âª Ã—Â”Ã—ÂÃ—Â™Ã—Â›Ã—Â•Ã—Âª Ã—ÂžÃ—Â™Ã—Â“ Ã—ÂÃ—Â—Ã—Â¨Ã—Â™ Ã—Â”Ã—Â©Ã—Â
    qlbl = QLabel(quality)
    styles = {
        '4K':      'background-color:#66cc66; color:black; padding:2px; border-radius:3px;',
        'FHD':     'background-color:#99ccff; color:black; padding:2px; border-radius:3px;',
        'HD':      'background-color:#ffff66; color:black; padding:2px; border-radius:3px;',
        'SD':      'background-color:#ff6666; color:white; padding:2px; border-radius:3px;',
        'Unknown': 'background-color:#999999; color:white; padding:2px; border-radius:3px;'
    }
    qlbl.setStyleSheet(styles.get(quality, styles['Unknown']))
    h.addWidget(qlbl)

    # 3. Ã—ÂÃ—Â Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â©Ã—Â”Ã—Â©Ã—Â•Ã—Â¨Ã—Â” Ã—ÂªÃ—ÂªÃ—ÂžÃ—Â¨Ã—Â— Ã—ÂÃ—Â—Ã—Â¨Ã—Â™ Ã—Â”Ã—ÂªÃ—Â•Ã—Â•Ã—Â™Ã—Âª:
    h.addStretch()

    return w


# ============================================================================
# ALL ORIGINAL DIALOG CLASSES (Preserved with enhanced styling)
# ============================================================================

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

            # Ã—Â”Ã—ÂªÃ—Â™Ã—Â§Ã—Â•Ã—ÂŸ: Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Â” Ã—ÂÃ—Â Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â”Ã—ÂžÃ—ÂªÃ—Â•Ã—Â¨Ã—Â’Ã—ÂžÃ—Âª Ã—Â›Ã—Â‘Ã—Â¨ Ã—Â§Ã—Â™Ã—Â™Ã—ÂžÃ—Âª
            if final_base in updated_categories:
                # Ã—ÂÃ—Â Ã—Â›Ã—Â‘Ã—Â¨ Ã—Â§Ã—Â™Ã—Â™Ã—ÂžÃ—Âª - Ã—Â”Ã—Â•Ã—Â¡Ã—Â£ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂœÃ—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â”Ã—Â§Ã—Â™Ã—Â™Ã—ÂžÃ—Âª
                updated_categories[final_base].extend(channels)
            else:
                # Ã—ÂÃ—Â Ã—ÂœÃ—Â Ã—Â§Ã—Â™Ã—Â™Ã—ÂžÃ—Âª - Ã—Â¦Ã—Â•Ã—Â¨ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â—Ã—Â“Ã—Â©Ã—Â”
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
        return all(ord(c)<128 for c in txt if c.isalpha())

    def run(self):
        # Ã—ÂÃ—Â•Ã—Â¡Ã—Â¤Ã—Â™Ã—Â Ã—ÂÃ—Âª Ã—Â›Ã—Âœ Ã—Â”Ã—Â©Ã—ÂžÃ—Â•Ã—Âª Ã—Â©Ã—Â¦Ã—Â¨Ã—Â™Ã—Âš Ã—ÂœÃ—ÂªÃ—Â¨Ã—Â’Ã—Â
        to_translate = set()
        for lst in self.categories.values():
            for entry in lst:
                name = entry.split(" (")[0].strip()
                if name and not self._is_english(name):
                    to_translate.add(name)

        # Ã—ÂžÃ—Â¡Ã—Â™Ã—Â¨Ã—Â™Ã—Â Ã—ÂžÃ—Â”-cache
        todo = [n for n in to_translate if n not in ChannelTranslateThread._cache]
        for i in range(0, len(todo), 50):
            chunk = todo[i:i+50]
            try:
                results = self.trans.translate_batch(chunk)
                for orig, tr in zip(chunk, results):
                    ChannelTranslateThread._cache[orig] = tr
            except:
                for orig in chunk:
                    ChannelTranslateThread._cache[orig] = orig

        # Ã—Â›Ã—Â¢Ã—Âª Ã—ÂžÃ—Â™Ã—Â™Ã—Â©Ã—ÂžÃ—Â™Ã—Â Ã—ÂÃ—Âª Ã—Â”Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â
        new_cats = {}
        mapping = {}
        count = 0
        total = sum(len(v) for v in self.categories.values())

        for cat, lst in self.categories.items():
            new_list = []
            for entry in lst:
                if "(" in entry and entry.endswith(")"):
                    name, rest = entry.split(" (",1)
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

        label1 = QLabel("Ã—Â‘Ã—Â—Ã—Â¨ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â§Ã—Â™Ã—Â™Ã—ÂžÃ—Âª Ã—ÂœÃ—Â”Ã—Â¢Ã—Â‘Ã—Â¨Ã—Â”:")
        self.categoryCombo = QComboBox()
        self.categoryCombo.addItems(self.categories)

        label2 = QLabel("Ã—ÂÃ—Â• Ã—Â”Ã—Â–Ã—ÂŸ Ã—Â©Ã—Â Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â—Ã—Â“Ã—Â©Ã—Â”:")
        self.newCategoryInput = QLineEdit()
        self.newCategoryInput.setPlaceholderText("Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â—Ã—Â“Ã—Â©Ã—Â”...")

        layout.addWidget(label1)
        layout.addWidget(self.categoryCombo)
        layout.addWidget(label2)
        layout.addWidget(self.newCategoryInput)

        buttonBox = QHBoxLayout()
        self.okButton = QPushButton("Ã¢ÂœÂ” OK")
        self.cancelButton = QPushButton("Ã¢ÂœÂ– Ã—Â‘Ã—Â™Ã—Â˜Ã—Â•Ã—Âœ")
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
                f"Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” '{new_name}' Ã—Â›Ã—Â‘Ã—Â¨ Ã—Â§Ã—Â™Ã—Â™Ã—ÂžÃ—Âª. Ã—Â‘Ã—Â—Ã—Â¨ Ã—Â©Ã—Â Ã—ÂÃ—Â—Ã—Â¨ Ã—ÂÃ—Â• Ã—Â”Ã—Â©Ã—ÂªÃ—ÂžÃ—Â© Ã—Â‘Ã—Â§Ã—Â™Ã—Â™Ã—ÂžÃ—Âª.",
            )
            return  # Ã—ÂÃ—Âœ Ã—ÂªÃ—Â¡Ã—Â’Ã—Â•Ã—Â¨ Ã—ÂÃ—Âª Ã—Â”Ã—Â—Ã—ÂœÃ—Â•Ã—ÂŸ
        self.accept()



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
                    extinf_line = self.parent.extinf_lookup.get(channel) or ""
                    if not extinf_line:
                        name = channel.split(" (")[0].strip()
                        extinf_line = f'#EXTINF:-1 group-title="{category}",{name}'
                    elif 'group-title="' not in extinf_line:
                        props, name = extinf_line.split(",", 1)
                        extinf_line = f'{props} group-title="{category}",{name}'

                    url = self.parent.getUrl(channel)
                    file.write(f"{extinf_line}\n{url}\n")

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

        # Ã¢ÂÂ© Ã—ÂžÃ—Â¢Ã—Â‘Ã—Â¨ Ã—ÂÃ—Â•Ã—Â˜Ã—Â•Ã—ÂžÃ—Â˜Ã—Â™ Ã—ÂœÃ—Â©Ã—Â“Ã—Â” Ã—Â”Ã—Â‘Ã—Â Ã—Â‘Ã—ÂœÃ—Â—Ã—Â™Ã—Â¦Ã—Â” Ã—Â¢Ã—Âœ Enter
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
            QMessageBox.warning(self, "Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â”", "Ã—Â Ã—Â Ã—ÂœÃ—ÂžÃ—ÂœÃ—Â Host, Username Ã—Â•-Password")
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
                # Ã¢Â†Â Ã—Â”Ã—Â—Ã—ÂœÃ—Â¤Ã—Â Ã—Â• Ã—ÂÃ—Âª Ã—Â”Ã—Â¡Ã—Â“Ã—Â¨: Ã—Â§Ã—Â•Ã—Â“Ã—Â m3u_plus
                for t in ("m3u_plus", "m3u"):
                    url = f"{scheme}://{netloc}/get.php?username={username}&password={password}&type={t}"
                    try:
                        resp = session.get(url, timeout=5, allow_redirects=True)
                        print(f"Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Â”: {url} Ã¢Â†Â’ {resp.status_code}")
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
            QMessageBox.critical(self, "Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â”", "Ã—ÂœÃ—Â Ã—Â Ã—ÂžÃ—Â¦Ã—Â URL Ã—ÂªÃ—Â§Ã—Â™Ã—ÂŸ Ã¢Â€Â“ Ã—Â‘Ã—Â“Ã—Â•Ã—Â§ Host Ã—Â•Ã—Â Ã—Â¡Ã—Â” Ã—Â©Ã—Â•Ã—Â‘")
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

            # Headers Ã—Â—Ã—Â©Ã—Â•Ã—Â‘Ã—Â™Ã—Â Ã¢Â€Â“ Ã—Â™Ã—Â© Ã—Â©Ã—Â¨Ã—ÂªÃ—Â™Ã—Â Ã—Â©Ã—ÂœÃ—Â Ã—Â¢Ã—Â•Ã—Â‘Ã—Â“Ã—Â™Ã—Â Ã—Â‘Ã—ÂœÃ—Â™ User-Agent
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "*/*"
            }

            session = setup_session()  # Ã¢Â†Â Ã—Â©Ã—Â•Ã—Â¨Ã—Â” Ã—Â—Ã—Â“Ã—Â©Ã—Â” Ã—ÂœÃ—Â©Ã—Â™Ã—Â¤Ã—Â•Ã—Â¨
            response = session.get(self.m3uURL, headers=headers, timeout=10)  # Ã¢Â†Â Ã—Â©Ã—Â™Ã—ÂžÃ—Â•Ã—Â© Ã—Â‘Ã—Â©Ã—Â™Ã—Â¤Ã—Â•Ã—Â¨
            response.raise_for_status()  # Ã—ÂžÃ—Â¨Ã—Â™Ã—Â Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â” Ã—ÂÃ—Â Ã—Â”Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—ÂœÃ—Â Ã—Â™Ã—Â¨Ã—Â“ Ã—ÂªÃ—Â§Ã—Â™Ã—ÂŸ

            # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Âª Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ
            content = response.text.strip()
            if not content.startswith("#EXTM3U"):
                QMessageBox.critical(self, "Invalid File", "Downloaded file is not a valid M3U playlist.")
                return

            # Ã—Â‘Ã—Â—Ã—Â™Ã—Â¨Ã—Âª Ã—ÂžÃ—Â™Ã—Â§Ã—Â•Ã—Â Ã—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Â”
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

        # session Ã—Â¢Ã—Â Ã—Â›Ã—Â•Ã—ÂªÃ—Â¨Ã—Â•Ã—Âª Ã—Â©Ã—Âœ Ã—Â“Ã—Â¤Ã—Â“Ã—Â¤Ã—ÂŸ
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

    def __init__(self, channels, duplicate_names=None):  # Ã—Â”Ã—Â¤Ã—Â•Ã—Âš Ã—ÂÃ—Âª duplicate_names Ã—ÂœÃ—ÂÃ—Â•Ã—Â¤Ã—Â¦Ã—Â™Ã—Â•Ã—Â Ã—ÂœÃ—Â™
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
                # Ã—ÂžÃ—Â—Ã—Â›Ã—Â™Ã—Â Ã—Â¨Ã—Â’Ã—Â¢ Ã—Â§Ã—Â˜Ã—ÂŸ Ã—ÂœÃ—Â¤Ã—Â Ã—Â™ Ã—Â™Ã—Â¦Ã—Â™Ã—ÂÃ—Â” Ã—Â›Ã—Â“Ã—Â™ Ã—ÂœÃ—Â Ã—ÂœÃ—Â§Ã—Â¨Ã—Â•Ã—Â¢ Ã—Â¡Ã—Â™Ã—Â’Ã—Â Ã—ÂœÃ—Â™Ã—Â Ã—Â‘Ã—ÂÃ—ÂžÃ—Â¦Ã—Â¢
                time.sleep(0.05)
                break
            status = "Offline"; reason = "Unknown"
            try:
                res = requests.get(url, headers=headers, stream=True, timeout=4)
                if res.status_code < 400 and any(x in res.text.lower() for x in ["#extm3u", ".ts", ".mp4", ".m3u8"]):
                    status = "Online"; reason = "OK"
                    # Ã—Â›Ã—ÂÃ—ÂŸ Ã—ÂªÃ—Â•Ã—Â›Ã—ÂœÃ—Â• Ã—ÂœÃ—Â”Ã—Â•Ã—Â¡Ã—Â™Ã—Â£ Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Â•Ã—Âª Ã—Â Ã—Â•Ã—Â¡Ã—Â¤Ã—Â•Ã—Âª dup Ã—Â•Ã—Â›Ã—Â•Ã—Â³
                else:
                    reason = f"HTTP {res.status_code}"
            except Exception as e:
                reason = str(e)
            checked += 1
            if status == "Offline":
                offline += 1
            # Ã—Â©Ã—Â™Ã—Â“Ã—Â•Ã—Â¨ Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ
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
                # Ã—Â©Ã—Â™Ã—ÂžÃ—Â•Ã—Â© Ã—Â‘-GET Ã—Â¢Ã—Â stream Ã—Â›Ã—Â“Ã—Â™ Ã—ÂœÃ—Â“Ã—ÂžÃ—Â•Ã—Âª Ã—Â Ã—Â’Ã—ÂŸ Ã—ÂÃ—ÂžÃ—Â™Ã—ÂªÃ—Â™
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
        self.channel_category_mapping = channel_category_mapping  # Ã—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Âª Ã—Â”Ã—ÂžÃ—Â™Ã—Â“Ã—Â¢
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
            status_item = self.channelTable.item(row, 2)  # Status Ã—Â Ã—ÂžÃ—Â¦Ã—Â Ã—Â‘Ã—Â¢Ã—ÂžÃ—Â•Ã—Â“Ã—Â” 2
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

        # Ã—ÂžÃ—Â©Ã—ÂªÃ—Â Ã—Â™ Ã—ÂÃ—ÂªÃ—Â—Ã—Â•Ã—Âœ Ã—Â—Ã—Â™Ã—Â•Ã—Â Ã—Â™Ã—Â™Ã—Â
        self.scan_results = []
        self.thread = None
        self._is_closing = False
        self.duplicates = duplicates if duplicates else []

        # Debug info
        print(f"[Init] Starting with {len(channels) if channels else 0} channels")
        print(f"[Init] Parent exists: {parent is not None}")
        print(f"[Init] Parent has categories: {hasattr(parent, 'categories') if parent else False}")

        # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Âª Ã—ÂªÃ—Â§Ã—Â™Ã—Â Ã—Â•Ã—Âª Ã—Â Ã—ÂªÃ—Â•Ã—Â Ã—Â™Ã—Â Ã—ÂžÃ—Â©Ã—Â•Ã—Â¤Ã—Â¨Ã—Âª
        if not channels or not isinstance(channels, (list, tuple)):
            # Ã—Â Ã—Â¡Ã—Â” Ã—ÂœÃ—Â§Ã—Â‘Ã—Âœ channels Ã—ÂžÃ—Â”-parent
            if parent and hasattr(parent, 'channels'):
                channels = parent.channels
                print(f"[Init] Retrieved {len(channels)} channels from parent")
            else:
                QMessageBox.warning(None, "Error", "No channels data available for scanning.")
                self.reject()
                return

        # Ã—Â©Ã—ÂžÃ—Â•Ã—Â¨ Ã—ÂÃ—Âª Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â”Ã—ÂžÃ—Â§Ã—Â•Ã—Â¨Ã—Â™Ã—Â™Ã—Â
        original_channels = channels.copy()

        try:
            # Ã—Â‘Ã—Â—Ã—Â™Ã—Â¨Ã—Âª Ã—ÂÃ—Â•Ã—Â¤Ã—ÂŸ Ã—Â”Ã—Â¡Ã—Â¨Ã—Â™Ã—Â§Ã—Â”
            scan_choice = self._showScanChoiceDialog()
            if scan_choice is None:
                self.reject()
                return

            # Ã—ÂÃ—Â Ã—Â Ã—Â‘Ã—Â—Ã—Â¨Ã—Â” Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â¡Ã—Â¤Ã—Â¦Ã—Â™Ã—Â¤Ã—Â™Ã—Âª
            if scan_choice == "category":
                selected_category = self._showCategorySelectionDialog()
                if selected_category is None:
                    self.reject()
                    return

                print(f"[Init] Selected category: '{selected_category}'")

                # Ã—Â¡Ã—Â Ã—ÂŸ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂœÃ—Â¤Ã—Â™ Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â”
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

        # Ã—Â©Ã—ÂžÃ—Â•Ã—Â¨ Ã—ÂÃ—Âª Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â”Ã—Â¡Ã—Â•Ã—Â¤Ã—Â™Ã—Â™Ã—Â
        self.channels = channels

        # Ã—Â”Ã—Â’Ã—Â“Ã—Â¨Ã—Âª Ã—Â”Ã—Â—Ã—ÂœÃ—Â•Ã—ÂŸ
        self.setWindowTitle("Smart Scan In Progress")
        self.resize(900, 500)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        # Ã—Â¢Ã—Â™Ã—Â¦Ã—Â•Ã—Â‘ Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—Â•Ã—Â™Ã—Â¢Ã—Â™Ã—Âœ
        self.setStyleSheet(self._getOptimizedStyleSheet())

        # cache Ã—Â¦Ã—Â‘Ã—Â¢Ã—Â™Ã—Â Ã—ÂœÃ—Â‘Ã—Â™Ã—Â¦Ã—Â•Ã—Â¢Ã—Â™Ã—Â Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â™Ã—Â
        self._color_cache = {
            'offline': QColor("#ffebee"),
            'duplicate': QColor("#fff3e0"),
            'online': QColor("#e8f5e8"),
            'white': QColor("white")
        }

        # Ã—Â‘Ã—Â Ã—Â™Ã—Â™Ã—Âª Ã—Â”-UI
        self._buildUI()

        # Ã—Â”Ã—ÂªÃ—Â—Ã—Âœ Ã—Â¡Ã—Â¨Ã—Â™Ã—Â§Ã—Â”
        self._startScanning()

    def _getOptimizedStyleSheet(self):
        """StyleSheet Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—Â•Ã—ÂžÃ—ÂÃ—Â•Ã—Â¤Ã—Â˜Ã—Â"""
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
        """Ã—Â‘Ã—Â Ã—Â™Ã—Â™Ã—Âª Ã—ÂžÃ—ÂžÃ—Â©Ã—Â§ Ã—ÂžÃ—Â©Ã—ÂªÃ—ÂžÃ—Â© Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Ã—Â›Ã—Â•Ã—ÂªÃ—Â¨Ã—Âª
        title_label = QLabel("Ã°ÂŸÂ”Â Smart Channel Scanner")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2;")
        layout.addWidget(title_label)

        # Ã—Â¡Ã—Â˜Ã—Â˜Ã—Â™Ã—Â¡Ã—Â˜Ã—Â™Ã—Â§Ã—Â•Ã—Âª
        self.labelStats = QLabel("Initializing scan...")
        self.labelStats.setStyleSheet("font-size: 14px; font-weight: bold; color: #1976D2; padding: 5px;")
        layout.addWidget(self.labelStats)

        # Ã—Â¤Ã—Â¡ Ã—Â”Ã—ÂªÃ—Â§Ã—Â“Ã—ÂžÃ—Â•Ã—Âª
        self.progressBar = QProgressBar(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(len(self.channels))
        self.progressBar.setValue(0)
        layout.addWidget(self.progressBar)

        # Ã—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ
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

        # Ã—Â˜Ã—Â‘Ã—ÂœÃ—Â” Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â”
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Channel", "Status", "Reason", "URL"])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)

        # Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨Ã—Â™Ã—Â
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
        Ã—ÂžÃ—ÂžÃ—Â™Ã—Â¨ Ã—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Â•Ã—Âª Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂœÃ—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ Ã—ÂÃ—Â—Ã—Â™Ã—Â“ Ã—Â©Ã—Âœ [(name, url)].
        Ã—ÂªÃ—Â•Ã—ÂžÃ—Âš Ã—Â‘:
        - Ã—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Â” Ã—Â©Ã—Âœ tuples/list: (name, url)
        - Ã—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Â” Ã—Â©Ã—Âœ Ã—ÂžÃ—Â—Ã—Â¨Ã—Â•Ã—Â–Ã—Â•Ã—Âª Ã—Â‘Ã—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ "Name (URL)"
        - Ã—ÂžÃ—ÂªÃ—Â¢Ã—ÂœÃ—Â Ã—ÂžÃ—Â¤Ã—Â¨Ã—Â™Ã—Â˜Ã—Â™Ã—Â Ã—Â©Ã—ÂœÃ—Â Ã—Â Ã—Â™Ã—ÂªÃ—ÂŸ Ã—ÂœÃ—Â—Ã—ÂœÃ—Â¥ Ã—ÂžÃ—Â”Ã—Â URL Ã—ÂªÃ—Â§Ã—Â™Ã—ÂŸ
        - Ã—ÂžÃ—Â¡Ã—Â™Ã—Â¨ Ã—Â›Ã—Â¤Ã—Â™Ã—ÂœÃ—Â•Ã—Â™Ã—Â•Ã—Âª Ã—Â–Ã—Â”Ã—Â•Ã—Âª Ã—Â‘Ã—Â“Ã—Â™Ã—Â•Ã—Â§, Ã—ÂªÃ—Â•Ã—Âš Ã—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Â” Ã—Â¢Ã—Âœ Ã—Â¡Ã—Â“Ã—Â¨
        """
        normalized = []

        for ch in channels:
            try:
                name = None
                url = None

                # Ã—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ [(name, url)] Ã—ÂÃ—Â• [name, url]
                if isinstance(ch, (list, tuple)) and len(ch) >= 2:
                    name = str(ch[0]).strip()
                    url = str(ch[1]).strip()

                # Ã—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ "Name (URL)"
                elif isinstance(ch, str):
                    s = ch.strip()
                    if " (" in s and s.endswith(")"):
                        # rsplit Ã—Â›Ã—Â“Ã—Â™ Ã—ÂœÃ—Â Ã—ÂœÃ—Â©Ã—Â‘Ã—Â•Ã—Â¨ Ã—Â©Ã—ÂžÃ—Â•Ã—Âª Ã—Â©Ã—ÂžÃ—Â›Ã—Â™Ã—ÂœÃ—Â™Ã—Â "("
                        name_part, rest = s.rsplit(" (", 1)
                        name = name_part.strip()
                        url = rest[:-1].strip()  # Ã—Â”Ã—Â¡Ã—Â¨Ã—Âª ')'
                    else:
                        # Ã—ÂÃ—Â Ã—Â–Ã—Â• Ã—ÂžÃ—Â—Ã—Â¨Ã—Â•Ã—Â–Ã—Âª Ã—Â©Ã—ÂœÃ—Â Ã—Â‘Ã—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ "Name (URL)"
                        # Ã—Â Ã—Â•Ã—Â•Ã—Â“Ã—Â Ã—Â©Ã—ÂœÃ—Â¤Ã—Â—Ã—Â•Ã—Âª Ã—Â™Ã—Â© URL. Ã—ÂÃ—Â Ã—ÂÃ—Â™Ã—ÂŸ - Ã—Â Ã—Â“Ã—ÂœÃ—Â’.
                        if s.lower().startswith(("http://", "https://")):
                            name = s  # Ã—Â©Ã—Â Ã—Â–Ã—ÂžÃ—Â Ã—Â™ Ã—Â–Ã—Â”Ã—Â” Ã—ÂœÃ–Â¾URL
                            url = s

                # Ã—Â•Ã—ÂœÃ—Â™Ã—Â“Ã—Â¦Ã—Â™Ã—Â™Ã—Âª URL Ã—Â‘Ã—Â¡Ã—Â™Ã—Â¡Ã—Â™Ã—Âª
                if not url or not url.lower().startswith(("http://", "https://")):
                    continue

                # Ã—Â©Ã—Â Ã—Â‘Ã—Â¨Ã—Â™Ã—Â¨Ã—Âª Ã—ÂžÃ—Â—Ã—Â“Ã—Âœ Ã—ÂÃ—Â Ã—Â—Ã—Â¡Ã—Â¨
                if not name:
                    name = url

                normalized.append((name, url))

            except Exception:
                # Ã—Â¤Ã—Â¨Ã—Â™Ã—Â˜ Ã—Â‘Ã—Â¢Ã—Â™Ã—Â™Ã—ÂªÃ—Â™ - Ã—ÂžÃ—Â“Ã—ÂœÃ—Â’Ã—Â™Ã—Â
                continue

        # Ã—Â”Ã—Â¡Ã—Â¨Ã—Âª Ã—Â›Ã—Â¤Ã—Â™Ã—ÂœÃ—Â•Ã—Â™Ã—Â•Ã—Âª Ã—Â–Ã—Â”Ã—Â•Ã—Âª Ã—Â‘Ã—Â“Ã—Â™Ã—Â•Ã—Â§ Ã—ÂªÃ—Â•Ã—Âš Ã—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Â” Ã—Â¢Ã—Âœ Ã—Â”Ã—Â¡Ã—Â“Ã—Â¨
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
        """Ã—Â”Ã—ÂªÃ—Â—Ã—Âœ Ã—ÂÃ—Âª Ã—ÂªÃ—Â”Ã—ÂœÃ—Â™Ã—Âš Ã—Â”Ã—Â¡Ã—Â¨Ã—Â™Ã—Â§Ã—Â”"""
        if not self.channels:
            QMessageBox.warning(self, "Error", "No channels to scan.")
            self.reject()
            return

        try:
            # Ã—Â¦Ã—Â•Ã—Â¨ Ã—ÂÃ—Âª Ã—Â”-thread Ã—Â¢Ã—Â Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â (Ã—Â‘Ã—ÂœÃ—Â™ duplicate_names Ã—Â¡Ã—Â˜Ã—Â˜Ã—Â™)
            self.thread = SmartScanThread(self.channels, self.duplicates)

            # Ã—Â—Ã—Â‘Ã—Â¨ Ã—ÂÃ—Âª Ã—Â”Ã—Â¡Ã—Â™Ã—Â’Ã—Â Ã—ÂœÃ—Â™Ã—Â
            self.thread.progress.connect(self.updateProgress)
            self.thread.finished.connect(self.scanFinished)

            # Ã—Â”Ã—ÂªÃ—Â—Ã—Âœ Ã—ÂÃ—Âª Ã—Â”Ã—Â¡Ã—Â¨Ã—Â™Ã—Â§Ã—Â”
            self.thread.start()

            # Ã—Â”Ã—Â¤Ã—Â¢Ã—Âœ Ã—Â˜Ã—Â™Ã—Â™Ã—ÂžÃ—Â¨ Ã—ÂœÃ—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—ÂªÃ—Â¦Ã—Â•Ã—Â’Ã—Â”
            if hasattr(self, 'timer'):
                self.timer.start(100)  # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—Â›Ã—Âœ 100ms

        except Exception as e:
            print(f"[Scan Start Error] {e}")
            QMessageBox.critical(self, "Error", f"Failed to start scanning: {str(e)}")
            self.reject()

    def _showScanChoiceDialog(self):
        """Ã—Â—Ã—ÂœÃ—Â•Ã—ÂŸ Ã—Â‘Ã—Â—Ã—Â™Ã—Â¨Ã—Âª Ã—Â¡Ã—Â¨Ã—Â™Ã—Â§Ã—Â” Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Choose Scan Type")
            dialog.setFixedSize(350, 150)
            dialog.setModal(True)

            layout = QVBoxLayout(dialog)

            title = QLabel("Select scanning method:")
            title.setStyleSheet("font-size: 14px; font-weight: bold;")
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
        """Ã—Â—Ã—ÂœÃ—Â•Ã—ÂŸ Ã—Â‘Ã—Â—Ã—Â™Ã—Â¨Ã—Âª Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—Â•Ã—ÂžÃ—Â©Ã—Â•Ã—Â¤Ã—Â¨"""
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
            title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
            layout.addWidget(title)

            # Ã—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Â” Ã—Â¢Ã—Â Ã—ÂžÃ—Â™Ã—Â“Ã—Â¢
            category_list = QListWidget()
            category_list.setStyleSheet("font-size: 12px;")

            for category_name in sorted(categories.keys()):
                channel_count = len(categories[category_name])
                display_text = f"{category_name} ({channel_count} channels)"
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, category_name)
                category_list.addItem(item)

            # Ã—Â‘Ã—Â—Ã—Â¨ Ã—ÂÃ—Âª Ã—Â”Ã—Â¤Ã—Â¨Ã—Â™Ã—Â˜ Ã—Â”Ã—Â¨Ã—ÂÃ—Â©Ã—Â•Ã—ÂŸ Ã—Â›Ã—Â‘Ã—Â¨Ã—Â™Ã—Â¨Ã—Âª Ã—ÂžÃ—Â—Ã—Â“Ã—Âœ
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
        """Ã—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂÃ—Â•Ã—ÂœÃ—Â˜Ã—Â¨Ã—Â”-Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—Â¢Ã—Â Ã—ÂÃ—ÂœÃ—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—ÂªÃ—Â Ã—ÂžÃ—Â©Ã—Â•Ã—Â¤Ã—Â¨"""
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

            # Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—ÂžÃ—Â™Ã—ÂœÃ—Â•Ã—ÂŸ Ã—ÂœÃ—Â—Ã—Â™Ã—Â¤Ã—Â•Ã—Â© Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ O(1)
            category_names_dict = {}

            for ch in category_channels:
                try:
                    # Ã—Â Ã—Â¨Ã—ÂžÃ—Â•Ã—Âœ Ã—Â”Ã—Â©Ã—Â
                    normalized = ch.strip().lower()
                    category_names_dict[normalized] = ch

                    # Ã—ÂÃ—Â Ã—Â™Ã—Â© Ã—Â¡Ã—Â•Ã—Â’Ã—Â¨Ã—Â™Ã—Â™Ã—Â, Ã—Â”Ã—Â•Ã—Â¡Ã—Â£ Ã—Â’Ã—Â Ã—ÂÃ—Âª Ã—Â”Ã—Â©Ã—Â Ã—Â‘Ã—ÂœÃ—Â¢Ã—Â“Ã—Â™Ã—Â”Ã—Â
                    if ' (' in ch:
                        base_name = ch.split(' (')[0].strip().lower()
                        category_names_dict[base_name] = ch

                except Exception as e:
                    print(f"[Filter] Error processing category channel '{ch}': {e}")
                    continue

            print(f"[Filter] Created lookup dict with {len(category_names_dict)} entries")

            # Ã—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—Â¢Ã—Â lookup
            filtered = []
            seen = set()  # Ã—ÂœÃ—ÂžÃ—Â Ã—Â™Ã—Â¢Ã—Âª Ã—Â›Ã—Â¤Ã—Â™Ã—ÂœÃ—Â•Ã—Â™Ã—Â•Ã—Âª

            for channel in channels:
                try:
                    channel_lower = channel.strip().lower()

                    # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Â” Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â” Ã—Â‘Ã—ÂžÃ—Â™Ã—ÂœÃ—Â•Ã—ÂŸ
                    if channel_lower in category_names_dict:
                        if channel not in seen:
                            filtered.append(channel)
                            seen.add(channel)
                        continue

                    # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Âª Ã—Â©Ã—Â Ã—Â‘Ã—Â¡Ã—Â™Ã—Â¡
                    if ' (' in channel:
                        base_name = channel.split(' (')[0].strip().lower()
                        if base_name in category_names_dict:
                            if channel not in seen:
                                filtered.append(channel)
                                seen.add(channel)
                            continue

                    # Ã—Â—Ã—Â™Ã—Â¤Ã—Â•Ã—Â© Ã—Â—Ã—ÂœÃ—Â§Ã—Â™ Ã—Â¨Ã—Â§ Ã—ÂÃ—Â Ã—Â Ã—Â“Ã—Â¨Ã—Â©
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

            # Ã—ÂÃ—Â Ã—ÂœÃ—Â Ã—Â Ã—ÂžÃ—Â¦Ã—ÂÃ—Â• Ã—Â”Ã—ÂªÃ—ÂÃ—ÂžÃ—Â•Ã—Âª, Ã—Â”Ã—Â—Ã—Â–Ã—Â¨ Ã—ÂÃ—Âª Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™ Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â‘Ã—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ Ã—Â”Ã—Â Ã—Â›Ã—Â•Ã—ÂŸ
            if not filtered and category_channels:
                print("[Filter] No matches found, converting category channels to tuples")
                # Ã—Â”Ã—ÂžÃ—Â¨Ã—Â” Ã—ÂœÃ—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ Ã—Â©Ã—Âœ tuples
                converted = []
                for ch in category_channels:
                    try:
                        if " (" in ch and ch.endswith(")"):
                            name = ch.split(" (")[0].strip()
                            url = ch.split(" (", 1)[1].rstrip(")")
                            converted.append((name, url))
                        else:
                            # Ã—ÂÃ—Â Ã—Â”Ã—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ Ã—ÂœÃ—Â Ã—ÂžÃ—Â•Ã—Â›Ã—Â¨, Ã—Â Ã—Â“Ã—ÂœÃ—Â’
                            print(f"[Filter] Skipping invalid format: {ch}")
                    except Exception as e:
                        print(f"[Filter] Error converting channel: {e}")
                        continue
                return converted if converted else channels  # Ã—Â”Ã—Â—Ã—Â–Ã—Â¨ Ã—ÂÃ—Âª Ã—Â”Ã—ÂžÃ—Â§Ã—Â•Ã—Â¨Ã—Â™ Ã—ÂÃ—Â Ã—Â”Ã—Â”Ã—ÂžÃ—Â¨Ã—Â” Ã—Â Ã—Â›Ã—Â©Ã—ÂœÃ—Â”

            return filtered

        except Exception as e:
            print(f"[Filter Channels Error] {e}")
            import traceback
            traceback.print_exc()
            return channels

    def updateProgress(self, checked, offline, duplicate, data):
        """Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—Â”Ã—ÂªÃ—Â§Ã—Â“Ã—ÂžÃ—Â•Ã—Âª Ã—ÂÃ—Â•Ã—ÂœÃ—Â˜Ã—Â¨Ã—Â”-Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨"""
        try:
            if self._is_closing:
                return

            name, url, status, reason = data
            total = self.progressBar.maximum()
            problematic = offline + duplicate

            # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—Â˜Ã—Â§Ã—Â¡Ã—Â˜
            self.labelStats.setText(
                f"Scanned: {checked}/{total} | Offline: {offline} | Duplicates: {duplicate} | Issues: {problematic}"
            )

            # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—Â¤Ã—Â¡ Ã—Â”Ã—ÂªÃ—Â§Ã—Â“Ã—ÂžÃ—Â•Ã—Âª
            self.progressBar.setValue(checked)

            # Ã—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Âª Ã—ÂªÃ—Â•Ã—Â¦Ã—ÂÃ—Â”
            self.scan_results.append((name, status, reason, url))

            # Ã—Â”Ã—Â•Ã—Â¡Ã—Â¤Ã—Â” Ã—ÂœÃ—Â˜Ã—Â‘Ã—ÂœÃ—Â”
            self._addTableRow(name, status, reason, url)

        except Exception as e:
            print(f"[Update Progress Error] {e}")

    def _addTableRow(self, name, status, reason, url):
        """Ã—Â”Ã—Â•Ã—Â¡Ã—Â¤Ã—Âª Ã—Â©Ã—Â•Ã—Â¨Ã—Â” Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â” Ã—ÂœÃ—Â˜Ã—Â‘Ã—ÂœÃ—Â”"""
        try:
            if self._is_closing:
                return

            row = self.table.rowCount()
            self.table.insertRow(row)

            # Ã—Â”Ã—Â•Ã—Â¡Ã—Â¤Ã—Âª Ã—Â¤Ã—Â¨Ã—Â™Ã—Â˜Ã—Â™Ã—Â
            self.table.setItem(row, 0, QTableWidgetItem(str(name)))

            status_item = QTableWidgetItem(str(status))

            # Ã—Â¦Ã—Â‘Ã—Â™Ã—Â¢Ã—Â” Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â”
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
        """Ã—Â¨Ã—Â¢Ã—Â Ã—Â•Ã—ÂŸ Ã—Â˜Ã—Â‘Ã—ÂœÃ—Â” Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨"""
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
        """Ã—Â”Ã—Â—Ã—ÂœÃ—Âª Ã—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â”"""
        try:
            self.refreshTable()
        except Exception as e:
            print(f"[Apply Filter Error] {e}")

    def scanFinished(self):
        """Ã—Â¡Ã—Â™Ã—Â•Ã—Â Ã—Â¡Ã—Â¨Ã—Â™Ã—Â§Ã—Â”"""
        try:
            if self._is_closing:
                return

            self.labelStats.setText(self.labelStats.text() + " Ã¢ÂœÂ… Done.")
            self.stopBtn.setEnabled(False)
            self.progressBar.setValue(self.progressBar.maximum())
            print("[Scan] Scan completed successfully")

        except Exception as e:
            print(f"[Scan Finished Error] {e}")

    def stopScan(self):
        """Ã—Â¢Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—Â¡Ã—Â¨Ã—Â™Ã—Â§Ã—Â” Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â”"""
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
        """Ã—Â¡Ã—Â™Ã—ÂžÃ—Â•Ã—ÂŸ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â‘Ã—Â¢Ã—Â™Ã—Â™Ã—ÂªÃ—Â™Ã—Â™Ã—Â Ã—Â‘Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â•Ã—Âª Ã—Â©Ã—Â™Ã—Â"""
        try:
            if not self.scan_results:
                QMessageBox.information(self, "No Results", "No scan results available.")
                return

            urls_to_mark = set()
            channel_statuses = {}
            duplicate_count = 0
            offline_count = 0

            # Ã—ÂÃ—Â™Ã—Â¡Ã—Â•Ã—Â£ Ã—Â Ã—ÂªÃ—Â•Ã—Â Ã—Â™Ã—Â Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨
            for name, status, reason, url in self.scan_results:
                if name not in channel_statuses:
                    channel_statuses[name] = []
                channel_statuses[name].append({
                    'status': status.lower(),
                    'url': url,
                    'is_offline': 'offline' in status.lower()
                })

            # Ã—Â¢Ã—Â™Ã—Â‘Ã—Â•Ã—Â“ Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨
            for name, entries in channel_statuses.items():
                offline_entries = [e for e in entries if e['is_offline']]
                online_entries = [e for e in entries if not e['is_offline']]

                # Ã—Â¡Ã—Â™Ã—ÂžÃ—Â•Ã—ÂŸ Ã—ÂÃ—Â•Ã—Â¤Ã—ÂœÃ—Â™Ã—Â™Ã—ÂŸ
                for entry in offline_entries:
                    urls_to_mark.add(entry['url'])
                    offline_count += 1

                # Ã—Â¡Ã—Â™Ã—ÂžÃ—Â•Ã—ÂŸ Ã—Â›Ã—Â¤Ã—Â•Ã—ÂœÃ—Â™Ã—Â (Ã—Â¨Ã—Â§ Ã—ÂÃ—Â•Ã—Â Ã—ÂœÃ—Â™Ã—Â™Ã—ÂŸ Ã—Â Ã—Â•Ã—Â¡Ã—Â¤Ã—Â™Ã—Â)
                if len(online_entries) > 1:
                    for entry in online_entries[1:]:
                        urls_to_mark.add(entry['url'])
                        duplicate_count += 1

            total_marked = len(urls_to_mark)

            # Ã—Â¡Ã—Â™Ã—ÂžÃ—Â•Ã—ÂŸ Ã—Â‘Ã—Â¤Ã—Â•Ã—Â¢Ã—Âœ
            if self.parent() and hasattr(self.parent(), "selectChannelsByUrls"):
                self.parent().selectChannelsByUrls(urls_to_mark)
                QMessageBox.information(
                    self, "Marked Successfully",
                    f"Ã¢ÂœÂ… Found and marked:\n"
                    f"Ã¢Â€Â¢ {duplicate_count} duplicate channels\n"
                    f"Ã¢Â€Â¢ {offline_count} offline channels\n"
                    f"Ã¢Â”ÂÃ¢Â”ÂÃ¢Â”ÂÃ¢Â”ÂÃ¢Â”ÂÃ¢Â”ÂÃ¢Â”ÂÃ¢Â”ÂÃ¢Â”ÂÃ¢Â”ÂÃ¢Â”ÂÃ¢Â”ÂÃ¢Â”ÂÃ¢Â”ÂÃ¢Â”Â\n"
                    f"Total: {total_marked} channels marked"
                )
                print(f"[Mark] Marked {total_marked} channels")
            else:
                QMessageBox.warning(self, "Error", "Parent method not found.")

        except Exception as e:
            print(f"[Mark Channels Error] {e}")
            QMessageBox.critical(self, "Error", f"Failed to mark channels: {str(e)}")

    def closeEvent(self, event):
        """Ã—Â¡Ã—Â’Ã—Â™Ã—Â¨Ã—Â” Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â” Ã—Â•Ã—Â‘Ã—Â˜Ã—Â•Ã—Â—Ã—Â”"""
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
        """Ã—Â“Ã—Â—Ã—Â™Ã—Â™Ã—Â” Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â”"""
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
        # Ã—Â˜Ã—Â•Ã—Â¢Ã—ÂŸ Ã—ÂÃ—Âª Ã—Â›Ã—Âœ Ã—Â”Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â Ã—ÂœÃ–Â¾cache Ã—Â‘Ã—Â¤Ã—Â¢Ã—Â Ã—ÂÃ—Â—Ã—Âª
        self.logo_cache = load_logo_cache()
        self.initUI()
        self.logo_cache = load_logo_cache()
        self.logosFinished.connect(self.onLogosFinished)

    @property
    def full_text(self) -> str:
        """
        Ã—ÂžÃ—Â—Ã—Â–Ã—Â™Ã—Â¨ Ã—ÂÃ—Âª Ã—Â›Ã—Âœ Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—Â”Ã–Â¾M3U Ã—Â©Ã—ÂžÃ—Â•Ã—Â¦Ã—Â’ Ã—Â‘Ã—Â¢Ã—Â•Ã—Â¨Ã—Âš.
        """
        return self.textEdit.toPlainText()


    def merge_or_fix_epg(self):
        """
        Ã—ÂžÃ—ÂÃ—Â—Ã—Â“ Ã—ÂÃ—Â• Ã—ÂžÃ—ÂªÃ—Â§Ã—ÂŸ Ã—ÂÃ—Âª Ã—Â©Ã—Â•Ã—Â¨Ã—Âª Ã—Â”Ã–Â¾EPG Ã—Â‘Ã—Â¨Ã—ÂÃ—Â© Ã—Â”Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—ÂœÃ—Â¤Ã—Â™ Ã—Â¡Ã—Â¤Ã—Â§Ã—Â™Ã—Â Ã—ÂžÃ—Â–Ã—Â•Ã—Â”Ã—Â™Ã—Â.
        Ã—Â©Ã—Â•Ã—ÂžÃ—Â¨ Ã—Â©Ã—Â•Ã—Â¨Ã—Âª EXTM3U Ã—ÂÃ—Â—Ã—Âª Ã—Â‘Ã—ÂœÃ—Â‘Ã—Â“, Ã—Â¢Ã—Â Ã—Â›Ã—Âœ Ã—Â§Ã—Â™Ã—Â©Ã—Â•Ã—Â¨Ã—Â™ Ã—Â”Ã–Â¾EPG Ã—Â”Ã—ÂªÃ—Â§Ã—Â¤Ã—Â™Ã—Â Ã—Â©Ã—Â Ã—ÂžÃ—Â¦Ã—ÂÃ—Â•.
        """
        import os
        import json
        import re
        from PyQt5.QtWidgets import QMessageBox

        # Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â” Ã—Â©Ã—ÂœÃ—Â‘ 1: Ã—ÂÃ—Â¡Ã—Â•Ã—Â£ Ã—Â§Ã—Â™Ã—Â©Ã—Â•Ã—Â¨Ã—Â™ EPG Ã—Â§Ã—Â™Ã—Â™Ã—ÂžÃ—Â™Ã—Â Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”
        all_epg_links = set()
        # Ã—ÂÃ—Â Ã—Â Ã—Â©Ã—ÂžÃ—Â¨Ã—Â• Ã—Â›Ã—Â•Ã—ÂªÃ—Â¨Ã—Â•Ã—Âª EPG Ã—Â‘Ã—Â¢Ã—Â‘Ã—Â¨
        if hasattr(self, 'epg_headers'):
            for hdr in self.epg_headers:
                # Ã—ÂžÃ—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â›Ã—Âœ URL Ã—Â©Ã—ÂžÃ—Â•Ã—Â¤Ã—Â™Ã—Â¢ Ã—Â‘- x-tvg-url="..."
                urls = re.findall(r'x-tvg-url="([^"]+)"', hdr)
                for u in urls:
                    all_epg_links.update(u.split(','))

        # Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â” Ã—Â©Ã—ÂœÃ—Â‘ 2: Ã—Â˜Ã—Â¢Ã—ÂŸ Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ M3U Ã—Â”Ã—Â Ã—Â•Ã—Â›Ã—Â—Ã—Â™ Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”
        content = getattr(self, 'last_loaded_m3u', None) or self.textEdit.toPlainText()
        if not content:
            QMessageBox.warning(self, "EPG Error", "Ã—ÂÃ—Â™Ã—ÂŸ Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—ÂœÃ–Â¾M3U Ã—ÂœÃ—Â˜Ã—Â¢Ã—Â™Ã—Â Ã—Â” Ã—ÂÃ—Â• Ã—ÂœÃ—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ.")
            return

        # Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â” Ã—Â©Ã—ÂœÃ—Â‘ 3: Ã—Â˜Ã—Â¢Ã—ÂŸ JSON Ã—Â©Ã—Âœ Ã—Â¡Ã—Â¤Ã—Â§Ã—Â™ EPG Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”
        providers_path = os.path.join(os.path.dirname(__file__), "EPG_providers_full.json")
        try:
            with open(providers_path, "r", encoding="utf-8") as f:
                providers = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "EPG Error", f"Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â” Ã—Â‘Ã—Â§Ã—Â¨Ã—Â™Ã—ÂÃ—Âª Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—Â¡Ã—Â¤Ã—Â§Ã—Â™Ã—Â:\n{e}")
            return

        # Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â” Ã—Â©Ã—ÂœÃ—Â‘ 4: Ã—Â–Ã—Â”Ã—Â” Ã—Â¡Ã—Â¤Ã—Â§Ã—Â™Ã—Â Ã—Â‘Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—ÂœÃ—Â¤Ã—Â™ Ã—ÂžÃ—Â™Ã—ÂœÃ—Â™Ã—Â Ã—ÂÃ—Â• Ã—Â“Ã—Â•Ã—ÂžÃ—Â™Ã—Â™Ã—Â Ã—Â™Ã—Â Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”
        lower = content.lower()
        # Ã—Â›Ã—Âœ Ã—Â›Ã—ÂªÃ—Â•Ã—Â‘Ã—Â•Ã—Âª URL Ã—Â‘Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥
        urls_in_file = [line.strip() for line in content.splitlines() if line.strip().startswith("http")]
        domains = {urlparse(u).netloc.lower().lstrip("www.") for u in urls_in_file}

        for provider, epg_list in providers.items():
            prov_l = provider.lower()
            # Ã—Â–Ã—Â™Ã—Â”Ã—Â•Ã—Â™ Ã—ÂœÃ—Â¤Ã—Â™ Ã—Â©Ã—Â Ã—Â”Ã—Â¡Ã—Â¤Ã—Â§ Ã—Â‘Ã—ÂªÃ—Â•Ã—Âš Ã—Â”Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ
            if prov_l in lower:
                all_epg_links.update(epg_list)
                continue
            # Ã—Â–Ã—Â™Ã—Â”Ã—Â•Ã—Â™ Ã—ÂœÃ—Â¤Ã—Â™ Ã—Â“Ã—Â•Ã—ÂžÃ—Â™Ã—Â™Ã—ÂŸ Ã—Â©Ã—Âœ Ã—ÂÃ—Â—Ã—Â“ Ã—ÂžÃ—Â§Ã—Â™Ã—Â©Ã—Â•Ã—Â¨Ã—Â™ Ã—Â”Ã–Â¾EPG
            for epg_url in epg_list:
                dom = urlparse(epg_url).netloc.lower().lstrip("www.")
                if dom in domains:
                    all_epg_links.update(epg_list)
                    break

        # Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â” Ã—Â©Ã—ÂœÃ—Â‘ 5: Ã—Â‘Ã—Â Ã—Â™Ã—Â™Ã—Â” Ã—Â•Ã—Â Ã—Â™Ã—Â§Ã—Â•Ã—Â™ Ã—Â©Ã—Âœ Ã—Â”Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—Â”Ã—Â—Ã—Â“Ã—Â© Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”
        cleaned = []
        for line in content.splitlines():
            # Ã—ÂžÃ—Â©Ã—ÂžÃ—Â™Ã—Â˜ Ã—Â¨Ã—Â§ Ã—Â©Ã—Â•Ã—Â¨Ã—Â•Ã—Âª Ã—Â©Ã—ÂžÃ—ÂªÃ—Â—Ã—Â™Ã—ÂœÃ—Â•Ã—Âª Ã—Â‘Ã–Â¾#EXTM3U
            if not line.startswith("#EXTM3U"):
                cleaned.append(line)
        # Ã—Â‘Ã—Â Ã—Â” Ã—Â©Ã—Â•Ã—Â¨Ã—Âª EXTM3U Ã—Â—Ã—Â“Ã—Â©Ã—Â” Ã—Â¢Ã—Â Ã—Â›Ã—Âœ Ã—Â”Ã—Â§Ã—Â™Ã—Â©Ã—Â•Ã—Â¨Ã—Â™Ã—Â
        if all_epg_links:
            links = ",".join(sorted(all_epg_links))
            new_header = f'#EXTM3U x-tvg-url="{links}"'
        else:
            new_header = "#EXTM3U"
        new_content = new_header + "\n" + "\n".join(cleaned)

        # Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â” Ã—Â©Ã—ÂœÃ—Â‘ 6: Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—Â”Ã—ÂžÃ—Â¢Ã—Â¨Ã—Â›Ã—Âª Ã—Â•Ã—ÂªÃ—Â¦Ã—Â•Ã—Â’Ã—Â” Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”Ã¢Â€Â”
        self.epg_headers = [new_header]  # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Âª Ã—Â”Ã–Â¾EPG headers
        self.last_loaded_m3u = new_content  # Ã—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Â” Ã—Â¤Ã—Â Ã—Â™Ã—ÂžÃ—Â™Ã—Âª
        self.loadM3UFromText(new_content)  # Ã—Â˜Ã—Â¢Ã—Â™Ã—Â Ã—Â” Ã—ÂžÃ—Â—Ã—Â“Ã—Â© Ã—ÂœÃ—ÂžÃ—Â¢Ã—Â¨Ã—Â›Ã—Âª

        QMessageBox.information(self, "EPG Updated", "Ã¢ÂœÂ… Ã—Â©Ã—Â•Ã—Â¨Ã—Âª EPG Ã—Â¢Ã—Â•Ã—Â“Ã—Â›Ã—Â Ã—Â” Ã—Â•Ã—Â”Ã—Â•Ã—Â–Ã—Â Ã—Â” Ã—ÂžÃ—Â—Ã—Â“Ã—Â©.")

    def open_channel_context_menu(self, position):
        """
        Ã—ÂªÃ—Â¤Ã—Â¨Ã—Â™Ã—Â˜ Ã—Â§Ã—ÂœÃ—Â™Ã—Â§Ã–Â¾Ã—Â™Ã—ÂžÃ—Â Ã—Â™ Ã—Â¢Ã—Âœ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—Â‘Ã—Â•Ã—Â“Ã—Â“: Ã—Â Ã—Â’Ã—ÂŸ Ã—ÂÃ—Â•Ã—ÂªÃ—Â• Ã—Â‘-VLC Ã—ÂÃ—Â• preview Ã—ÂœÃ—Â¨Ã—Â™Ã—Â‘Ã—Â•Ã—Â™.
        """
        item = self.channelList.itemAt(position)
        if not item:
            return

        # Ã—Â©Ã—Â•Ã—ÂœÃ—Â¤Ã—Â™Ã—Â Ã—ÂÃ—Âª Ã—Â”Ã—Â¢Ã—Â¨Ã—Âš Ã—Âž-UserRole, Ã—Â•Ã—ÂžÃ—Â’Ã—Â‘Ã—Â™Ã—Â Ã—ÂœÃ—Â˜Ã—Â§Ã—Â¡Ã—Â˜ Ã—ÂÃ—Â Ã—Â–Ã—Â” Ã—ÂœÃ—Â Ã—ÂžÃ—Â—Ã—Â¨Ã—Â•Ã—Â–Ã—Âª
        raw = item.data(Qt.UserRole)
        entry = raw if isinstance(raw, str) else item.text().strip()

        menu = QMenu(self)

        # Ã¢Â–Â¶ Ã—Â Ã—Â’Ã—ÂŸ Ã—ÂÃ—Âª Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—Â‘-VLC
        play_action = QAction("Ã¢Â–Â¶ Ã—Â Ã—Â’Ã—ÂŸ Ã—Â‘Ã–Â¾VLC", self)
        play_action.triggered.connect(lambda _, e=entry: self.play_channel_with_name(e))
        menu.addAction(play_action)

        # Ã¢Â–Â¶ Ã—Â¦Ã—Â¤Ã—Â” Ã—Â‘Ã—Â›Ã—Âœ Ã—Â”Ã—Â Ã—Â‘Ã—Â—Ã—Â¨Ã—Â™Ã—Â (preview)
        preview_action = QAction("Ã¢Â–Â¶ Ã—Â¦Ã—Â¤Ã—Â” Ã—Â‘Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â Ã—Â‘Ã—Â—Ã—Â¨Ã—Â™Ã—Â", self)
        preview_action.triggered.connect(self.previewSelectedChannels)
        menu.addAction(preview_action)

        menu.exec_(self.channelList.viewport().mapToGlobal(position))

    def chooseFilterMethod(self):
        """Ã—Â‘Ã—Â—Ã—Â™Ã—Â¨Ã—Â” Ã—Â™Ã—Â©Ã—Â™Ã—Â¨Ã—Â” Ã—Â‘Ã—Â™Ã—ÂŸ Ã—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ Ã—Â§Ã—ÂœÃ—ÂÃ—Â¡Ã—Â™ Ã—ÂœÃ—ÂžÃ—ÂªÃ—Â§Ã—Â“Ã—Â"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ã°ÂŸÂŽÂ¯ Ã—Â‘Ã—Â—Ã—Â¨ Ã—Â©Ã—Â™Ã—Â˜Ã—Âª Ã—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ")
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

        # Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨ Ã—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ Ã—Â§Ã—ÂœÃ—ÂÃ—Â¡Ã—Â™
        classic_btn = QPushButton("Ã°ÂŸÂ“Â‹ Ã—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ Ã—Â§Ã—ÂœÃ—ÂÃ—Â¡Ã—Â™ (Ã—Â™Ã—Â©Ã—Â¨Ã—ÂÃ—Âœ Ã—Â‘Ã—ÂœÃ—Â‘Ã—Â“)")
        classic_btn.setStyleSheet("background-color: black; color: white;")
        classic_btn.clicked.connect(lambda: [dialog.accept(), self.showLanguageChoice()])

        # Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨ Ã—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ Ã—ÂžÃ—ÂªÃ—Â§Ã—Â“Ã—Â
        advanced_btn = QPushButton("Ã°ÂŸÂšÂ€ Ã—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ Ã—ÂžÃ—ÂªÃ—Â§Ã—Â“Ã—Â (Ã—Â™Ã—Â©Ã—Â¨Ã—ÂÃ—Âœ + Ã—Â¢Ã—Â•Ã—ÂœÃ—Â)")
        advanced_btn.setStyleSheet("background-color: red; color: white;")
        advanced_btn.clicked.connect(lambda: [dialog.accept(), self.runAdvancedFilter()])

        layout.addWidget(classic_btn)
        layout.addWidget(advanced_btn)

        dialog.exec_()

    def showLanguageChoice(self):
        """Ã—Â‘Ã—Â—Ã—Â™Ã—Â¨Ã—Âª Ã—Â©Ã—Â¤Ã—Â” Ã—ÂœÃ—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ Ã—Â”Ã—Â§Ã—ÂœÃ—ÂÃ—Â¡Ã—Â™"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ã—Â‘Ã—Â—Ã—Â¨ Ã—Â©Ã—Â¤Ã—Â”")
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

        hebrew_btn = QPushButton(" Ã—Â¢Ã—Â‘Ã—Â¨Ã—Â™Ã—Âª")
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
            QMessageBox.warning(self, "Ã—ÂÃ—Â™Ã—ÂŸ Ã—Â Ã—ÂªÃ—Â•Ã—Â Ã—Â™Ã—Â", "Ã—ÂÃ—Â™Ã—ÂŸ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂœÃ—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ")
            return
        self.filter_system.chooseIsraelLanguageAndRunAdvanced()

    def filterIsraelChannelsFromKeywords(self, lang):
        """
        Ã—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ Ã—Â™Ã—Â©Ã—Â¨Ã—ÂÃ—ÂœÃ—Â™ Ã—Â Ã—Â§Ã—Â™ Ã—Â•Ã—ÂžÃ—Â“Ã—Â•Ã—Â™Ã—Â§, Ã—Â‘Ã—ÂœÃ—Â™ Ã—Â¨Ã—Â“Ã—Â™Ã—Â•.
        Ã—Â–Ã—Â™Ã—Â”Ã—Â•Ã—Â™ Ã—Â™Ã—Â©Ã—Â¨Ã—ÂÃ—ÂœÃ—Â™:
        1) Ã—Â©Ã—Â Ã—Â‘Ã—Â¢Ã—Â‘Ã—Â¨Ã—Â™Ã—Âª
        2) Ã—Â“Ã—Â¤Ã—Â•Ã—Â¡Ã—Â™ IL Ã—Â‘Ã—Â’Ã—Â‘Ã—Â•Ã—ÂœÃ—Â•Ã—Âª Ã—ÂžÃ—Â™Ã—ÂœÃ—Â”: ' IL ', '(IL)', 'IL:', '-IL-', 'ISR'
        3) Ã—ÂžÃ—Â•Ã—ÂªÃ—Â’Ã—Â™Ã—Â/Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â™Ã—Â©Ã—Â¨Ã—ÂÃ—ÂœÃ—Â™Ã—Â™Ã—Â Ã—Â™Ã—Â“Ã—Â•Ã—Â¢Ã—Â™Ã—Â
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

        # Ã—Â Ã—Â‘Ã—Â Ã—Â” Ã—ÂžÃ—Â‘Ã—Â Ã—Â” Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª
        filtered = {cat: [] for cat in keywords_map}
        if 'Other' not in filtered:
            filtered['Other'] = []

        # Ã—ÂžÃ—Â¢Ã—Â‘Ã—Â¨ Ã—Â¢Ã—Âœ Ã—Â›Ã—Âœ Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â
        for _category, channels in self.categories.items():
            for entry in channels:
                # Ã—Â—Ã—Â™Ã—ÂœÃ—Â•Ã—Â¥ Ã—Â©Ã—Â Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥
                if isinstance(entry, str) and ' (' in entry and entry.endswith(')'):
                    name = entry.split(' (', 1)[0].strip()
                else:
                    name = str(entry).strip()

                if _is_israeli_name(name):
                    cat = _best_category(name)
                    filtered[cat].append(entry)

        # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ UI
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
            "Ã—Â‘Ã—Â—Ã—Â¨ Ã—Â¡Ã—Â’Ã—Â Ã—Â•Ã—ÂŸ Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â",
            "Ã—Â‘Ã—Â—Ã—Â¨ Ã—ÂªÃ—Â¦Ã—Â•Ã—Â’Ã—Â”:",
            ["English Only", "Hebrew Only", "English | Hebrew"],
            2,
            False
        )
        if not ok:
            return

        # Ã—Â”Ã—ÂªÃ—Â—Ã—ÂœÃ—Âª Ã—Â¡Ã—Â¨Ã—Â’Ã—Âœ Ã—Â”Ã—ÂªÃ—Â§Ã—Â“Ã—ÂžÃ—Â•Ã—Âª
        self.progressDialog = QProgressDialog("Ã—ÂžÃ—ÂªÃ—Â¨Ã—Â’Ã—Â Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª...", "Ã—Â‘Ã—Â™Ã—Â˜Ã—Â•Ã—Âœ", 0, len(self.categories), self)
        self.progressDialog.setWindowTitle("Ã—ÂžÃ—ÂªÃ—Â¨Ã—Â’Ã—Â...")
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

        # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ EXTINF Ã—Â‘Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—Â”Ã—Â˜Ã—Â§Ã—Â¡Ã—Â˜
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
        QMessageBox.information(self, "Ã—Â‘Ã—Â•Ã—Â¦Ã—Â¢", f"Ã—Â©Ã—ÂžÃ—Â•Ã—Âª Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—ÂªÃ—Â•Ã—Â¨Ã—Â’Ã—ÂžÃ—Â• Ã—ÂœÃ—Â¤Ã—Â™: {mode}")

    def on_channels_translated(self, new_categories, mapping):
        # Ã—Â¡Ã—Â’Ã—Â™Ã—Â¨Ã—Âª Ã—Â”Ã—Â¤Ã—Â¨Ã—Â•Ã—Â’Ã—Â¨Ã—Â¡
        try:
            self.chProgress.close()
        except:
            pass

        # 1. Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ self.categories
        self.categories = new_categories

        # 2. Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ QListWidget Ã—Â©Ã—Âœ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª
        self.updateCategoryList()

        # 3. Ã—Â‘Ã—ÂªÃ—Â™Ã—Â‘Ã—Âª Ã—Â”Ã—Â˜Ã—Â§Ã—Â¡Ã—Â˜ (M3U Content) - Ã—Â Ã—Â—Ã—ÂœÃ—Â™Ã—Â£ Ã—Â©Ã—ÂžÃ—Â•Ã—Âª Ã—Â‘Ã–Â¾EXTINF
        content = self.textEdit.toPlainText().splitlines()
        out = []
        for line in content:
            if line.startswith("#EXTINF"):
                # Ã—Â Ã—Â—Ã—ÂœÃ—Â™Ã—Â£ Ã—Â›Ã—Âœ Ã—ÂžÃ—Â™Ã—Â¤Ã—Â•Ã—Â™ Ã—Â©Ã—Â™Ã—Â©
                for old, new in mapping.items():
                    # old Ã—Â‘Ã—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ "OldName (URL)" Ã¢Â‡Â’ Ã—Â©Ã—Â Ã—Â™Ã—Â©Ã—ÂŸ Ã—ÂÃ—Â—Ã—Â¨Ã—Â™ Ã—Â”Ã—Â¤Ã—Â¡Ã—Â™Ã—Â§
                    old_name = old.split(" (")[0]
                    new_name = new.split(" (")[0]
                    # Ã—ÂžÃ—Â—Ã—ÂœÃ—Â™Ã—Â¤Ã—Â™Ã—Â Ã—ÂÃ—Âª after-last-comma
                    if f",{old_name}" in line:
                        parts = line.rsplit(",", 1)
                        line = f"{parts[0]},{new_name}"
                        break
            out.append(line)
        self.safely_update_text_edit("\n".join(out))

        # 4. Ã—Â¨Ã—Â¢Ã—Â Ã—Â•Ã—ÂŸ UI Ã¢Â€Â“ Ã—Â Ã—Â‘Ã—Â—Ã—Â¨ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â¨Ã—ÂÃ—Â©Ã—Â•Ã—Â Ã—Â”
        if self.categoryList.count():
            self.categoryList.setCurrentRow(0)
            self.display_channels(self.categoryList.currentItem())

        # 5. Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—Â”Ã—ÂžÃ—Â—Ã—Â¨Ã—Â•Ã—Â–Ã—Â•Ã—Âª Ã—Â”Ã—ÂœÃ—Â•Ã—Â’Ã—Â™Ã—Â•Ã—Âª
        self.regenerateM3UTextOnly()

        QMessageBox.information(self, "Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â", "Ã—Â›Ã—Âœ Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂªÃ—Â•Ã—Â¨Ã—Â’Ã—ÂžÃ—Â• Ã—ÂœÃ—ÂÃ—Â Ã—Â’Ã—ÂœÃ—Â™Ã—Âª Ã—Â‘Ã—Â”Ã—Â¦Ã—ÂœÃ—Â—Ã—Â”!")

    def translateChannels(self):
        """Ã—Â“Ã—Â™Ã—ÂÃ—ÂœÃ—Â•Ã—Â’ Ã—ÂžÃ—Â©Ã—Â•Ã—Â¤Ã—Â¨ Ã—Â¢Ã—Â 3 Ã—ÂÃ—Â¤Ã—Â©Ã—Â¨Ã—Â•Ã—Â™Ã—Â•Ã—Âª"""
        dlg = QDialog(self)
        dlg.setWindowTitle("Ã—ÂªÃ—Â¨Ã—Â’Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â")
        dlg.setModal(True)
        dlg.setMinimumSize(400, 250)

        layout = QVBoxLayout(dlg)

        # Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨ Ã—ÂœÃ—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â Ã—Â•Ã—Â›Ã—Â—Ã—Â™Ã—Âª
        btn_current = QPushButton("Ã°ÂŸÂ“Â Ã—ÂªÃ—Â¨Ã—Â’Ã—Â Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â Ã—Â•Ã—Â›Ã—Â—Ã—Â™Ã—Âª")
        btn_current.clicked.connect(lambda: [dlg.accept(), self._translateCategory()])

        # Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨ Ã—ÂœÃ—Â‘Ã—Â—Ã—Â™Ã—Â¨Ã—Âª Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—ÂžÃ—Â¨Ã—Â•Ã—Â‘Ã—Â•Ã—Âª - Ã—Â—Ã—Â“Ã—Â©!
        btn_selected = QPushButton("Ã¢Â˜Â‘Ã¯Â¸Â Ã—ÂªÃ—Â¨Ã—Â’Ã—Â Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—Â Ã—Â‘Ã—Â—Ã—Â¨Ã—Â•Ã—Âª")
        btn_selected.setStyleSheet("background-color: #9b59b6; color: white;")
        btn_selected.clicked.connect(lambda: [dlg.accept(), self._translateSelectedCategories()])

        # Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨ Ã—ÂœÃ—Â›Ã—Âœ Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª
        btn_all = QPushButton("Ã°ÂŸÂŒÂ Ã—ÂªÃ—Â¨Ã—Â’Ã—Â Ã—ÂÃ—Âª Ã—Â›Ã—Âœ Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â")
        btn_all.clicked.connect(lambda: [dlg.accept(), self._translateAll()])

        layout.addWidget(btn_current)
        layout.addWidget(btn_selected)  # Ã—Â”Ã—Â—Ã—Â“Ã—Â©!
        layout.addWidget(btn_all)

        dlg.exec_()

    def _translateSelectedCategories(self):
        """Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—Â Ã—Â‘Ã—Â—Ã—Â¨Ã—Â•Ã—Âª Ã—Â‘Ã—ÂœÃ—Â‘Ã—Â“"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ã—Â‘Ã—Â—Ã—Â¨ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—ÂœÃ—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â")
        dialog.setMinimumSize(400, 500)

        layout = QVBoxLayout(dialog)

        # Ã—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Â” Ã—Â¢Ã—Â checkboxes
        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.MultiSelection)

        for category in self.categories.keys():
            item = QListWidgetItem(f"{category} ({len(self.categories[category])} Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â)")
            item.setCheckState(Qt.Unchecked)
            list_widget.addItem(item)

        layout.addWidget(QLabel("Ã—Â¡Ã—ÂžÃ—ÂŸ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—ÂœÃ—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â:"))
        layout.addWidget(list_widget)

        # Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨Ã—Â™ Ã—Â¤Ã—Â¢Ã—Â•Ã—ÂœÃ—Â”
        btn_layout = QHBoxLayout()

        select_all_btn = QPushButton("Ã—Â‘Ã—Â—Ã—Â¨ Ã—Â”Ã—Â›Ã—Âœ")
        select_all_btn.clicked.connect(lambda: [
            list_widget.item(i).setCheckState(Qt.Checked)
            for i in range(list_widget.count())
        ])

        deselect_all_btn = QPushButton("Ã—Â‘Ã—Â˜Ã—Âœ Ã—Â”Ã—Â›Ã—Âœ")
        deselect_all_btn.clicked.connect(lambda: [
            list_widget.item(i).setCheckState(Qt.Unchecked)
            for i in range(list_widget.count())
        ])

        translate_btn = QPushButton("Ã—ÂªÃ—Â¨Ã—Â’Ã—Â Ã—Â Ã—Â‘Ã—Â—Ã—Â¨Ã—Â•Ã—Âª")
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
                self._startFastTranslation(selected, f"Ã—ÂžÃ—ÂªÃ—Â¨Ã—Â’Ã—Â {len(selected)} Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª")
            else:
                QMessageBox.warning(dialog, "Ã—ÂÃ—Â–Ã—Â”Ã—Â¨Ã—Â”", "Ã—ÂœÃ—Â Ã—Â Ã—Â‘Ã—Â—Ã—Â¨Ã—Â• Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª")

        translate_btn.clicked.connect(start_translation)
        dialog.exec_()

    def _translateAll(self):
        """Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—Â›Ã—Âœ Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â - Ã—Â¢Ã—Â Ã—ÂÃ—Â•Ã—Â¤Ã—Â˜Ã—Â™Ã—ÂžÃ—Â™Ã—Â–Ã—Â¦Ã—Â™Ã—Â•Ã—Âª Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â•Ã—Âª"""
        if not self.categories:
            QMessageBox.information(self, "Ã—ÂžÃ—Â™Ã—Â“Ã—Â¢", "Ã—ÂÃ—Â™Ã—ÂŸ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—ÂœÃ—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â")
            return

        total_channels = sum(len(channels) for channels in self.categories.values())

        # Ã—ÂÃ—Â–Ã—Â”Ã—Â¨Ã—Â” Ã—ÂÃ—Â Ã—Â™Ã—Â© Ã—Â”Ã—Â¨Ã—Â‘Ã—Â” Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â
        if total_channels > 5000:
            reply = QMessageBox.question(
                self, "Ã—ÂÃ—Â–Ã—Â”Ã—Â¨Ã—Â”",
                f"Ã—Â™Ã—Â© {total_channels:,} Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂœÃ—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â.\n"
                f"Ã—Â”Ã—ÂªÃ—Â”Ã—ÂœÃ—Â™Ã—Âš Ã—Â¢Ã—ÂœÃ—Â•Ã—Âœ Ã—ÂœÃ—Â§Ã—Â—Ã—Âª Ã—Â–Ã—ÂžÃ—ÂŸ Ã—Â¨Ã—Â‘.\n"
                f"Ã—Â”Ã—ÂÃ—Â Ã—ÂœÃ—Â”Ã—ÂžÃ—Â©Ã—Â™Ã—Âš?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        self._startFastTranslation(self.categories, "Ã—ÂžÃ—ÂªÃ—Â¨Ã—Â’Ã—Â Ã—ÂÃ—Âª Ã—Â›Ã—Âœ Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â")

    def _startFastTranslation(self, categories_to_translate, status_message):
        """Ã—Â”Ã—ÂªÃ—Â—Ã—ÂœÃ—Âª Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—Â¢Ã—Â Ã—ÂÃ—Â•Ã—Â¤Ã—Â˜Ã—Â™Ã—ÂžÃ—Â™Ã—Â–Ã—Â¦Ã—Â™Ã—Â•Ã—Âª"""
        from PyQt5.QtCore import QThread, pyqtSignal

        class FastChannelTranslateThread(QThread):
            """Thread Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—ÂœÃ—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â¢Ã—Â batch processing"""
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
                    """Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—Â‘Ã—Â§Ã—Â‘Ã—Â•Ã—Â¦Ã—Â•Ã—Âª Ã—ÂœÃ—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â•Ã—Âª Ã—ÂžÃ—Â™Ã—Â˜Ã—Â‘Ã—Â™Ã—Âª"""
                    results = {}

                    # Ã—Â—Ã—ÂœÃ—Â•Ã—Â§Ã—Â” Ã—ÂœÃ—Â§Ã—Â‘Ã—Â•Ã—Â¦Ã—Â•Ã—Âª Ã—Â§Ã—Â˜Ã—Â Ã—Â•Ã—Âª
                    text_batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]

                    for batch in text_batches:
                        if self._stop_requested:
                            break

                        try:
                            # Ã—Â Ã—Â™Ã—Â¡Ã—Â™Ã—Â•Ã—ÂŸ Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â batch
                            translated_batch = translator.translate_batch(batch)
                            for original, translated in zip(batch, translated_batch):
                                results[original] = clean(translated) if translated else original
                        except:
                            # fallback Ã—ÂœÃ—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—Â™Ã—Â—Ã—Â™Ã—Â“ Ã—ÂÃ—Â batch Ã—Â Ã—Â›Ã—Â©Ã—Âœ
                            for text in batch:
                                try:
                                    time.sleep(0.1)  # Ã—Â”Ã—ÂžÃ—ÂªÃ—Â Ã—Â” Ã—Â§Ã—Â¦Ã—Â¨Ã—Â”
                                    result = translator.translate(text)
                                    results[text] = clean(result) if result else text
                                except:
                                    results[text] = text  # Ã—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Âª Ã—Â”Ã—ÂžÃ—Â§Ã—Â•Ã—Â¨ Ã—ÂÃ—Â Ã—Â Ã—Â›Ã—Â©Ã—Âœ

                    return results

                try:
                    # Ã—ÂÃ—ÂªÃ—Â—Ã—Â•Ã—Âœ Ã—ÂžÃ—ÂªÃ—Â¨Ã—Â’Ã—Â
                    translator_en = GoogleTranslator(source='auto', target='en')

                    # Ã—ÂÃ—Â™Ã—Â¡Ã—Â•Ã—Â£ Ã—Â›Ã—Âœ Ã—Â”Ã—Â˜Ã—Â§Ã—Â¡Ã—Â˜Ã—Â™Ã—Â Ã—Â©Ã—Â¦Ã—Â¨Ã—Â™Ã—Âš Ã—ÂœÃ—ÂªÃ—Â¨Ã—Â’Ã—Â
                    texts_to_translate = set()
                    channel_names = []

                    for channels in self.categories.values():
                        for channel in channels:
                            # Ã—Â—Ã—Â™Ã—ÂœÃ—Â•Ã—Â¥ Ã—Â©Ã—Â Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥
                            if " (" in channel and channel.endswith(")"):
                                name = channel.split(" (")[0].strip()
                            else:
                                name = channel.strip()

                            if name and not is_english(name):
                                texts_to_translate.add(name)

                            channel_names.append((channel, name))

                    self.progress.emit(0, "Ã—ÂžÃ—Â›Ã—Â™Ã—ÂŸ Ã—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Âª Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—ÂžÃ—Â™Ã—Â...", 0)

                    # Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â batch Ã—Â©Ã—Âœ Ã—Â›Ã—Âœ Ã—Â”Ã—Â˜Ã—Â§Ã—Â¡Ã—Â˜Ã—Â™Ã—Â
                    if texts_to_translate:
                        translation_cache = batch_translate(translator_en, list(texts_to_translate))
                        self.progress.emit(50, "Ã—ÂžÃ—Â™Ã—Â™Ã—Â©Ã—Â Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—ÂžÃ—Â™Ã—Â...", 50)
                    else:
                        translation_cache = {}

                    # Ã—Â™Ã—Â™Ã—Â©Ã—Â•Ã—Â Ã—Â”Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—ÂžÃ—Â™Ã—Â
                    updated_categories = {}
                    category_mapping = {}

                    total_categories = len(self.categories)

                    for i, (category_name, channels) in enumerate(self.categories.items()):
                        if self._stop_requested:
                            break

                        # Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—Â©Ã—Â Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â”
                        translated_category = translation_cache.get(category_name, category_name)

                        # Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â
                        translated_channels = []
                        for channel in channels:
                            if " (" in channel and channel.endswith(")"):
                                name = channel.split(" (")[0].strip()
                                url_part = channel.split(" (", 1)[1]

                                # Ã—Â©Ã—Â™Ã—ÂžÃ—Â•Ã—Â© Ã—Â‘cache Ã—ÂœÃ—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â
                                translated_name = translation_cache.get(name, name)
                                translated_channel = f"{translated_name} ({url_part}"
                            else:
                                translated_name = translation_cache.get(channel.strip(), channel)
                                translated_channel = translated_name

                            translated_channels.append(translated_channel)

                        # Ã—ÂÃ—Â™Ã—Â—Ã—Â•Ã—Â“ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—Â–Ã—Â”Ã—Â•Ã—Âª
                        if translated_category in updated_categories:
                            updated_categories[translated_category].extend(translated_channels)
                        else:
                            updated_categories[translated_category] = translated_channels

                        category_mapping[category_name] = translated_category

                        # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ progress
                        progress = ((i + 1) / total_categories) * 50 + 50
                        self.progress.emit(i + 1, f"Ã—ÂžÃ—Â¢Ã—Â‘Ã—Â“: {category_name[:30]}...", progress)

                    self.finished.emit(updated_categories, category_mapping)

                except Exception as e:
                    self.error.emit(f"Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â” Ã—Â‘Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â: {str(e)}")

        # Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—Â•Ã—Â”Ã—Â¨Ã—Â¦Ã—Âª Thread
        self.channel_translate_thread = FastChannelTranslateThread(categories_to_translate)

        # Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Progress Dialog
        progress_dialog = self._createTranslationProgressDialog(status_message)

        # Ã—Â—Ã—Â™Ã—Â‘Ã—Â•Ã—Â¨ Ã—Â¡Ã—Â™Ã—Â’Ã—Â Ã—ÂœÃ—Â™Ã—Â
        self.channel_translate_thread.progress.connect(progress_dialog.update_progress)
        self.channel_translate_thread.finished.connect(lambda categories, mapping: [
            progress_dialog.accept(),
            self._applyChannelTranslation(categories, mapping)
        ])
        self.channel_translate_thread.error.connect(lambda error: [
            progress_dialog.reject(),
            QMessageBox.critical(self, "Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â”", error)
        ])

        # Ã—Â”Ã—Â¦Ã—Â’Ã—Âª Dialog Ã—Â•Ã—Â”Ã—ÂªÃ—Â—Ã—ÂœÃ—Âª Thread
        progress_dialog.show()
        self.channel_translate_thread.start()

    def _createTranslationProgressDialog(self, title):
        """Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª dialog Ã—Â”Ã—ÂªÃ—Â§Ã—Â“Ã—ÂžÃ—Â•Ã—Âª Ã—ÂžÃ—Â•Ã—Â“Ã—Â¨Ã—Â Ã—Â™"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel
        from PyQt5.QtCore import Qt

        dialog = QDialog(self)
        dialog.setWindowTitle("Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â")
        dialog.setModal(True)
        dialog.setMinimumSize(400, 150)
        dialog.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)

        # Ã—ÂªÃ—Â•Ã—Â•Ã—Â™Ã—Âª Ã—Â¡Ã—Â˜Ã—Â˜Ã—Â•Ã—Â¡
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

        # Ã—Â¤Ã—Â¡ Ã—Â”Ã—ÂªÃ—Â§Ã—Â“Ã—ÂžÃ—Â•Ã—Âª
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

        # Ã—ÂªÃ—Â•Ã—Â•Ã—Â™Ã—Âª Ã—ÂÃ—Â—Ã—Â•Ã—Â–Ã—Â™Ã—Â Ã—Â•Ã—Â¤Ã—Â¨Ã—Â˜Ã—Â™Ã—Â
        details_label = QLabel("Ã—ÂžÃ—ÂªÃ—Â—Ã—Â™Ã—Âœ...")
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

        # Ã—Â¤Ã—Â•Ã—Â Ã—Â§Ã—Â¦Ã—Â™Ã—Â” Ã—ÂœÃ—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ
        def update_progress(processed, current_item, percentage):
            progress_bar.setValue(int(percentage))
            details_label.setText(f"{percentage:.1f}% - {current_item}")

            if percentage >= 100:
                status_label.setText("Ã¢ÂœÂ… Ã—Â”Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—Â”Ã—Â•Ã—Â©Ã—ÂœÃ—Â!")
                details_label.setText("Ã—Â¡Ã—Â•Ã—Â’Ã—Â¨...")

        dialog.update_progress = update_progress
        return dialog

    def _applyChannelTranslation(self, translated_categories, category_mapping):
        """Ã—Â™Ã—Â™Ã—Â©Ã—Â•Ã—Â Ã—ÂªÃ—Â•Ã—Â¦Ã—ÂÃ—Â•Ã—Âª Ã—Â”Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â - Ã—ÂžÃ—Â¢Ã—Â“Ã—Â›Ã—ÂŸ Ã—Â¨Ã—Â§ Ã—ÂÃ—Âª Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—Â©Ã—ÂªÃ—Â•Ã—Â¨Ã—Â’Ã—ÂžÃ—Â•"""

        # Ã—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Âª Ã—ÂžÃ—Â¦Ã—Â‘ Ã—ÂœÃ—Â¤Ã—Â Ã—Â™
        channels_before = sum(len(channels) for channels in self.categories.values())
        categories_before = len(self.categories)

        # Ã—Â‘Ã—ÂžÃ—Â§Ã—Â•Ã—Â Ã—ÂœÃ—Â”Ã—Â—Ã—ÂœÃ—Â™Ã—Â£ Ã—ÂÃ—Âª Ã—Â›Ã—Âœ self.categories, Ã—Â Ã—Â¢Ã—Â“Ã—Â›Ã—ÂŸ Ã—Â¨Ã—Â§ Ã—ÂÃ—Âª Ã—ÂžÃ—Â” Ã—Â©Ã—ÂªÃ—Â•Ã—Â¨Ã—Â’Ã—Â
        for old_category, new_category in category_mapping.items():
            if old_category in self.categories:
                # Ã—ÂÃ—Â Ã—Â”Ã—Â©Ã—Â Ã—Â”Ã—Â©Ã—ÂªÃ—Â Ã—Â”
                if old_category != new_category:
                    # Ã—Â”Ã—Â¢Ã—Â‘Ã—Â¨ Ã—ÂÃ—Âª Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂœÃ—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â”Ã—Â—Ã—Â“Ã—Â©Ã—Â”
                    if new_category in self.categories:
                        # Ã—ÂÃ—Â Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â”Ã—Â—Ã—Â“Ã—Â©Ã—Â” Ã—Â›Ã—Â‘Ã—Â¨ Ã—Â§Ã—Â™Ã—Â™Ã—ÂžÃ—Âª - Ã—ÂžÃ—Â–Ã—Â’
                        self.categories[new_category].extend(translated_categories[new_category])
                    else:
                        # Ã—Â¦Ã—Â•Ã—Â¨ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â—Ã—Â“Ã—Â©Ã—Â”
                        self.categories[new_category] = translated_categories[new_category]

                    # Ã—ÂžÃ—Â—Ã—Â§ Ã—ÂÃ—Âª Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â”Ã—Â™Ã—Â©Ã—Â Ã—Â”
                    del self.categories[old_category]
                else:
                    # Ã—ÂÃ—Â Ã—Â”Ã—Â©Ã—Â Ã—ÂœÃ—Â Ã—Â”Ã—Â©Ã—ÂªÃ—Â Ã—Â”, Ã—Â¨Ã—Â§ Ã—Â¢Ã—Â“Ã—Â›Ã—ÂŸ Ã—ÂÃ—Âª Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â
                    self.categories[old_category] = translated_categories[old_category]

        # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—Â”Ã—ÂªÃ—Â¦Ã—Â•Ã—Â’Ã—Â”
        self.cleanEmptyCategories()
        self.updateCategoryList()
        self.regenerateM3UTextOnly()

        if self.categoryList.count() > 0:
            self.categoryList.setCurrentRow(0)
            self.display_channels(self.categoryList.currentItem())

        # Ã—Â”Ã—Â¦Ã—Â’Ã—Âª Ã—ÂªÃ—Â•Ã—Â¦Ã—ÂÃ—Â•Ã—Âª
        channels_after = sum(len(channels) for channels in self.categories.values())
        categories_after = len(self.categories)

        QMessageBox.information(
            self, "Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—Â”Ã—Â•Ã—Â©Ã—ÂœÃ—Â",
            f"Ã¢ÂœÂ… Ã—ÂªÃ—Â•Ã—Â¨Ã—Â’Ã—ÂžÃ—Â• {len(category_mapping)} Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª\n"
            f"Ã°ÂŸÂ“ÂŠ Ã—Â¡Ã—Â”\"Ã—Â› Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â: {channels_after:,}"
        )

    def _translateCategory(self):
        # Ã—Â‘Ã—Â•Ã—Â—Ã—Â¨ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â”
        items = list(self.categories.keys())
        cat, ok = QInputDialog.getItem(self, "Ã—Â‘Ã—Â—Ã—Â¨ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â”", "Ã—ÂªÃ—Â¨Ã—Â’Ã—Â Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â”:", items, 0, False)
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
            QMessageBox.information(self, "Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â", "Ã—ÂÃ—Â™Ã—ÂŸ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂœÃ—ÂªÃ—Â¨Ã—Â’Ã—Â.")
            return

        # 1. Ã—Â™Ã—Â•Ã—Â¦Ã—Â¨Ã—Â™Ã—Â Ã—Â•Ã—Â©Ã—Â•Ã—ÂžÃ—Â¨Ã—Â™Ã—Â Ã—ÂÃ—Âª Ã—Â”Ã—Â“Ã—Â™Ã—ÂÃ—ÂœÃ—Â•Ã—Â’ Ã—Â‘Ã—ÂžÃ—Â©Ã—ÂªÃ—Â Ã—Â” Ã—Â©Ã—Âœ Ã—Â”Ã—ÂžÃ—Â•Ã—Â¤Ã—Â¢
        self.chProgress = QProgressDialog(
            "Ã—ÂžÃ—ÂªÃ—Â¨Ã—Â’Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â...",  # Ã—Â˜Ã—Â§Ã—Â¡Ã—Â˜ Ã—Â¨Ã—ÂÃ—Â©Ã—Â™
            "Ã—Â‘Ã—Â™Ã—Â˜Ã—Â•Ã—Âœ",  # Ã—Â˜Ã—Â§Ã—Â¡Ã—Â˜ Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨ Ã—Â‘Ã—Â™Ã—Â˜Ã—Â•Ã—Âœ
            0, total,  # Ã—Â˜Ã—Â•Ã—Â•Ã—Â— Ã—Â”Ã—Â¢Ã—Â¨Ã—Â›Ã—Â™Ã—Â
            self  # parent
        )
        self.chProgress.setWindowModality(Qt.WindowModal)
        self.chProgress.setWindowTitle("Ã—ÂªÃ–Â´Ã—Â¨Ã—Â’Ã—Â•Ã–Â¼Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â")
        self.chProgress.setMinimumDuration(0)  # Ã—ÂœÃ—Â”Ã—Â¦Ã—Â™Ã—Â’ Ã—ÂžÃ—Â™Ã—Â“
        self.chProgress.setAutoClose(True)  # Ã—ÂœÃ—Â¡Ã—Â’Ã—Â•Ã—Â¨ Ã—ÂÃ—Â•Ã—Â˜Ã—Â•Ã—ÂžÃ—Â˜Ã—Â™Ã—Âª Ã—Â‘Ã—Â”Ã—Â’Ã—Â¢Ã—Â” Ã—ÂœÃ—ÂžÃ—Â§Ã—Â¡Ã—Â™Ã—ÂžÃ—Â•Ã—Â
        self.chProgress.setAutoReset(True)  # Ã—ÂœÃ—ÂÃ—Â¤Ã—Â¡ Ã—ÂÃ—Âª Ã—Â”Ã—Â¢Ã—Â¨Ã—Âš Ã—ÂÃ—Â Ã—Â™Ã—Â•Ã—Â¤Ã—Â¢Ã—Âœ Ã—Â©Ã—Â•Ã—Â‘
        self.chProgress.canceled.connect(lambda: getattr(self, 'chThread', None) and self.chThread.terminate())
        self.chProgress.show()

        # 2. Ã—ÂÃ—ÂªÃ—Â—Ã—Â•Ã—Âœ Ã—Â”-QThread
        self.chThread = ChannelTranslateThread(cats_dict)
        # Ã—Â”Ã—Â¤Ã—Â¨Ã—Â“Ã—Âª Ã—Â”Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—ÂœÃ—Â¨Ã—Â¦Ã—Â£ Ã—Â§Ã—Â¨Ã—Â™Ã—ÂÃ—Â•Ã—Âª Ã—Â Ã—Â§Ã—Â™ Ã—Â™Ã—Â•Ã—ÂªÃ—Â¨
        self.chThread.progress.connect(self._update_translation_progress)
        # Ã—Â›Ã—Â©Ã—Â”Ã—Â¡Ã—ÂªÃ—Â™Ã—Â™Ã—Â Ã¢Â€Â“ Ã—Â Ã—Â¡Ã—Â’Ã—Â•Ã—Â¨ Ã—ÂÃ—Âª Ã—Â”-QProgressDialog Ã—Â•Ã—ÂÃ—Â– Ã—Â Ã—Â§Ã—Â¨Ã—Â Ã—ÂœÃ—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ UI
        self.chThread.finished.connect(lambda new_cats, mapping: (
            self.chProgress.setValue(self.chProgress.maximum()),
            self.chProgress.close(),
            self._onTranslated(new_cats, mapping, cats_dict)
        ))
        self.chThread.start()

    def _update_translation_progress(self, idx: int, name: str):
        """
        Ã—ÂžÃ—Â¢Ã—Â“Ã—Â›Ã—ÂŸ Ã—ÂÃ—Âª Ã—Â”Ã—Â¡Ã—Â¨Ã—Â’Ã—Âœ Ã—Â•Ã—ÂÃ—Âª Ã—Â”Ã—ÂªÃ—Â•Ã—Â•Ã—Â™Ã—Âª Ã—Â‘Ã—Â›Ã—Âœ Ã—ÂÃ—Â™Ã—Â¨Ã—Â•Ã—Â¢ Ã—Â¤Ã—Â¨Ã—Â•Ã—Â’Ã—Â¨Ã—Â¡
        """
        self.chProgress.setValue(idx)
        self.chProgress.setLabelText(f"Ã—ÂžÃ—ÂªÃ—Â¨Ã—Â’Ã—Â: {name} ({idx}/{self.chProgress.maximum()})")

    def _onTranslated(self, new_cats, mapping, orig_dict):
        # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—Â¨Ã—Â§ Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—Â©Ã—Â¢Ã—Â•Ã—Â‘Ã—Â“Ã—Â•
        for cat in orig_dict:
            self.categories[cat] = new_cats.get(cat, [])

        self.updateCategoryList()
        cur = self.categoryList.currentItem()
        if cur:
            self.display_channels(cur)

        # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—Â©Ã—ÂžÃ—Â•Ã—Âª Ã—Â‘Ã—ÂªÃ—Â•Ã—Âš #EXTINF Ã—Â‘Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—Â”Ã—Â’Ã—ÂœÃ—Â™Ã—ÂœÃ—Â™
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
        QMessageBox.information(self, "Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â", "Ã—Â”Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—Â”Ã—Â¡Ã—ÂªÃ—Â™Ã—Â™Ã—Â Ã—Â‘Ã—Â”Ã—Â¦Ã—ÂœÃ—Â—Ã—Â”.")

    def play_channel_with_name(self, entry):
        """
        Ã—ÂžÃ—Â¤Ã—Â¢Ã—Â™Ã—Âœ VLC Ã—Â¨Ã—Â§ Ã—Â¢Ã—Âœ Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—Â”Ã—Â™Ã—Â—Ã—Â™Ã—Â“ Ã—Â©Ã—Â‘Ã—Â—Ã—Â¨Ã—Â Ã—Â• (entry = "Name (URL)").
        Ã—Â”Ã—Â§Ã—Â•Ã—Â“ Ã—Â™Ã—Â“Ã—ÂÃ—Â’ Ã—ÂœÃ—Â‘Ã—Â Ã—Â•Ã—Âª Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ M3U Ã—ÂªÃ—Â§Ã—Â™Ã—ÂŸ Ã—Â¢Ã—Â #EXTM3U, Ã—Â©Ã—Â•Ã—Â¨Ã—Âª EXTINF Ã—Â Ã—Â›Ã—Â•Ã—Â Ã—Â” Ã—Â•Ã—Â©Ã—Â•Ã—Â¨Ã—Âª URL.
        Ã—Â’Ã—Â¨Ã—Â¡Ã—Â” Ã—ÂžÃ—ÂªÃ—Â•Ã—Â§Ã—Â Ã—Âª Ã—Â¢Ã—Â Ã—Â˜Ã—Â™Ã—Â¤Ã—Â•Ã—Âœ Ã—ÂžÃ—ÂœÃ—Â Ã—Â‘Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â•Ã—Âª.
        """
        try:
            # Ã—Â•Ã—Â™Ã—Â“Ã—Â•Ã—Â Ã—Â©Ã—Â–Ã—Â” Ã—ÂžÃ—Â—Ã—Â¨Ã—Â•Ã—Â–Ã—Âª
            if not isinstance(entry, str):
                entry = str(entry) if entry else ""

            if not entry.strip():
                QMessageBox.warning(self, "Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â”", "Ã—ÂœÃ—Â Ã—Â Ã—Â‘Ã—Â—Ã—Â¨ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—ÂªÃ—Â§Ã—Â™Ã—ÂŸ Ã—ÂœÃ—Â”Ã—Â¤Ã—Â¢Ã—ÂœÃ—Â”.")
                return

            # Ã—Â¤Ã—Â¢Ã—Â Ã—Â•Ã—Â— Ã—Â©Ã—Â Ã—Â•-URL Ã—Â¢Ã—Â Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Â•Ã—Âª Ã—Â‘Ã—Â˜Ã—Â™Ã—Â—Ã—Â•Ã—Âª
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
                    QMessageBox.warning(self, "Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â”", f"Ã—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—ÂœÃ—Â Ã—ÂªÃ—Â§Ã—Â™Ã—ÂŸ:\n{entry}")
                    return
            else:
                QMessageBox.warning(self, "Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â”", "Ã—ÂœÃ—Â Ã—Â Ã—Â™Ã—ÂªÃ—ÂŸ Ã—ÂœÃ—Â—Ã—ÂœÃ—Â¥ URL Ã—ÂžÃ—ÂªÃ—Â•Ã—Âš Ã—Â”Ã—Â¤Ã—Â¨Ã—Â™Ã—Â˜.")
                return

            # Ã—Â•Ã—Â™Ã—Â“Ã—Â•Ã—Â Ã—Â©Ã—Â™Ã—Â© Ã—Â©Ã—Â Ã—Â•URL Ã—ÂªÃ—Â§Ã—Â™Ã—Â Ã—Â™Ã—Â
            if not name or not url:
                QMessageBox.warning(self, "Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â”", "Ã—Â©Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—ÂÃ—Â• URL Ã—Â—Ã—Â¡Ã—Â¨Ã—Â™Ã—Â Ã—ÂÃ—Â• Ã—ÂœÃ—Â Ã—ÂªÃ—Â§Ã—Â™Ã—Â Ã—Â™Ã—Â.")
                return

            # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Â” Ã—Â‘Ã—Â¡Ã—Â™Ã—Â¡Ã—Â™Ã—Âª Ã—Â©Ã—Âœ URL
            if not any(url.lower().startswith(protocol) for protocol in
                       ['http://', 'https://', 'rtmp://', 'rtsp://', 'udp://']):
                reply = QMessageBox.question(
                    self, "URL Ã—ÂœÃ—Â Ã—ÂªÃ—Â§Ã—Â™Ã—ÂŸ",
                    f"Ã—Â”-URL Ã—Â Ã—Â¨Ã—ÂÃ—Â” Ã—ÂœÃ—Â Ã—ÂªÃ—Â§Ã—Â™Ã—ÂŸ:\n{url}\n\nÃ—Â”Ã—ÂÃ—Â Ã—ÂœÃ—Â”Ã—ÂžÃ—Â©Ã—Â™Ã—Âš Ã—Â‘Ã—Â›Ã—Âœ Ã—Â–Ã—ÂÃ—Âª?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return

            # Ã—Â Ã—Â¡Ã—Â™Ã—Â•Ã—ÂŸ Ã—ÂœÃ—Â§Ã—Â‘Ã—Âœ Ã—ÂÃ—Âª Ã—Â©Ã—Â•Ã—Â¨Ã—Âª Ã—Â”-EXTINF Ã—Â”Ã—ÂžÃ—Â§Ã—Â•Ã—Â¨Ã—Â™Ã—Âª Ã—ÂžÃ—Â”-lookup
            extinf_line = ""
            try:
                if hasattr(self, 'extinf_lookup') and self.extinf_lookup:
                    extinf_line = self.extinf_lookup.get(entry, "")
            except:
                pass

            if not extinf_line:
                # Ã—ÂÃ—Â Ã—ÂÃ—Â™Ã—ÂŸ, Ã—Â‘Ã—Â•Ã—Â Ã—Â™Ã—Â Ã—ÂÃ—Â—Ã—Âª Ã—Â™Ã—Â“Ã—Â Ã—Â™Ã—Âª
                logo = ""
                try:
                    logo = get_saved_logo(name) or ""
                except:
                    pass

                logo_tag = f' tvg-logo="{logo}"' if logo else ""

                # Ã—ÂžÃ—Â•Ã—Â¦Ã—ÂÃ—Â™Ã—Â Ã—ÂÃ—Âª Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â”Ã—Â Ã—Â•Ã—Â›Ã—Â—Ã—Â™Ã—Âª Ã—ÂœÃ—Â”Ã—Â¦Ã—Â‘Ã—Â” Ã—Â‘-group-title Ã—Â‘Ã—Â¦Ã—Â•Ã—Â¨Ã—Â” Ã—Â‘Ã—Â˜Ã—Â•Ã—Â—Ã—Â”
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

            # Ã—Â›Ã—Â•Ã—ÂªÃ—Â‘Ã—Â™Ã—Â Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ M3U Ã—Â–Ã—ÂžÃ—Â Ã—Â™
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
                    self, "Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â” Ã—Â‘Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—Â–Ã—ÂžÃ—Â Ã—Â™",
                    f"Ã—ÂœÃ—Â Ã—Â Ã—Â™Ã—ÂªÃ—ÂŸ Ã—ÂœÃ—Â™Ã—Â¦Ã—Â•Ã—Â¨ Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—Â–Ã—ÂžÃ—Â Ã—Â™:\n{e}"
                )
                return

            # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Âª Ã—Â§Ã—Â™Ã—Â•Ã—Â VLC Ã—Â‘Ã—Â Ã—ÂªÃ—Â™Ã—Â‘
            vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
            if not os.path.exists(vlc_path):
                # Ã—Â Ã—Â™Ã—Â¡Ã—Â™Ã—Â•Ã—ÂŸ Ã—ÂœÃ—Â—Ã—Â¤Ã—Â© VLC Ã—Â‘Ã—ÂžÃ—Â™Ã—Â§Ã—Â•Ã—ÂžÃ—Â™Ã—Â Ã—Â Ã—Â•Ã—Â¡Ã—Â¤Ã—Â™Ã—Â
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
                        self, "VLC Ã—ÂœÃ—Â Ã—Â Ã—ÂžÃ—Â¦Ã—Â",
                        f"Ã—ÂœÃ—Â Ã—Â Ã—ÂžÃ—Â¦Ã—Â VLC Ã—Â‘Ã—ÂÃ—Â£ Ã—ÂÃ—Â—Ã—Â“ Ã—ÂžÃ—Â”Ã—Â Ã—ÂªÃ—Â™Ã—Â‘Ã—Â™Ã—Â Ã—Â”Ã—Â‘Ã—ÂÃ—Â™Ã—Â:\n" +
                        "\n".join([vlc_path] + alternative_paths) +
                        "\n\nÃ—ÂÃ—Â Ã—Â Ã—Â”Ã—ÂªÃ—Â§Ã—ÂŸ VLC Ã—ÂÃ—Â• Ã—Â¢Ã—Â“Ã—Â›Ã—ÂŸ Ã—ÂÃ—Âª Ã—Â”Ã—Â Ã—ÂªÃ—Â™Ã—Â‘ Ã—Â‘Ã—Â§Ã—Â•Ã—Â“."
                    )
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                    return

            # Ã—Â”Ã—Â¤Ã—Â¢Ã—ÂœÃ—Âª VLC
            try:
                process = subprocess.Popen([vlc_path, temp_path])

                # Ã—Â”Ã—Â•Ã—Â“Ã—Â¢Ã—Âª Ã—Â”Ã—Â¦Ã—ÂœÃ—Â—Ã—Â” Ã—Â§Ã—Â¦Ã—Â¨Ã—Â”
                QMessageBox.information(
                    self, "VLC Ã—Â”Ã—Â•Ã—Â¤Ã—Â¢Ã—Âœ",
                    f"Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ '{name}' Ã—Â”Ã—Â•Ã—Â¤Ã—Â¢Ã—Âœ Ã—Â‘-VLC Ã—Â‘Ã—Â”Ã—Â¦Ã—ÂœÃ—Â—Ã—Â”!"
                )

            except Exception as e:
                QMessageBox.critical(
                    self, "Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â” Ã—Â‘Ã—Â”Ã—Â¤Ã—Â¢Ã—ÂœÃ—Âª VLC",
                    f"Ã—ÂœÃ—Â Ã—Â Ã—Â™Ã—ÂªÃ—ÂŸ Ã—ÂœÃ—Â”Ã—Â¤Ã—Â¢Ã—Â™Ã—Âœ VLC:\n{e}"
                )
                try:
                    os.remove(temp_path)
                except:
                    pass

        except Exception as e:
            error_msg = f"Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â” Ã—Â›Ã—ÂœÃ—ÂœÃ—Â™Ã—Âª Ã—Â‘Ã—Â”Ã—Â¤Ã—Â¢Ã—ÂœÃ—Âª Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥: {e}"
            print(f"[ERROR] {error_msg}")
            QMessageBox.critical(self, "Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â”", error_msg)

    def getCurrentEntry(self):
        """
        Ã—ÂžÃ—Â—Ã—Â–Ã—Â™Ã—Â¨Ã—Â” Ã—ÂÃ—Âª Ã—Â”-entry Ã—Â”Ã—Â Ã—Â•Ã—Â›Ã—Â—Ã—Â™ Ã—ÂžÃ—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Âª Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â,
        Ã—Â›Ã—Â¤Ã—Â™ Ã—Â©Ã—Â Ã—Â©Ã—ÂžÃ—Â¨ Ã—Â‘-UserRole Ã—Â›"Name (URL)".
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
        QMessageBox.information(self, "Logo Scan", "Ã¢ÂœÂ… Ã—Â¡Ã—Â¨Ã—Â™Ã—Â§Ã—Âª Ã—Â”Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â Ã—Â”Ã—Â•Ã—Â©Ã—ÂœÃ—ÂžÃ—Â” Ã—Â‘Ã—Â”Ã—Â¦Ã—ÂœÃ—Â—Ã—Â”!")

    def initUI(self):
        # Ã—Â›Ã—Â•Ã—ÂªÃ—Â¨Ã—Âª Ã—Â”Ã—Â—Ã—ÂœÃ—Â•Ã—ÂŸ Ã—Â•Ã—ÂžÃ—ÂÃ—Â¤Ã—Â™Ã—Â™Ã—Â Ã—Â™Ã—Â Ã—Â›Ã—ÂœÃ—ÂœÃ—Â™Ã—Â™Ã—Â
        self.setWindowTitle('M3U Playlist Editor')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowMinMaxButtonsHint |
                            Qt.WindowCloseButtonHint)

        # Ã—Â’Ã—Â•Ã—Â¤Ã—ÂŸ Ã—Â’Ã—ÂœÃ—Â•Ã—Â‘Ã—ÂœÃ—Â™
        font = QFont('Arial', 10)
        QApplication.setFont(font)

        # Ã—ÂœÃ—Â™Ã—Â™Ã—ÂÃ—ÂÃ—Â•Ã—Â˜ Ã—Â¨Ã—ÂÃ—Â©Ã—Â™
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # Ã¢Â”Â€Ã¢Â”Â€Ã¢Â”Â€ Ã—ÂœÃ—Â•Ã—Â’Ã—Â• Ã—Â¢Ã—ÂœÃ—Â™Ã—Â•Ã—ÂŸ Ã¢Â”Â€Ã¢Â”Â€Ã¢Â”Â€
        logo_frame = QFrame(self)
        logo_frame.setStyleSheet("background-color: black;")
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(0, 0, 0, 0)

        logo_label = QLabel(self)
        image_path = r'C:\Users\Master_PC\Desktop\IPtv_projects\Projects Eldad\M3u_Editor_EldadV1\Main Logo.jpg'
        if os.path.exists(image_path):
            pix = QPixmap(image_path).scaledToHeight(80, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
        else:
            logo_label.setText("Logo not found.")
        logo_label.setAlignment(Qt.AlignCenter)

        logo_layout.addWidget(logo_label)
        main_layout.addWidget(logo_frame)

        # Ã¢Â”Â€Ã¢Â”Â€Ã¢Â”Â€ Ã—Â©Ã—Â•Ã—Â¨Ã—Âª Ã—Â—Ã—Â™Ã—Â¤Ã—Â•Ã—Â© Ã¢Â”Â€Ã¢Â”Â€Ã¢Â”Â€
        self.searchBox = QLineEdit(self)
        self.searchBox.setPlaceholderText("Ã°ÂŸÂ”Â Ã—Â—Ã—Â™Ã—Â¤Ã—Â•Ã—Â© Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—ÂÃ—Â• Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥...")
        self.searchBox.textChanged.connect(self.handleSearchTextChanged)

        reset_btn = QPushButton("Ã°ÂŸÂ”Â„ Ã—ÂÃ—Â™Ã—Â¤Ã—Â•Ã—Â¡", self)
        reset_btn.setStyleSheet("padding:3px; font-weight:bold;")
        reset_btn.clicked.connect(lambda: self.searchBox.setText(""))

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.searchBox)
        search_layout.addWidget(reset_btn)
        main_layout.addLayout(search_layout)

        # Ã¢Â”Â€Ã¢Â”Â€Ã¢Â”Â€ Ã—Â›Ã—Â•Ã—ÂªÃ—Â¨Ã—Âª Ã—Â¨Ã—ÂÃ—Â©Ã—Â™Ã—Âª Ã¢Â”Â€Ã¢Â”Â€Ã¢Â”Â€
        title = QLabel("M3U Playlist Editor", self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size:25px; font-weight:bold; background-color:black; color:white;"
        )
        main_layout.addWidget(title)

        # Ã¢Â”Â€Ã¢Â”Â€Ã¢Â”Â€ Ã—ÂžÃ—Â™Ã—Â“Ã—Â¢ Ã—Â¢Ã—Âœ Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—Â•Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã¢Â”Â€Ã¢Â”Â€Ã¢Â”Â€
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

        # Ã¢Â”Â€Ã¢Â”Â€Ã¢Â”Â€ Ã—ÂÃ—Â–Ã—Â•Ã—Â¨Ã—Â™Ã—Â Ã—ÂÃ—Â—Ã—Â¨Ã—Â™Ã—Â (Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª, Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â, M3U content, Ã—Â›Ã—ÂœÃ—Â™Ã—Â) Ã¢Â”Â€Ã¢Â”Â€Ã¢Â”Â€
        main_layout.addLayout(self.create_category_section())
        main_layout.addLayout(self.create_channel_section())
        main_layout.addLayout(self.create_m3u_content_section())
        main_layout.addLayout(self.create_Tools())

        # Ã¢Â”Â€Ã¢Â”Â€Ã¢Â”Â€ Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨Ã—Â™ VLC (Play & Preview) Ã¢Â”Â€Ã¢Â”Â€Ã¢Â”Â€
        vlc_icon = QIcon("icons/vlc.png")

        vlc_layout = QHBoxLayout()

        # Ã¢Â–Â¶ Ã—Â Ã—Â’Ã—ÂŸ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—Â‘Ã—Â•Ã—Â“Ã—Â“
        self.playButton = QPushButton("Ã¢Â–Â¶ Ã—Â Ã—Â’Ã—ÂŸ Ã—Â‘Ã–Â¾VLC", self)
        self.playButton.setIcon(vlc_icon)
        self.playButton.setIconSize(QSize(24, 24))
        self.playButton.setStyleSheet(
            "background-color: navy; color: white; font-weight: bold;"
        )
        self.playButton.clicked.connect(
            lambda: self.play_channel_with_name(self.getCurrentEntry())
        )
        vlc_layout.addWidget(self.playButton)

        # Ã¢Â–Â¶ Preview Ã—ÂœÃ—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂžÃ—Â¨Ã—Â•Ã—Â‘Ã—Â™Ã—Â
        self.previewButton = QPushButton("Ã¢Â–Â¶ Ã—Â¦Ã—Â¤Ã—Â” Ã—Â‘Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â", self)
        self.previewButton.setIcon(vlc_icon)
        self.previewButton.setIconSize(QSize(24, 24))
        self.previewButton.setStyleSheet(
            "background-color: navy; color: white; font-weight: bold;"
        )
        self.previewButton.clicked.connect(self.previewSelectedChannels)
        vlc_layout.addWidget(self.previewButton)

        # Ã¢Â–Â¶ Translate Channels Ã¢Â†Â” Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨ Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â
        self.translateChannelsButton = QPushButton("Ã°ÂŸÂŒÂ Ã—ÂªÃ—Â¨Ã—Â’Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â", self)
        self.translateChannelsButton.setStyleSheet(
            "background-color: navy; color: white; font-weight: bold;"
        )
        vlc_layout.addWidget(self.translateChannelsButton)
        # Ã—Â‘Ã—Â¨Ã—Â’Ã—Â¢ Ã—Â©Ã—ÂœÃ—Â—Ã—Â™Ã—Â¦Ã—Â” Ã¢Â€Â“ Ã—Â Ã—Â¤Ã—ÂªÃ—Â— Ã—Â“Ã—Â™Ã—ÂÃ—ÂœÃ—Â•Ã—Â’ Ã—Â¤Ã—Â Ã—Â™Ã—ÂžÃ—Â™ Ã—Â¢Ã—Â 2 Ã—ÂÃ—Â¤Ã—Â©Ã—Â¨Ã—Â•Ã—Â™Ã—Â•Ã—Âª
        self.translateChannelsButton.clicked.connect(self.translateChannels)

        # Ã—Â‘Ã—Â¡Ã—Â•Ã—Â£, Ã—ÂžÃ—Â•Ã—Â¡Ã—Â™Ã—Â¤Ã—Â™Ã—Â Ã—ÂÃ—Âª vlc_layout Ã—ÂœÃ–Â¾main_layout
        main_layout.addLayout(vlc_layout)

        # Ã—ÂœÃ—Â—Ã—Â¦Ã—ÂŸ Checker Ã—Â•Ã—Â›Ã—Â“Ã—Â•Ã—ÂžÃ—Â”
        self.urlCheckButton = QPushButton('IPTV Checker', self)
        self.urlCheckButton.setStyleSheet("background-color: purple; color: white;")
        self.urlCheckButton.clicked.connect(self.openURLCheckerDialog)
        main_layout.addWidget(self.urlCheckButton)

        # Ã—Â•Ã—Â•Ã—Â™Ã—Â“Ã—Â•Ã—Â Ã—Â›Ã—Â•Ã—ÂªÃ—Â¨Ã—Âª EXTM3U
        self.textEdit.textChanged.connect(self.ensure_extm3u_header)

    def create_channel_section(self):
        """
        Ã—Â‘Ã—Â•Ã—Â Ã—Â” Ã—ÂÃ—Âª Ã—Â”Ã–Â¾UI Ã—ÂœÃ—Â˜Ã—Â™Ã—Â¤Ã—Â•Ã—Âœ Ã—Â‘Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â:
        - Ã—Â›Ã—Â•Ã—ÂªÃ—Â¨Ã—Âª
        - ComboBox Ã—ÂœÃ—ÂžÃ—Â™Ã—Â•Ã—ÂŸ
        - QListWidget Ã—ÂœÃ—Â”Ã—Â¦Ã—Â’Ã—Âª Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â
        - Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨Ã—Â™Ã—Â Ã—ÂœÃ—Â”Ã—Â•Ã—Â¡Ã—Â¤Ã—Â”/Ã—ÂžÃ—Â—Ã—Â™Ã—Â§Ã—Â”/Ã—Â”Ã—Â¢Ã—Â‘Ã—Â¨Ã—Â”/Ã—Â¢Ã—Â¨Ã—Â™Ã—Â›Ã—Â”/Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Âª Ã—Â›Ã—Â¤Ã—Â™Ã—ÂœÃ—Â•Ã—Â™Ã—Â•Ã—Âª
        """
        layout = QVBoxLayout()

        # Ã—Â›Ã—Â•Ã—ÂªÃ—Â¨Ã—Âª
        channel_title = QLabel("Channels", self)
        channel_title.setAlignment(Qt.AlignCenter)
        channel_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(channel_title)

        # ComboBox Ã—ÂœÃ—ÂžÃ—Â™Ã—Â•Ã—ÂŸ
        self.sortingComboBox = QComboBox(self)
        self.sortingComboBox.addItems([
            "Sort by Name A-Z",
            "Sort by Name Z-A",
            "Sort by Stream Type",
            "Sort by Group Title",
            "Sort by URL Length",
            "Sort by Quality (4K Ã¢Â†Â’ SD)"
        ])
        self.sortingComboBox.currentIndexChanged.connect(self.sortChannels)
        layout.addWidget(self.sortingComboBox)

        # Ã—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Âª Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â
        self.channelList = QListWidget(self)
        self.channelList.setSelectionMode(QListWidget.MultiSelection)
        self.channelList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.channelList.customContextMenuRequested.connect(self.open_channel_context_menu)
        layout.addWidget(self.channelList)

        # Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨Ã—Â™ Ã—Â¤Ã—Â¢Ã—Â•Ã—ÂœÃ—Â” Ã—ÂœÃ—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â
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

        layout.addLayout(button_layout)

        # Ã—Â—Ã—Â™Ã—Â‘Ã—Â•Ã—Â¨ Ã—ÂÃ—Â•Ã—ÂªÃ—Â•Ã—Âª (Signals) Ã—ÂœÃ—ÂžÃ—ÂªÃ—Â•Ã—Â“Ã—Â•Ã—Âª
        self.addChannelButton.clicked.connect(self.addChannel)
        self.deleteChannelButton.clicked.connect(self.deleteSelectedChannels)
        self.moveChannelUpButton.clicked.connect(self.moveChannelUp)
        self.moveChannelDownButton.clicked.connect(self.moveChannelDown)
        self.selectAllChannelsButton.clicked.connect(self.selectAllChannels)
        self.clearChannelsSelectionButton.clicked.connect(self.deselectAllChannels)
        self.moveSelectedChannelButton.clicked.connect(self.moveSelectedChannel)
        self.editSelectedChannelButton.clicked.connect(self.editSelectedChannel)
        # self.checkDoublesButton Ã—Â—Ã—Â•Ã—Â‘Ã—Â¨Ã—Â” Ã—Â›Ã—Â‘Ã—Â¨ Ã—ÂœÃ—Â¢Ã—Â™Ã—Âœ

        return layout

    def inject_logo(self, line, channel_name, logo_db=None):
        """
        Injects saved logo into a #EXTINF line if missing.
        logo_db - optional dictionary to speed up repeated calls
        """
        # Ã—ÂÃ—Â Ã—Â›Ã—Â‘Ã—Â¨ Ã—Â§Ã—Â™Ã—Â™Ã—Â Ã—ÂªÃ—Â’ tvg-logo Ã—Â‘Ã—Â©Ã—Â•Ã—Â¨Ã—Â”, Ã—ÂœÃ—Â Ã—Â¢Ã—Â•Ã—Â©Ã—Â™Ã—Â Ã—Â›Ã—ÂœÃ—Â•Ã—Â
        if 'tvg-logo="' in line:
            return line

        # Ã—Â©Ã—ÂœÃ—Â™Ã—Â¤Ã—Âª Ã—ÂœÃ—Â•Ã—Â’Ã—Â• Ã—ÂžÃ—Â”-DB Ã—ÂÃ—Â Ã—ÂœÃ—Â Ã—Â”Ã—Â•Ã—Â¢Ã—Â‘Ã—Â¨ Ã—ÂœÃ—Â•Ã—Â’Ã—Â• Ã—ÂžÃ—Â‘Ã—Â—Ã—Â•Ã—Â¥
        if logo_db is None:
            # Ã—Â©Ã—Â™Ã—ÂžÃ—Â•Ã—Â© Ã—Â‘Ã—Â§Ã—Â¨Ã—Â™Ã—ÂÃ—Â” Ã—Â”Ã—Â Ã—Â›Ã—Â•Ã—Â Ã—Â”: get_saved_logo Ã—ÂžÃ—Â§Ã—Â‘Ã—ÂœÃ—Âª Ã—Â¨Ã—Â§ Ã—ÂÃ—Â¨Ã—Â’Ã—Â•Ã—ÂžÃ—Â Ã—Â˜ Ã—ÂÃ—Â—Ã—Â“
            logo = get_saved_logo(channel_name)
        else:
            logo = logo_db.get(channel_name)
            if isinstance(logo, list):
                logo = logo[0] if logo else None
            elif not isinstance(logo, str):
                logo = None

        # Ã—ÂÃ—Â Ã—ÂžÃ—Â¦Ã—ÂÃ—Â Ã—Â• URL Ã—ÂœÃ—Â•Ã—Â’Ã—Â• Ã—ÂªÃ—Â§Ã—Â™Ã—ÂŸ, Ã—ÂžÃ—Â©Ã—Â‘Ã—Â¦Ã—Â™Ã—Â Ã—ÂÃ—Â•Ã—ÂªÃ—Â• Ã—Â‘-EXTINF
        if logo and isinstance(logo, str) and logo.startswith("http"):
            return line.replace(
                "#EXTINF:-1",
                f'#EXTINF:-1 tvg-logo="{logo}"'
            )

        # Ã—ÂÃ—Â Ã—ÂœÃ—Â Ã—ÂžÃ—Â¦Ã—ÂÃ—Â Ã—Â• Ã—ÂœÃ—Â•Ã—Â’Ã—Â•, Ã—ÂžÃ—Â—Ã—Â–Ã—Â™Ã—Â¨Ã—Â™Ã—Â Ã—ÂÃ—Âª Ã—Â”Ã—Â©Ã—Â•Ã—Â¨Ã—Â” Ã—Â”Ã—ÂžÃ—Â§Ã—Â•Ã—Â¨Ã—Â™Ã—Âª Ã—ÂœÃ—ÂœÃ—Â Ã—Â©Ã—Â™Ã—Â Ã—Â•Ã—Â™
        return line

    def exportM3UWithFullData(self, output_path):
        """
        Ã—Â’Ã—Â¨Ã—Â¡Ã—Â” Ã—ÂžÃ—Â©Ã—Â•Ã—Â¤Ã—Â¨Ã—Âª Ã—ÂœÃ—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Âª Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ M3U Ã—Â”Ã—Â›Ã—Â•Ã—ÂœÃ—ÂœÃ—Âª:
        - EXTINF Ã—ÂžÃ—ÂœÃ—Â Ã—Â›Ã—Â•Ã—ÂœÃ—Âœ tvg-id, group-title, Ã—ÂœÃ—Â•Ã—Â’Ã—Â•
        - Ã—Â©Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—ÂžÃ—ÂœÃ—Â
        - Ã—ÂœÃ—Â™Ã—Â Ã—Â§ Ã—ÂžÃ—Â§Ã—Â•Ã—Â¨Ã—Â™
        - Ã—Â©Ã—Â™Ã—ÂžÃ—Â•Ã—Â© Ã—Â‘Ã—Â˜Ã—Â•Ã—Â— Ã—Â‘Ã—ÂžÃ—Â¤Ã—Â•Ã—Âª lookup, Ã—ÂœÃ—ÂœÃ—Â Ã—ÂªÃ—ÂœÃ—Â•Ã—Âª Ã—Â‘Ã—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ Ã—ÂžÃ—Â—Ã—Â¨Ã—Â•Ã—Â–Ã—Âª
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

                    # Ã—Â©Ã—ÂœÃ—Â™Ã—Â¤Ã—Âª Ã—Â©Ã—Â•Ã—Â¨Ã—Âª EXTINF Ã—ÂžÃ—ÂœÃ—ÂÃ—Â”
                    extinf_line = self.extinf_lookup.get(name)
                    if not extinf_line:
                        extinf_line = f"#EXTINF:-1,{name}"

                    # Ã—Â”Ã—Â–Ã—Â¨Ã—Â§Ã—Âª Ã—ÂœÃ—Â•Ã—Â’Ã—Â• Ã—ÂœÃ—Â¤Ã—Â™ Ã—Â©Ã—Â
                    extinf_line = self.inject_logo(extinf_line, name, logo_db)

                    # Ã—Â©Ã—ÂœÃ—Â™Ã—Â¤Ã—Âª Ã—ÂœÃ—Â™Ã—Â Ã—Â§ Ã—ÂžÃ—Â”Ã–Â¾map Ã—ÂÃ—Â Ã—Â Ã—Â©Ã—ÂžÃ—Â¨Ã—Â”
                    url = self.urls.get(name)

                    # Ã—Â’Ã—Â™Ã—Â‘Ã—Â•Ã—Â™ - Ã—Â¤Ã—Â¢Ã—Â Ã—Â•Ã—Â— Ã—ÂžÃ—ÂªÃ—Â•Ã—Âš Ã—Â”Ã—Â©Ã—Â Ã—ÂÃ—Â Ã—Â Ã—Â“Ã—Â¨Ã—Â©
                    if not url and " (" in name:
                        url = name.split(" (")[-1].strip(")")
                        name = name.split(" (")[0].strip()

                    if not url:
                        print(f"Ã¢ÂšÂ Ã¯Â¸Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ '{name}' Ã—ÂœÃ—Â Ã—Â›Ã—Â•Ã—ÂœÃ—Âœ URL, Ã—Â“Ã—Â™Ã—ÂœÃ—Â•Ã—Â’.")
                        continue

                    out.write(extinf_line + "\n")
                    out.write(url + "\n")

    def openM3UConverterDialog(self):
        from PyQt5.QtCore import Qt
        # Ã—Â™Ã—Â•Ã—Â¦Ã—Â¨Ã—Â™Ã—Â Ã—ÂÃ—Âª Ã—Â”Ã—Â“Ã—Â™Ã—ÂÃ—ÂœÃ—Â•Ã—Â’ Ã—Â•Ã—ÂžÃ—Â•Ã—Â•Ã—Â“Ã—ÂÃ—Â™Ã—Â Ã—Â©Ã—Â”Ã—Â•Ã—Â Ã—Â™Ã—Â™Ã—ÂžÃ—Â—Ã—Â§ Ã—ÂÃ—Â•Ã—Â˜Ã—Â•Ã—ÂžÃ—Â˜Ã—Â™Ã—Âª Ã—Â‘Ã—Â¡Ã—Â’Ã—Â™Ã—Â¨Ã—Â”
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

            # Ã—Â¡Ã—Â•Ã—Â’Ã—Â¨Ã—Â™Ã—Â Ã—Â“Ã—Â¨Ã—Âš accept() Ã—Â›Ã—Â“Ã—Â™ Ã—Â©Ã—Â”-deleteLater Ã—Â™Ã—Â¢Ã—Â‘Ã—Â•Ã—Â“
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

        # Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨ Ã—Â˜Ã—Â¢Ã—Â™Ã—Â Ã—Âª Ã—Â§Ã—Â‘Ã—Â¦Ã—Â™Ã—Â Ã—ÂžÃ—Â§Ã—Â•Ã—ÂžÃ—Â™Ã—Â™Ã—Â Ã—Â•Ã—Â˜Ã—Â¢Ã—Â™Ã—Â Ã—Â” Ã—ÂžÃ—Â™Ã—Â™Ã—Â“Ã—Â™Ã—Âª
        load_files_button = QPushButton("Ã°ÂŸÂ“Â‚ UPLOAD FROM DRIVE", dialog)
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
                    QMessageBox.warning(dialog, "File Error", f"Ã¢ÂÂŒ Failed to load {path}:\n{str(e)}")

            self.loadM3UFromText(combined_content, append=False)
            QMessageBox.information(dialog, "Success", "All selected M3U files were loaded into the editor.")
            dialog.close()

        load_files_button.clicked.connect(handle_load_local_files)

        # Ã—Â”Ã—Â“Ã—Â‘Ã—Â§Ã—Â” Ã—Â—Ã—Â›Ã—ÂžÃ—Â” + Ã—ÂžÃ—Â¢Ã—Â‘Ã—Â¨ Ã—Â©Ã—Â•Ã—Â¨Ã—Â”
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

        # Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨ Ã—Â”Ã—Â•Ã—Â¨Ã—Â“Ã—Âª URL Ã—ÂžÃ—Â¨Ã—Â•Ã—Â‘Ã—Â™Ã—Â - Ã—Â Ã—Â©Ã—ÂÃ—Â¨ Ã—ÂœÃ—ÂžÃ—Â™ Ã—Â©Ã—Â¨Ã—Â•Ã—Â¦Ã—Â” Ã—Â“Ã—Â¨Ã—Âš URL
        download_button = QPushButton("C0nvert URL ", dialog)
        download_button.setStyleSheet("background-color: red; color: white;")
        layout.addWidget(download_button)

        # Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨ Ã—Â¡Ã—Â’Ã—Â™Ã—Â¨Ã—Â”
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
                    session = setup_session()  # Ã¢Â†Â Ã—Â—Ã—Â“Ã—Â©
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
                    print(f"Failed to download: {url} Ã¢Â€Â” {e}")

            if valid_count == 0:
                QMessageBox.warning(dialog, "No Valid URLs", "None of the URLs were valid M3U files.")
                return

            choice = QMessageBox.question(
                dialog,
                "Ã°ÂŸÂ“Â¥ Load All?",
                f"<b style='font-size:14px;'>Ã¢ÂœÂ… <u>{valid_count} M3U files</u> downloaded successfully.</b><br><br>"
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
                "Ã°ÂŸÂ“Â¦ Save Merged File?",
                f"<b style='font-size:14px;'>Ã°ÂŸÂ’Â¾ Do you want to save all <u>{valid_count} files</u> as one merged M3U file?</b>",
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

                        # Ã¢ÂœÂ… Ã—Â›Ã—ÂÃ—ÂŸ Ã—Â”Ã—ÂªÃ—Â™Ã—Â§Ã—Â•Ã—ÂŸ: Ã—Â Ã—Â•Ã—Â¡Ã—Â™Ã—Â£ Ã—Â Ã—Â™Ã—Â§Ã—Â•Ã—Â™ Ã—Â©Ã—Â•Ã—Â¨Ã—Â•Ã—Âª Ã—Â¨Ã—Â™Ã—Â§Ã—Â•Ã—Âª Ã—Â’Ã—Â Ã—Â‘Ã—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Â” Ã—Â Ã—Â¤Ã—Â¨Ã—Â“Ã—Âª:
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
        Ã—Â˜Ã—Â•Ã—Â¢Ã—ÂŸ Ã—Â˜Ã—Â§Ã—Â¡Ã—Â˜ M3U, Ã—Â“Ã—Â•Ã—ÂÃ—Â’ Ã—Â©Ã—ÂªÃ—ÂžÃ—Â™Ã—Â“ Ã—ÂªÃ—Â”Ã—Â™Ã—Â” Ã—Â©Ã—Â•Ã—Â¨Ã—Âª EXTM3U Ã—Â¢Ã—Â tvg-url,
        Ã—ÂžÃ—Â Ã—Â¡Ã—Â” Ã—Â¢Ã—Â‘Ã—Â¨Ã—Â™Ã—Âª Ã—ÂªÃ—Â—Ã—Â™Ã—ÂœÃ—Â”, Ã—Â•Ã—ÂžÃ—ÂªÃ—Â¢Ã—Â“ Ã—ÂžÃ—ÂÃ—Â™Ã—Â¤Ã—Â” Ã—Â Ã—ÂÃ—Â¡Ã—Â¤Ã—Â• Ã—Â§Ã—Â™Ã—Â©Ã—Â•Ã—Â¨Ã—Â™ Ã—Â”-EPG.
        """
        import threading

        # Ã—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Â” Ã—Â©Ã—Âœ Ã—Â”Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—Â”Ã—ÂÃ—Â—Ã—Â¨Ã—Â•Ã—ÂŸ Ã—Â¢Ã—Â‘Ã—Â•Ã—Â¨ Ã—Â¤Ã—Â•Ã—Â Ã—Â§Ã—Â¦Ã—Â™Ã—Â•Ã—Âª Ã—ÂžÃ—Â©Ã—ÂœÃ—Â™Ã—ÂžÃ—Â•Ã—Âª
        self.last_loaded_m3u = content

        # Ã—ÂÃ—Â Ã—ÂœÃ—Â append Ã—ÂžÃ—Â Ã—Â§Ã—Â™Ã—Â Ã—ÂÃ—Âª Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª
        if not append:
            self.categories.clear()

        # Ã—Â Ã—Â™Ã—Â”Ã—Â•Ã—Âœ meta Ã—ÂœÃ—ÂžÃ—Â§Ã—Â•Ã—Â¨Ã—Â•Ã—Âª EPG Ã—Â”Ã—ÂÃ—Â—Ã—Â¨Ã—Â•Ã—Â Ã—Â™Ã—Â
        if not hasattr(self, "last_epg_sources") or not append:
            self.last_epg_sources = []  # Ã—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Âª Ã—ÂžÃ—Â—Ã—Â¨Ã—Â•Ã—Â–Ã—Â•Ã—Âª Ã—ÂªÃ—Â™Ã—ÂÃ—Â•Ã—Â¨ Ã—ÂžÃ—Â§Ã—Â•Ã—Â¨ Ã—Â”-EPG

        # ----- 1) Ã—Â Ã—Â™Ã—Â”Ã—Â•Ã—Âœ EPG headers -----
        # Ã—ÂÃ—ÂªÃ—Â—Ã—Â•Ã—Âœ self.epg_headers Ã—Â‘Ã—Â¤Ã—Â¢Ã—Â Ã—Â”Ã—Â¨Ã—ÂÃ—Â©Ã—Â•Ã—Â Ã—Â” (Ã—ÂÃ—Â• Ã—Â‘Ã—Â›Ã—Âœ load Ã—ÂžÃ—Â—Ã—Â“Ã—Â©)
        if not hasattr(self, "epg_headers") or not append:
            self.epg_headers = []

        # Ã—Â©Ã—ÂœÃ—Â‘ 1: Ã—ÂÃ—Â¡Ã—Â•Ã—Â£ Ã—ÂÃ—Âª Ã—Â›Ã—Âœ Ã—Â”-EPG headers Ã—Â›Ã—Â¤Ã—Â™ Ã—Â©Ã—Â”Ã—Â Ã—Â‘Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥
        detected_epg_headers = []
        for line in content.splitlines():  # splitlines() Ã—ÂœÃ—ÂœÃ—Â strip
            if line.startswith("#EXTM3U") and ("url-tvg=" in line or "x-tvg-url=" in line or "tvg-url=" in line):
                detected_epg_headers.append(line.strip())

        # Ã—Â©Ã—ÂœÃ—Â‘ 2: Ã—Â”Ã—Â•Ã—Â¡Ã—Â¤Ã—Âª headers Ã—Â™Ã—Â™Ã—Â—Ã—Â•Ã—Â“Ã—Â™Ã—Â™Ã—Â (Ã—ÂÃ—Â™Ã—Â—Ã—Â•Ã—Â“)
        for header in detected_epg_headers:
            if header not in self.epg_headers:
                self.epg_headers.append(header)

        if detected_epg_headers:
            self.last_epg_sources.append("EPG Ã—ÂžÃ—Â”Ã—Â›Ã—Â•Ã—ÂªÃ—Â¨Ã—Âª Ã—Â‘Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥")

        # Ã—ÂÃ—Â Ã—ÂÃ—Â™Ã—ÂŸ Ã—ÂÃ—Â£ header Ã—Â–Ã—ÂžÃ—Â™Ã—ÂŸ, Ã—Â Ã—Â Ã—Â¡Ã—Â” 2 Ã—ÂžÃ—Â¡Ã—ÂœÃ—Â•Ã—ÂœÃ—Â™Ã—Â Ã—ÂœÃ—Â¤Ã—Â Ã—Â™ merge_or_fix_epg:
        #   Ã—Â. Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ sidecar Ã—Â¢Ã—Â Ã—ÂÃ—Â•Ã—ÂªÃ—Â• Ã—Â©Ã—Â Ã—Â‘Ã—Â¡Ã—Â™Ã—Â¡ (xml Ã—ÂÃ—Â• xml.gz) => Ã—Â Ã—Â‘Ã—Â Ã—Â” tvg-url Ã—ÂžÃ—ÂžÃ—Â Ã—Â•
        #   Ã—Â‘. Ã—ÂÃ—Â Ã—Â’Ã—Â Ã—Â–Ã—Â” Ã—ÂœÃ—Â Ã—Â§Ã—Â™Ã—Â™Ã—Â, Ã—Â Ã—Â©Ã—ÂªÃ—ÂžÃ—Â© Ã—Â‘-merge_or_fix_epg Ã—Â›Ã—Â“Ã—Â™ Ã—ÂœÃ—ÂÃ—Â—Ã—Â“ Ã—Â¡Ã—Â¤Ã—Â§Ã—Â™Ã—Â Ã—ÂžÃ—Â•Ã—Â›Ã—Â¨Ã—Â™Ã—Â
        if not self.epg_headers:
            sidecar_urls = self._try_load_sidecar_epg()
            if sidecar_urls:
                # Ã—Â‘Ã—Â Ã—Â” header Ã—Â—Ã—Â“Ã—Â© Ã—Â¢Ã—Âœ Ã—Â‘Ã—Â¡Ã—Â™Ã—Â¡ sidecar
                new_hdr = '#EXTM3U tvg-url="' + ",".join(sidecar_urls) + '"'
                self.epg_headers.append(new_hdr)
                self.last_epg_sources.append("EPG Ã—ÂžÃ—Â§Ã—Â•Ã—Â‘Ã—Â¥ sidecar Ã—ÂžÃ—Â§Ã—Â•Ã—ÂžÃ—Â™")
            else:
                # Ã—ÂÃ—Â™Ã—Â—Ã—Â•Ã—Â“/Ã—Â–Ã—Â™Ã—Â”Ã—Â•Ã—Â™ Ã—ÂÃ—Â•Ã—Â˜Ã—Â•Ã—ÂžÃ—Â˜Ã—Â™ Ã—ÂžÃ—ÂªÃ—Â•Ã—Âš Ã—Â¡Ã—Â¤Ã—Â§Ã—Â™Ã—Â
                try:
                    self.merge_or_fix_epg(content=content, prefer_hebrew=True, update_only=True)
                    if self.epg_headers:
                        self.last_epg_sources.append("EPG Ã—Âž-EPG_providers_full.json")
                except Exception:
                    # Ã—ÂÃ—Â Ã—Â Ã—Â›Ã—Â©Ã—Âœ, Ã—Â Ã—ÂžÃ—Â©Ã—Â™Ã—Âš Ã—Â’Ã—Â Ã—Â‘Ã—ÂœÃ—Â™ EPG Ã—Â›Ã—Â“Ã—Â™ Ã—ÂœÃ—Â Ã—ÂœÃ—Â—Ã—Â¡Ã—Â•Ã—Â Ã—Â˜Ã—Â¢Ã—Â™Ã—Â Ã—Â”
                    pass

        # ----- 3) Ã—Â Ã—Â™Ã—Â§Ã—Â•Ã—Â™ Ã—Â›Ã—Âœ Ã—Â©Ã—Â•Ã—Â¨Ã—Â•Ã—Âª EXTM3U Ã—Â”Ã—ÂžÃ—Â§Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—ÂžÃ—Â”Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ -----
        lines = [line for line in content.splitlines() if not line.startswith("#EXTM3U")]

        # ----- 4) Ã—Â‘Ã—Â Ã—Â™Ã—Â™Ã—Âª Ã—Â©Ã—Â•Ã—Â¨Ã—Âª EXTM3U Ã—ÂÃ—Â—Ã—Â™Ã—Â“Ã—Â” Ã—Â¢Ã—Â Ã—Â¢Ã—Â“Ã—Â™Ã—Â¤Ã—Â•Ã—Âª Ã—ÂœÃ—Â¢Ã—Â‘Ã—Â¨Ã—Â™Ã—Âª -----
        unified_header = self.buildUnifiedEPGHeader()

        # Ã—ÂžÃ—Â™Ã—Â–Ã—Â•Ã—Â’ Ã—ÂœÃ—Â›Ã—Â“Ã—Â™ Ã—Â˜Ã—Â§Ã—Â¡Ã—Â˜ Ã—Â¡Ã—Â•Ã—Â¤Ã—Â™ Ã—ÂœÃ—Â”Ã—Â¦Ã—Â’Ã—Â” Ã—Â•Ã—ÂœÃ—Â¢Ã—Â™Ã—Â‘Ã—Â•Ã—Â“
        content2 = unified_header + "\n\n" + "\n".join(lines)

        # ----- 5) Ã—Â¤Ã—Â¨Ã—Â¡ Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ M3U -----
        self.parseM3UContentEnhanced(content2)
        self.updateCategoryList()
        self.buildSearchCompleter()

        # ----- 6) Ã—Â‘Ã—Â—Ã—Â™Ã—Â¨Ã—Âª Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â¨Ã—ÂÃ—Â©Ã—Â•Ã—Â Ã—Â” -----
        if self.categoryList.count() > 0:
            self.categoryList.setCurrentRow(0)
            self.display_channels(self.categoryList.currentItem())

        # ----- 7) Ã—Â¡Ã—Â¨Ã—Â™Ã—Â§Ã—Âª Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â Ã—Â‘Ã—Â¨Ã—Â§Ã—Â¢ -----
        threading.Thread(
            target=self.extract_and_save_logos_for_all_channels,
            args=(content2,),
            daemon=True
        ).start()


    def extract_and_save_logos_for_all_channels(self, content):
        """
        Ã—Â¡Ã—Â¨Ã—Â™Ã—Â§Ã—Â” Ã—Â—Ã—Â›Ã—ÂžÃ—Â” Ã¢Â€Â“ Ã—Â©Ã—Â•Ã—ÂžÃ—Â¨Ã—Âª Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â Ã—Â¨Ã—Â§ Ã—ÂÃ—Â Ã—Â”Ã—Â Ã—ÂœÃ—Â Ã—Â§Ã—Â™Ã—Â™Ã—ÂžÃ—Â™Ã—Â, Ã—Â©Ã—Â•Ã—ÂžÃ—Â¨Ã—Âª Ã—Â¤Ã—Â¢Ã—Â Ã—ÂÃ—Â—Ã—Âª Ã—Â‘Ã—Â¡Ã—Â•Ã—Â£.
        """
        try:
            logo_db = {}
            if os.path.exists(LOGO_DB_PATH):
                with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                    logo_db = json.load(f)

            seen = set()
            updated = False  # Ã—Â Ã—Â“Ã—Â¢ Ã—ÂÃ—Â Ã—Â‘Ã—Â›Ã—ÂœÃ—Âœ Ã—Â Ã—Â•Ã—Â¡Ã—Â¤Ã—Â• Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â

            lines = content.strip().splitlines()
            for i in range(len(lines)):
                if lines[i].startswith("#EXTINF:"):
                    name_match = re.search(r",(.+)", lines[i])
                    channel_name = name_match.group(1).strip() if name_match else ""

                    logo_match = re.search(r'tvg-logo="([^"]+)"', lines[i])
                    logo_url = logo_match.group(1).strip() if logo_match else ""

                    if not channel_name or not logo_url:
                        continue

                    # Ã—Â•Ã—Â“Ã—Â Ã—Â©Ã—ÂÃ—Â™Ã—ÂŸ Ã—Â›Ã—Â¤Ã—Â™Ã—ÂœÃ—Â•Ã—Â™Ã—Â•Ã—Âª
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
                        print(f"[LOGO] Ã¢ÂœÂ… {channel_name} | {logo_url}")

            if updated:
                with open(LOGO_DB_PATH, "w", encoding="utf-8") as f:
                    json.dump(logo_db, f, indent=2, ensure_ascii=False)
                print("[LOGO] Ã¢ÂœÂ” Ã—Â›Ã—Âœ Ã—Â”Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â Ã—Â”Ã—Â—Ã—Â“Ã—Â©Ã—Â™Ã—Â Ã—Â Ã—Â©Ã—ÂžÃ—Â¨Ã—Â•.")

            else:
                print("[LOGO] Ã¢ÂÂ© Ã—ÂÃ—Â™Ã—ÂŸ Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â Ã—Â—Ã—Â“Ã—Â©Ã—Â™Ã—Â Ã—ÂœÃ—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Â”.")

        except Exception as e:
            print(f"[LOGO ERROR] Failed to extract logos: {e}")

    def open_logo_manager(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ã—Â Ã—Â™Ã—Â”Ã—Â•Ã—Âœ Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â Ã—ÂœÃ—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂžÃ—Â™Ã—Â©Ã—Â¨Ã—ÂÃ—Âœ")
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

        # Ã°ÂŸÂ”Â Ã—Â©Ã—Â•Ã—Â¨Ã—Âª Ã—Â—Ã—Â™Ã—Â¤Ã—Â•Ã—Â©
        search_box = QLineEdit()
        search_box.setPlaceholderText("Ã°ÂŸÂ”Â Ã—Â—Ã—Â¤Ã—Â© Ã—ÂœÃ—Â¤Ã—Â™ Ã—Â©Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—ÂÃ—Â• Ã—Â›Ã—ÂªÃ—Â•Ã—Â‘Ã—Âª Ã—ÂœÃ—Â•Ã—Â’Ã—Â•")
        layout.addWidget(search_box)

        table = QTableWidget(dialog)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Ã¢ÂœÂ”", "Ã—Â©Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥", "Ã—ÂœÃ—Â•Ã—Â’Ã—Â• (URL)"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSortingEnabled(True)
        layout.addWidget(table)

        # Ã¢ÂœÂ… Ã—Â¨Ã—Â¢Ã—Â Ã—Â•Ã—ÂŸ Ã—Â Ã—ÂªÃ—Â•Ã—Â Ã—Â™Ã—Â Ã—ÂœÃ—Â˜Ã—Â‘Ã—ÂœÃ—Â”
        def load_table_data():
            table.setRowCount(0)
            seen = set()  # Ã—ÂœÃ—Â Ã—ÂœÃ—Â”Ã—Â¦Ã—Â™Ã—Â’ Ã—Â›Ã—Â¤Ã—Â•Ã—ÂœÃ—Â™Ã—Â

            try:
                with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except:
                data = {}

            row = 0
            for name, logos in data.items():
                if is_israeli_channel("", name):
                    # Ã—Â•Ã—Â“Ã—Â Ã—Â©Ã—Â”Ã—Â¢Ã—Â¨Ã—Âš Ã—Â”Ã—Â•Ã—Â Ã—ÂªÃ—ÂžÃ—Â™Ã—Â“ Ã—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Â”
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

        load_table_data()  # Ã—Â˜Ã—Â¢Ã—ÂŸ Ã—Â¤Ã—Â¢Ã—Â Ã—Â¨Ã—ÂÃ—Â©Ã—Â•Ã—Â Ã—Â”

        def filter_table():
            text = search_box.text().lower()
            for row in range(table.rowCount()):
                show = False
                for col in range(1, 3):  # Ã—Â©Ã—Â Ã—Â•Ã—ÂœÃ—Â•Ã—Â’Ã—Â•
                    item = table.item(row, col)
                    if item and text in item.text().lower():
                        show = True
                        break
                table.setRowHidden(row, not show)

        search_box.textChanged.connect(filter_table)

        # Ã°ÂŸÂ”Â˜ Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨Ã—Â™Ã—Â
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

        select_all_btn = QPushButton("Ã—Â‘Ã—Â—Ã—Â¨ Ã—Â”Ã—Â›Ã—Âœ")
        deselect_all_btn = QPushButton("Ã—Â‘Ã—Â˜Ã—Âœ Ã—Â‘Ã—Â—Ã—Â™Ã—Â¨Ã—Â”")
        refresh_btn = QPushButton("Ã°ÂŸÂ”Âƒ Ã—Â¨Ã—Â¢Ã—Â Ã—ÂŸ Ã—Â˜Ã—Â‘Ã—ÂœÃ—Â”")
        delete_btn = QPushButton("Ã°ÂŸÂ—Â‘Ã¯Â¸Â Ã—ÂžÃ—Â—Ã—Â§ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â Ã—Â‘Ã—Â—Ã—Â¨Ã—Â™Ã—Â")
        close_btn = QPushButton("Ã—Â¡Ã—Â’Ã—Â•Ã—Â¨")

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

            to_remove = {}  # name Ã¢Â†Â’ [logos to remove]

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
                QMessageBox.information(dialog, "Ã—Â‘Ã—Â•Ã—Â¦Ã—Â¢", f"Ã—Â”Ã—Â•Ã—Â¡Ã—Â¨Ã—Â• {removed_count} Ã—Â¤Ã—Â¨Ã—Â™Ã—Â˜Ã—Â™Ã—Â.")
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

            # Ã°ÂŸÂ§Â¹ Ã—ÂÃ—Â™Ã—Â¤Ã—Â•Ã—Â¡ Ã¢Â€Â“ Ã—ÂÃ—Â Ã—ÂÃ—Â™Ã—ÂŸ Ã—Â˜Ã—Â§Ã—Â¡Ã—Â˜
            if not text:
                # Ã—ÂÃ—Â™Ã—Â¤Ã—Â•Ã—Â¡ Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—Â¢Ã—Â batch updates
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

            # Ã—Â¦Ã—Â‘Ã—Â¢Ã—Â™Ã—Â Ã—ÂžÃ—Â•Ã—Â›Ã—Â Ã—Â™Ã—Â Ã—ÂžÃ—Â¨Ã—ÂÃ—Â©
            yellow_color = QColor("#fff88a")
            white_color = QColor("white")
            green_color = QColor("#c0ffc0")

            # Ã°ÂŸÂ”Â Ã—Â—Ã—Â™Ã—Â¤Ã—Â•Ã—Â© Ã—Â‘Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª - Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—Â™Ã—Â•Ã—ÂªÃ—Â¨ Ã—Â¢Ã—Â caching
            category_found = False
            category_count = self.categoryList.count()

            # Ã—Â”Ã—Â©Ã—Â‘Ã—ÂªÃ—Âª Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—Â Ã—Â™Ã—Â Ã—ÂœÃ—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â•Ã—Âª
            self.categoryList.setUpdatesEnabled(False)

            for i in range(category_count):
                item = self.categoryList.item(i)
                item_text = item.text()

                # cache Ã—Â©Ã—Âœ Ã—Â”Ã—Â˜Ã—Â§Ã—Â¡Ã—Â˜ Ã—Â”Ã—Â Ã—Â§Ã—Â™
                if not hasattr(item, '_cached_clean_text'):
                    item._cached_clean_text = item_text.split(" (")[0].lower()

                if text in item._cached_clean_text:
                    item.setBackground(yellow_color)
                    if not category_found:  # Ã—Â¨Ã—Â§ Ã—Â¤Ã—Â¢Ã—Â Ã—ÂÃ—Â—Ã—Âª
                        self.categoryList.setCurrentItem(item)
                        category_found = True
                else:
                    item.setBackground(white_color)

            self.categoryList.setUpdatesEnabled(True)

            # Ã—ÂÃ—Â Ã—Â Ã—ÂžÃ—Â¦Ã—ÂÃ—Â” Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” - Ã—Â”Ã—Â¦Ã—Â’ Ã—ÂÃ—Âª Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â
            if category_found:
                current_item = self.categoryList.currentItem()
                if current_item:
                    self.display_channels(current_item)
                return

            # Ã°ÂŸÂ”Â Ã—ÂÃ—Â Ã—ÂœÃ—Â Ã—Â Ã—ÂžÃ—Â¦Ã—ÂÃ—Â” Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã¢Â€Â“ Ã—Â—Ã—Â¤Ã—Â© Ã—Â‘Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â (Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—Â™Ã—Â•Ã—ÂªÃ—Â¨)
            if not category_found:
                # Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—ÂžÃ—Â™Ã—ÂœÃ—Â•Ã—ÂŸ Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—ÂœÃ—Â—Ã—Â™Ã—Â¤Ã—Â•Ã—Â© Ã—ÂÃ—Â Ã—ÂœÃ—Â Ã—Â§Ã—Â™Ã—Â™Ã—Â
                if not hasattr(self, '_channel_lookup_cache'):
                    self._channel_lookup_cache = {}
                    for category, channels in self.categories.items():
                        for channel in channels:
                            channel_clean = channel.split(" (")[0].lower()
                            if channel_clean not in self._channel_lookup_cache:
                                self._channel_lookup_cache[channel_clean] = []
                            self._channel_lookup_cache[channel_clean].append((category, channel))

                # Ã—Â—Ã—Â™Ã—Â¤Ã—Â•Ã—Â© Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—Â‘Ã—ÂžÃ—Â™Ã—ÂœÃ—Â•Ã—ÂŸ
                found_channel = None
                found_category = None

                # Ã—Â—Ã—Â™Ã—Â¤Ã—Â•Ã—Â© Ã—Â™Ã—Â©Ã—Â™Ã—Â¨ Ã—Â‘Ã—ÂžÃ—Â™Ã—ÂœÃ—Â•Ã—ÂŸ
                for cached_channel, category_channel_pairs in self._channel_lookup_cache.items():
                    if text in cached_channel:
                        found_category, found_channel = category_channel_pairs[0]
                        break

                if found_channel and found_category:
                    # Ã—Â”Ã—Â©Ã—Â‘Ã—ÂªÃ—Âª Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—Â Ã—Â™Ã—Â
                    self.categoryList.setUpdatesEnabled(False)
                    self.channelList.setUpdatesEnabled(False)

                    # Ã—ÂÃ—Â™Ã—Â¤Ã—Â•Ã—Â¡ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª
                    for i in range(category_count):
                        self.categoryList.item(i).setBackground(white_color)

                    # Ã—ÂžÃ—Â¦Ã—Â™Ã—ÂÃ—Âª Ã—Â•Ã—Â¡Ã—Â™Ã—ÂžÃ—Â•Ã—ÂŸ Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â”Ã—Â Ã—Â›Ã—Â•Ã—Â Ã—Â”
                    for i in range(category_count):
                        item = self.categoryList.item(i)
                        if found_category in item.text():
                            item.setBackground(yellow_color)
                            self.categoryList.setCurrentItem(item)
                            self.display_channels(item)
                            break

                    # Ã—ÂžÃ—Â¦Ã—Â™Ã—ÂÃ—Âª Ã—Â•Ã—Â¡Ã—Â™Ã—ÂžÃ—Â•Ã—ÂŸ Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥
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

                    # Ã—Â”Ã—Â¤Ã—Â¢Ã—ÂœÃ—Âª Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—Â Ã—Â™Ã—Â
                    self.categoryList.setUpdatesEnabled(True)
                    self.channelList.setUpdatesEnabled(True)

        except Exception as e:
            print(f"[Search Error] {e}")
            # Ã—Â•Ã—Â“Ã—Â Ã—Â©Ã—Â”Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—Â Ã—Â™Ã—Â Ã—ÂžÃ—Â•Ã—Â¤Ã—Â¢Ã—ÂœÃ—Â™Ã—Â Ã—Â‘Ã—ÂžÃ—Â§Ã—Â¨Ã—Â” Ã—Â©Ã—Âœ Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â”
            if hasattr(self, 'categoryList'):
                self.categoryList.setUpdatesEnabled(True)
            if hasattr(self, 'channelList'):
                self.channelList.setUpdatesEnabled(True)

    def buildSearchCompleter(self):
        search_terms = list(self.categories.keys())
        for ch_list in self.categories.values():
            for ch in ch_list:
                search_terms.append(ch.split(" (")[0])
        completer = QCompleter(sorted(set(search_terms)), self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)  # Ã¢Â†Â Ã—ÂžÃ—ÂÃ—Â¤Ã—Â©Ã—Â¨ Ã—Â—Ã—Â™Ã—Â¤Ã—Â•Ã—Â© Ã—Â’Ã—Â Ã—Â‘Ã—ÂÃ—ÂžÃ—Â¦Ã—Â¢
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
        Ã—ÂžÃ—Â§Ã—Â‘Ã—Âœ Ã—ÂÃ—Âª Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—Â”Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—Â›Ã—Â˜Ã—Â§Ã—Â¡Ã—Â˜, Ã—ÂžÃ—Â–Ã—Â”Ã—Â” Ã—ÂÃ—Âª Ã—Â›Ã—Âœ Ã—Â©Ã—Â•Ã—Â¨Ã—Â•Ã—Âª Ã—Â”Ã–Â¾EPG Ã—Â•Ã—ÂžÃ—Â—Ã—Â–Ã—Â™Ã—Â¨ Ã—ÂÃ—Â•Ã—ÂªÃ—ÂŸ Ã—ÂžÃ—Â¡Ã—Â•Ã—Â“Ã—Â¨Ã—Â•Ã—Âª Ã—Â‘Ã—ÂªÃ—Â—Ã—Â™Ã—ÂœÃ—Âª Ã—Â”Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥,
        Ã—ÂªÃ—Â•Ã—Âš Ã—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Â” Ã—Â¢Ã—Âœ Ã—Â©Ã—Â•Ã—Â¨Ã—Âª Ã—Â”Ã–Â¾#EXTM3U Ã—Â‘Ã—Â¨Ã—ÂÃ—Â©.
        """
        lines = content.strip().splitlines()

        # Ã—Â•Ã—Â“Ã—Â Ã—Â©Ã—Â™Ã—Â© EXT_HEADER
        if not lines or not lines[0].startswith("#EXTM3U"):
            lines.insert(0, "#EXTM3U")

        # Ã—Â—Ã—Â™Ã—ÂœÃ—Â•Ã—Â¥ Ã—Â©Ã—Â•Ã—Â¨Ã—Â•Ã—Âª EPG
        epg_lines = [line for line in lines if line.startswith("#EXTM3U x-tvg-url=")]
        # Ã—Â”Ã—Â¡Ã—Â¨Ã—Âª Ã—Â©Ã—Â•Ã—Â¨Ã—Â•Ã—Âª EPG Ã—ÂžÃ—ÂžÃ—Â™Ã—Â§Ã—Â•Ã—ÂžÃ—ÂŸ Ã—Â”Ã—ÂžÃ—Â§Ã—Â•Ã—Â¨Ã—Â™
        cleaned_lines = [line for line in lines if
                         not line.startswith("#EXTM3U x-tvg-url=") and not line.startswith("#EXTM3U")]

        # Ã—Â‘Ã—Â Ã—Â™Ã—Â™Ã—Âª Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—Â—Ã—Â“Ã—Â©
        result_lines = ["#EXTM3U"] + epg_lines + cleaned_lines
        return "\n".join(result_lines)

    # Ã—Â©Ã—Â™Ã—ÂžÃ—Â•Ã—Â© Ã—Â‘Ã—Â¤Ã—Â•Ã—Â Ã—Â§Ã—Â¦Ã—Â™Ã—Â” Ã—Â–Ã—Â•:
    # fixed_content = ensure_epg_url_header(original_content)
    # self.textEdit.setPlainText(fixed_content)

    def mergeM3Us(self):
        """Ã—ÂžÃ—Â™Ã—Â–Ã—Â•Ã—Â’ Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ M3U Ã—Â Ã—Â•Ã—Â¡Ã—Â£ Ã—ÂœÃ—Â¤Ã—ÂœÃ—Â™Ã—Â™Ã—ÂœÃ—Â™Ã—Â¡Ã—Â˜ Ã—Â”Ã—Â§Ã—Â™Ã—Â™Ã—Â - Ã—Â’Ã—Â¨Ã—Â¡Ã—Â” Ã—ÂžÃ—ÂªÃ—Â•Ã—Â§Ã—Â Ã—Âª"""

        # Ã—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Âª Ã—ÂžÃ—Â¦Ã—Â‘ Ã—Â”Ã—Â Ã—Â•Ã—Â›Ã—Â—Ã—Â™ Ã—ÂœÃ—Â¤Ã—Â Ã—Â™ Ã—Â”Ã—ÂžÃ—Â™Ã—Â–Ã—Â•Ã—Â’
        channels_before = self.count_total_channels()

        # Ã—Â‘Ã—Â—Ã—Â™Ã—Â¨Ã—Âª Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—ÂœÃ—Â¦Ã—Â™Ã—Â¨Ã—Â•Ã—Â£
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

        # Ã—Â§Ã—Â¨Ã—Â™Ã—ÂÃ—Â” Ã—ÂœÃ—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—Â”Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥
        try:
            with open(fileName, 'r', encoding='utf-8') as f:
                new_content = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read file:\n{e}")
            return

        # Ã—Â¢Ã—Â™Ã—Â‘Ã—Â•Ã—Â“ Ã—Â”Ã—Â©Ã—Â•Ã—Â¨Ã—Â•Ã—Âª
        lines = [l.strip() for l in new_content.strip().splitlines() if l.strip()]

        # Ã—Â˜Ã—Â¢Ã—Â™Ã—Â Ã—Âª Ã—Â‘Ã—Â¡Ã—Â™Ã—Â¡ Ã—Â”Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â
        logo_db = {}
        if os.path.exists(LOGO_DB_PATH):
            try:
                with open(LOGO_DB_PATH, 'r', encoding='utf-8') as lf:
                    logo_db = json.load(lf)
            except:
                pass

        # Ã—Â¡Ã—Â¤Ã—Â™Ã—Â¨Ã—Âª Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â—Ã—Â“Ã—Â©Ã—Â™Ã—Â Ã—Â©Ã—Â Ã—Â•Ã—Â¡Ã—Â¤Ã—Â• (Ã—Â¨Ã—Â§ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂªÃ—Â§Ã—Â™Ã—Â Ã—Â™Ã—Â)
        channels_added = 0
        merged_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Â” Ã—ÂÃ—Â Ã—Â–Ã—Â• Ã—Â©Ã—Â•Ã—Â¨Ã—Âª EXTINF
            if line.startswith("#EXTINF:"):
                # Ã—Â•Ã—Â™Ã—Â“Ã—Â•Ã—Â Ã—Â©Ã—Â™Ã—Â© URL Ã—Â‘Ã—Â©Ã—Â•Ã—Â¨Ã—Â” Ã—Â”Ã—Â‘Ã—ÂÃ—Â”
                if i + 1 < len(lines) and not lines[i + 1].startswith("#"):
                    extinf_line = line
                    url_line = lines[i + 1]

                    # Ã—Â—Ã—Â™Ã—ÂœÃ—Â•Ã—Â¥ Ã—Â©Ã—Â Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥
                    name_match = re.search(r',(.+)', extinf_line)
                    channel_name = name_match.group(1).strip() if name_match else "Unknown Channel"

                    # Ã—Â”Ã—Â–Ã—Â¨Ã—Â§Ã—Âª Ã—ÂœÃ—Â•Ã—Â’Ã—Â•
                    extinf_line = self.inject_logo(extinf_line, channel_name, logo_db)

                    # Ã—Â”Ã—Â•Ã—Â¡Ã—Â¤Ã—Â” Ã—ÂœÃ—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Â”
                    merged_lines.extend([extinf_line, url_line])
                    channels_added += 1

                    i += 2  # Ã—Â“Ã—Â™Ã—ÂœÃ—Â•Ã—Â’ Ã—Â¢Ã—Âœ Ã—Â©Ã—ÂªÃ—Â™ Ã—Â”Ã—Â©Ã—Â•Ã—Â¨Ã—Â•Ã—Âª Ã—Â©Ã—Â¢Ã—Â•Ã—Â‘Ã—Â“Ã—Â•
                else:
                    # EXTINF Ã—ÂœÃ—ÂœÃ—Â URL - Ã—Â“Ã—Â™Ã—ÂœÃ—Â•Ã—Â’
                    i += 1
            else:
                # Ã—Â©Ã—Â•Ã—Â¨Ã—Â” Ã—ÂÃ—Â—Ã—Â¨Ã—Âª - Ã—Â“Ã—Â™Ã—ÂœÃ—Â•Ã—Â’
                i += 1

        if channels_added == 0:
            QMessageBox.information(self, "M3U Merge", "Ã—ÂœÃ—Â Ã—Â Ã—ÂžÃ—Â¦Ã—ÂÃ—Â• Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂªÃ—Â§Ã—Â™Ã—Â Ã—Â™Ã—Â Ã—ÂœÃ—Â¦Ã—Â™Ã—Â¨Ã—Â•Ã—Â£")
            return

        # Ã—ÂžÃ—Â™Ã—Â–Ã—Â•Ã—Â’ Ã—Â”Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—ÂœÃ—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—Â”Ã—Â§Ã—Â™Ã—Â™Ã—Â
        current_content = self.textEdit.toPlainText()

        # Ã—Â‘Ã—Â Ã—Â™Ã—Â™Ã—Âª Ã—Â”Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—Â”Ã—Â—Ã—Â“Ã—Â©
        if current_content.strip():
            # Ã—Â™Ã—Â© Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—Â§Ã—Â™Ã—Â™Ã—Â - Ã—Â”Ã—Â•Ã—Â¡Ã—Â¤Ã—Â” Ã—Â‘Ã—Â¡Ã—Â•Ã—Â£
            if not current_content.endswith('\n'):
                current_content += '\n'
            new_full_content = current_content + '\n'.join(merged_lines)
        else:
            # Ã—ÂÃ—Â™Ã—ÂŸ Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—Â§Ã—Â™Ã—Â™Ã—Â - Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—Â—Ã—Â“Ã—Â©
            unified_header = self.buildUnifiedEPGHeader()
            new_full_content = unified_header + '\n' + '\n'.join(merged_lines)

        # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—Â”Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—Â‘Ã—Â¢Ã—Â•Ã—Â¨Ã—Âš
        self.textEdit.blockSignals(True)
        self.textEdit.setPlainText(new_full_content)
        self.textEdit.blockSignals(False)

        # Ã—ÂžÃ—Â™Ã—Â–Ã—Â•Ã—Â’ Ã—Â”Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—ÂœÃ—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª (Ã—Â›Ã—Â•Ã—ÂœÃ—Âœ Ã—Â›Ã—Â¤Ã—Â™Ã—ÂœÃ—Â•Ã—Â™Ã—Â•Ã—Âª)
        merged_content_for_categories = '\n'.join(merged_lines)
        self.mergeM3UContentToCategories(merged_content_for_categories, allow_duplicates=True)

        # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—ÂªÃ—Â¦Ã—Â•Ã—Â’Ã—Â”
        self.cleanEmptyCategories()
        self.updateCategoryList()
        self.regenerateM3UTextOnly()

        # Ã—Â—Ã—Â–Ã—Â¨Ã—Â” Ã—ÂœÃ—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â”Ã—Â¨Ã—ÂÃ—Â©Ã—Â•Ã—Â Ã—Â” Ã—ÂÃ—Â Ã—Â§Ã—Â™Ã—Â™Ã—ÂžÃ—Âª
        if self.categoryList.count():
            self.categoryList.setCurrentRow(0)
            self.display_channels(self.categoryList.currentItem())

        # Ã—Â¡Ã—Â¤Ã—Â™Ã—Â¨Ã—Âª Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂÃ—Â—Ã—Â¨Ã—Â™ Ã—Â”Ã—ÂžÃ—Â™Ã—Â–Ã—Â•Ã—Â’
        channels_after = self.count_total_channels()
        actual_added = channels_after - channels_before

        # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—ÂªÃ—Â¦Ã—Â•Ã—Â’Ã—Âª Ã—Â©Ã—Â Ã—Â”Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥
        current_file_text = self.fileNameLabel.text()
        if "Merged with:" not in current_file_text:
            self.fileNameLabel.setText(f"{current_file_text} | Merged with: {os.path.basename(fileName)}")
        else:
            self.fileNameLabel.setText(f"{current_file_text}, {os.path.basename(fileName)}")

        # Ã—Â”Ã—Â¦Ã—Â’Ã—Âª Ã—Â”Ã—Â•Ã—Â“Ã—Â¢Ã—Âª Ã—Â”Ã—Â¦Ã—ÂœÃ—Â—Ã—Â” Ã—Â¢Ã—Â Ã—Â¤Ã—Â™Ã—Â¨Ã—Â•Ã—Â˜
        message = f"""Ã—Â”Ã—ÂžÃ—Â™Ã—Â–Ã—Â•Ã—Â’ Ã—Â”Ã—Â•Ã—Â©Ã—ÂœÃ—Â Ã—Â‘Ã—Â”Ã—Â¦Ã—ÂœÃ—Â—Ã—Â”!

    Ã°ÂŸÂ“ÂŠ Ã—Â¡Ã—Â™Ã—Â›Ã—Â•Ã—Â:
    Ã¢Â€Â¢ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â©Ã—Â Ã—Â•Ã—Â¡Ã—Â¤Ã—Â•: {channels_added}
    Ã¢Â€Â¢ Ã—Â¡Ã—Â”"Ã—Â› Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂœÃ—Â¤Ã—Â Ã—Â™: {channels_before:,}
    Ã¢Â€Â¢ Ã—Â¡Ã—Â”"Ã—Â› Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂÃ—Â—Ã—Â¨Ã—Â™: {channels_after:,}
    Ã¢Â€Â¢ Ã—Â”Ã—Â’Ã—Â™Ã—Â“Ã—Â•Ã—Âœ Ã—Â‘Ã—Â¤Ã—Â•Ã—Â¢Ã—Âœ: {actual_added:,}

    Ã¢ÂœÂ… Ã—Â›Ã—Âœ Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â•Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—Â Ã—Â•Ã—Â¡Ã—Â¤Ã—Â• Ã—ÂœÃ—Â¤Ã—ÂœÃ—Â™Ã—Â™Ã—ÂœÃ—Â™Ã—Â¡Ã—Â˜"""

        QMessageBox.information(self, "M3U Merge Completed", message)

        # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Âª Ã—Â¢Ã—Â§Ã—Â‘Ã—Â™Ã—Â•Ã—Âª (Ã—ÂÃ—Â•Ã—Â¤Ã—Â¦Ã—Â™Ã—Â•Ã—Â Ã—ÂœÃ—Â™ - Ã—ÂœÃ—Â”Ã—Â¡Ã—Â¨Ã—Â” Ã—Â‘Ã—Â™Ã—Â™Ã—Â¦Ã—Â•Ã—Â¨)
        if actual_added != channels_added:
            print(f"Warning: Expected {channels_added} but actual increase was {actual_added}")

    def count_total_channels(self):
        """Ã—Â¡Ã—Â¤Ã—Â™Ã—Â¨Ã—Âª Ã—Â¡Ã—Â”"Ã—Â› Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â‘Ã—Â›Ã—Âœ Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª"""
        total = 0
        for category_channels in self.categories.values():
            total += len(category_channels)
        return total

    def loadM3UFromText(self, content, append=False):
        # Ã—ÂÃ—Â Ã—ÂœÃ—Â append Ã—ÂžÃ—Â Ã—Â§Ã—Â™Ã—Â Ã—ÂÃ—Âª Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª
        if not append:
            self.categories.clear()

        # ----- 1Ã¯Â¸ÂÃ¢ÂƒÂ£ Ã—Â Ã—Â™Ã—Â”Ã—Â•Ã—Âœ EPG headers -----
        # Ã—ÂÃ—ÂªÃ—Â—Ã—Â•Ã—Âœ self.epg_headers Ã—Â‘Ã—Â¤Ã—Â¢Ã—Â Ã—Â”Ã—Â¨Ã—ÂÃ—Â©Ã—Â•Ã—Â Ã—Â” (Ã—ÂÃ—Â• Ã—Â‘Ã—Â›Ã—Âœ load Ã—ÂžÃ—Â—Ã—Â“Ã—Â©)
        if not hasattr(self, "epg_headers") or not append:
            self.epg_headers = []

        # Ã—Â©Ã—ÂœÃ—Â‘ 1: Ã—ÂÃ—Â¡Ã—Â•Ã—Â£ Ã—ÂÃ—Âª Ã—Â›Ã—Âœ Ã—Â”Ã–Â¾EPG headers (Ã—Â‘Ã—ÂœÃ—Â™ strip Ã—Â¢Ã—Âœ Ã—Â›Ã—Âœ Ã—Â”Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥)
        detected_epg_headers = []
        for line in content.splitlines():  # <-- splitlines() Ã—Â‘Ã—ÂœÃ—Â™ strip()
            if line.startswith("#EXTM3U") and ("url-tvg=" in line or "x-tvg-url=" in line):
                detected_epg_headers.append(line.strip())

        # Ã—Â©Ã—ÂœÃ—Â‘ 2: Ã—Â”Ã—Â•Ã—Â¡Ã—Â¤Ã—Âª headers Ã—Â™Ã—Â™Ã—Â—Ã—Â•Ã—Â“Ã—Â™Ã—Â™Ã—Â
        for header in detected_epg_headers:
            if header not in self.epg_headers:
                self.epg_headers.append(header)

        # Ã—Â©Ã—ÂœÃ—Â‘ 3: Ã—Â Ã—Â™Ã—Â§Ã—Â•Ã—Â™ Ã—Â›Ã—Âœ Ã—Â©Ã—Â•Ã—Â¨Ã—Â•Ã—Âª EXTÃÂœ3U (Ã—Â‘Ã—ÂœÃ—Â™ Ã—ÂœÃ—Â”Ã—Â¡Ã—Â™Ã—Â¨ Ã—Â¨Ã—Â•Ã—Â•Ã—Â—Ã—Â™Ã—Â)
        lines = [
            line for line in content.splitlines()  # <-- Ã—Â©Ã—Â•Ã—Â‘ splitlines() Ã—Â‘Ã—ÂœÃ—Â™ strip()
            if not line.startswith("#EXTM3U")
        ]

        # ----- 2Ã¯Â¸ÂÃ¢ÂƒÂ£ Ã—Â‘Ã—Â Ã—Â™Ã—Â™Ã—Âª Ã—Â©Ã—Â•Ã—Â¨Ã—Âª EXTÃÂœ3U Ã—ÂÃ—Â—Ã—Â™Ã—Â“Ã—Â” -----
        unified_header = self.buildUnifiedEPGHeader()
        # Ã—ÂžÃ—Â•Ã—Â¡Ã—Â™Ã—Â¤Ã—Â™Ã—Â Ã—Â©Ã—ÂªÃ—Â™ Ã—Â”Ã—Â©Ã—Â•Ã—Â¨Ã—Â•Ã—Âª Ã—Â”Ã—Â‘Ã—ÂÃ—Â•Ã—Âª: Ã—Â›Ã—Â•Ã—ÂªÃ—Â¨Ã—Âª, Ã—Â©Ã—Â•Ã—Â¨Ã—Â” Ã—Â¨Ã—Â™Ã—Â§Ã—Â”, Ã—Â•Ã—ÂÃ—Â– Ã—Â›Ã—Âœ Ã—Â”Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ
        content2 = unified_header + "\n\n" + "\n".join(lines)

        # ----- 4Ã¯Â¸ÂÃ¢ÂƒÂ£ Ã—Â¤Ã—Â¨Ã—Â¡ Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ M3U -----
        self.parseM3UContentEnhanced(content2)
        self.updateCategoryList()
        self.buildSearchCompleter()

        # ----- 5Ã¯Â¸ÂÃ¢ÂƒÂ£ Ã—Â‘Ã—Â—Ã—Â™Ã—Â¨Ã—Âª Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â¨Ã—ÂÃ—Â©Ã—Â•Ã—Â Ã—Â” -----
        if self.categoryList.count() > 0:
            self.categoryList.setCurrentRow(0)
            self.display_channels(self.categoryList.currentItem())

        # ----- 6Ã¯Â¸ÂÃ¢ÂƒÂ£ Ã—Â¡Ã—Â¨Ã—Â™Ã—Â§Ã—Âª Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â Ã—Â‘Ã—Â¨Ã—Â§Ã—Â¢ -----
        threading.Thread(
            target=self.extract_and_save_logos_for_all_channels,
            args=(content2,),
            daemon=True
        ).start()

    def mergeM3UContentToCategories(self, content, allow_duplicates=True):
        """
        Ã—ÂžÃ—ÂžÃ—Â–Ã—Â’ Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ M3U Ã—ÂœÃ—ÂªÃ—Â•Ã—Âš self.categories.
        Ã—ÂÃ—Â allow_duplicates=True Ã¢Â€Â“ Ã—ÂžÃ—Â•Ã—Â¡Ã—Â™Ã—Â£ Ã—Â’Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â©Ã—Â›Ã—Â‘Ã—Â¨ Ã—Â§Ã—Â™Ã—Â™Ã—ÂžÃ—Â™Ã—Â Ã—Â‘Ã—ÂÃ—Â•Ã—ÂªÃ—Â” Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â”.
        Ã—Â’Ã—Â¨Ã—Â¡Ã—Â” Ã—ÂžÃ—ÂªÃ—Â•Ã—Â§Ã—Â Ã—Âª Ã—Â¢Ã—Â Ã—Â˜Ã—Â™Ã—Â¤Ã—Â•Ã—Âœ Ã—ÂžÃ—Â©Ã—Â•Ã—Â¤Ã—Â¨ Ã—Â‘Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â•Ã—Âª Ã—Â•Ã—Â¡Ã—Â¤Ã—Â™Ã—Â¨Ã—Â” Ã—ÂžÃ—Â“Ã—Â•Ã—Â™Ã—Â§Ã—Âª.
        """
        if not content or not content.strip():
            return

        lines = [line.strip() for line in content.strip().splitlines() if line.strip()]

        # Ã—ÂÃ—ÂªÃ—Â—Ã—Â•Ã—Âœ Ã—Â”Ã—ÂžÃ—Â˜Ã—ÂžÃ—Â•Ã—ÂŸ Ã—Â©Ã—Âœ EXTINF Ã—ÂÃ—Â Ã—ÂœÃ—Â Ã—Â§Ã—Â™Ã—Â™Ã—Â
        if not hasattr(self, 'extinf_lookup'):
            self.extinf_lookup = {}

        # Ã—ÂžÃ—Â©Ã—ÂªÃ—Â Ã—Â™Ã—Â Ã—ÂœÃ—ÂžÃ—Â¢Ã—Â§Ã—Â‘
        channels_processed = 0
        categories_created = 0

        i = 0
        while i < len(lines):
            line = lines[i]

            # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Â” Ã—ÂÃ—Â Ã—Â–Ã—Â• Ã—Â©Ã—Â•Ã—Â¨Ã—Âª EXTINF
            if line.startswith("#EXTINF:"):
                # Ã—Â•Ã—Â™Ã—Â“Ã—Â•Ã—Â Ã—Â©Ã—Â™Ã—Â© Ã—Â©Ã—Â•Ã—Â¨Ã—Âª URL Ã—ÂÃ—Â—Ã—Â¨Ã—Â™Ã—Â”
                if i + 1 >= len(lines) or lines[i + 1].startswith("#"):
                    print(f"Warning: EXTINF line without URL at index {i}: {line}")
                    i += 1
                    continue

                extinf_line = line
                url_line = lines[i + 1]

                # Ã—Â•Ã—Â™Ã—Â“Ã—Â•Ã—Â Ã—Â©Ã—Â”-URL Ã—ÂªÃ—Â§Ã—Â™Ã—ÂŸ
                if not (url_line.startswith("http://") or url_line.startswith("https://") or
                        url_line.startswith("rtmp://") or url_line.startswith("rtsp://")):
                    print(f"Warning: Invalid URL format at index {i + 1}: {url_line}")
                    i += 2
                    continue

                # Ã—Â—Ã—Â™Ã—ÂœÃ—Â•Ã—Â¥ Ã—Â©Ã—Â Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥
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

                # Ã—Â—Ã—Â™Ã—ÂœÃ—Â•Ã—Â¥ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â”
                group_match = re.search(r'group-title="([^"]*)"', extinf_line)
                category = group_match.group(1).strip() if group_match else "UncategorizedÃ°ÂŸÂ“Âº"

                # Ã—Â•Ã—Â™Ã—Â“Ã—Â•Ã—Â Ã—Â©Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—ÂœÃ—Â Ã—Â¨Ã—Â™Ã—Â§Ã—Â”
                if not category:
                    category = "UncategorizedÃ°ÂŸÂ“Âº"

                # Ã—Â—Ã—Â™Ã—ÂœÃ—Â•Ã—Â¥ Ã—ÂœÃ—Â•Ã—Â’Ã—Â• (Ã—ÂÃ—Â•Ã—Â¤Ã—Â¦Ã—Â™Ã—Â•Ã—Â Ã—ÂœÃ—Â™)
                logo_match = re.search(r'tvg-logo="([^"]*)"', extinf_line)
                logo = logo_match.group(1).strip() if logo_match else None

                # Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—Â¨Ã—Â©Ã—Â•Ã—ÂžÃ—Âª Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥
                channel_entry = f"{channel_name} ({url_line})"

                # Ã—Â”Ã—Â•Ã—Â¡Ã—Â¤Ã—Âª Ã—ÂœÃ—Â•Ã—Â’Ã—Â• Ã—ÂœÃ—Â¨Ã—Â©Ã—Â•Ã—ÂžÃ—Â” Ã—ÂÃ—Â Ã—Â§Ã—Â™Ã—Â™Ã—Â
                if logo and logo.strip():
                    channel_entry += f' tvg-logo="{logo}"'

                # Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—ÂÃ—Â Ã—ÂœÃ—Â Ã—Â§Ã—Â™Ã—Â™Ã—ÂžÃ—Âª
                if category not in self.categories:
                    self.categories[category] = []
                    categories_created += 1
                    print(f"Created new category: {category}")

                # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Âª Ã—Â›Ã—Â¤Ã—Â™Ã—ÂœÃ—Â•Ã—Â™Ã—Â•Ã—Âª
                should_add = True
                if not allow_duplicates:
                    # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Â” Ã—ÂžÃ—Â“Ã—Â•Ã—Â™Ã—Â§Ã—Âª Ã—Â™Ã—Â•Ã—ÂªÃ—Â¨ - Ã—Â”Ã—Â©Ã—Â•Ã—Â•Ã—ÂÃ—Â” Ã—ÂœÃ—Â¤Ã—Â™ Ã—Â©Ã—Â Ã—Â•URL
                    existing_entries = self.categories[category]
                    for existing_entry in existing_entries:
                        existing_name = existing_entry.split(" (")[0].strip()
                        existing_url_match = re.search(r'\(([^)]+)\)', existing_entry)
                        existing_url = existing_url_match.group(1) if existing_url_match else ""

                        if existing_name == channel_name and existing_url == url_line:
                            should_add = False
                            print(f"Duplicate found in category '{category}': {channel_name}")
                            break

                # Ã—Â”Ã—Â•Ã—Â¡Ã—Â¤Ã—Âª Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥
                if should_add:
                    self.categories[category].append(channel_entry)
                    channels_processed += 1

                    # Ã—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Âª EXTINF Ã—ÂœÃ—ÂžÃ—Â¢Ã—Â§Ã—Â‘
                    self.extinf_lookup[channel_entry] = extinf_line

                    print(f"Added channel to '{category}': {channel_name}")

                i += 2  # Ã—Â“Ã—Â™Ã—ÂœÃ—Â•Ã—Â’ Ã—Â¢Ã—Âœ Ã—Â©Ã—ÂªÃ—Â™ Ã—Â”Ã—Â©Ã—Â•Ã—Â¨Ã—Â•Ã—Âª Ã—Â©Ã—Â¢Ã—Â•Ã—Â‘Ã—Â“Ã—Â•

            else:
                # Ã—Â©Ã—Â•Ã—Â¨Ã—Â” Ã—Â©Ã—ÂÃ—Â™Ã—Â Ã—Â” EXTINF - Ã—Â“Ã—Â™Ã—ÂœÃ—Â•Ã—Â’
                i += 1

        print(f"Merge completed: {channels_processed} channels added, {categories_created} categories created")

    def cleanEmptyCategories(self):
        """
        Ã—ÂžÃ—Â¡Ã—Â™Ã—Â¨ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—Â¨Ã—Â™Ã—Â§Ã—Â•Ã—Âª Ã—Âž-self.categories
        Ã—Â’Ã—Â¨Ã—Â¡Ã—Â” Ã—ÂžÃ—Â©Ã—Â•Ã—Â¤Ã—Â¨Ã—Âª Ã—Â¢Ã—Â Ã—ÂœÃ—Â•Ã—Â’Ã—Â™Ã—Â
        """
        empty_categories = []

        for category_name, channels in list(self.categories.items()):
            # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Â” Ã—ÂÃ—Â Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â¨Ã—Â™Ã—Â§Ã—Â” Ã—ÂÃ—Â• Ã—ÂžÃ—Â›Ã—Â™Ã—ÂœÃ—Â” Ã—Â¨Ã—Â§ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂœÃ—Â Ã—ÂªÃ—Â§Ã—Â™Ã—Â Ã—Â™Ã—Â
            valid_channels = []
            for channel in channels:
                # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Â” Ã—Â©Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—ÂžÃ—Â›Ã—Â™Ã—Âœ Ã—Â©Ã—Â Ã—Â•-URL
                if " (" in channel and channel.endswith(")"):
                    name_part = channel.split(" (")[0].strip()
                    url_part = channel.split(" (")[1].rstrip(")").strip()

                    if name_part and url_part:
                        valid_channels.append(channel)

            if not valid_channels:
                empty_categories.append(category_name)
            else:
                # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â¢Ã—Â Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂªÃ—Â§Ã—Â™Ã—Â Ã—Â™Ã—Â Ã—Â‘Ã—ÂœÃ—Â‘Ã—Â“
                self.categories[category_name] = valid_channels

        # Ã—Â”Ã—Â¡Ã—Â¨Ã—Âª Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—Â¨Ã—Â™Ã—Â§Ã—Â•Ã—Âª
        for empty_cat in empty_categories:
            print(f"Removing empty category: {empty_cat}")
            del self.categories[empty_cat]

        if empty_categories:
            print(f"Cleaned {len(empty_categories)} empty categories")

    def validateChannelEntry(self, channel_entry):
        """
        Ã—Â‘Ã—Â•Ã—Â“Ã—Â§ Ã—ÂÃ—Â Ã—Â¨Ã—Â©Ã—Â•Ã—ÂžÃ—Âª Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—ÂªÃ—Â§Ã—Â™Ã—Â Ã—Â”
        Ã—ÂžÃ—Â—Ã—Â–Ã—Â™Ã—Â¨: (is_valid: bool, channel_name: str, url: str, error_msg: str)
        """
        if not channel_entry or not isinstance(channel_entry, str):
            return False, "", "", "Empty or invalid entry type"

        channel_entry = channel_entry.strip()
        if not channel_entry:
            return False, "", "", "Empty entry after strip"

        # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Âª Ã—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ Ã—Â‘Ã—Â¡Ã—Â™Ã—Â¡Ã—Â™
        if " (" not in channel_entry or not channel_entry.endswith(")"):
            return False, "", "", "Invalid format - missing '(' or ')'"

        try:
            # Ã—Â—Ã—Â™Ã—ÂœÃ—Â•Ã—Â¥ Ã—Â©Ã—Â Ã—Â•-URL
            name_part = channel_entry.split(" (")[0].strip()
            url_with_extras = channel_entry.split(" (", 1)[1].rstrip(")")

            # Ã—Â—Ã—Â™Ã—ÂœÃ—Â•Ã—Â¥ URL (Ã—Â¢Ã—Â“ Ã—ÂœÃ—Â¨Ã—Â•Ã—Â•Ã—Â— Ã—Â”Ã—Â¨Ã—ÂÃ—Â©Ã—Â•Ã—ÂŸ Ã—ÂÃ—Â• Ã—Â¡Ã—Â•Ã—Â£ Ã—Â”Ã—ÂžÃ—Â—Ã—Â¨Ã—Â•Ã—Â–Ã—Âª)
            url_part = url_with_extras.split()[0] if url_with_extras else ""

            # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Â•Ã—Âª Ã—ÂªÃ—Â§Ã—Â™Ã—Â Ã—Â•Ã—Âª
            if not name_part:
                return False, name_part, url_part, "Empty channel name"

            if not url_part:
                return False, name_part, url_part, "Empty URL"

            # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Âª Ã—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ URL
            valid_protocols = ["http://", "https://", "rtmp://", "rtsp://"]
            if not any(url_part.startswith(protocol) for protocol in valid_protocols):
                return False, name_part, url_part, f"Invalid URL protocol: {url_part}"

            return True, name_part, url_part, ""

        except Exception as e:
            return False, "", "", f"Error parsing entry: {str(e)}"

    def getChannelStatistics(self):
        """
        Ã—ÂžÃ—Â—Ã—Â–Ã—Â™Ã—Â¨ Ã—Â¡Ã—Â˜Ã—Â˜Ã—Â™Ã—Â¡Ã—Â˜Ã—Â™Ã—Â§Ã—Â•Ã—Âª Ã—ÂžÃ—Â¤Ã—Â•Ã—Â¨Ã—Â˜Ã—Â•Ã—Âª Ã—Â¢Ã—Âœ Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â
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

                    # Ã—Â¡Ã—Â¤Ã—Â™Ã—Â¨Ã—Âª Ã—Â¤Ã—Â¨Ã—Â•Ã—Â˜Ã—Â•Ã—Â§Ã—Â•Ã—ÂœÃ—Â™Ã—Â
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

        # Ã—Â–Ã—Â™Ã—Â”Ã—Â•Ã—Â™ Ã—Â›Ã—Â¤Ã—Â™Ã—ÂœÃ—Â•Ã—Â™Ã—Â•Ã—Âª
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

        # Ã—Â›Ã—Â•Ã—ÂªÃ—Â¨Ã—Âª Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª
        category_title = QLabel("Categories", self)
        category_title.setAlignment(Qt.AlignCenter)
        category_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(category_title)

        # Ã—Â§Ã—Â•Ã—ÂžÃ—Â‘Ã—Â•Ã—Â‘Ã—Â•Ã—Â§Ã—Â¡ Ã—ÂžÃ—Â™Ã—Â•Ã—ÂŸ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª
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
            "Sort by English Category Name"  # Ã¢ÂœÂ… Ã—Â—Ã—Â“Ã—Â©
        ])

        self.categorySortComboBox.currentIndexChanged.connect(self.sortCategories)
        layout.addWidget(self.categorySortComboBox)

        # Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨Ã—Â™ Ã—Â¤Ã—Â¢Ã—Â•Ã—ÂœÃ—Â•Ã—Âª
        button_layout = QHBoxLayout()

        self.addCategoryButton = QPushButton('Add Category')
        self.updateCategoryButton = QPushButton('Edit Category Name')
        self.deleteCategoryButton = QPushButton('Delete Selected')
        self.moveCategoryUpButton = QPushButton('Move Category Up')
        self.moveCategoryDownButton = QPushButton('Move Category Down')
        self.selectAllButton = QPushButton('Select All')
        self.deselectAllButton = QPushButton('Deselect All')
        self.translateCategoriesButton = QPushButton("Ã°ÂŸÂŒÂ Auto Translate")

        # Ã—Â¦Ã—Â‘Ã—Â¢Ã—Â™Ã—Â Ã—ÂœÃ—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨Ã—Â™Ã—Â
        self.selectAllButton.setStyleSheet("background-color: navy; color: white;")
        self.deselectAllButton.setStyleSheet("background-color: navy; color: white;")
        self.updateCategoryButton.setStyleSheet("background-color: red; color: white;")
        self.deleteCategoryButton.setStyleSheet("background-color: red; color: white;")
        self.addCategoryButton.setStyleSheet("background-color: green; color: white;")
        self.moveCategoryUpButton.setStyleSheet("background-color: green; color: white;")
        self.moveCategoryDownButton.setStyleSheet("background-color: green; color: white;")
        self.translateCategoriesButton.setStyleSheet("background-color: navy; color: white;")

        # Ã—Â”Ã—Â•Ã—Â¡Ã—Â¤Ã—Âª Ã—Â”Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨Ã—Â™Ã—Â Ã—ÂœÃ—Â©Ã—Â•Ã—Â¨Ã—Â”
        button_layout.addWidget(self.addCategoryButton)
        button_layout.addWidget(self.updateCategoryButton)
        button_layout.addWidget(self.deleteCategoryButton)
        button_layout.addWidget(self.moveCategoryUpButton)
        button_layout.addWidget(self.moveCategoryDownButton)
        button_layout.addWidget(self.selectAllButton)
        button_layout.addWidget(self.deselectAllButton)
        button_layout.addWidget(self.translateCategoriesButton)

        layout.addLayout(button_layout)

        # Ã—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Âª Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª
        self.categoryList = QListWidget(self)
        self.categoryList.setSelectionMode(QAbstractItemView.MultiSelection)  # Ã—Â‘Ã—Â—Ã—Â™Ã—Â¨Ã—Â” Ã—ÂžÃ—Â¨Ã—Â•Ã—Â‘Ã—Â”
        layout.addWidget(self.categoryList)

        # Ã—Â—Ã—Â™Ã—Â‘Ã—Â•Ã—Â¨ Ã—Â¤Ã—Â¢Ã—Â•Ã—ÂœÃ—Â•Ã—Âª
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

        self.batchM3UDownloadButton = QPushButton('Ã°ÂŸÂ”Â€ Smart M3U Loader', self)
        self.batchM3UDownloadButton.setStyleSheet("background-color: black; color: white;")
        self.batchM3UDownloadButton.clicked.connect(self.openBatchDownloader)
        buttons_layout.addWidget(self.batchM3UDownloadButton)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        # M3U URL Converter button
        self.m3uUrlConverterButton = QPushButton('Ã°ÂŸÂ”Â Xtream Converter', self)
        self.m3uUrlConverterButton.setStyleSheet("background-color: black; color: white;")
        self.m3uUrlConverterButton.clicked.connect(self.openM3UConverterDialog)
        buttons_layout.addWidget(self.m3uUrlConverterButton)

        self.convertPortalButton = QPushButton('Ã°ÂŸÂŒÂ Advanced Portal Converter', self)
        self.convertPortalButton.setStyleSheet("background-color: black; color: white;")
        self.convertPortalButton.clicked.connect(self.convertStalkerToM3U)
        buttons_layout.addWidget(self.convertPortalButton)


        # Export Groups button
        self.exportGroupButton = QPushButton('Ã°ÂŸÂ“Â¤ Export Groups', self)
        self.exportGroupButton.setStyleSheet("background-color: black; color: white;")
        self.exportGroupButton.clicked.connect(self.openExportDialog)
        buttons_layout.addWidget(self.exportGroupButton)

        self.filterIsraelChannelsButton = QPushButton('Ã°ÂŸÂŽÂ¯ Filtered Export', self)
        self.filterIsraelChannelsButton.setStyleSheet("background-color: black; color: white;")
        self.filterIsraelChannelsButton.clicked.connect(self.chooseFilterMethod)  # Ã—Â¨Ã—Â§ Ã—Â¤Ã—Â¢Ã—Â Ã—ÂÃ—Â—Ã—Âª!

        # Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—Â”Ã—ÂžÃ—Â¢Ã—Â¨Ã—Â›Ã—Âª Ã—Â”Ã—ÂžÃ—ÂªÃ—Â§Ã—Â“Ã—ÂžÃ—Âª
        self.filter_system = M3UFilterEnhanced(self)

        buttons_layout.addWidget(self.filterIsraelChannelsButton)

        self.smartScanButton = QPushButton('Ã°ÂŸÂ”Â Smart Scan', self)
        self.smartScanButton.setStyleSheet("background-color: black; color: white; font-weight: ;")
        self.smartScanButton.clicked.connect(self.openSmartScanDialog)
        buttons_layout.addWidget(self.smartScanButton)


        self.mergeEPGButton = QPushButton('Ã°ÂŸÂ“Âº Fix EPG', self)
        self.mergeEPGButton.setStyleSheet("background-color: black; color: white;")
        self.mergeEPGButton.clicked.connect(self.merge_or_fix_epg)
        buttons_layout.addWidget(self.mergeEPGButton)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        # Add the horizontal layout to the vertical layout
        layout.addLayout(buttons_layout)

        return layout

    def convertStalkerToM3U(self):
        """Ã—Â”Ã—ÂžÃ—Â¨Ã—Âª Portal/Stalker Ã—Âœ-M3U - Ã—Â’Ã—Â¨Ã—Â¡Ã—Â” Ã—ÂžÃ—ÂªÃ—Â§Ã—Â“Ã—ÂžÃ—Âª"""

        if not PORTAL_CONVERTER_AVAILABLE:
            QMessageBox.critical(
                self,
                "Feature Not Available",
                "Portal Converter module is not available.\n"
                "Please ensure portal_extensions.py is in the M3U_EDITOR folder."
            )
            return

        try:
            # Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—Â—Ã—ÂœÃ—Â•Ã—ÂŸ Ã—Â”Ã—ÂžÃ—ÂžÃ—Â™Ã—Â¨ Ã—Â”Ã—ÂžÃ—ÂªÃ—Â§Ã—Â“Ã—Â
            converter = AdvancedPortalConverter(self)
            converter.exec_()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Portal Converter Error",
                f"Failed to open Portal Converter:\n\n{str(e)}"
            )
            print(f"Portal Converter Error: {e}")

    def displayTotalChannels(self):
        """
        Ã—ÂžÃ—Â—Ã—Â©Ã—Â‘Ã—Âª Ã—Â•Ã—ÂžÃ—Â¦Ã—Â™Ã—Â’Ã—Â” Ã—ÂÃ—Âª Ã—Â›Ã—ÂžÃ—Â•Ã—Âª Ã—Â›Ã—Âœ Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â‘Ã—Â›Ã—Âœ Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª
        Ã—Â•Ã—ÂÃ—Âª Ã—ÂžÃ—Â¡Ã—Â¤Ã—Â¨ Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª, Ã—Â‘Ã—ÂªÃ—Â•Ã—Â•Ã—Â™Ã—Âª Ã—Â’Ã—ÂœÃ—Â•Ã—Â‘Ã—ÂœÃ—Â™Ã—Âª Ã—ÂÃ—Â—Ã—Âª.
        """
        total_channels = sum(len(ch_list) for ch_list in self.categories.values())
        total_categories = len(self.categories)
        text = f"Ã°ÂŸÂ“Âº Total Channels: {total_channels}   |   Ã°ÂŸÂ—Â‚ Categories: {total_categories}"
        self.channelCountLabel.setText(text)
        self.channelCountLabel.setToolTip(
            f"{total_channels} Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â‘Ã–Â¾{total_categories} Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª"
        )

    def sortChannels(self):
        """
        Ã—ÂžÃ—ÂžÃ—Â™Ã—Â™Ã—ÂŸ Ã—ÂÃ—Âª self.categories[<Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â Ã—Â•Ã—Â›Ã—Â—Ã—Â™Ã—Âª>] Ã—Â¢Ã—Â¤Ã—Â´Ã—Â™ Ã—Â”Ã—ÂÃ—Â¤Ã—Â©Ã—Â¨Ã—Â•Ã—Âª Ã—Â©Ã—Â‘-sortingComboBox
        Ã—Â•Ã—ÂÃ—Â– Ã—ÂžÃ—Â¨Ã—Â¢Ã—Â Ã—ÂŸ Ã—ÂÃ—Âª Ã—Â”Ã—ÂªÃ—Â¦Ã—Â•Ã—Â’Ã—Â” Ã—Â•Ã—Â”-M3U.
        """
        # Ã—Â‘Ã—Â•Ã—Â“Ã—Â§ Ã—Â©Ã—Â™Ã—Â© Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â Ã—Â‘Ã—Â—Ã—Â¨Ã—Âª
        cur_item = self.categoryList.currentItem()
        if not cur_item:
            return

        # Ã—Â©Ã—Â Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” (Ã—ÂœÃ—ÂœÃ—Â Ã—Â”Ã—Â¡Ã—Â¤Ã—Â™Ã—Â¨Ã—Â” Ã—Â©Ã—Â‘Ã—Â¡Ã—Â•Ã—Â’Ã—Â¨Ã—Â™Ã—Â™Ã—Â)
        cur_cat = cur_item.text().split(" (")[0].strip()
        if cur_cat not in self.categories:
            return

        # Ã—ÂÃ—Â•Ã—Â¤Ã—Â¦Ã—Â™Ã—Â™Ã—Âª Ã—Â”Ã—ÂžÃ—Â™Ã—Â•Ã—ÂŸ Ã—Â”Ã—Â Ã—Â‘Ã—Â—Ã—Â¨Ã—Âª Ã—ÂžÃ—Â”-ComboBox
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

        elif option == "Sort by Quality (4K Ã¢Â†Â’ SD)":
            # Ã—ÂžÃ—Â©Ã—ÂªÃ—ÂžÃ—Â© Ã—Â‘Ã—Â¤Ã—Â•Ã—Â Ã—Â§Ã—Â¦Ã—Â™Ã—Â” detect_stream_quality Ã—Â”Ã—ÂžÃ—Â–Ã—Â”Ã—Â” Ã—ÂÃ—Â™Ã—Â›Ã—Â•Ã—Âª Ã—ÂžÃ—ÂªÃ—Â•Ã—Âš Ã—Â”Ã—ÂžÃ—Â—Ã—Â¨Ã—Â•Ã—Â–Ã—Âª
            def quality_rank(entry: str) -> int:
                q = detect_stream_quality(entry)
                return {
                    "4K": 0,
                    "FHD": 1,
                    "HD": 2,
                    "SD": 3
                }.get(q, 4)

            channels.sort(key=quality_rank)

        # Ã—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Âª Ã—Â”Ã—ÂªÃ—Â•Ã—Â¦Ã—ÂÃ—Â” Ã—Â‘Ã—Â—Ã—Â–Ã—Â¨Ã—Â” Ã—Â‘Ã—ÂžÃ—Â™Ã—ÂœÃ—Â•Ã—ÂŸ
        self.categories[cur_cat] = channels

        # Ã—Â¨Ã—Â¢Ã—Â Ã—Â•Ã—ÂŸ Ã—Â”Ã—ÂªÃ—Â¦Ã—Â•Ã—Â’Ã—Â” Ã—Â•Ã—Â›Ã—ÂªÃ—Â™Ã—Â‘Ã—Âª Ã—Â”-M3U Ã—Â”Ã—ÂžÃ—Â¢Ã—Â•Ã—Â“Ã—Â›Ã—ÂŸ
        self.display_channels(cur_item)
        self.regenerateM3UTextOnly()

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
        self.exportTelegramButton = QPushButton(" Export to Telegram")  # Ã¢Â†Â Ã—Â›Ã—Â¤Ã—ÂªÃ—Â•Ã—Â¨ Ã—Â—Ã—Â“Ã—Â©
        self.exportTelegramButton.setIcon(QIcon("icons/telegram.png"))

        self.loadButton.setStyleSheet("background-color: green; color: white;")
        self.saveButton.setStyleSheet("background-color: red; color: white;")
        self.mergeButton.setStyleSheet("background-color: blue; color: white;")
        self.exportTelegramButton.setStyleSheet("background-color: teal; color: white;")

        self.loadButton.clicked.connect(self.loadM3U)
        self.saveButton.clicked.connect(self.saveM3U)
        self.mergeButton.clicked.connect(self.mergeM3Us)
        self.exportTelegramButton.clicked.connect(self.exportToTelegram)  # Ã¢Â†Â Ã—Â—Ã—Â™Ã—Â‘Ã—Â•Ã—Â¨ Ã—ÂœÃ—Â¤Ã—Â•Ã—Â Ã—Â§Ã—Â¦Ã—Â™Ã—Â”

        # Ã—Â”Ã—Â•Ã—Â¡Ã—Â¤Ã—Â” Ã—ÂœÃ—ÂœÃ—Â™Ã—Â™Ã—ÂÃ—ÂÃ—Â•Ã—Â˜
        button_layout.addWidget(self.loadButton)
        button_layout.addWidget(self.saveButton)
        button_layout.addWidget(self.mergeButton)
        button_layout.addWidget(self.exportTelegramButton)  # Ã¢Â†Â Ã—Â‘Ã—Â¡Ã—Â•Ã—Â£ Ã—ÂžÃ—Â™Ã—ÂžÃ—Â™Ã—ÂŸ

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

            # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—Â”Ã—Â¡Ã—Â¤Ã—Â™Ã—Â¨Ã—Â” Ã—Â”Ã—Â›Ã—ÂœÃ—ÂœÃ—Â™Ã—Âª Ã—Â©Ã—Âœ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â + Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª
            self.displayTotalChannels()

    def cleanEmptyCategories(self):
        """
        Ã—ÂžÃ—Â Ã—Â§Ã—Â” Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—Â¨Ã—Â™Ã—Â§Ã—Â•Ã—Âª Ã—ÂžÃ—ÂªÃ—Â•Ã—Âš self.categories
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
                if isinstance(channel, dict):  # Ã—Â‘Ã—ÂžÃ—Â‘Ã—Â Ã—Â” Ã—Â”Ã—Â—Ã—Â“Ã—Â©
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

            # Ã—Â—Ã—Â¡Ã—Â™Ã—ÂžÃ—Âª Ã—Â¡Ã—Â™Ã—Â’Ã—Â Ã—ÂœÃ—Â™Ã—Â Ã—Â•Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—Â Ã—Â™Ã—Â Ã—Â‘Ã—Â–Ã—ÂžÃ—ÂŸ Ã—Â”Ã—Â”Ã—Â–Ã—Â–Ã—Â”
            self.categoryList.blockSignals(True)
            self.setUpdatesEnabled(False)

            # Ã—Â”Ã—Â–Ã—Â–Ã—Âª Ã—Â”Ã—Â¤Ã—Â¨Ã—Â™Ã—Â˜ Ã—Â‘Ã—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Âª Ã—Â”-UI
            item = self.categoryList.takeItem(current_row)
            if item is None:
                # Ã—Â”Ã—Â’Ã—Â Ã—Â” Ã—ÂœÃ—ÂžÃ—Â§Ã—Â¨Ã—Â” Ã—Â Ã—Â“Ã—Â™Ã—Â¨
                self.categoryList.blockSignals(False)
                self.setUpdatesEnabled(True)
                return

            self.categoryList.insertItem(current_row - 1, item)
            self.categoryList.setCurrentRow(current_row - 1)

            # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—Â¡Ã—Â“Ã—Â¨ Ã—Â”Ã—ÂžÃ—Â™Ã—ÂœÃ—Â•Ã—ÂŸ Ã—Â‘Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â•Ã—Âª Ã—Â•Ã—ÂœÃ—ÂœÃ—Â Ã—Â”Ã—Â§Ã—Â¤Ã—Â¦Ã—Â•Ã—Âª
            keys = list(self.categories.keys())
            keys[current_row - 1], keys[current_row] = keys[current_row], keys[current_row - 1]

            # Ã—Â‘Ã—Â Ã—Â™Ã—Â™Ã—Â” Ã—ÂžÃ—Â—Ã—Â“Ã—Â© Ã—Â¢Ã—Âœ Ã—Â‘Ã—Â¡Ã—Â™Ã—Â¡ Ã—Â”Ã—Â¦Ã—Â™Ã—ÂœÃ—Â•Ã—Â Ã—Â”Ã—Â§Ã—Â™Ã—Â™Ã—Â Ã—Â›Ã—Â“Ã—Â™ Ã—ÂœÃ—ÂžÃ—Â Ã—Â•Ã—Â¢ Ã—Â’Ã—Â™Ã—Â©Ã—Â” Ã—ÂªÃ—Â•Ã—Âš Ã—Â©Ã—Â™Ã—Â Ã—Â•Ã—Â™
            old_categories = self.categories
            self.categories = {k: old_categories[k] for k in keys}

        except Exception as e:
            try:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"moveCategoryUp failed: {e}")
            except Exception:
                pass
        finally:
            # Ã—Â©Ã—Â—Ã—Â¨Ã—Â•Ã—Â¨ Ã—Â—Ã—Â¡Ã—Â™Ã—ÂžÃ—Â•Ã—Âª Ã—Â•Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—Â Ã—Â™Ã—Â
            self.categoryList.blockSignals(False)
            self.setUpdatesEnabled(True)

            # Ã—Â¨Ã—Â¢Ã—Â Ã—Â•Ã—ÂŸ Ã—ÂžÃ—Â•Ã—Â©Ã—Â”Ã—Â” Ã—ÂœÃ—Â˜Ã—Â™Ã—Â§ Ã—Â”Ã—Â‘Ã—Â Ã—Â©Ã—Âœ Ã—ÂœÃ—Â•Ã—ÂœÃ—ÂÃ—Âª Ã—Â”Ã—ÂÃ—Â™Ã—Â¨Ã—Â•Ã—Â¢Ã—Â™Ã—Â Ã—ÂœÃ—ÂžÃ—Â Ã—Â™Ã—Â¢Ã—Âª Ã—Â§Ã—Â¨Ã—Â™Ã—Â¡Ã—Â•Ã—Âª Qt
            idx = max(0, current_row - 1)
            QTimer.singleShot(0, lambda: self.refreshCategoryListOnly(selected_index=idx))
            QTimer.singleShot(0, self.regenerateM3UTextOnly)

    def moveCategoryDown(self):
        try:
            current_row = self.categoryList.currentRow()
            last_index = self.categoryList.count() - 1
            if current_row < 0 or current_row >= last_index:
                return

            # Ã—Â—Ã—Â¡Ã—Â™Ã—ÂžÃ—Âª Ã—Â¡Ã—Â™Ã—Â’Ã—Â Ã—ÂœÃ—Â™Ã—Â Ã—Â•Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—Â Ã—Â™Ã—Â Ã—Â‘Ã—Â–Ã—ÂžÃ—ÂŸ Ã—Â”Ã—Â”Ã—Â–Ã—Â–Ã—Â”
            self.categoryList.blockSignals(True)
            self.setUpdatesEnabled(False)

            # Ã—Â”Ã—Â–Ã—Â–Ã—Âª Ã—Â”Ã—Â¤Ã—Â¨Ã—Â™Ã—Â˜ Ã—Â‘Ã—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Âª Ã—Â”-UI
            item = self.categoryList.takeItem(current_row)
            if item is None:
                self.categoryList.blockSignals(False)
                self.setUpdatesEnabled(True)
                return

            self.categoryList.insertItem(current_row + 1, item)
            self.categoryList.setCurrentRow(current_row + 1)

            # Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—Â¡Ã—Â“Ã—Â¨ Ã—Â”Ã—ÂžÃ—Â™Ã—ÂœÃ—Â•Ã—ÂŸ Ã—Â‘Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â•Ã—Âª Ã—Â•Ã—ÂœÃ—ÂœÃ—Â Ã—Â”Ã—Â§Ã—Â¤Ã—Â¦Ã—Â•Ã—Âª
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
            # Ã—Â©Ã—Â—Ã—Â¨Ã—Â•Ã—Â¨ Ã—Â—Ã—Â¡Ã—Â™Ã—ÂžÃ—Â•Ã—Âª Ã—Â•Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—Â Ã—Â™Ã—Â
            self.categoryList.blockSignals(False)
            self.setUpdatesEnabled(True)

            # Ã—Â¨Ã—Â¢Ã—Â Ã—Â•Ã—ÂŸ Ã—ÂžÃ—Â•Ã—Â©Ã—Â”Ã—Â” Ã—ÂœÃ—Â˜Ã—Â™Ã—Â§ Ã—Â”Ã—Â‘Ã—Â Ã—Â©Ã—Âœ Ã—ÂœÃ—Â•Ã—ÂœÃ—ÂÃ—Âª Ã—Â”Ã—ÂÃ—Â™Ã—Â¨Ã—Â•Ã—Â¢Ã—Â™Ã—Â
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
            country_order = ['il', 'usa', 'uk', 'fr', 'es', 'de', 'ru', 'ar']  # Ã—Â“Ã—Â•Ã—Â’Ã—ÂžÃ—Â”

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
        # Ã—ÂžÃ—Â˜Ã—ÂžÃ—Â•Ã—ÂŸ Ã—Â¡Ã—Â˜Ã—Â˜Ã—Â™ Ã—ÂœÃ—Â‘Ã—Â™Ã—Â¦Ã—Â•Ã—Â¢Ã—Â™Ã—Â Ã—ÂžÃ—Â§Ã—Â¡Ã—Â™Ã—ÂžÃ—ÂœÃ—Â™Ã—Â™Ã—Â
        if not hasattr(self, '_logo_db_cache'):
            self._logo_db_cache = {}
            self._logo_db_timestamp = 0

        # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Âª Ã—ÂžÃ—Â˜Ã—ÂžÃ—Â•Ã—ÂŸ Ã—ÂžÃ—ÂÃ—Â•Ã—Â“ Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â”
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

        # EPG header - Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—ÂžÃ—ÂÃ—Â•Ã—Â“
        if hasattr(self, "epg_headers") and self.epg_headers:
            header = self.buildUnifiedEPGHeader()
        else:
            header = "#EXTM3U"

        # Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Â” Ã—ÂÃ—Â—Ã—Âª Ã—Â’Ã—Â“Ã—Â•Ã—ÂœÃ—Â” Ã—Â‘Ã—ÂžÃ—Â§Ã—Â•Ã—Â append Ã—ÂžÃ—Â¨Ã—Â•Ã—Â‘Ã—Â™Ã—Â - Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—Â¤Ã—Â™ 50
        all_lines = [header]

        # Ã—ÂÃ—Â•Ã—Â¤Ã—Â˜Ã—Â™Ã—ÂžÃ—Â™Ã—Â–Ã—Â¦Ã—Â™Ã—Â” Ã—ÂžÃ—Â˜Ã—Â•Ã—Â¨Ã—Â¤Ã—Âª: list comprehension Ã—Â¢Ã—Â Ã—Â¤Ã—Â¢Ã—Â•Ã—ÂœÃ—Â” Ã—ÂÃ—Â—Ã—Âª
        for category, channels in self.categories.items():
            # Ã—Â¤Ã—Â™Ã—ÂœÃ—Â˜Ã—Â¨Ã—Â™Ã—Â Ã—Â’ Ã—Â•Ã—Â—Ã—Â™Ã—ÂªÃ—Â•Ã—Âš Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—Â‘Ã—ÂžÃ—Â§Ã—Â•Ã—Â try/except Ã—ÂÃ—Â™Ã—Â˜Ã—Â™
            valid_channels = [
                (ch.split(" (", 1)[0].strip(), ch.split(" (", 1)[1].strip(") \n"))
                for ch in channels
                if " (" in ch and ch.count(" (") == 1
            ]

            # Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—Â©Ã—Â•Ã—Â¨Ã—Â•Ã—Âª M3U Ã—Â‘Ã—ÂžÃ—Â§Ã—Â‘Ã—Â¥ - Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—Â¤Ã—Â™ 100
            for name, url in valid_channels:
                # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Âª logo Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â”
                logo_url = logo_db.get(name)
                if isinstance(logo_url, list) and logo_url:
                    logo_url = logo_url[0]

                # Ã—Â‘Ã—Â Ã—Â™Ã—Â™Ã—Â” Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨Ã—Â” Ã—Â©Ã—Âœ EXTINF
                if logo_url:
                    extinf = f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="{category}",{name}'
                else:
                    extinf = f'#EXTINF:-1 group-title="{category}",{name}'

                all_lines.extend([extinf, url])

        # join Ã—ÂÃ—Â—Ã—Â“ Ã—Â‘Ã—ÂžÃ—Â§Ã—Â•Ã—Â Ã—Â”Ã—Â¨Ã—Â‘Ã—Â” - Ã—ÂžÃ—Â”Ã—Â™Ã—Â¨ Ã—Â¤Ã—Â™ 1000
        self.safely_update_text_edit("\n".join(all_lines))

    def exportM3UWithLogos(self, path):
        """
        Ã—Â™Ã—Â™Ã—Â¦Ã—Â•Ã—Â Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ M3U Ã—ÂœÃ—ÂÃ—Â—Ã—Â¨ Ã—Â”Ã—Â–Ã—Â¨Ã—Â§Ã—Âª Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â Ã—ÂžÃ—ÂªÃ—Â•Ã—Âš Ã—Â”Ã–Â¾DB.
        """
        if not self.full_text:
            print("Ã¢Â›Â” Ã—ÂÃ—Â™Ã—ÂŸ Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—ÂœÃ—Â™Ã—Â™Ã—Â¦Ã—Â.")
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

            print(f"[LOGO] Ã¢ÂœÂ… Ã—Â™Ã—Â™Ã—Â¦Ã—Â•Ã—Â Ã—Â¢Ã—Â Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â Ã—Â‘Ã—Â•Ã—Â¦Ã—Â¢: {path}")

        except Exception as e:
            print(f"[LOGO] Ã¢ÂÂŒ Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â” Ã—Â‘Ã—Â™Ã—Â™Ã—Â¦Ã—Â•Ã—Â Ã—Â¢Ã—Â Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â: {e}")

    def get_saved_logo(channel_name):
        try:
            with open(LOGO_DB_PATH, "r", encoding="utf-8") as f:
                logos = json.load(f)
                logo = logos.get(channel_name)
                if isinstance(logo, list):
                    return logo[0] if logo else None
                return logo
        except Exception as e:
            print(f"[LOGO] Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â” Ã—Â‘Ã—Â§Ã—Â¨Ã—Â™Ã—ÂÃ—Âª Ã—Â‘Ã—Â¡Ã—Â™Ã—Â¡ Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â: {e}")
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
            # Ã¢Â†Â Ã—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Â” Ã—Â©Ã—Âœ Ã—Â”Ã—ÂžÃ—Â—Ã—Â¨Ã—Â•Ã—Â–Ã—Âª Ã—Â”Ã—ÂžÃ—ÂœÃ—ÂÃ—Â” Ã—Â‘Ã—ÂžÃ—Â§Ã—Â•Ã—Â Ã—ÂÃ—Â—Ã—Â“ Ã—Â‘Ã—ÂœÃ—Â‘Ã—Â“
            channel_item.setData(Qt.UserRole, full_entry)
            self.channelList.addItem(channel_item)

            selected_category = self.categoryList.currentItem()
            if selected_category:
                cat = selected_category.text().split(" (")[0].strip()
                self.categories[cat].append(full_entry)
                self.updateM3UContent()
            # Ã—ÂÃ—Â—Ã—Â¨Ã—Â™ Ã—Â›Ã—Âœ Ã—Â©Ã—Â™Ã—Â Ã—Â•Ã—Â™ Ã—Â‘-self.categories Ã—Â›Ã—Â“Ã—ÂÃ—Â™ Ã—Â’Ã—Â
            self.display_channels(self.categoryList.currentItem())

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

        # Ã¢Â†Â Ã—Â”Ã—Â•Ã—Â¡Ã—Â¤Ã—Â” Ã—Â›Ã—ÂÃ—ÂŸ Ã¢Â€Â” Ã—Â‘Ã—Â“Ã—Â™Ã—Â•Ã—Â§ Ã—ÂÃ—Â—Ã—Â¨Ã—Â™ Ã—Â©Ã—Â™Ã—Â Ã—Â•Ã—Â™ Ã—Â”Ã–Â¾categories:
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

        # Ã—Â˜Ã—Â¢Ã—ÂŸ Ã—Â¤Ã—Â¢Ã—Â Ã—ÂÃ—Â—Ã—Âª Ã—ÂÃ—Âª Ã—Â”Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â
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
                    # Ã—Â‘Ã—Â“Ã—Â•Ã—Â§ Ã—ÂÃ—Â Ã—Â§Ã—Â™Ã—Â™Ã—Â tvg-logo Ã—Â‘Ã—Â©Ã—Â•Ã—Â¨Ã—Â” Ã—Â¢Ã—Â¦Ã—ÂžÃ—Â”
                    match = re.search(r'tvg-logo="([^"]+)"', channel)
                    if match:
                        logo_url = match.group(1).strip()
                        existing = logo_db.get(name, [])
                        if isinstance(existing, str):
                            existing = [existing]

                        # Ã—ÂÃ—Âœ Ã—ÂªÃ—Â©Ã—ÂžÃ—Â•Ã—Â¨ Ã—Â©Ã—Â•Ã—Â‘ Ã—ÂÃ—Â Ã—Â›Ã—Â‘Ã—Â¨ Ã—Â§Ã—Â™Ã—Â™Ã—Â
                        if logo_url and logo_url not in existing:
                            logo_db.setdefault(name, []).append(logo_url)
                            save_logo_for_channel(name, logo_url)
                    else:
                        logo_url = get_saved_logo(name)
                else:
                    logo_url = get_saved_logo(name)

                # Ã—Â¦Ã—Â•Ã—Â¨ EXTINF Ã—Â¢Ã—Â Ã—ÂÃ—Â• Ã—Â‘Ã—ÂœÃ—Â™ Ã—ÂœÃ—Â•Ã—Â’Ã—Â•
                if logo_url:
                    extinf = f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="{category}",{name}'
                else:
                    extinf = f'#EXTINF:-1 group-title="{category}",{name}'

                updated_lines.append(f"{extinf}\n{url}")

        # Ã—Â‘Ã—Â“Ã—Â•Ã—Â§ Ã—ÂÃ—Â Ã—Â™Ã—Â© Ã—Â©Ã—Â™Ã—Â Ã—Â•Ã—Â™ Ã—ÂÃ—ÂžÃ—Â™Ã—ÂªÃ—Â™ Ã—Â‘Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—ÂœÃ—Â¤Ã—Â Ã—Â™ setPlainText (Ã—ÂžÃ—ÂÃ—Â•Ã—Â“ Ã—ÂÃ—Â™Ã—Â˜Ã—Â™)
        new_content = "\n".join(updated_lines)
        if self.textEdit.toPlainText().strip() != new_content.strip():
            self.safely_update_text_edit(new_content)

        print("[LOG] Ã°ÂŸÂ”Â„ Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ M3U Ã—Â‘Ã—Â•Ã—Â¦Ã—Â¢", "Ã—Â›Ã—Â•Ã—ÂœÃ—Âœ Ã—Â¡Ã—Â¨Ã—Â™Ã—Â§Ã—Âª Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â" if not skip_logos else "Ã—ÂœÃ—ÂœÃ—Â Ã—Â¡Ã—Â¨Ã—Â™Ã—Â§Ã—Âª Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â")


    def moveChannelUp(self):
        """
        Ã—ÂžÃ—Â¢Ã—Â‘Ã—Â™Ã—Â¨ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—ÂÃ—Â—Ã—Â“ Ã—ÂœÃ—ÂžÃ—Â¢Ã—ÂœÃ—Â” Ã—Â”Ã—ÂŸ Ã—Â‘-UI Ã—Â•Ã—Â”Ã—ÂŸ Ã—Â‘-metadata Ã—Â©Ã—Âœ self.categories.
        """
        current_row = self.channelList.currentRow()
        if current_row <= 0:
            return

        # Ã—ÂžÃ—Â•Ã—Â¦Ã—Â™Ã—ÂÃ—Â™Ã—Â Ã—ÂÃ—Âª Ã—Â”Ã–Â¾entry Ã—Â”Ã—ÂžÃ—ÂœÃ—Â
        current_item = self.channelList.item(current_row)
        full_entry = current_item.data(Qt.UserRole)

        # Ã—ÂžÃ—Â•Ã—Â¦Ã—ÂÃ—Â™Ã—Â Ã—ÂÃ—Âª Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â”Ã—Â¤Ã—Â¢Ã—Â™Ã—ÂœÃ—Â”
        category = self.categoryList.currentItem().text().split(" (")[0].strip()
        real_category = {k.strip(): k for k in self.categories.keys()}.get(category, category)
        channels = self.categories.get(real_category, [])

        # Ã—Â”Ã—Â—Ã—ÂœÃ—Â¤Ã—Âª Ã—ÂžÃ—Â™Ã—Â§Ã—Â•Ã—ÂžÃ—Â™Ã—Â Ã—Â‘Ã—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Âª Ã—Â”Ã—Â¤Ã—Â•Ã—Â Ã—ÂœÃ—Â™Ã—Â
        channels[current_row], channels[current_row - 1] = channels[current_row - 1], channels[current_row]
        self.categories[real_category] = channels

        # Ã—Â‘Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—Â”-UI Ã—ÂžÃ—Â•Ã—Â—Ã—Â§Ã—Â™Ã—Â Ã—Â•Ã—ÂžÃ—Â•Ã—Â¡Ã—Â™Ã—Â¤Ã—Â™Ã—Â Ã—Â¢Ã—Â Ã—Â”Ã—Â Ã—ÂªÃ—Â•Ã—Â Ã—Â™Ã—Â Ã—Â”Ã—ÂžÃ—Â¢Ã—Â•Ã—Â“Ã—Â›Ã—Â Ã—Â™Ã—Â
        self.channelList.takeItem(current_row)
        new_item = QListWidgetItem(full_entry.split(" (")[0].strip())
        new_item.setData(Qt.UserRole, full_entry)
        self.channelList.insertItem(current_row - 1, new_item)
        self.channelList.setCurrentRow(current_row - 1)

        # Ã—Â¨Ã—Â¢Ã—Â Ã—Â•Ã—ÂŸ Ã—Â”Ã—ÂžÃ—Â—Ã—Â¨Ã—Â•Ã—Â–Ã—Âª Ã—ÂœÃ–Â¾M3U
        self.regenerateM3UTextOnly()

    def moveChannelDown(self):
        """
        Ã—ÂžÃ—Â¢Ã—Â‘Ã—Â™Ã—Â¨ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—ÂÃ—Â—Ã—Â“ Ã—ÂœÃ—ÂžÃ—Â˜Ã—Â” Ã—Â”Ã—ÂŸ Ã—Â‘-UI Ã—Â•Ã—Â”Ã—ÂŸ Ã—Â‘-metadata Ã—Â©Ã—Âœ self.categories.
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
        for i in range(self.channelList.count()):
            self.channelList.item(i).setSelected(True)

    def deselectAllChannels(self):
        for i in range(self.channelList.count()):
            self.channelList.item(i).setSelected(False)

    def moveSelectedChannel(self):
        """
        Ã—ÂžÃ—Â¢Ã—Â‘Ã—Â™Ã—Â¨ Ã—ÂÃ—Âª Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â”Ã—ÂžÃ—Â¡Ã—Â•Ã—ÂžÃ—Â Ã—Â™Ã—Â Ã—ÂœÃ—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â©Ã—Â Ã—Â‘Ã—Â—Ã—Â¨Ã—Â” Ã—Â‘Ã—Â“Ã—Â™Ã—ÂÃ—ÂœÃ—Â•Ã—Â’, Ã—ÂžÃ—Â¦Ã—Â™Ã—Â’ Ã—Â”Ã—Â•Ã—Â“Ã—Â¢Ã—Âª Ã—Â¡Ã—Â™Ã—Â›Ã—Â•Ã—Â,
        Ã—Â•Ã—ÂžÃ—Â•Ã—Â—Ã—Â§ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â¨Ã—Â™Ã—Â§Ã—Â” Ã—ÂÃ—Â Ã—Â”Ã—Â¢Ã—Â‘Ã—Â¨Ã—Â Ã—Â• Ã—ÂÃ—Âª Ã—Â›Ã—Âœ Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂžÃ—ÂžÃ—Â Ã—Â”.
        """
        try:
            # 1. Ã—Â©Ã—ÂœÃ—Â™Ã—Â¤Ã—Âª Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â”Ã—ÂžÃ—Â¡Ã—Â•Ã—ÂžÃ—Â Ã—Â™Ã—Â
            items = self.channelList.selectedItems()
            if not items:
                QMessageBox.warning(self, "Warning", "No channels selected for moving.")
                return

            # 2. Ã—Â”Ã—ÂžÃ—Â¨Ã—Âª Ã—Â¤Ã—Â¨Ã—Â™Ã—Â˜Ã—Â™Ã—Â Ã—ÂœÃ—ÂžÃ—Â—Ã—Â¨Ã—Â•Ã—Â–Ã—Â•Ã—Âª Ã—ÂžÃ—ÂœÃ—ÂÃ—Â•Ã—Âª "Name (URL)"
            selected_entries = []
            for item in items:
                raw = item.data(Qt.UserRole)
                entry = raw if isinstance(raw, str) else item.text().strip()
                selected_entries.append(entry)
            selected_names = [e.split(" (")[0].strip() for e in selected_entries]

            # 3. Ã—Â“Ã—Â™Ã—ÂÃ—ÂœÃ—Â•Ã—Â’ Ã—Â‘Ã—Â—Ã—Â™Ã—Â¨Ã—Âª Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â—Ã—Â“Ã—Â©Ã—Â”/Ã—Â§Ã—Â™Ã—Â™Ã—ÂžÃ—Âª
            dialog = MoveChannelsDialog(self, list(self.categories.keys()))
            if dialog.exec_() != QDialog.Accepted:
                return
            target = dialog.getSelectedCategory().strip()
            if not target:
                QMessageBox.warning(self, "Warning", "No target category specified.")
                return

            # 4. Ã—Â”Ã—Â•Ã—Â¡Ã—Â¤Ã—Âª Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â—Ã—Â“Ã—Â©Ã—Â” Ã—ÂÃ—Â Ã—Â¦Ã—Â¨Ã—Â™Ã—Âš
            if target not in self.categories:
                self.categories[target] = []

            # 5. Ã—Â©Ã—Â Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â”Ã—Â Ã—Â•Ã—Â›Ã—Â—Ã—Â™Ã—Âª
            current_item = self.categoryList.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Warning", "No source category selected.")
                return
            source = current_item.text().split(" (")[0].strip()
            if source not in self.categories:
                QMessageBox.warning(self, "Warning", f"Category '{source}' does not exist.")
                return

            # 6. Ã—Â¤Ã—Â™Ã—ÂœÃ—Â•Ã—Â— Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂœÃ—ÂžÃ—Â•Ã—Â¢Ã—Â‘Ã—Â¨Ã—Â™Ã—Â Ã—Â•Ã—ÂœÃ—Â©Ã—ÂÃ—Â¨Ã—Â™Ã—Â™Ã—Â
            original = self.categories[source]
            moved = [entry for entry in original if entry.split(" (")[0].strip() in selected_names]
            remaining = [entry for entry in original if entry.split(" (")[0].strip() not in selected_names]

            # 7. Ã—Â‘Ã—Â™Ã—Â¦Ã—Â•Ã—Â¢ Ã—Â”Ã—ÂžÃ—Â¢Ã—Â‘Ã—Â¨ Ã—Â‘Ã—ÂžÃ—Â‘Ã—Â Ã—Â” Ã—Â”Ã—Â Ã—ÂªÃ—Â•Ã—Â Ã—Â™Ã—Â
            self.categories[source] = remaining
            self.categories[target].extend(moved)

            # 8. Ã—ÂžÃ—Â—Ã—Â™Ã—Â§Ã—Âª Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â¨Ã—Â™Ã—Â§Ã—Â”
            if not self.categories[source]:
                del self.categories[source]

            # 9. Ã—Â¨Ã—Â™Ã—Â¢Ã—Â Ã—Â•Ã—ÂŸ Ã—Â”Ã—ÂªÃ—Â¦Ã—Â•Ã—Â’Ã—Â”
            self.regenerateM3UTextOnly()
            self.updateCategoryList()
            # Ã—Â‘Ã—Â—Ã—Â™Ã—Â¨Ã—Âª Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â”Ã—Â™Ã—Â¢Ã—Â“Ã—Â™Ã—Âª Ã—Â•Ã—Â”Ã—Â¦Ã—Â’Ã—Âª Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â©Ã—ÂœÃ—Â”
            for i in range(self.categoryList.count()):
                if self.categoryList.item(i).text().split(" (")[0].strip() == target:
                    self.categoryList.setCurrentRow(i)
                    self.display_channels(self.categoryList.item(i))
                    break

            # 10. Ã—Â Ã—Â™Ã—Â§Ã—Â•Ã—Â™ Ã—Â‘Ã—Â—Ã—Â™Ã—Â¨Ã—Â•Ã—Âª Ã—Â•Ã—Â”Ã—Â¦Ã—Â’Ã—Âª Ã—Â”Ã—Â•Ã—Â“Ã—Â¢Ã—Âª Ã—Â¡Ã—Â™Ã—Â›Ã—Â•Ã—Â
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
        Ã—Â¤Ã—Â•Ã—ÂªÃ—Â— Ã—Â‘-VLC Ã—ÂÃ—Âª Ã—Â›Ã—Âœ Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â”Ã—ÂžÃ—Â¡Ã—Â•Ã—ÂžÃ—Â Ã—Â™Ã—Â (Ã—Â¨Ã—Â™Ã—Â‘Ã—Â•Ã—Â™ Ã—Â‘Ã—Â—Ã—Â™Ã—Â¨Ã—Â”).
        Ã—Â™Ã—Â•Ã—Â¦Ã—Â¨ Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ M3U Ã—Â–Ã—ÂžÃ—Â Ã—Â™ Ã—Â¢Ã—Â #EXTM3U Ã—Â•Ã—Â©Ã—Â•Ã—Â¨Ã—Â” Ã—ÂœÃ—Â›Ã—Âœ EXTINF+URL.
        Ã—ÂžÃ—Â¦Ã—Â™Ã—Â’ Ã—ÂÃ—Âª Ã—Â©Ã—Â Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—Â‘-VLC Ã—Â›Ã—Â™ Ã—ÂžÃ—Â©Ã—ÂªÃ—ÂžÃ—Â© Ã—Â‘Ã—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ Ã—Â”Ã—Â Ã—Â›Ã—Â•Ã—ÂŸ.
        Ã—Â’Ã—Â¨Ã—Â¡Ã—Â” Ã—ÂžÃ—ÂªÃ—Â•Ã—Â§Ã—Â Ã—Âª Ã—Â¢Ã—Â Ã—Â˜Ã—Â™Ã—Â¤Ã—Â•Ã—Âœ Ã—ÂžÃ—ÂœÃ—Â Ã—Â‘Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â•Ã—Âª.
        """
        items = self.channelList.selectedItems()
        if not items:
            QMessageBox.warning(self, "Ã—ÂÃ—Â™Ã—ÂŸ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â Ã—Â‘Ã—Â—Ã—Â¨Ã—Â™Ã—Â", "Ã—Â‘Ã—Â—Ã—Â¨ Ã—ÂœÃ—Â¤Ã—Â—Ã—Â•Ã—Âª Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—ÂÃ—Â—Ã—Â“ Ã—ÂœÃ—Â¦Ã—Â¤Ã—Â™Ã—Â™Ã—Â”.")
            return

        # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Âª Ã—Â§Ã—Â™Ã—Â•Ã—Â VLC
        vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
        if not os.path.exists(vlc_path):
            QMessageBox.critical(self, "VLC Ã—ÂœÃ—Â Ã—Â Ã—ÂžÃ—Â¦Ã—Â", f"Ã—ÂœÃ—Â Ã—Â Ã—ÂžÃ—Â¦Ã—Â VLC Ã—Â‘Ã—Â Ã—ÂªÃ—Â™Ã—Â‘:\n{vlc_path}")
            return

        # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Âª Ã—ÂžÃ—Â¡Ã—Â¤Ã—Â¨ Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â”Ã—Â Ã—Â‘Ã—Â—Ã—Â¨Ã—Â™Ã—Â
        valid_channels = 0

        try:
            # Ã—Â‘Ã—Â•Ã—Â Ã—Â™Ã—Â Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ M3U Ã—Â–Ã—ÂžÃ—Â Ã—Â™
            with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".m3u", delete=False, encoding="utf-8"
            ) as f:
                f.write("#EXTM3U\n")

                for item in items:
                    try:
                        # Ã—Â˜Ã—Â™Ã—Â¤Ã—Â•Ã—Âœ Ã—Â‘Ã—Â˜Ã—Â•Ã—Â— Ã—Â‘-UserRole data
                        raw = item.data(Qt.UserRole) if item else None
                        entry = raw if isinstance(raw, str) else (item.text().strip() if item else "")

                        if not entry:
                            continue

                        # Ã—ÂžÃ—Â¤Ã—Â¨Ã—Â§Ã—Â™Ã—Â Ã—ÂœÃ–Â¾name Ã—Â•Ã–Â¾url Ã—Â¢Ã—Â Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Â•Ã—Âª Ã—Â‘Ã—Â˜Ã—Â™Ã—Â—Ã—Â•Ã—Âª
                        if "(" in entry and entry.endswith(")"):
                            parts = entry.split(" (", 1)  # Ã—ÂžÃ—Â’Ã—Â‘Ã—Â™Ã—Âœ Ã—ÂœÃ—Â¤Ã—Â™Ã—Â¦Ã—Â•Ã—Âœ Ã—Â™Ã—Â—Ã—Â™Ã—Â“
                            if len(parts) >= 2:
                                name = parts[0].strip()
                                url = parts[1].rstrip(")").strip()
                            else:
                                continue
                        else:
                            # Ã—ÂÃ—Â Ã—Â”Ã—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ Ã—Â©Ã—Â‘Ã—Â•Ã—Â¨, Ã—Â“Ã—Â™Ã—ÂœÃ—Â•Ã—Â’ Ã—Â¢Ã—Âœ Ã—Â”Ã—Â¤Ã—Â¨Ã—Â™Ã—Â˜
                            print(f"[WARNING] Invalid channel format: {entry}")
                            continue

                        # Ã—Â•Ã—Â™Ã—Â“Ã—Â•Ã—Â Ã—Â©Ã—Â™Ã—Â© Ã—Â©Ã—Â Ã—Â•URL
                        if not name or not url:
                            continue

                        # Ã—ÂžÃ—Â Ã—Â¡Ã—Â™Ã—Â Ã—ÂœÃ—Â”Ã—Â©Ã—Â™Ã—Â’ #EXTINF Ã—ÂžÃ—Â§Ã—Â•Ã—Â¨Ã—Â™ Ã—ÂÃ—Â Ã—Â™Ã—Â©
                        extinf = None
                        if hasattr(self, 'extinf_lookup') and self.extinf_lookup:
                            extinf = self.extinf_lookup.get(entry)

                        if not extinf:
                            # Ã—Â™Ã—Â•Ã—Â¦Ã—Â¨Ã—Â™Ã—Â EXTINF Ã—ÂªÃ—Â§Ã—Â Ã—Â™ Ã—Â¢Ã—Â Ã—Â©Ã—Â Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—ÂÃ—Â—Ã—Â¨Ã—Â™ Ã—Â”Ã—Â¤Ã—Â¡Ã—Â™Ã—Â§
                            logo = ""
                            try:
                                logo = get_saved_logo(name) or ""
                            except:
                                pass

                            logo_tag = f' tvg-logo="{logo}"' if logo else ""

                            # group-title Ã—Â Ã—ÂœÃ—Â§Ã—Â— Ã—Âž-categoryList Ã—Â‘Ã—Â¦Ã—Â•Ã—Â¨Ã—Â” Ã—Â‘Ã—Â˜Ã—Â•Ã—Â—Ã—Â”
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

            # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Â” Ã—Â©Ã—Â™Ã—Â© Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂªÃ—Â§Ã—Â™Ã—Â Ã—Â™Ã—Â
            if valid_channels == 0:
                QMessageBox.warning(
                    self, "Ã—ÂÃ—Â™Ã—ÂŸ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂªÃ—Â§Ã—Â™Ã—Â Ã—Â™Ã—Â",
                    "Ã—ÂœÃ—Â Ã—Â Ã—ÂžÃ—Â¦Ã—ÂÃ—Â• Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—ÂªÃ—Â§Ã—Â™Ã—Â Ã—Â™Ã—Â Ã—ÂœÃ—Â¦Ã—Â¤Ã—Â™Ã—Â™Ã—Â”.\nÃ—Â‘Ã—Â“Ã—Â•Ã—Â§ Ã—ÂÃ—Âª Ã—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â”Ã—Â Ã—Â‘Ã—Â—Ã—Â¨Ã—Â™Ã—Â."
                )
                try:
                    os.remove(temp_path)
                except:
                    pass
                return

            # Ã—Â”Ã—Â•Ã—Â“Ã—Â¢Ã—Â” Ã—ÂžÃ—Â™Ã—Â“Ã—Â¢Ã—Â™Ã—Âª Ã—Â¢Ã—Âœ Ã—ÂžÃ—Â¡Ã—Â¤Ã—Â¨ Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â
            if valid_channels > 1:
                reply = QMessageBox.question(
                    self, "Ã—Â¤Ã—ÂªÃ—Â™Ã—Â—Ã—Âª Ã—ÂžÃ—Â¡Ã—Â¤Ã—Â¨ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â",
                    f"Ã—Â”Ã—ÂÃ—Â Ã—ÂœÃ—Â¤Ã—ÂªÃ—Â•Ã—Â— {valid_channels} Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â‘-VLC?\n\nÃ—Â–Ã—Â” Ã—Â¢Ã—ÂœÃ—Â•Ã—Âœ Ã—ÂœÃ—Â¦Ã—Â¨Ã—Â•Ã—Âš Ã—Â”Ã—Â¨Ã—Â‘Ã—Â” Ã—ÂžÃ—Â©Ã—ÂÃ—Â‘Ã—Â™ Ã—ÂžÃ—Â¢Ã—Â¨Ã—Â›Ã—Âª.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                    return

            # Ã—ÂžÃ—Â¨Ã—Â™Ã—Â¦Ã—Â™Ã—Â Ã—ÂÃ—Âª VLC Ã—Â¢Ã—Âœ Ã—Â›Ã—Âœ Ã—Â”Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥
            process = subprocess.Popen([vlc_path, temp_path])

            # Ã—Â”Ã—Â•Ã—Â“Ã—Â¢Ã—Âª Ã—Â”Ã—Â¦Ã—ÂœÃ—Â—Ã—Â”
            QMessageBox.information(
                self, "VLC Ã—Â”Ã—Â•Ã—Â¤Ã—Â¢Ã—Âœ",
                f"VLC Ã—Â”Ã—Â•Ã—Â¤Ã—Â¢Ã—Âœ Ã—Â‘Ã—Â”Ã—Â¦Ã—ÂœÃ—Â—Ã—Â” Ã—Â¢Ã—Â {valid_channels} Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â.\n\nÃ—Â”Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—Â”Ã—Â–Ã—ÂžÃ—Â Ã—Â™ Ã—Â™Ã—Â™Ã—ÂžÃ—Â—Ã—Â§ Ã—ÂÃ—Â•Ã—Â˜Ã—Â•Ã—ÂžÃ—Â˜Ã—Â™Ã—Âª Ã—Â›Ã—Â©Ã—ÂªÃ—Â¡Ã—Â’Ã—Â•Ã—Â¨ Ã—ÂÃ—Âª VLC."
            )

        except Exception as e:
            error_msg = f"Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â” Ã—Â›Ã—ÂœÃ—ÂœÃ—Â™Ã—Âª Ã—Â‘Ã—Â”Ã—Â¨Ã—Â¦Ã—Âª VLC: {e}"
            print(f"[ERROR] {error_msg}")
            QMessageBox.critical(self, "Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â” Ã—Â‘Ã—Â”Ã—Â¨Ã—Â¦Ã—Âª VLC", error_msg)

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
        Ã—ÂžÃ—Â¦Ã—Â™Ã—Â’ Ã—ÂÃ—Âª Ã—Â”Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â‘Ã—ÂÃ—Â•Ã—Â¤Ã—ÂŸ Ã—Â’Ã—Â¨Ã—Â¤Ã—Â™ Ã—Â¢Ã—Â Ã—ÂªÃ—Â’ Ã—ÂÃ—Â™Ã—Â›Ã—Â•Ã—Âª.
        """
        self.channelList.clear()
        if item is None:
            return

        cat = item.text().split(" (")[0].strip()
        real = {k.strip(): k for k in self.categories}.get(cat)
        if not real:
            return

        for entry in self.categories[real]:
            name = entry.split(" (")[0].strip()
            quality = detect_stream_quality(entry)
            widget = create_channel_widget(name, quality)

            lw_item = QListWidgetItem()
            lw_item.setSizeHint(widget.sizeHint())
            lw_item.setData(Qt.UserRole, entry)
            self.channelList.addItem(lw_item)
            self.channelList.setItemWidget(lw_item, widget)

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

        # Ã—Â Ã—Â™Ã—Â§Ã—Â•Ã—Â™ Ã—Â”Ã—Â©Ã—Â Ã—ÂžÃ—Â”Ã—Â©Ã—Â•Ã—Â•Ã—ÂÃ—Â•Ã—Âª Ã—ÂœÃ—Â Ã—ÂªÃ—Â§Ã—Â™Ã—Â Ã—Â•Ã—Âª (Ã—Â¨Ã—Â•Ã—Â•Ã—Â—Ã—Â™Ã—Â, Ã—ÂªÃ—Â•Ã—Â•Ã—Â™Ã—Â Ã—ÂžÃ—Â•Ã—Â¡Ã—ÂªÃ—Â¨Ã—Â™Ã—Â)
        normalized_input = category_name.strip()

        # Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—ÂžÃ—Â¤Ã—Â” Ã—Â©Ã—Âœ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—ÂžÃ—Â Ã—Â•Ã—Â¨Ã—ÂžÃ—ÂœÃ—Â•Ã—Âª Ã¢Â†Â’ Ã—ÂžÃ—Â§Ã—Â•Ã—Â¨
        normalized_map = {k.strip(): k for k in self.categories.keys()}

        # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Â” Ã—Â”Ã—ÂÃ—Â Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â§Ã—Â™Ã—Â™Ã—ÂžÃ—Âª
        if normalized_input not in normalized_map:
            QMessageBox.warning(self, "Warning", f"Category '{normalized_input}' not found in categories.")
            return

        # Ã—Â©Ã—ÂœÃ—Â•Ã—Â£ Ã—ÂÃ—Âª Ã—Â”Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â” Ã—Â”Ã—ÂžÃ—Â§Ã—Â•Ã—Â¨Ã—Â™Ã—Âª Ã—ÂžÃ—Â”Ã—ÂžÃ—Â¢Ã—Â¨Ã—Â›Ã—Âª
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

        # Ã—ÂžÃ—Â›Ã—Â™Ã—Â Ã—Â™Ã—Â Ã—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Âª Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â•Ã—ÂžÃ—Â™Ã—Â¤Ã—Â•Ã—Â™ Ã—ÂœÃ—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª
        channels = []
        category_map = {}
        for cat, lst in self.categories.items():
            for ch in lst:
                name = ch.split(" (")[0].strip()
                url = self.getUrl(ch)
                if url:
                    channels.append((name, url))
                    category_map[name.lower()] = cat

        # Ã—Â™Ã—Â•Ã—Â¦Ã—Â¨Ã—Â™Ã—Â Ã—ÂÃ—Âª Ã—Â”Ã—Â“Ã—Â™Ã—ÂÃ—ÂœÃ—Â•Ã—Â’ Ã—Â•Ã—ÂžÃ—Â•Ã—Â•Ã—Â“Ã—ÂÃ—Â™Ã—Â Ã—Â©Ã—Â”Ã—Â•Ã—Â Ã—Â™Ã—Â™Ã—ÂžÃ—Â—Ã—Â§ Ã—ÂÃ—Â•Ã—Â˜Ã—Â•Ã—ÂžÃ—Â˜Ã—Â™Ã—Âª
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

        dialog.setLayout(layout)  # Ã¢Â†Â Ã—Â—Ã—Â•Ã—Â‘Ã—Â”
        dialog.exec_()  # Ã¢Â†Â Ã—Â—Ã—Â•Ã—Â‘Ã—Â”

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
                    removed_count += 1  # Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¥ Ã—Â™Ã—Â™Ã—ÂžÃ—Â—Ã—Â§
                else:
                    new_channels.append(channel)

            self.categories[category] = new_channels

        self.updateM3UContent()
        self.display_channels(self.categoryList.currentItem())  # Ã—Â¨Ã—Â¢Ã—Â Ã—Â•Ã—ÂŸ Ã—Â”Ã—ÂªÃ—Â¦Ã—Â•Ã—Â’Ã—Â” Ã—ÂœÃ—ÂÃ—Â—Ã—Â¨ Ã—Â”Ã—ÂžÃ—Â—Ã—Â™Ã—Â§Ã—Â”
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
        targets = set(zip(names_to_delete, urls_to_delete))  # Ã—Â”Ã—Â¤Ã—Â•Ã—Âš Ã—ÂœÃ—Â¨Ã—Â©Ã—Â™Ã—ÂžÃ—Â” Ã—Â©Ã—Âœ Ã—Â–Ã—Â•Ã—Â’Ã—Â•Ã—Âª Ã—ÂžÃ—Â“Ã—Â•Ã—Â™Ã—Â§Ã—Â™Ã—Â

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
        Example: "Channel Name (http://...)" Ã¢Â†Â’ returns http://...
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

                # Ã—Â˜Ã—Â¢Ã—ÂŸ M3U Ã—Â“Ã—Â¨Ã—Âš Ã—Â”Ã—ÂžÃ—ÂªÃ—Â•Ã—Â“Ã—Â” Ã—Â”Ã—Â¨Ã—ÂÃ—Â©Ã—Â™Ã—Âª
                self.loadM3UFromText(content, append=False)

                # Ã¢ÂœÂ… Ã—Â¢Ã—Â“Ã—Â›Ã—Â•Ã—ÂŸ Ã—ÂªÃ—Â¦Ã—Â•Ã—Â’Ã—Â”
                total_channels = sum(len(channels) for channels in self.categories.values())
                total_categories = len(self.categories)
                summary = f"Ã°ÂŸÂ“Âº Total Channels: {total_channels}   |   Ã°ÂŸÂ—Â‚ Categories: {total_categories}"
                self.channelCountLabel.setText(summary)
                self.channelCountLabel.setToolTip(f"{total_channels} Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â Ã—Â‘Ã—Â¡Ã—Âš Ã—Â”Ã—Â›Ã—Âœ Ã—Â‘-{total_categories} Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª")
                self.fileNameLabel.setText(f"Loaded File: {os.path.basename(fileName)}")

                # Ã°ÂŸÂ§Â  Ã—Â˜Ã—Â¢Ã—Â™Ã—Â Ã—Âª Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ EPG Ã—ÂÃ—Â•Ã—Â˜Ã—Â•Ã—ÂžÃ—Â˜Ã—Â™Ã—Âª Ã—ÂÃ—Â Ã—Â§Ã—Â™Ã—Â™Ã—Â
                epg_base = os.path.splitext(fileName)[0]
                for ext in [".xml", ".xml.gz"]:
                    epg_candidate = epg_base + ext
                    if os.path.exists(epg_candidate):
                        self.loadEPG(epg_candidate)
                        break  # Ã—Â Ã—Â˜Ã—Â¢Ã—ÂŸ Ã—Â¨Ã—Â§ Ã—ÂÃ—Âª Ã—Â”Ã—Â¨Ã—ÂÃ—Â©Ã—Â•Ã—ÂŸ Ã—Â©Ã—Â Ã—ÂžÃ—Â¦Ã—Â

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

            # Ã°ÂŸÂ§Â  Ã—ÂžÃ—Â™Ã—Â•Ã—ÂŸ Ã—ÂœÃ—Â¤Ã—Â™ Ã—Â–Ã—ÂžÃ—ÂŸ Ã—Â”Ã—ÂªÃ—Â—Ã—ÂœÃ—Â”
            for programmes in self.epg_data.values():
                programmes.sort(key=lambda p: p.get('start', ''))

            QMessageBox.information(self, "EPG Loaded", f"Ã°ÂŸÂ“Â… EPG data loaded successfully.\nEntries parsed: {count}")

        except Exception as e:
            QMessageBox.critical(self, "EPG Error", f"Failed to load EPG file:\n{str(e)}")

    def openEPGViewer(self, tvg_id):
        from PyQt5.QtWidgets import QScrollArea, QCheckBox
        from datetime import datetime

        if not hasattr(self, 'epg_data') or tvg_id not in self.epg_data:
            QMessageBox.information(self, "EPG Viewer", "No EPG data available.")
            return

        # === Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—Â“Ã—Â™Ã—ÂÃ—ÂœÃ—Â•Ã—Â’ ===
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Ã°ÂŸÂ“Âº Ã—ÂœÃ—Â•Ã—Â— Ã—Â©Ã—Â™Ã—Â“Ã—Â•Ã—Â¨Ã—Â™Ã—Â: {tvg_id}")
        dialog.resize(600, 700)
        main_layout = QVBoxLayout(dialog)

        # === Ã—Â©Ã—Â•Ã—Â¨Ã—Âª Ã—Â—Ã—Â™Ã—Â¤Ã—Â•Ã—Â© ===
        search_input = QLineEdit()
        search_input.setPlaceholderText("Ã°ÂŸÂ”Â Ã—Â—Ã—Â¤Ã—Â© Ã—ÂªÃ—Â•Ã—Â›Ã—Â Ã—Â™Ã—Âª Ã—ÂœÃ—Â¤Ã—Â™ Ã—Â©Ã—Â Ã—ÂÃ—Â• Ã—ÂªÃ—Â™Ã—ÂÃ—Â•Ã—Â¨...")
        main_layout.addWidget(search_input)

        # === Ã—ÂªÃ—Â™Ã—Â‘Ã—Âª Ã—Â¡Ã—Â™Ã—ÂžÃ—Â•Ã—ÂŸ - Ã—Â¨Ã—Â§ Ã—Â¢Ã—Â›Ã—Â©Ã—Â™Ã—Â• ===
        now_only_checkbox = QCheckBox("Ã°ÂŸÂ“Â¡ Ã—Â”Ã—Â¦Ã—Â’ Ã—Â¨Ã—Â§ Ã—ÂªÃ—Â•Ã—Â›Ã—Â Ã—Â™Ã—Â•Ã—Âª Ã—Â©Ã—ÂžÃ—Â©Ã—Â•Ã—Â“Ã—Â¨Ã—Â•Ã—Âª Ã—Â¢Ã—Â›Ã—Â©Ã—Â™Ã—Â•")
        main_layout.addWidget(now_only_checkbox)

        # === Ã—ÂÃ—Â–Ã—Â•Ã—Â¨ Ã—Â’Ã—ÂœÃ—Â™Ã—ÂœÃ—Â” ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        # === Ã—Â¤Ã—Â•Ã—Â Ã—Â§Ã—Â¦Ã—Â™Ã—Â™Ã—Âª Ã—Â¨Ã—Â¢Ã—Â Ã—Â•Ã—ÂŸ (Ã—Â¤Ã—Â Ã—Â™Ã—ÂžÃ—Â™Ã—Âª) ===
        def refresh_epg_view():
            # Ã—Â Ã—Â™Ã—Â§Ã—Â•Ã—Â™ Ã—ÂªÃ—Â¦Ã—Â•Ã—Â’Ã—Â” Ã—Â§Ã—Â•Ã—Â“Ã—ÂžÃ—Âª
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

                # Ã—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ Ã—ÂœÃ—Â¤Ã—Â™ Ã—Â—Ã—Â™Ã—Â¤Ã—Â•Ã—Â©
                if keyword and keyword not in title.lower() and keyword not in desc.lower():
                    continue

                # Ã—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ Ã—ÂœÃ—Â¤Ã—Â™ Ã—Â–Ã—ÂžÃ—ÂŸ Ã—Â Ã—Â•Ã—Â›Ã—Â—Ã—Â™
                try:
                    start_dt = datetime.strptime(start[:12], '%Y%m%d%H%M')
                    stop_dt = datetime.strptime(stop[:12], '%Y%m%d%H%M')
                    if show_now_only and not (start_dt <= now <= stop_dt):
                        continue
                except:
                    pass  # Ã—ÂžÃ—Â§Ã—Â¨Ã—Â” Ã—Â©Ã—Âœ Ã—Â¤Ã—Â•Ã—Â¨Ã—ÂžÃ—Â˜ Ã—ÂªÃ—ÂÃ—Â¨Ã—Â™Ã—Âš Ã—Â©Ã—Â’Ã—Â•Ã—Â™

                # Ã—ÂªÃ—Â¨Ã—Â’Ã—Â•Ã—Â Ã—ÂªÃ—ÂÃ—Â¨Ã—Â™Ã—Â›Ã—Â™Ã—Â
                def format_time(ts):
                    try:
                        return datetime.strptime(ts[:12], '%Y%m%d%H%M').strftime('%d/%m/%Y %H:%M')
                    except:
                        return ts

                # Ã—ÂªÃ—Â¦Ã—Â•Ã—Â’Ã—Âª Ã—ÂªÃ—Â•Ã—Â›Ã—Â Ã—Â™Ã—Âª
                label = QLabel(f"""
                    <b style="font-size:14px;">{title}</b><br>
                    <span style="color:gray;">{desc}</span><br>
                    <span style="color:blue;">{format_time(start)} Ã¢Â†Â’ {format_time(stop)}</span>
                """)
                label.setWordWrap(True)

                program_box = QVBoxLayout()
                program_box.addWidget(label)

                if play_url:
                    play_button = QPushButton("Ã¢Â–Â¶ Ã—Â”Ã—Â¤Ã—Â¢Ã—Âœ")
                    play_button.setStyleSheet("background-color: green; color: white; font-weight: bold;")
                    play_button.clicked.connect(lambda _, url=play_url: self.playCatchupStream(url))
                    program_box.addWidget(play_button)

                # Ã—Â¢Ã—Â˜Ã—Â™Ã—Â¤Ã—Â” Ã—Â‘Ã–Â¾QWidget
                program_widget = QWidget()
                program_widget.setLayout(program_box)
                scroll_layout.addWidget(program_widget)

            if scroll_layout.count() == 0:
                scroll_layout.addWidget(QLabel("Ã¢ÂÂŒ Ã—ÂœÃ—Â Ã—Â Ã—ÂžÃ—Â¦Ã—ÂÃ—Â• Ã—ÂªÃ—Â•Ã—Â›Ã—Â Ã—Â™Ã—Â•Ã—Âª Ã—ÂªÃ—Â•Ã—ÂÃ—ÂžÃ—Â•Ã—Âª."))

        # === Ã—Â”Ã—Â¤Ã—Â¢Ã—ÂœÃ—Âª Ã—Â¨Ã—Â¢Ã—Â Ã—Â•Ã—ÂŸ ===
        search_input.textChanged.connect(refresh_epg_view)
        now_only_checkbox.stateChanged.connect(refresh_epg_view)

        # Ã—Â¨Ã—Â¢Ã—Â Ã—Â•Ã—ÂŸ Ã—Â¨Ã—ÂÃ—Â©Ã—Â•Ã—ÂŸ
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
        Ã—Â›Ã—Â•Ã—ÂªÃ—Â‘Ã—Âª Ã—ÂÃ—Âª Ã—Â”Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—Â”Ã—ÂžÃ—ÂœÃ—Â Ã—Â©Ã—Âœ Ã—Â”-M3U Ã—ÂœÃ—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—Â–Ã—ÂžÃ—Â Ã—Â™ Ã—Â•Ã—Â©Ã—Â•Ã—ÂœÃ—Â—Ã—Âª Ã—ÂœÃ—Â˜Ã—ÂœÃ—Â’Ã—Â¨Ã—Â,
        Ã—Â¢Ã—Â Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—Â©Ã—ÂžÃ—Â•Ã—Âª Ã—Â§Ã—Â‘Ã—Â¦Ã—Â™Ã—Â Ã—ÂÃ—Â•Ã—Â˜Ã—Â•Ã—ÂžÃ—Â˜Ã—Â™Ã—Â™Ã—Â Ã—Â•Ã—Â—Ã—Â›Ã—ÂžÃ—Â™Ã—Â.
        """

        # Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—Â©Ã—Â Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—ÂÃ—Â•Ã—Â˜Ã—Â•Ã—ÂžÃ—Â˜Ã—Â™
        today = datetime.now()
        date_str = today.strftime("%d-%m-%Y")

        # Ã—Â‘Ã—Â“Ã—Â™Ã—Â§Ã—Âª Ã—Â›Ã—ÂžÃ—Â” Ã—Â§Ã—Â‘Ã—Â¦Ã—Â™Ã—Â Ã—Â Ã—Â©Ã—ÂœÃ—Â—Ã—Â• Ã—Â”Ã—Â™Ã—Â•Ã—Â
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

        # Ã—Â¡Ã—Â¤Ã—Â™Ã—Â¨Ã—Âª Ã—Â™Ã—Â™Ã—Â¦Ã—Â•Ã—ÂÃ—Â™Ã—Â Ã—ÂžÃ—Â•Ã—Â¦Ã—ÂœÃ—Â—Ã—Â™Ã—Â Ã—Â”Ã—Â™Ã—Â•Ã—Â
        today_exports = exports_data.get(today_key, [])
        successful_today = [exp for exp in today_exports if exp.get('success', False)]
        count = len(successful_today)

        # Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Âª Ã—Â©Ã—Â Ã—Â”Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥
        if count == 0:
            auto_name = f"EGTV_{date_str}.m3u"
        else:
            auto_name = f"EGTV_{date_str}_({count}).m3u"

        # Ã—Â©Ã—ÂÃ—ÂœÃ—Âª Ã—Â©Ã—Â Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—Â¢Ã—Â Ã—Â”Ã—Â¦Ã—Â¢Ã—Â” Ã—ÂÃ—Â•Ã—Â˜Ã—Â•Ã—ÂžÃ—Â˜Ã—Â™Ã—Âª
        name, ok = QInputDialog.getText(
            self, "Ã—Â™Ã—Â™Ã—Â¦Ã—Â•Ã—Â Ã—ÂœÃ—Â˜Ã—ÂœÃ—Â’Ã—Â¨Ã—Â",
            f"Ã—Â©Ã—Â Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—ÂžÃ—Â•Ã—Â¦Ã—Â¢: {auto_name}\n\nÃ—Â”Ã—Â©Ã—ÂªÃ—ÂžÃ—Â© Ã—Â‘Ã—Â©Ã—Â Ã—Â”Ã—ÂžÃ—Â•Ã—Â¦Ã—Â¢ Ã—ÂÃ—Â• Ã—Â”Ã—Â›Ã—Â Ã—Â¡ Ã—Â©Ã—Â Ã—ÂÃ—Â—Ã—Â¨:",
            text=auto_name
        )

        if not ok or not name.strip():
            return
        if not name.lower().endswith(".m3u"):
            name += ".m3u"

        # Ã—Â›Ã—Â•Ã—ÂªÃ—Â‘ Ã—ÂœÃ—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—Â–Ã—ÂžÃ—Â Ã—Â™ Ã—Â¢Ã—Â tempfile.NamedTemporaryFile
        try:
            with tempfile.NamedTemporaryFile(
                    mode="w", delete=False, suffix=".m3u", encoding="utf-8"
            ) as tmp:
                content = self.textEdit.toPlainText()
                # Ã—Â•Ã—Â™Ã—Â“Ã—Â•Ã—Â Ã—Â©Ã—Â”Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ Ã—ÂžÃ—ÂªÃ—Â—Ã—Â™Ã—Âœ Ã—Â‘-EXTM3U
                if not content.startswith("#EXTM3U"):
                    content = "#EXTM3U\n" + content
                tmp.write(content)
                tmp_path = tmp.name
        except Exception as e:
            QMessageBox.critical(
                self, "Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â” Ã—Â‘Ã—Â›Ã—ÂªÃ—Â™Ã—Â‘Ã—Âª Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥",
                f"Ã—ÂœÃ—Â Ã—Â Ã—Â™Ã—ÂªÃ—ÂŸ Ã—ÂœÃ—Â›Ã—ÂªÃ—Â•Ã—Â‘ Ã—ÂÃ—Âª Ã—Â”Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—Â”Ã—Â–Ã—ÂžÃ—Â Ã—Â™:\n{e}"
            )
            return

        # Ã—Â©Ã—Â•Ã—ÂœÃ—Â— Ã—ÂœÃ—Â˜Ã—ÂœÃ—Â’Ã—Â¨Ã—Â
        try:
            success = send_to_telegram(tmp_path, filename=name)
        except Exception as e:
            # Ã—Â¨Ã—Â™Ã—Â©Ã—Â•Ã—Â Ã—Â›Ã—Â™Ã—Â©Ã—ÂœÃ—Â•Ã—ÂŸ
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
                self, "Ã—Â©Ã—Â’Ã—Â™Ã—ÂÃ—Â” Ã—Â‘-Telegram",
                f"Ã—Â§Ã—Â¨Ã—Â™Ã—Â¡Ã—Â” Ã—Â‘Ã—Â¢Ã—Âª Ã—Â©Ã—ÂœÃ—Â™Ã—Â—Ã—Â” Ã—ÂœÃ—Â˜Ã—ÂœÃ—Â’Ã—Â¨Ã—Â:\n{e}"
            )
            return

        # Ã—Â¨Ã—Â™Ã—Â©Ã—Â•Ã—Â Ã—Â”Ã—ÂªÃ—Â•Ã—Â¦Ã—ÂÃ—Â”
        try:
            if today_key not in exports_data:
                exports_data[today_key] = []
            exports_data[today_key].append({
                "filename": name,
                "timestamp": datetime.now().isoformat(),
                "success": success
            })

            # Ã—Â Ã—Â™Ã—Â§Ã—Â•Ã—Â™ Ã—Â Ã—ÂªÃ—Â•Ã—Â Ã—Â™Ã—Â Ã—Â™Ã—Â©Ã—Â Ã—Â™Ã—Â (Ã—Â©Ã—ÂžÃ—Â™Ã—Â¨Ã—Â” Ã—Â©Ã—Âœ 7 Ã—Â™Ã—ÂžÃ—Â™Ã—Â)
            cutoff_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            exports_data = {k: v for k, v in exports_data.items() if k >= cutoff_date}

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(exports_data, f, ensure_ascii=False, indent=2)
        except:
            pass  # Ã—ÂœÃ—Â Ã—Â§Ã—Â¨Ã—Â™Ã—Â˜Ã—Â™ Ã—ÂÃ—Â Ã—Â”Ã—Â¨Ã—Â™Ã—Â©Ã—Â•Ã—Â Ã—Â Ã—Â›Ã—Â©Ã—Âœ

        # Ã—ÂžÃ—Â¦Ã—Â™Ã—Â’ Ã—ÂªÃ—Â•Ã—Â¦Ã—ÂÃ—Â” Ã—ÂœÃ—ÂžÃ—Â©Ã—ÂªÃ—ÂžÃ—Â©
        if success:
            # Ã—Â—Ã—Â™Ã—Â©Ã—Â•Ã—Â‘ Ã—Â¡Ã—Â˜Ã—Â˜Ã—Â™Ã—Â¡Ã—Â˜Ã—Â™Ã—Â§Ã—Â•Ã—Âª Ã—Â¤Ã—Â©Ã—Â•Ã—Â˜Ã—Â•Ã—Âª
            total_today = len(exports_data.get(today_key, []))
            successful_today_updated = len(
                [exp for exp in exports_data.get(today_key, []) if exp.get('success', False)])

            QMessageBox.information(
                self, "Telegram",
                f"Ã—Â”Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ '{name}' Ã—Â Ã—Â©Ã—ÂœÃ—Â— Ã—Â‘Ã—Â”Ã—Â¦Ã—ÂœÃ—Â—Ã—Â”!\n\nÃ—Â¡Ã—Â˜Ã—Â˜Ã—Â™Ã—Â¡Ã—Â˜Ã—Â™Ã—Â§Ã—Â•Ã—Âª Ã—Â”Ã—Â™Ã—Â•Ã—Â:\nÃ—Â™Ã—Â™Ã—Â¦Ã—Â•Ã—ÂÃ—Â™Ã—Â Ã—ÂžÃ—Â•Ã—Â¦Ã—ÂœÃ—Â—Ã—Â™Ã—Â: {successful_today_updated}\nÃ—Â¡Ã—Â”\"Ã—Â› Ã—Â Ã—Â™Ã—Â¡Ã—Â™Ã—Â•Ã—Â Ã—Â•Ã—Âª: {total_today}"
            )
        else:
            QMessageBox.warning(
                self, "Telegram", f"Ã—Â©Ã—ÂœÃ—Â™Ã—Â—Ã—Â” Ã—Â©Ã—Âœ '{name}' Ã—Â Ã—Â›Ã—Â©Ã—ÂœÃ—Â”."
            )

        # (Ã—ÂÃ—Â•Ã—Â¤Ã—Â¦Ã—Â™Ã—Â•Ã—Â Ã—ÂœÃ—Â™) Ã—ÂžÃ—Â—Ã—Â™Ã—Â§Ã—Âª Ã—Â”Ã—Â§Ã—Â•Ã—Â‘Ã—Â¥ Ã—Â”Ã—Â–Ã—ÂžÃ—Â Ã—Â™
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
        Ã—ÂœÃ—Â Ã—Â¡Ã—Â•Ã—Â¨Ã—Â§ Ã—ÂœÃ—Â•Ã—Â’Ã—Â•Ã—ÂÃ—Â™Ã—Â Ã¢Â€Â“ Ã—Â¨Ã—Â§ Ã—Â‘Ã—Â•Ã—Â Ã—Â” Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—Â•Ã—ÂªÃ—Â•Ã—Â›Ã—ÂŸ.
        """
        self.categories.clear()
        self.extinf_lookup = {}  # Ã¢Â†Â Ã¢Â†Â Ã¢Â†Â Ã¢ÂœÂ… Ã—ÂžÃ—Â•Ã—Â¡Ã—Â™Ã—Â¤Ã—Â™Ã—Â Ã—Â™Ã—Â¦Ã—Â™Ã—Â¨Ã—Â” Ã—Â©Ã—Âœ Ã—Â”Ã—ÂžÃ—Â™Ã—ÂœÃ—Â•Ã—ÂŸ Ã—Â”Ã—Â–Ã—Â”
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

        # Ã—Â¤Ã—Â¨Ã—Â¡ Ã—Â§Ã—Â˜Ã—Â’Ã—Â•Ã—Â¨Ã—Â™Ã—Â•Ã—Âª Ã—Â•Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â
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
        dialog.setWindowTitle("Ã—Â‘Ã—Â—Ã—Â¨ Ã—Â©Ã—Â¤Ã—Â” Ã—ÂœÃ—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â")
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

        label = QLabel("Ã—Â‘Ã—Â—Ã—Â¨ Ã—Â©Ã—Â¤Ã—Â” Ã—ÂœÃ—Â¡Ã—Â™Ã—Â Ã—Â•Ã—ÂŸ Ã—Â¢Ã—Â¨Ã—Â•Ã—Â¦Ã—Â™Ã—Â:")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        hebrew_btn = QPushButton("Ã°ÂŸÂ‡Â®Ã°ÂŸÂ‡Â± Ã—Â¢Ã—Â‘Ã—Â¨Ã—Â™Ã—Âª")
        hebrew_btn.setStyleSheet("background-color: black; color: white;")
        english_btn = QPushButton("English Ã°ÂŸÂ‡Â¬Ã°ÂŸÂ‡Â§")
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
        if 'Ã—Â—Ã—Â“Ã—Â©Ã—Â•Ã—Âª' in channel or 'News' in channel:
            return 'News'
        elif 'Ã—Â¡Ã—Â¨Ã—Â˜Ã—Â™Ã—Â' in channel or 'Movies' in channel:
            return 'Movies'
        elif 'kids' in channel or 'Kids' in channel:
            return 'Kids'
        elif 'Ã—Â¡Ã—Â¤Ã—Â•Ã—Â¨Ã—Â˜' in channel or 'Sports' in channel:
            return 'Sports'
        elif 'Ã—ÂªÃ—Â™Ã—Â¢Ã—Â•Ã—Â“' in channel or 'Documentaries' in channel:
            return 'Documentaries'
        elif 'Yes' in channel or 'Yes' in channel:
            return 'Yes'
        elif 'Hot' in channel or 'hot' in channel:
            return 'Hot'
        elif 'Ã—ÂžÃ—Â•Ã—Â–Ã—Â™Ã—Â§Ã—Â”' in channel or 'Music' in channel:
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



# ============================================================================
# MAIN APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply the modern stylesheet globally
    app.setStyleSheet(get_modern_stylesheet())

    # Set application properties
    app.setApplicationName("M3U Editor V3 - Modern Edition")
    app.setApplicationVersion("3.0")
    app.setOrganizationName("Modern UI Studios")

    # Create and show the main window
    editor = M3UEditor()
    editor.show()

    # Start the application
    sys.exit(app.exec_())