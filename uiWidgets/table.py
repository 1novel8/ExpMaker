from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QGridLayout, QTextEdit
from PyQt5.QtCore import Qt
from .buttons import PrimaryButton
from .styles import default_table, representation_table_label


class TableLabel(QTextEdit):
    def __init__(self, data):
        QTextEdit.__init__(self)
        self.setText(data)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setTextInteractionFlags(Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse)
        self.setMinimumHeight(40)
        self.setMinimumWidth(200)
        self.setStyleSheet('color: #AAAAAA; background-color: #22232F; font-size: 14px;'
                           'padding-right: 10px;padding-left: 15px')


class TableWidget(QWidget):
    def __init__(self, parent=None, headers=None, with_clear=False):
        QWidget.__init__(self, parent)
        self.__row_count = 0
        self.box = QGridLayout(self)
        self.table = QTableWidget(self)
        self.init_table_defaults(headers)
        self.box.addWidget(self.table, 0, 0, 21, 21)
        if with_clear:
            self.clear_btn = PrimaryButton(parent, 'clear', on_click=self.clear_table)
            self.box.addWidget(self.clear_btn, 21, 10, 2, 2)
            # self.hide()

    def init_table_defaults(self, headers):
        self.table.horizontalHeader().setCascadingSectionResizes(True)
        self.table.verticalHeader().setCascadingSectionResizes(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setMinimumSectionSize(50)
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setAlternatingRowColors(True)
        self.table.setAutoScroll(True)
        self.table.setStyleSheet(default_table)

    def get_row_count(self):
        return self.__row_count

    def add_representation_row(self, title, with_span=True):
        self.table.setRowCount(self.__row_count + 1)
        title_label = TableLabel(title)
        title_label.setStyleSheet(representation_table_label)
        self.table.setCellWidget(self.__row_count, 0, title_label)
        if with_span:
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setMinimumHeight(20)
            self.table.setSpan(self.__row_count, 0, 1, self.columnCount())
        self.__row_count += 1

    def add_row(self, row_li):
        self.__row_count += 1
        self.table.setRowCount(self.__row_count)
        for i, cell in enumerate(row_li):
            self.setItem(self.__row_count-1, i, QTableWidgetItem(cell))

    def add_widgets_row(self, widgets_row):
        self.__row_count += 1
        self.table.setRowCount(self.__row_count)
        for i, cell in enumerate(widgets_row):
            self.table.setCellWidget(self.__row_count-1, i, cell)

    def clear_table(self):
        self.__row_count = 0
        self.table.reset()
        self.table.clearSpans()
        self.table.setRowCount(1)
