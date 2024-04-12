from os import getcwd

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel

base_dir = getcwd()


class LogoFrame(QFrame):
    def __init__(self, parent=None, title=""):
        QFrame.__init__(self, parent)
        self.logo_box = QGridLayout(self)
        self.logo_img = QLabel(self)
        self.logo_img.setGeometry(10, 10, 100, 100)
        self.logo_img.setPixmap(QPixmap('%s\\Images\\logo.png' % base_dir))
        self.logo_img.setMaximumHeight(40)
        self.logo_img.setMaximumWidth(40)
        self.logo_img.setScaledContents(True)
        self.logo_title_lbl = QLabel(title, self)
        self.logo_title_lbl.setStyleSheet("font-size: 24px;")
        self.logo_box.addWidget(self.logo_img, 0, 0, 2, 2)
        self.logo_box.addWidget(self.logo_title_lbl, 0, 3, 2, 100)
        self.logo_box.addWidget(QLabel(''), 1, 2, 1, 100)
