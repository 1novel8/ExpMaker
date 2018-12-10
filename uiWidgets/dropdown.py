from PyQt5.QtWidgets import (QComboBox)


class Dropdown(QComboBox):
    def __init__(self, parent=None, data=(), width=60):
        QComboBox.__init__(self, parent)
        self.data = data
        self.change_data(data)
        # self.setStyleSheet(u'font-size: 12px')
        self.set_min_width(width)
        self.setMaxVisibleItems(30)

    def set_min_width(self, width):
        self.setMinimumWidth(width)

    def change_data(self, new_data):
        self.clear()
        self.addItems(new_data)
        self.data = new_data

    def get_current_item(self):
        if len(self.data):
            cur_ind = self.currentIndex()
            return self.data[cur_ind]
