__author__ = 'Alex Konkov'

from PyQt5.QtWidgets import (QMainWindow, QFrame, QGridLayout)


class SettingsWindow(QMainWindow):
    def __init__(self, parent=None, title='', width=710, height=450):
        super(SettingsWindow, self).__init__(parent)
        self.setWindowTitle(title)
        self.resize(width, height)
        self.main_frame = QFrame(self)
        self.grid = QGridLayout(self.main_frame)
        self.main_frame.setFrameShape(QFrame.StyledPanel)
        self.main_frame.setFrameShadow(QFrame.Raised)
        self.setCentralWidget(self.main_frame)
        self.colored_blocks = {}

    def add_widget(self, widget, *args):
        self.grid.addWidget(widget, *args)
