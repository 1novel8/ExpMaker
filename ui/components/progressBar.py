from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QProgressBar

from ui.styles import progress_bar


class ProgressBar(QProgressBar):
    def __init__(self, parent=None, hidden=False):
        QProgressBar.__init__(self, parent)
        self.setStyleSheet(progress_bar)
        self.setHidden(hidden)
        self.setMinimumSize(QSize(240, 30))

    def update_value(self, val):
        self.setValue(val * 100)
