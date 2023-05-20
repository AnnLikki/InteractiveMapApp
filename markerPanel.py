import os
from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QGridLayout, QCheckBox, QPushButton, QTextEdit, \
    QComboBox, QScrollArea

from markers import MarkerItem


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
        label_marker_image = QLabel("Marker Icon")

        type_chooser = QComboBox()
        type_chooser.addItems(MarkerItem.getTypes())

        self.folder_path = MarkerItem.getPaths()[MarkerItem.getTypes().index(type_chooser.currentText())]

        marker_image_scroll = QScrollArea()
        marker_image_widget = QWidget()
        marker_image_grid = QGridLayout()
        marker_image_widget.setLayout(marker_image_grid)
        marker_image_scroll.setWidgetResizable(True)
        marker_image_scroll.setWidget(marker_image_widget)
        marker_image_widget.setFixedWidth(160)
        marker_image_grid.setContentsMargins(0, 0, 0, 0)
        marker_image_grid.setSpacing(2)
        marker_image_grid.setAlignment(Qt.AlignTop)

        def update_type():

            while marker_image_grid.count():
                widget = marker_image_grid.takeAt(0).widget()
                if widget is not None:
                    widget.deleteLater()

            self.folder_path = MarkerItem.getPaths()[MarkerItem.getTypes().index(type_chooser.currentText())]

            # Get a list of image files in the folder
            image_files = [file for file in os.listdir(self.folder_path) if file.endswith(".png")]
            # Create QPixmap objects for each image file
            marker_images = []
            for file in image_files:
                image_path = os.path.join(self.folder_path, file)
                pixmap = QPixmap(image_path)
                marker_images.append(pixmap)

            # Function of changing marker's pixmap
            def handleMarkerImageSelection(type_string, ind):
                self.marker.setImageByType(type_string, ind)  # Set the pixmap on the marker

            for index, pixmap in enumerate(marker_images):
                image_button = QPushButton()
                image_button.setCheckable(True)
                image_button.setIcon(QIcon(pixmap))
                image_button.clicked.connect(partial(handleMarkerImageSelection, type_chooser.currentText(), index))
                image_button.setAutoExclusive(True)  # Set button as exclusively check-able
                image_button.adjustSize()
                image_button.setFixedHeight(image_button.width())
                marker_image_grid.addWidget(image_button, index // 5, index % 5)

        update_type()

        type_chooser.currentTextChanged.connect(update_type)

        marker_options_layout.addWidget(label_marker_image, 0, 0)
        marker_options_layout.addWidget(type_chooser, 1, 0)
        marker_options_layout.addWidget(marker_image_scroll, 2, 0)

        # Show marker name checkbox
        show_name_checkbox = QCheckBox("Show marker name")
        show_name_checkbox.setChecked(self.marker.showing)
        marker_options_layout.addWidget(show_name_checkbox, 3, 0)

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
