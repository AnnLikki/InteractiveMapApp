import os

from PySide6.QtCore import QRectF
from PySide6.QtGui import QFont, QPixmap, QColor
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsTextItem


def getImagePathsByCategory(category):  # TODO Test this function with exceptions
    if category in MarkerItem.PathsByCategory.keys():
        folder_path = MarkerItem.PathsByCategory[category]
    else:
        folder_path = list(MarkerItem.PathsByCategory.keys())[0]
        raise ValueError("No such category of markers:", category, "is not in MarkerItem.PathsByCategory:",
                         MarkerItem.PathsByCategory.keys())

    # Get a list of image files in the folder
    return [file for file in os.listdir(folder_path) if file.endswith(".png")]


class MarkerItem(QGraphicsPixmapItem):
    max_size = 128
    PathsByCategory = {"Basic": "markers/basic", "Adventure": "markers/adventure",
                       "Creatures and plants": "markers/creatures&plants", "Landmarks": "markers/landmarks",
                       "People": "markers/people", "Town": "markers/town", "Village": "markers/village",
                       "World map": "markers/worldmap"}

    def __init__(self, pos, category=list(PathsByCategory.keys())[0], image_index=0, name="", showing=False, desc="",
                 color=QColor("black")):
        # Copying data
        self.pos = pos
        self.category = category
        self.image_index = image_index
        self.name = name
        self.showing = showing
        self.desc = desc
        self.color = color

        super().__init__()

        # Additional data
        self.size = 32
        self.slider = 25
        self.pixmap = None

        self.setPos(self.pos)
        self.setImageByType(self.category, self.image_index)

        # Creating a child QGraphicsTextItem as a marker label
        self.name_textItem = QGraphicsTextItem(self)
        self.name_textItem.setPlainText(self.name)
        self.name_textItem.setFont(QFont("Arial", 10))
        self.setTextColor(self.color)

        self.setShowing(self.showing)

        self.setFlag(QGraphicsPixmapItem.ItemIgnoresTransformations)
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable)

    def boundingRect(self):
        return QRectF(-self.size / 2, -self.size / 2, self.size, self.size)

    def setImageByType(self, category, index):
        image_path = os.path.join(MarkerItem.PathsByCategory[category], getImagePathsByCategory(category)[index])
        pixmap = QPixmap(image_path)
        self.category = category
        self.pixmap = pixmap
        self.image_index = index
        self.updatePixmap()

    def setSlider(self, slider):
        self.slider = slider
        self.size = MarkerItem.max_size * self.slider // 100
        self.setOffset(-self.size / 2, -self.size / 2)
        self.updatePixmap()
        self.updateNamePosition()

    def updatePixmap(self):
        super().setPixmap(self.pixmap.scaled(self.size, self.size))

    def setName(self, text):
        self.name = text
        self.name_textItem.setPlainText(self.name)
        self.updateNamePosition()

    def updateNamePosition(self):
        # Position the name item underneath the marker item
        name_x = -self.name_textItem.boundingRect().width() / 2
        name_y = self.size / 2
        self.name_textItem.setPos(name_x, name_y)

    def setShowing(self, showing):
        self.showing = showing
        self.name_textItem.setVisible(showing)

    def setTextColor(self, color):
        self.color = color
        self.name_textItem.setDefaultTextColor(self.color)

    def setMovable(self, movable):
        if movable:
            self.setFlags(self.flags() | QGraphicsPixmapItem.ItemIsMovable)
        else:
            self.setFlags(self.flags() & ~QGraphicsPixmapItem.ItemIsMovable)
