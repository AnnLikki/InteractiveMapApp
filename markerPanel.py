import os
from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QGridLayout, QCheckBox, QPushButton, QTextEdit, \
    QComboBox, QScrollArea

from markers import MarkerItem


class MarkerPanel(QWidget):

    def __init__(self, marker, scene):
        super().__init__()

        self.marker = marker
        self.scene = scene

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        # Add UI elements to the marker panel
        label_top = QLabel("Place a new marker or label")
        layout.addWidget(label_top, 0, 0, 1, 2)

        # Name field
        label_name = QLabel("Name")
        name_field = QLineEdit(self.marker.name)

        def handleTextChanged():
            self.marker.setName(name_field.text())

        name_field.textChanged.connect(handleTextChanged)
        layout.addWidget(label_name, 1, 0, 1, 2)
        layout.addWidget(name_field, 2, 0, 1, 2)

        # Description field
        description_label = QLabel("Description")
        layout.addWidget(description_label, 3, 0, 1, 1)
        description_field = QTextEdit(self.marker.desc)
        description_field.setMaximumHeight(25)
        layout.addWidget(description_field, 4, 0, 1, 2)

        hide_desc_button = QPushButton()

        def toggle_desc():
            if description_field.maximumHeight() != 25:
                hide_desc_button.setIcon(QIcon("ui/expand.png"))
                description_field.setMaximumHeight(25)
            else:
                hide_desc_button.setIcon(QIcon("ui/collapse.png"))
                description_field.setMaximumHeight(1000)

        hide_desc_button.clicked.connect(toggle_desc)
        hide_desc_button.setMaximumWidth(25)
        layout.addWidget(hide_desc_button, 3, 1, 1, 1)

        toggle_desc()

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
        marker_image_grid.setContentsMargins(0, 0, 0, 0)  # necessary
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

            for i, pixmap in enumerate(marker_images):
                image_button = QPushButton()
                image_button.setCheckable(True)
                image_button.setIcon(QIcon(pixmap))
                image_button.clicked.connect(partial(handleMarkerImageSelection, type_chooser.currentText(), i))
                image_button.setAutoExclusive(True)  # Set button as exclusively check-able
                image_button.adjustSize()
                image_button.setFixedHeight(image_button.width())
                marker_image_grid.addWidget(image_button, i // 5, i % 5)

        update_type()

        type_chooser.currentTextChanged.connect(update_type)

        layout.addWidget(label_marker_image, 5, 0, 1, 2)
        layout.addWidget(type_chooser, 6, 0, 1, 2)
        layout.addWidget(marker_image_scroll, 7, 0, 1, 2)

        # Show marker name checkbox
        show_name_checkbox = QCheckBox("Show marker name")
        show_name_checkbox.setChecked(self.marker.showing)
        layout.addWidget(show_name_checkbox, 8, 0, 1, 2)

        def handleShowNameState(state):
            if state:
                self.marker.showName()
            else:
                self.marker.hideName()

        show_name_checkbox.stateChanged.connect(handleShowNameState)

        label_label_text = QLabel("Text Color")
        layout.addWidget(label_label_text, 9, 0, 1, 2)

        color_panel = QWidget()
        colors_layout = QGridLayout()
        self.color_buttons = []

        self.selected_color = QColor("black")

        colors = [QColor("black"), QColor("red"), QColor("blue"), QColor("green"), QColor("yellow"),
                  QColor("white"), QColor("orange"), QColor("pink"), QColor("purple"), QColor("lightGreen")]

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
            colors_layout.addWidget(button, index // 5, index % 5)
            self.color_buttons.append(button)

        color_panel.setLayout(colors_layout)
        layout.addWidget(color_panel, 10, 0, 1, 2)

        # Move button
        move_button = QPushButton("Move")
        move_button.setCheckable(True)
        move_button.setIcon(QIcon("ui/move.png"))

        def handleMoveButton(checked):
            self.marker.setMovable(checked)

        move_button.toggled.connect(handleMoveButton)
        layout.addWidget(move_button, 11, 0, 1, 2)

        # Save button
        save_button = QPushButton("Save")
        save_button.setIcon(QIcon("ui/save.png"))

        def handleSaveButton():
            self.marker.desc = description_field.toPlainText()
            self.marker.pos = self.marker.scenePos()
            self.scene.clearSelection()
            self.deleteLater()

        save_button.clicked.connect(handleSaveButton)
        layout.addWidget(save_button, 12, 0, 1, 2)

        # Delete button
        delete_button = QPushButton("Delete")
        delete_button.setIcon(QIcon("ui/delete.png"))

        def handleDeleteButton():
            self.scene.removeItem(self.marker)
            self.marker = None
            self.deleteLater()

        delete_button.clicked.connect(handleDeleteButton)
        layout.addWidget(delete_button, 13, 0, 1, 2)
