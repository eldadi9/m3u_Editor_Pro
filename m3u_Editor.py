from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTextEdit, QInputDialog, QListWidget, QListWidgetItem, QComboBox,
    QHBoxLayout, QLabel, QMessageBox, QDialog, QLineEdit, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap  # Add this line
import sys
import os
import re


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

    def getSelectedCategory(self):
        return self.newCategoryInput.text() if self.newCategoryInput.text() else self.categoryCombo.currentText()

    def getSelectedCategory(self):
        return self.newCategoryInput.text() if self.newCategoryInput.text() else self.categoryCombo.currentText()


class M3UEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.categories = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle('M3U Playlist Editor')
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Add image at the top
        logo_label = QLabel(self)
        image_path = r'C:\Users\Master_PC\Desktop\IPtv_projects\Projects Eldad\M3u_Editor_EldadV1\Main Logo.jpg'

        # Check if the image exists and load it
        if os.path.exists(image_path):
            logo_pixmap = QPixmap(image_path)
            if not logo_pixmap.isNull():  # Check if the pixmap was loaded successfully
                logo_pixmap = logo_pixmap.scaled(150, 200,Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(logo_pixmap)
            else:
                logo_label.setText("Failed to load image.")  # Fallback text
                logo_label.setAlignment(Qt.AlignCenter)
        else:
            logo_label.setText("Image not found.")
            logo_label.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(logo_label)

        # Title
        title = QLabel("M3U Playlist Editor", self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)

        # File info layout
        file_info_layout = QHBoxLayout()
        self.fileNameLabel = QLabel("No file loaded", self)
        self.fileNameLabel.setAlignment(Qt.AlignRight)
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
                    self.parseM3UContent(self.textEdit.toPlainText())

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
        self.updateCategoryButton = QPushButton('Update Category Name')
        self.deleteCategoryButton = QPushButton('Delete Selected')
        self.moveCategoryUpButton = QPushButton('Move Category Up')
        self.moveCategoryDownButton = QPushButton('Move Category Down')
        self.selectAllButton = QPushButton('Select All')
        self.deselectAllButton = QPushButton('Deselect All')

        # Apply button colors
        self.selectAllButton.setStyleSheet("background-color: blue; color: white;")
        self.deselectAllButton.setStyleSheet("background-color: blue; color: white;")

        self.updateCategoryButton.setStyleSheet("background-color: red; color: white;")
        self.deleteCategoryButton.setStyleSheet("background-color: red; color: white;")

        self.addCategoryButton.setStyleSheet("background-color: green; color: white;")
        self.moveCategoryUpButton.setStyleSheet("background-color: green; color: white;")
        self.moveCategoryDownButton.setStyleSheet("background-color: green; color: white;")

        # Add buttons to layout
        button_layout.addWidget(self.addCategoryButton)
        button_layout.addWidget(self.updateCategoryButton)
        button_layout.addWidget(self.deleteCategoryButton)
        button_layout.addWidget(self.moveCategoryUpButton)
        button_layout.addWidget(self.moveCategoryDownButton)
        button_layout.addWidget(self.selectAllButton)
        button_layout.addWidget(self.deselectAllButton)

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
                try:
                    self.categories[target_category] = []
                    self.updateCategoryList()  # Refresh the UI with the new category
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to create new category: {str(e)}")
                    return

            # Validate the current category
            current_category_item = self.categoryList.currentItem()
            if not current_category_item:
                QMessageBox.warning(self, "Warning", "No category selected.")
                return

            current_category = current_category_item.text().split(" (")[0]
            if current_category not in self.categories:
                QMessageBox.warning(self, "Warning", "The current category does not exist.")
                return

            moved_channels = []

            # Move the selected channels
            try:
                for item in selected_items:
                    if not item:  # Skip if the item is None
                        continue
                    channel_name = item.text()
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

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while moving channels: {str(e)}")

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
        category = item.text().split(" (")[0]  # Extract the category name
        self.channelList.clear()

        # Get channels in the selected category
        channels = self.categories.get(category, [])
        for channel in channels:
            channel_name = channel.split(" (")[0]
            channel_item = QListWidgetItem(channel_name)
            self.channelList.addItem(channel_item)

        # Update the total channel count label
        self.channelCountLabel.setText(f"Total Channels: {len(channels)}")

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
            except UnicodeDecodeError:
                with open(fileName, 'r', encoding='latin-1') as file:
                    content = file.read()
            self.textEdit.setPlainText(content)
            self.parseM3UContent(content)

            # Display the file name in the label
            self.fileNameLabel.setText(f"Loaded File: {fileName.split('/')[-1]}")  # Only show the file name

    def saveM3U(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save M3U File", "", "M3U Files (*.m3u);;All Files (*)",
                                                  options=options)
        if fileName:
            with open(fileName, 'w', encoding='utf-8') as file:
                file.write(self.textEdit.toPlainText())

    def parseM3UContent(self, content):
        """
        Parse M3U content to handle group-title and #EXTGRP.
        - If group-title exists, ignore #EXTGRP.
        - If group-title does not exist, use #EXTGRP and remove it.
        """
        self.categories.clear()
        updated_lines = []
        current_group = None  # To track the group name from #EXTGRP

        lines = content.splitlines()

        for i, line in enumerate(lines):
            if line.startswith("#EXTGRP:"):
                # Extract the group name from the #EXTGRP line
                current_group = line.split(":", 1)[1].strip()
                continue  # Skip the #EXTGRP line itself

            if line.startswith("#EXTINF:"):
                if "group-title=" not in line and current_group:
                    # Add group-title if missing and current_group exists
                    line = re.sub(r'(#EXTINF:[^\n]*?),', f'\\1 group-title="{current_group}",', line)
                current_group = None  # Reset after usage

            updated_lines.append(line)

        # Join updated lines and parse categories
        content = "\n".join(updated_lines)
        category_pattern = re.compile(r'#EXTINF.*group-title="([^"]+)".*,(.*)\n(.*)')
        for match in category_pattern.findall(content):
            group_title, channel_name, channel_url = match
            if group_title not in self.categories:
                self.categories[group_title] = []
            self.categories[group_title].append(f"{channel_name.strip()} ({channel_url.strip()})")

        # Update the QTextEdit and the category list
        self.textEdit.setPlainText(content)
        self.categoryList.clear()
        for category, channels in self.categories.items():
            item = QListWidgetItem(f"{category} ({len(channels)})")  # Add count of channels to the category name
            self.categoryList.addItem(item)

            def parseM3UContentWithGroup(self, content):
                """
                Parse M3U content, dynamically adding group-title if #EXTGRP is present.
                Updates categories and channels without altering the existing parseM3UContent logic.
                """
                # Temporary storage for categories and channels
                updated_categories = {}
                updated_lines = []

                lines = content.splitlines()
                current_group = None  # To track the current group from #EXTGRP

                for line in lines:
                    if line.startswith("#EXTGRP:"):
                        # Extract the group name from the #EXTGRP line
                        current_group = line.split(":", 1)[1].strip()
                    elif line.startswith("#EXTINF:") and "group-title=" not in line:
                        # If group-title is missing, add it using the current_group
                        if current_group:
                            line = re.sub(r'(#EXTINF:[^\n]*?),', f'\\1 group-title="{current_group}",', line)
                    updated_lines.append(line)

                # Combine updated lines into a modified M3U content
                updated_content = "\n".join(updated_lines)

                # Extract categories and channels from the updated content
                category_pattern = re.compile(r'#EXTINF.*group-title="([^"]+)".*,(.*)\n(.*)')
                for match in category_pattern.findall(updated_content):
                    group_title, channel_name, channel_url = match
                    if group_title not in updated_categories:
                        updated_categories[group_title] = []
                    updated_categories[group_title].append(f"{channel_name.strip()} ({channel_url.strip()})")

                # Update the instance's categories and channels
                self.categories = updated_categories

                # Update the QTextEdit and the category list
                self.textEdit.setPlainText(updated_content)
                self.categoryList.clear()
                for category, channels in self.categories.items():
                    item = QListWidgetItem(
                        f"{category} ({len(channels)})")  # Add count of channels to the category name
                    self.categoryList.addItem(item)

    def parseM3UContentWithGroup(self, content):
        """
        Parse M3U content, dynamically adding group-title if #EXTGRP is present.
        Updates categories and channels without altering the existing parseM3UContent logic.
        """
        # Temporary storage for categories and channels
        updated_categories = {}
        updated_lines = []

        lines = content.splitlines()
        current_group = None  # To track the current group from #EXTGRP

        for line in lines:
            if line.startswith("#EXTGRP:"):
                # Extract the group name from the #EXTGRP line
                current_group = line.split(":", 1)[1].strip()
            elif line.startswith("#EXTINF:") and "group-title=" not in line:
                # If group-title is missing, add it using the current_group
                if current_group:
                    line = re.sub(r'(#EXTINF:[^\n]*?),', f'\\1 group-title="{current_group}",', line)
            updated_lines.append(line)

        # Combine updated lines into a modified M3U content
        updated_content = "\n".join(updated_lines)

        # Extract categories and channels from the updated content
        category_pattern = re.compile(r'#EXTINF.*group-title="([^"]+)".*,(.*)\n(.*)')
        for match in category_pattern.findall(updated_content):
            group_title, channel_name, channel_url = match
            if group_title not in updated_categories:
                updated_categories[group_title] = []
            updated_categories[group_title].append(f"{channel_name.strip()} ({channel_url.strip()})")

        # Update the instance's categories and channels
        self.categories = updated_categories

        # Update the QTextEdit and the category list
        self.textEdit.setPlainText(updated_content)
        self.categoryList.clear()
        for category, channels in self.categories.items():
            item = QListWidgetItem(f"{category} ({len(channels)})")  # Add count of channels to the category name
            self.categoryList.addItem(item)

    def filterIsraelChannels(self):
        israel_keywords = ['Israel', 'IL', 'ISRAEL', 'Hebrew', 'hebrew', 'israeli', 'Israeli', 'Il', 'IL HD', 'ישראלי',
                           'Hebrew']
        sport_keywords = ['Sport 1', 'Sport 2', 'Sport 3', 'Sport 4', 'Sport 5', 'Sport-IL', 'Sport_il', 'Sport',
                          'ONE ', 'ONE HD', 'SPORT']
        yes_keywords = ['yes', 'Yes', 'YES', 'Yes_IL', 'YES_IL', 'Sport-IL', 'YES HD IL', 'YES TV', 'yes tv']
        hot_keywords = ['HOT', 'HOT CINEMA', 'Hot HBO', 'HOT cinema 1', 'HOT cinema 2', 'HOT cinema 3', 'HOT8 HD',
                        'HOT COMEDY CENTRAL', 'HOT CINEMA 4', 'HOT CINEMA 3', 'hot-IL', 'HoT']
        kids_keywords = ['Hop!', 'Israelit', 'Baby IL', 'Yaldut IL', 'NICK JR HD IL', 'NICK HD IL', 'JUNIOR IL',
                         'HOP HD IL', 'LULI IL', 'Disney Jr IL', 'TeenNick IL', 'ZOOM IL', 'KIDS HD IL', 'KIDS HD']
        news_keywords = ['Keshet 12 IL', 'Channel 9 HD IL', 'Channel 9 IL', 'Kan 11 IL', 'i24 IL', 'Channel 14',
                         'ערוץ 14', 'ערוץ 24', 'CHANNEL 13 HD']
        entertainment_keywords = ['HOT', 'Hot', 'HOT TV', 'Hot Tv', 'hot-IL', 'HoT']
        music_keywords = ['music', 'MUSIC', 'MTV']

        filtered_channels = {'Movies': [], 'News': [], 'Kids': [], 'Entertainment': [], 'Sports': [], 'Yes': [],
                             'Hot': [], 'Documentaries': [], 'Music': [], 'Other': []}

        for category, channels in self.categories.items():
            for channel in channels:
                # Check if any general Israeli keyword is in channel
                if any(keyword in channel for keyword in israel_keywords):
                    if any(sport_keyword in channel for sport_keyword in sport_keywords):
                        filtered_category = 'Sports'
                    elif any(hot_keyword in channel for hot_keyword in hot_keywords):
                        filtered_category = 'Hot'
                    elif any(yes_keyword in channel for yes_keyword in yes_keywords):
                        filtered_category = 'Yes'
                    elif any(kids_keyword in channel for kids_keyword in kids_keywords):
                        filtered_category = 'Kids'
                    elif any(news_keyword in channel for news_keyword in news_keywords):
                        filtered_category = 'News'
                    elif any(entertainment_keyword in channel for entertainment_keyword in entertainment_keywords):
                        filtered_category = 'Entertainment'
                    elif any(music_keyword in channel for music_keyword in music_keywords):
                        filtered_category = 'Music'
                    else:
                        filtered_category = self.getFilteredCategory(
                            channel)  # Catch-all for any unclassified but relevant channels
                    filtered_channels[filtered_category].append(channel)

        self.categories = filtered_channels
        self.categoryList.clear()
        for category, channels in self.categories.items():
            if channels:  # Only add categories that have channels
                self.categoryList.addItem(QListWidgetItem(category))
        self.updateM3UContent()

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
        else:
            return 'Other'

    def saveFilteredChannels(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Filtered Channels", "",
                                                  "M3U Files (*.m3u);;All Files (*)", options=options)
        if fileName:
            with open(fileName, 'w', encoding='utf-8') as file:
                for category, channels in self.categories.items():
                    for channel in channels:
                        try:
                            name, url = channel.rsplit(" (", 1)
                            file.write(f"#EXTINF:-1 group-title=\"{category}\", {name.strip()}\n{url.strip()[:-1]}\n")
                        except ValueError:
                            continue

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