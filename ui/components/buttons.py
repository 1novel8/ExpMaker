from PyQt5.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, QEvent
from ui.styles import primary_button


class PrimaryButton(QPushButton):
    def __init__(self, parent=None, title="...", on_click=lambda x: x, hidden=False):
        QPushButton.__init__(self, parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(primary_button)
        self.setText(title)
        self.setHidden(hidden)
        self.clicked.connect(on_click)
        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QEvent.HoverEnter:
            effect = QGraphicsDropShadowEffect(self)
            effect.setOffset(0, 0)
            effect.setBlurRadius(20)
            self.setGraphicsEffect(effect)
            return True
        if event.type() == QEvent.HoverLeave:
            effect = QGraphicsDropShadowEffect(self)
            effect.setOffset(0, 0)
            self.setGraphicsEffect(effect)
        return False
