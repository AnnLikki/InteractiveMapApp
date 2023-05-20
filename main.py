import datetime
import os
import pickle
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap, QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QToolBar, QGraphicsView, QGraphicsScene, QFileDialog, QTextEdit, QGraphicsPixmapItem, QSlider

from markerPanel import MarkerPanel
from markers import MarkerItem


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.picture_item = None
        self.resize(800, 600)

        # Create the main widget
        main_panel = QWidget()
        main_layout = QHBoxLayout()
        main_panel.setLayout(main_layout)

        # Create the left panel widget
        left_panel = QWidget()
        left_panel.setMaximumWidth(220)
        self.left_layout = QVBoxLayout()
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        left_panel.setLayout(self.left_layout)

        # Create the marker panel widget
        marker_panel = QWidget()
        marker_panel.setMaximumWidth(220)
        self.marker_layout = QVBoxLayout()
        marker_panel.setLayout(self.marker_layout)

        # Create the center panel widget
        center_panel = QWidget()
        center_layout = QVBoxLayout()
        center_panel.setLayout(center_layout)

        # Add UI elements to the center panel
        center_layout.addWidget(QLabel("Map View"))

        # Create a QGraphicsView and QGraphicsScene
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_scene.selectionChanged.connect(self.handleMarkerSelectionChanged)
        self.graphics_view.setScene(self.graphics_scene)

        # Drag and zoom of the QGraphicsView
        self.graphics_view = QGraphicsView(self.graphics_scene)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        # TODO Figure out the warning
        # noinspection PyUnresolvedReferences
        self.graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Connect wheel event to the zoom function
        self.graphics_view.wheelEvent = self.zoom_image
        # Connect the slot function to the clicked signal of the graphics view
        self.graphics_view.mouseDoubleClickEvent = self.place_new_marker

        center_layout.addWidget(self.graphics_view)

        # Create a toolbar
        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Create buttons
        button_new = QPushButton("New Map", self)
        button_new.clicked.connect(self.new_map)
        toolbar.addWidget(button_new)

        button_save = QPushButton("Save Map", self)
        button_save.clicked.connect(lambda: self.save_file("scene_data.dat"))
        toolbar.addWidget(button_save)

        button_load = QPushButton("Open Map", self)
        button_load.clicked.connect(self.load_data)
        toolbar.addWidget(button_load)

        button_reset = QPushButton("Reset Map Position", self)
        button_reset.clicked.connect(self.reset_image)
        toolbar.addWidget(button_reset)

        # Create a slider
        slider_label = QLabel("Marker Size")
        slider_label.setContentsMargins(20, 0, 10, 0)
        toolbar.addWidget(slider_label)

        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setMaximumWidth(200)
        self.slider.setMinimum(10)
        self.slider.setMaximum(100)
        self.slider.setValue(25)
        self.slider.valueChanged.connect(self.set_marker_size)
        toolbar.addWidget(self.slider)

        # Fill the main colors_layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(marker_panel)
        main_layout.addWidget(center_panel)

        # Create and set the central widget
        self.setCentralWidget(main_panel)

    def new_map(self, file_path=None):
        if file_path is None or file_path is False:
            # Open a file dialog to select an image file
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg)")

        # Check if a file was selected
        if file_path:
            # Clear the existing scene
            self.graphics_scene.clear()

            # Load the image file as QPixmap
            pixmap = QPixmap(file_path)

            # Create a QGraphicsPixmapItem with the loaded pixmap
            self.picture_item = self.graphics_scene.addPixmap(pixmap)

            # Set the scene rectangle to match the size of the pixmap item
            self.graphics_scene.setSceneRect(self.picture_item.boundingRect())

            self.reset_image()

    def zoom_image(self, event):
        # Get the position of the mouse cursor in scene coordinates
        mouse_pos = self.graphics_view.mapToScene(event.position().toPoint())

        # Adjust zoom level based on the wheel movement
        zoom_factor = 1.1 if event.angleDelta().y() > 0 else 0.9

        # Apply zoom transformation centered around the mouse cursor position
        # TODO Check this thing's relevance
        # self.graphics_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # self.graphics_view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.graphics_view.scale(zoom_factor, zoom_factor)

        # Adjust the view position to keep the mouse cursor in the same scene position after zooming
        new_mouse_pos = self.graphics_view.mapFromScene(mouse_pos)
        delta = new_mouse_pos - event.position().toPoint()
        self.graphics_view.horizontalScrollBar().setValue(self.graphics_view.horizontalScrollBar().value() + delta.x())
        self.graphics_view.verticalScrollBar().setValue(self.graphics_view.verticalScrollBar().value() + delta.y())

    def reset_image(self):
        # Reset the zoom level
        self.graphics_view.resetTransform()

        # Reset the position of the picture to the center of the scene
        self.graphics_view.setSceneRect(self.graphics_scene.itemsBoundingRect())
        self.graphics_view.centerOn(0, 0)

        # Rescale the picture to fit within the view
        scene_rect = self.graphics_scene.itemsBoundingRect()
        if not scene_rect.isNull():
            self.graphics_view.fitInView(scene_rect, Qt.AspectRatioMode.KeepAspectRatio)

    def place_new_marker(self, event):
        # Check if a picture has been loaded
        if self.picture_item is not None and self.marker_layout.isEmpty():

            # Get the cursor position in relation to the graphics view
            cursor_pos = event.position().toPoint()

            # Convert the cursor position to the scene coordinates, accounting for transformations
            scene_pos = self.graphics_view.mapToScene(cursor_pos)

            # Convert the scene coordinates to the coordinates of the picture item
            marker_pos = self.picture_item.mapFromScene(scene_pos)

            # Create the indicator marker using MarkerItem
            new_marker = MarkerItem(marker_pos, MarkerItem.getTypes()[0], 0)
            new_marker.updateSlider(self.slider.value())

            self.graphics_scene.addItem(new_marker)

            self.marker_layout.addWidget(MarkerPanel(new_marker, self.graphics_scene))

            # Hide the left panel
            while self.left_layout.count():
                widget = self.left_layout.takeAt(0).widget()
                if widget is not None:
                    widget.deleteLater()

    def show_existing_marker(self, marker):
        if self.picture_item is not None and self.marker_layout.isEmpty():

            while self.left_layout.count():
                widget = self.left_layout.takeAt(0).widget()
                if widget is not None:
                    widget.deleteLater()

            left_panel = QWidget()
            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignTop)
            left_panel.setMaximumWidth(220)

            # Label for marker name
            name_label = QLabel(marker.name)
            layout.addWidget(name_label)

            # Widget for marker description
            text_edit = QTextEdit(marker.desc)
            text_edit.setReadOnly(True)  # Make the text area read-only
            layout.addWidget(text_edit)

            # Button to edit marker
            edit_button = QPushButton("Edit")

            def handleEditButton():
                self.marker_layout.addWidget(MarkerPanel(marker, self.graphics_scene))
                left_panel.deleteLater()

            edit_button.clicked.connect(handleEditButton)
            layout.addWidget(edit_button)

            # Button to close
            close_button = QPushButton("Close")

            def handleCloseButton():
                left_panel.deleteLater()
                self.graphics_scene.clearSelection()

            close_button.clicked.connect(handleCloseButton)
            layout.addWidget(close_button)

            layout.setContentsMargins(0, 0, 0, 0)
            left_panel.setLayout(layout)

            self.left_layout.addWidget(left_panel)

    def handleMarkerSelectionChanged(self):
        selected_items = self.graphics_scene.selectedItems()
        if len(selected_items) == 1 and isinstance(selected_items[0], MarkerItem):
            marker = selected_items[0]
            self.show_existing_marker(marker)

    def set_marker_size(self):
        if self.picture_item is not None:
            items = self.graphics_scene.items()
            for marker in items:
                if isinstance(marker, MarkerItem):
                    marker.updateSlider(self.slider.value())

    # Save data to a file
    def save_file(self, filename):
        now = datetime.datetime.now()
        filename = "data/" + now.strftime("%Y-%m-%d-%H-%M") + filename

        # checking if the directory exist
        if not os.path.exists("data/"):
            os.makedirs("data/")

        items = self.graphics_scene.items()
        data = []
        for item in items:
            if isinstance(item, MarkerItem):
                item_dict = {
                    'type': 'Marker',
                    'pos': item.pos,
                    'typeInd': item.type_index,
                    'imgInd': item.img_index,
                    'name': item.name,
                    'desc': item.desc,
                    'showing': item.showing,
                    'color': item.getColor()
                }
                # print(item_dict)
                data.append(item_dict)
            elif isinstance(item, QGraphicsPixmapItem):
                item_dict = {
                    'type': 'Image',
                    'imgPath': "data/" + now.strftime("%Y-%m-%d-%H-%M") + '.png'
                }
                item.pixmap().save("data/" + now.strftime("%Y-%m-%d-%H-%M") + ".png")
                # print(item_dict)
                data.append(item_dict)

        # Save the item data to a file
        with open(filename, 'wb') as file:
            pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
            print("Data saved successfully.")

    # Load data from a file
    def load_data(self):

        # Open a file dialog to select the data file
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Data File", "", "Data Files (*.dat *.pickle)")

        # Check if a file was selected
        if file_path:
            # Clear the existing scene
            self.graphics_scene.clear()

            # Read the item data from the text file
            with open(file_path, 'rb') as file:
                data = pickle.load(file)

            # Create and add the items to the graphics scene
            for item_dict in reversed(data):
                if item_dict['type'] == 'Marker':
                    # Create the MarkerItem with the saved data
                    marker = MarkerItem(item_dict['pos'], item_dict['typeInd'], item_dict['imgInd'], item_dict['name'],
                                        item_dict['showing'], item_dict['desc'], QColor(item_dict['color']))
                    # print(marker)
                    marker.updateSlider(self.slider.value())
                    self.graphics_scene.addItem(marker)
                elif item_dict['type'] == 'Image':
                    # print("img")
                    self.new_map(item_dict['imgPath'])

            print("Data loaded successfully.")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
