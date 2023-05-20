import os

from PySide6.QtCore import QRectF
from PySide6.QtGui import QFont, QPixmap, QColor
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsTextItem


class MarkerItem(QGraphicsPixmapItem):

    def __init__(self, pos, type_index, img_index, name="", showing=False, desc="", color=QColor("black")):
        self.width = 32
        self.height = 32
        self.name = name
        self.desc = desc
        self.showing = showing
        self.type_index = type_index
        self.img_index = img_index

        super().__init__()

        self.setImageByType(self.type_index, self.img_index)
        self.pos = pos
        self.setPos(self.pos)

        # Adjust the position to render the center of the image as (x, y)
        offset_x = -self.width / 2
        offset_y = -self.height / 2
        self.setOffset(offset_x, offset_y)

        self.setFlag(QGraphicsPixmapItem.ItemIgnoresTransformations)
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable)

        self.name_item = QGraphicsTextItem(self)
        self.name_item.setPlainText(self.name)
        self.setFormat(color)
        self.updateNamePosition()
        self.updateShowing()

    def boundingRect(self):
        return QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

    @staticmethod
    def getTypes():
        return ["Basic", "Adventure", "Creatures and plants", "Landmarks", "People", "Town", "Village", "World map"]

    @staticmethod
    def getPaths():
        return ["markers/basic", "markers/adventure", "markers/creatures&plants", "markers/landmarks", "markers/people",
                "markers/town", "markers/village", "markers/worldmap"]

    def setImageByType(self, type_string, index):
        # Folder path containing the marker images
        folder_path = MarkerItem.getPaths()[0]
        if type_string in MarkerItem.getTypes():
            folder_path = MarkerItem.getPaths()[MarkerItem.getTypes().index(type_string)]

        # Get a list of image files in the folder
        image_files = [file for file in os.listdir(folder_path) if file.endswith(".png")]
        image_path = os.path.join(folder_path, image_files[index])
        pixmap = QPixmap(image_path)
        super().setPixmap(pixmap.scaled(self.width, self.height))
        self.img_index = index

    def setName(self, text):
        self.name = text
        self.name_item.setPlainText(self.name)
        self.updateNamePosition()

    def setDesc(self, text):
        self.desc = text

    def updateNamePosition(self):
        # Position the name item underneath the marker item
        name_x = -self.name_item.boundingRect().width() / 2
        name_y = self.height / 2 + 2  # Adjust the vertical position as desired
        self.name_item.setPos(name_x, name_y)

    def showName(self):
        self.showing = True
        self.name_item.setVisible(True)

    def hideName(self):
        self.showing = False
        self.name_item.setVisible(False)

    def updateShowing(self):
        if self.showing:
            self.showName()
        else:
            self.hideName()

    def isNameHidden(self):
        return self.name_item.isVisible()

    def setFormat(self, color=QColor("black")):
        self.name_item.setFont(QFont("Arial", 10))
        self.name_item.setDefaultTextColor(color)

    def getColor(self):
        return self.name_item.defaultTextColor()

    def setMovable(self, movable):
        if movable:
            self.setFlags(self.flags() | QGraphicsPixmapItem.ItemIsMovable)
        else:
            self.setFlags(self.flags() & ~QGraphicsPixmapItem.ItemIsMovable)

    # TODO size change method
