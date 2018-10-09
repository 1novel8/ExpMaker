from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from .styles import primary_button


class PrimaryButton(QPushButton):
    def __init__(self, parent=None, title="...", on_click=lambda x: x, hidden=False):
        QPushButton.__init__(self, parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(primary_button)
        self.setText(title)
        self.setHidden(hidden)
        self.clicked.connect(on_click)

