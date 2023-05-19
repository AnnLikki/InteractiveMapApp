import os
from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QGridLayout, QCheckBox, QPushButton, QTextEdit


class MarkerPanel(QWidget):

    def __init__(self, marker, scene):
        super().__init__()

        self.marker = marker
        self.scene = scene

        marker_layout = QVBoxLayout()
        marker_layout.setAlignment(Qt.AlignTop)
        self.setLayout(marker_layout)

        self.setFixedWidth(215)

        # Add UI elements to the marker panel
        label_instruction = QLabel("Place a new marker or label")
        marker_layout.addWidget(label_instruction)

        # Name field
        label_name = QLabel("Name")
        name_field = QLineEdit(self.marker.name)

        def handleTextChanged():
            self.marker.setName(name_field.text())

        name_field.textChanged.connect(handleTextChanged)
        marker_layout.addWidget(label_name)
        marker_layout.addWidget(name_field)

        # Description field
        label_description = QLabel("Description")
        description_field = QTextEdit(self.marker.desc)
        marker_layout.addWidget(label_description)
        marker_layout.addWidget(description_field)

        # Marker-specific options
        self.marker_option = QWidget()
        marker_options_layout = QGridLayout()
        marker_options_layout.setAlignment(Qt.AlignTop)

        # Marker image options
        label_marker_image = QLabel("Marker Image")

        # Folder path containing the marker images
        folder_path = "markers"
        # Get a list of image files in the folder
        image_files = [file for file in os.listdir(folder_path) if file.endswith(".png")]
        # Create QPixmap objects for each image file
        marker_images = []
        for file in image_files:
            image_path = os.path.join(folder_path, file)
            pixmap = QPixmap(image_path)
            marker_images.append(pixmap)

        # Function of changing marker's pixmap
        def handleMarkerImageSelection(ind):
            self.marker.setPixmap(ind)  # Set the pixmap on the marker

        marker_image_grid = QGridLayout()
        for index, pixmap in enumerate(marker_images):
            image_button = QPushButton()
            image_button.setCheckable(True)
            image_button.setIcon(QIcon(pixmap))
            image_button.clicked.connect(partial(handleMarkerImageSelection, index))
            image_button.setAutoExclusive(True)  # Set button as exclusively check-able
            marker_image_grid.addWidget(image_button, index // 5, index % 5)
        marker_options_layout.addWidget(label_marker_image, 0, 0)
        marker_options_layout.addLayout(marker_image_grid, 1, 0)

        # Show marker name checkbox
        show_name_checkbox = QCheckBox("Show marker name")
        show_name_checkbox.setChecked(self.marker.showing)
        marker_options_layout.addWidget(show_name_checkbox, 2, 0)

        def handleShowNameState(state):
            if state:
                self.marker.showName()
            else:
                self.marker.hideName()

        show_name_checkbox.stateChanged.connect(handleShowNameState)

        self.marker_option.setLayout(marker_options_layout)
        marker_layout.addWidget(self.marker_option)

        # Label-specific options
        label_option = QWidget()
        label_layout = QVBoxLayout()

        label_label_text = QLabel("Text Color")
        label_layout.addWidget(label_label_text)

        color_panel = QWidget()
        colors_layout = QGridLayout()
        self.color_buttons = []

        self.selected_color = QColor("black")

        colors = [QColor("black"), QColor("red"), QColor("blue"), QColor("green"), QColor("yellow"), QColor("white")]

        def handleColorSelection(ind):
            self.selected_color = self.color_buttons[ind].palette().button().color()
            self.marker.setFormat(self.selected_color)

        for index, color in enumerate(colors):
            button = QPushButton()
            button.setStyleSheet(f"background-color: {color.name()};")
            button.setFixedSize(20, 20)
            button.setCheckable(True)
            button.setAutoExclusive(True)  # Set button as exclusively check-able
            button.clicked.connect(partial(handleColorSelection, index))
            colors_layout.addWidget(button, index // 3, index % 3)
            self.color_buttons.append(button)

        color_panel.setLayout(colors_layout)
        label_layout.addWidget(color_panel)
        label_option.setLayout(label_layout)
        marker_layout.addWidget(label_option)

        # Move button
        move_button = QPushButton("Move")
        move_button.setCheckable(True)
        move_button.setIcon(QIcon("ui/move.png"))

        def handleMoveButton(checked):
            self.marker.setMovable(checked)

        move_button.toggled.connect(handleMoveButton)
        marker_layout.addWidget(move_button)

        # Save button
        save_button = QPushButton("Save")
        save_button.setIcon(QIcon("ui/save.png"))

        def handleSaveButton():
            self.marker.desc = description_field.toPlainText()
            self.scene.clearSelection()
            self.deleteLater()

        save_button.clicked.connect(handleSaveButton)
        marker_layout.addWidget(save_button)

        # Delete button
        delete_button = QPushButton("Delete")
        delete_button.setIcon(QIcon("ui/delete.png"))

        def handleDeleteButton():
            self.scene.removeItem(self.marker)
            self.marker = None
            self.deleteLater()

        delete_button.clicked.connect(handleDeleteButton)
        marker_layout.addWidget(delete_button)
