
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTextEdit, QInputDialog, QListWidget, QListWidgetItem, QComboBox,
    QHBoxLayout, QLabel, QMessageBox, QDialog, QLineEdit, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont  # Add this line
import sys
import os
import re
import traceback

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


    def getSelectedCategory(self):
        return self.newCategoryInput.text() if self.newCategoryInput.text() else self.categoryCombo.currentText()

    def getSelectedCategory(self):
        return self.newCategoryInput.text() if self.newCategoryInput.text() else self.categoryCombo.currentText()

class ExportGroupsDialog(QDialog):
    def __init__(self, categories, parent=None):
        super(ExportGroupsDialog, self).__init__(parent)
        self.categories = categories  # Make sure categories are stored in the instance
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout(self)
        self.setWindowTitle("Export Groups")

        # Option to export selected groups
        self.exportSelectedButton = QPushButton("Export Selected Groups", self)
        self.exportSelectedButton.clicked.connect(self.exportSelected)
        layout.addWidget(self.exportSelectedButton)

        # Option to export all groups
        self.exportAllButton = QPushButton("Export All Groups", self)
        self.exportAllButton.clicked.connect(self.exportAll)
        layout.addWidget(self.exportAllButton)

    def exportSelected(self):
        selectedCategory, ok = QInputDialog.getItem(self, "Select Group", "Choose a group to export:",
                                                    list(self.categories.keys()), 0, False)
        if ok and selectedCategory:
            self.exportGroup(selectedCategory)

    def exportAll(self):
        for category in self.categories.keys():
            self.exportGroup(category)

    def exportGroup(self, category):
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Group", f"{category}.m3u",
                                                  "M3U Files (*.m3u);;All Files (*)")
        if fileName:
            with open(fileName, 'w', encoding='utf-8') as file:
                file.write("#EXTM3U\n")
                for channel in self.categories[category]:
                    # Extract full EXTINF line from channel information
                    extinf_line = self.parent().getFullExtInfLine(channel)
                    url = self.parent().getUrl(channel)
                    file.write(f"{extinf_line}\n{url}\n")

    def parseChannelInfo(self, channel):
        # Regex to extract name, url and optional tvg-logo
        match = re.search(r'^(.+) \((http.+)\)$', channel)
        if match:
            name = match.group(1)
            url = match.group(2)
            return name, url
        return "", ""
class M3UEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.categories = {}
        self.initUI()

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

    def initUI(self):
        self.setWindowTitle('M3U Playlist Editor')
        self.setGeometry(100, 100, 800, 600)

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
                logo_pixmap = logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        title.setStyleSheet("font-size: 21px; font-weight: bold; background-color: black; color: white;")
        main_layout.addWidget(title)

        # Search components
        self.search_input = QLineEdit(self)
        self.search_button = QPushButton('Search', self)
        self.search_button.clicked.connect(self.perform_search)


        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        main_layout.addLayout(search_layout)

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

        # Button for filtering Israeli channels
        self.filterIsraelChannelsButton = QPushButton('Filter Israeli Channels', self)
        main_layout.addWidget(self.filterIsraelChannelsButton)
        self.filterIsraelChannelsButton.clicked.connect(self.filterIsraelChannels)

        # Button for adding new filtered categories dynamically
        self.addFilteredCategoryButton = QPushButton('Add Filtered Category', self)
        main_layout.addWidget(self.addFilteredCategoryButton)
        self.addFilteredCategoryButton.clicked.connect(self.addFilteredCategory)
        # Add other sections
        main_layout.addLayout(self.create_category_section())
        main_layout.addLayout(self.create_channel_section())
        main_layout.addLayout(self.create_m3u_content_section())

        # Ensure EXTM3U header
        self.textEdit.textChanged.connect(self.ensure_extm3u_header)
        # Ensure everything is added to main_layout
        self.setLayout(main_layout)
        # Adding Export Groups button at the top left
        self.exportGroupButton = QPushButton('Export Groups', self)
        self.exportGroupButton.clicked.connect(self.openExportDialog)
        top_layout = QHBoxLayout()  # Create a horizontal layout for the top row
        top_layout.addWidget(self.exportGroupButton)
        main_layout.addLayout(top_layout)  # Add this top layout to the main vertical layout
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

    def displayTotalChannels(self):
        total_channels = sum(len(channels) for channels in self.categories.values())
        self.channelCountLabel.setText(f"Total Channels: {total_channels}")

    def create_channel_section(self):
        layout = QVBoxLayout()
        channel_title = QLabel("Channels", self)
        channel_title.setAlignment(Qt.AlignCenter)
        channel_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(channel_title)

        self.sortingComboBox = QComboBox(self)
        self.sortingComboBox.addItems(["Sort by Name A-Z", "Sort by Name Z-A"])
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
        button_layout.addWidget(self.addChannelButton)
        button_layout.addWidget(self.deleteChannelButton)
        button_layout.addWidget(self.moveChannelUpButton)
        button_layout.addWidget(self.moveChannelDownButton)
        button_layout.addWidget(self.selectAllChannelsButton)
        button_layout.addWidget(self.clearChannelsSelectionButton)
        button_layout.addWidget(self.moveSelectedChannelButton)
        button_layout.addWidget(self.editSelectedChannelButton)
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
            self.display_channels(self.categoryList.currentItem())

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
        Deletes the selected channels from the current category and updates the M3U content.
        """
        selected_items = self.channelList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No channels selected for deletion.")
            return

        # Get the current category
        selected_category_item = self.categoryList.currentItem()
        if not selected_category_item:
            QMessageBox.warning(self, "Warning", "No category selected.")
            return

        current_category = selected_category_item.text().split(" (")[0]
        if current_category not in self.categories:
            QMessageBox.warning(self, "Warning", "Category not found.")
            return

        # List of channel names to delete
        channels_to_delete = [item.text() for item in selected_items]

        # Remove channels from the categories dictionary
        self.categories[current_category] = [
            channel for channel in self.categories[current_category]
            if channel.split(" (")[0] not in channels_to_delete
        ]

        # Update the M3U content to remove the deleted channels
        updated_lines = []
        skip_next_line = False
        for line in self.textEdit.toPlainText().splitlines():
            if skip_next_line:
                skip_next_line = False
                continue
            if line.startswith("#EXTINF") and any(chan in line for chan in channels_to_delete):
                skip_next_line = True  # Skip the URL line as well
                continue
            updated_lines.append(line)

        # Update the QTextEdit with the modified content
        self.textEdit.setPlainText("\n".join(updated_lines))

        # Refresh the channel list in the UI
        self.display_channels(selected_category_item)

        QMessageBox.information(self, "Success", "Selected channels have been deleted.")

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

    def getFullExtInfLine(self, channel):
            """
            Extracts or constructs the full EXTINF line from channel information,
            preserving attributes like 'tvg-logo'.
            """
            # This method assumes channel format includes all needed attributes
            # For example: 'Channel Name tvg-logo="logo.png" (http://url.com)'
            name_part = channel.split(' (')[0]  # Gets the part before the URL
            url = channel.split(' (')[1].strip(')')  # Extracts the URL
            return f"#EXTINF:-1 group-title=\"{self.getCategoryName(channel)}\",{name_part}"

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
                        'ONE HD', 'Eurosport 2', 'ONE HD', 'Sport 1 HD', 'EXTREME IL', 'Sport 5+ Live HD IL', 'ONE 2 HD IL', 'Sport 3 HD IL', 'Sport 5 HD IL ', 'SPORT 2 HD IL', 'Sport 1 HD IL', 'Sport 2 HD', 'Sport 3 HD', 'Sport 4 HD',
                        'Sport 5 HD', 'Sport 5 Live HD', 'Eurosport 1 HD', 'ESPN 2 HD USA', 'ESPN USA', 'Eurosport 1 HD', 'Red Bull TV HD',
                        'WWE Russian', 'Red Bull TV', 'MMA-TV.com HD', 'MMA-TV.com', 'MMA-TV.com orig', 'NHL', 'nba', 'NBA', 'wwe', 'WWE Network HD', 'Eurosport 2',
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
                       'MTV Club', 'Clubbing TV HD', 'IL: MTV HD', 'MTV 80s', 'MTV', 'MTV Pulse HD', 'IT: MTV HD', 'MTV Idol HD', 'VH1 Classic', 'Rock Classics', 'Europa Plus TV HD', 'Music Box Gold', 'music 24', 'MTV Hits orig',
                       'Club MTV', 'Bridge Deluxe HD', 'Now 90s HD UK', 'Now 80s HD UK', 'NOW 70s UK', 'Bridge TV', 'Bridge Deluxe HD orig', 'Bridge Hits',
                       'Bridge Rock', 'Europa Plus TV', 'Europa Plus TV orig', 'MTV Live HD', 'MTV Live HD orig',
                       'MTV 90s', 'MUSIC 24', 'Yosso TV Music Hits', 'Fresh Concerts', 'Fresh Dance',
                       'Sky High Concert HD', 'Movistar Musica HD', 'MTV' '1HD Music Television orig','4ever Music HD UA','4ever Music UA','B4U Music IN','BOX Music 4K HDR','Backus TV Music HD','Baraza Music HD','Biz Music HD UZ','CHANNEL 24 MUSIC HD IL','Classic Music','Classic Music HD','Disco Polo Music PL','EU Music HD UA','EU Music UA','FRESH Sad Music HD','HMTV IN','KLI Music HD',"MTV 00's PT",'MTV 00s RO', 'MTV 80s RO','MTV 90s','MTV Aitio HD SE','MTV Base UK','MTV Classic','MTV Classic USA','MTV Club','MTV HD CA','MTV Hits', 'MTV Hits RO','MTV India IN', 'MTV Live HD','MTV Live HD orig','MTV MUSIC IL','MTV Music UK','MTV POLSKA PL','MTV RO','MTV SE','MTV Viihde HD FI','MTV Viihde HD SE','MUSIC 24 IL','Music Box Gold','Music Box Russia','Music Box Russia HD','Music Box Russia orig','Music Channel RO','MusicBox GE','Prokop TV Music','Public Music IN','Retro Music TV HD CZ','SUN Music IN','Sochi Music HD','VB MTV Old Россия HD','VF Music','Vox Music TV PL','Yosso TV Music Hits','Z!Music HD','ТНТ Music','ТНТ Music HD','ТНТ Music orig' ],
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

        # Add "Israel Radio" to categories
        radio_category = " Israel Radio📻"
        if radio_category not in filtered_channels:
            filtered_channels[radio_category] = []

        # Load additional Israeli radio channels
        m3u_file_path = r"C:\Users\Master_PC\Desktop\IPtv_projects\Projects Eldad\M3u_Editor_EldadV1\IsraeliRadios.m3u"
        try:
            with open(m3u_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            current_name = None
            current_logo = None
            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF:"):
                    # Extract tvg-logo if it exists
                    logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                    current_logo = logo_match.group(1) if logo_match else None
                    # Extract channel name
                    current_name = line.split(",")[-1].strip()
                elif line.startswith("http") and current_name:
                    # Add channel to the "Israel Radio" category
                    channel_entry = f"{current_name} ({line})"
                    if current_logo:
                        channel_entry += f' tvg-logo="{current_logo}"'

                    filtered_channels[radio_category].append(channel_entry)
                    current_name = None
                    current_logo = None

        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"The file {m3u_file_path} was not found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while loading the M3U file: {e}")

        # Update categories and regenerate M3U content
        self.categories = filtered_channels
        self.updateCategoryList()  # Ensure category list is updated with counts
        self.updateM3UContent()  # Regenerate M3U content for correct order

        # Ensure categories are refreshed in the UI
        self.categoryList.clear()
        for category, channels in self.categories.items():
            display_text = f"{category} ({len(channels)})"
            self.categoryList.addItem(QListWidgetItem(display_text))

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

    def addFilteredCategory(self):
        category_name, ok = QInputDialog.getText(self, 'Add Filtered Category', 'Enter new filtered category name:')
        if ok and category_name:
            if category_name not in self.categories:
                self.categories[category_name] = []  # Initialize empty channel list for new category
                QMessageBox.information(self, "Category Added", f"Category '{category_name}' has been added.")
                self.updateCategoryList()  # Update the category list in the UI
            else:
                QMessageBox.warning(self, "Category Exists", f"The category '{category_name}' already exists.")


def main():
    app = QApplication(sys.argv)
    editor = M3UEditor()
    editor.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()