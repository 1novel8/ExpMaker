from os import getcwd

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel

base_dir = getcwd()


class IconLabel(QLabel):
    def __init__(self, parent=None, img='%s\\Images\\logo.png' % base_dir):
        QLabel.__init__(self, parent)
        self.setGeometry(10, 10, 50, 50)
        self.setPixmap(QPixmap(img))
        self.setMaximumHeight(20)
        self.setMaximumWidth(20)
        self.setScaledContents(True)
