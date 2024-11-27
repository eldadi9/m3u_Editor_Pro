from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTextEdit, QInputDialog, QListWidget, QListWidgetItem, QComboBox,
    QHBoxLayout, QLabel, QMessageBox, QDialog, QLineEdit, QAbstractItemView  # Add QAbstractItemView
)

from PyQt5.QtCore import Qt
import sys
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


class M3UEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.categories = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle('M3U Playlist Editor')
        self.setGeometry(100, 100, 800, 600)

        # Main Layout
        main_layout = QVBoxLayout(self)

        # Title Label
        title = QLabel("M3U Playlist Editor", self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)

        # File Name Label (Upper right)
        file_info_layout = QHBoxLayout()
        self.fileNameLabel = QLabel("No file loaded", self)
        self.fileNameLabel.setAlignment(Qt.AlignRight)
        file_info_layout.addWidget(self.fileNameLabel)

        # Total Channels Label (Below File Name)
        self.channelCountLabel = QLabel("Total Channels: 0", self)
        self.channelCountLabel.setAlignment(Qt.AlignRight)
        file_info_layout.addWidget(self.channelCountLabel)
        main_layout.addLayout(file_info_layout)

        # Add Sections
        main_layout.addLayout(self.create_category_section())
        main_layout.addLayout(self.create_channel_section())
        main_layout.addLayout(self.create_m3u_content_section())

        # Signal Connection
        self.textEdit.textChanged.connect(self.ensure_extm3u_header)

    # Ensure this method is defined inside the M3UEditor class
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

        self.addCategoryButton = QPushButton('Add Category')
        self.updateCategoryButton = QPushButton('Update Category Name')
        self.deleteCategoryButton = QPushButton('Delete Selected')
        self.moveCategoryUpButton = QPushButton('Move Category Up')
        self.moveCategoryDownButton = QPushButton('Move Category Down')
        self.selectAllButton = QPushButton('Select All')
        self.deselectAllButton = QPushButton('Deselect All')

        button_layout.addWidget(self.addCategoryButton)
        button_layout.addWidget(self.updateCategoryButton)
        button_layout.addWidget(self.deleteCategoryButton)
        button_layout.addWidget(self.moveCategoryUpButton)
        button_layout.addWidget(self.moveCategoryDownButton)
        button_layout.addWidget(self.selectAllButton)
        button_layout.addWidget(self.deselectAllButton)

        layout.addLayout(button_layout)
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

    def updateCategoryName(self):
        """
        Updates the name of a selected category, ensuring all associated channels
        and M3U content are updated correctly.
        """
        selected_item = self.categoryList.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "No category selected for updating.")
            return

        old_category_name = selected_item.text()
        new_category_name, ok = QInputDialog.getText(self, 'Edit Category', 'Enter new category name:',
                                                     text=old_category_name)
        if ok and new_category_name and new_category_name != old_category_name:
            # Update the category in the categories dictionary
            if new_category_name in self.categories:
                QMessageBox.warning(self, "Warning", f"The category '{new_category_name}' already exists.")
                return

            self.categories[new_category_name] = self.categories.pop(old_category_name)
            self.categoryList.currentItem().setText(new_category_name)

            # Update M3U content to reflect the new category name
            m3u_content = self.textEdit.toPlainText()
            updated_lines = []

            for line in m3u_content.splitlines():
                if f'group-title="{old_category_name}"' in line:
                    line = line.replace(f'group-title="{old_category_name}"', f'group-title="{new_category_name}"')
                updated_lines.append(line)

            self.textEdit.setPlainText("\n".join(updated_lines))
            QMessageBox.information(self, "Success",
                                    f"Category '{old_category_name}' has been renamed to '{new_category_name}'.")

            def updateCategoryList(self):
                """Updates the category list with the number of channels in each category."""
                self.categoryList.clear()  # Clear the current list
                for category, channels in self.categories.items():
                    # Display the category name along with the count of channels
                    display_text = f"{category} ({len(channels)})"
                    self.categoryList.addItem(display_text)

    def deleteSelectedCategories(self):
        """
        Deletes the selected categories and removes their channels from M3U content.
        """
        selected_items = self.categoryList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No categories selected for deletion.")
            return

        m3u_content = self.textEdit.toPlainText()
        updated_lines = []
        deleted_categories = []

        # Remove categories from the categories dictionary
        for item in selected_items:
            category_name = item.text()
            if category_name in self.categories:
                del self.categories[category_name]
                deleted_categories.append(category_name)
            self.categoryList.takeItem(self.categoryList.row(item))

        # Remove associated channels from M3U content
        skip_next_line = False
        for line in m3u_content.splitlines():
            if skip_next_line:
                skip_next_line = False
                continue
            if any(f'group-title="{category}"' in line for category in deleted_categories):
                skip_next_line = True  # Skip the URL line
                continue
            updated_lines.append(line)

        self.textEdit.setPlainText("\n".join(updated_lines))
        QMessageBox.information(self, "Success", "Selected categories and their channels have been removed.")

    def removeCategoryFromM3U(self, category_name):
        new_m3u_content = []
        for line in self.textEdit.toPlainText().splitlines():
            if not line.startswith("#EXTINF") or category_name not in line:
                new_m3u_content.append(line)
        self.textEdit.setPlainText("\n".join(new_m3u_content))

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
        selected_items = self.channelList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No channels selected for deletion.")
            return
        current_category = self.categoryList.currentItem().text()
        for item in selected_items:
            channel_info = item.text()
            self.channelList.takeItem(self.channelList.row(item))
            self.categories[current_category] = [
                c for c in self.categories[current_category] if c.split(" (")[0] != channel_info
            ]
        self.updateM3UContent()

    def updateM3UContent(self, old_category_name=None, new_category_name=None):
        m3u_content = ""
        for category, channels in self.categories.items():
            for channel in channels:
                try:
                    name, url = channel.rsplit(" (", 1)
                    m3u_content += f"#EXTINF:-1 group-title=\"{category}\", {name.strip()}\n{url.strip()[:-1]}\n"
                except ValueError:
                    continue
        self.textEdit.setPlainText(m3u_content)
        if old_category_name and new_category_name:
            self.textEdit.setPlainText(self.textEdit.toPlainText().replace(old_category_name, new_category_name))

    def moveChannelUp(self):
        current_row = self.channelList.currentRow()
        if current_row > 0:
            current_item = self.channelList.takeItem(current_row)
            self.channelList.insertItem(current_row - 1, current_item)
            self.channelList.setCurrentRow(current_row - 1)

            # Update the self.categories dictionary
            current_category = self.categoryList.currentItem().text()
            if current_category:
                channels = self.categories[current_category]
                # Swap the current channel with the one above it
                channels[current_row], channels[current_row - 1] = channels[current_row - 1], channels[current_row]
                self.categories[current_category] = channels

            # Regenerate the M3U content
            self.updateM3UContent()

    def moveChannelDown(self):
        current_row = self.channelList.currentRow()
        if current_row < self.channelList.count() - 1:
            current_item = self.channelList.takeItem(current_row)
            self.channelList.insertItem(current_row + 1, current_item)
            self.channelList.setCurrentRow(current_row + 1)

            # Update the self.categories dictionary
            current_category = self.categoryList.currentItem().text()
            if current_category:
                channels = self.categories[current_category]
                # Swap the current channel with the one below it
                channels[current_row], channels[current_row + 1] = channels[current_row + 1], channels[current_row]
                self.categories[current_category] = channels

            # Regenerate the M3U content
            self.updateM3UContent()

    def selectAllChannels(self):
        for i in range(self.channelList.count()):
            self.channelList.item(i).setSelected(True)

    def deselectAllChannels(self):
        for i in range(self.channelList.count()):
            self.channelList.item(i).setSelected(False)

    def moveSelectedChannel(self):
        selected_items = self.channelList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No channels selected for moving.")
            return
        dialog = MoveChannelsDialog(self, list(self.categories.keys()))
        if dialog.exec_():
            target_category = dialog.getSelectedCategory()
            if target_category not in self.categories:
                self.categories[target_category] = []
                self.categoryList.addItem(QListWidgetItem(target_category))
            current_category = self.categoryList.currentItem().text()
            moved_count = 0
            for item in selected_items:
                channel_name = item.text()
                url = self.getUrl(channel_name)
                full_entry = self.findFullM3UEntry(channel_name, current_category)
                if full_entry:
                    self.categories[target_category].append(full_entry)
                    self.categories[current_category] = [
                        c for c in self.categories[current_category] if c.split(" (")[0] != channel_name
                    ]
                    moved_count += 1
            self.display_channels(self.categoryList.currentItem())
            self.updateM3UContent()
            QMessageBox.information(self, "Success", f"Moved {moved_count} channels to {target_category}")

    def editSelectedChannel(self):
        selected_items = self.channelList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No channels selected for editing.")
            return
        for item in selected_items:
            channel_info = item.text()
            new_name, ok = QInputDialog.getText(self, 'Edit Channel', 'Edit channel name:', text=channel_info.strip())
            if ok and new_name:
                url = self.getUrl(channel_info)
                item.setText(new_name.strip())
                current_category = self.categoryList.currentItem().text()
                self.categories[current_category] = [
                    f"{new_name.strip()} ({url})" if c.split(" (")[0] == channel_info else c for c in
                    self.categories[current_category]
                ]
                self.updateM3UContent()

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
        Parse M3U content to populate categories and channels.
        Automatically adds group-title if #EXTGRP is present.
        """
        self.categories.clear()
        updated_lines = []
        lines = content.splitlines()

        current_group = None  # To track the group name from #EXTGRP

        for line in lines:
            if line.startswith("#EXTGRP:"):
                # Extract the group name from the #EXTGRP line
                current_group = line.split(":", 1)[1].strip()
            elif line.startswith("#EXTINF:") and "group-title=" not in line:
                # Add group-title if missing and current_group exists
                if current_group:
                    line = re.sub(r'(#EXTINF:[^\n]*?),', f'\\1 group-title="{current_group}",', line)
            updated_lines.append(line)

        # Update the content with the modified lines
        content = "\n".join(updated_lines)

        # Parse the updated content for categories and channels
        category_pattern = re.compile(r'#EXTINF.*group-title="([^"]+)".*,(.*)\n(.*)')
        for match in category_pattern.findall(content):
            group_title, channel_name, channel_url = match
            if group_title not in self.categories:
                self.categories[group_title] = []
            self.categories[group_title].append(f"{channel_name.strip()} ({channel_url.strip()})")

        # Update the QTextEdit and the category list
        self.textEdit.setPlainText(content)
        self.categoryList.clear()
        for category in self.categories.keys():
            self.categoryList.addItem(QListWidgetItem(category))

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
        israel_keywords = ['ישראל', 'IL', 'ISRAEL', 'עברית', 'hebrew', 'israeli']
        filtered_channels = {'Movies': [], 'News': [], 'Kids': [], 'Entertainment': [], 'Sports': []}
        for category, channels in self.categories.items():
            for channel in channels:
                if any(keyword in channel for keyword in israel_keywords):
                    filtered_category = self.getFilteredCategory(channel)
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
        elif 'ילדים' in channel or 'Kids' in channel:
            return 'Kids'
        elif 'ספורט' in channel or 'Sports' in channel:
            return 'Sports'
        else:
            return 'Entertainment'

    def saveFilteredChannels(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Filtered Channels", "",
                                                  "M3U Files (*.m3u);;All Files (*)", options=options)
        if fileName:
            with open(fileName, 'w', encoding='utf-8') as file:
                for category, channels in our.categories.items():
                    for channel in channels:
                        try:
                            name, url = channel.rsplit(" (", 1)
                            file.write(f"#EXTINF:-1 group-title=\"{category}\", {name.strip()}\n{url.strip()[:-1]}\n")
                        except ValueError:
                            continue


def main():
    app = QApplication(sys.argv)
    editor = M3UEditor()
    editor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()