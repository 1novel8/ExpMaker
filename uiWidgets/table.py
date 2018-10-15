from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QGridLayout, QTextEdit
from PyQt5.QtCore import Qt
from .buttons import PrimaryButton
from .styles import default_table
import time


class TableLabel(QTextEdit):
    def __init__(self, data):
        QTextEdit.__init__(self)
        self.setText(data)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setTextInteractionFlags(Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse)
        self.setMinimumHeight(40)
        self.setMinimumWidth(200)
        self.setStyleSheet(u'color: #AAAAAA; background-color: #22232F; border: 1.5px solid #C10000;'
                           u'border-bottom-right-radius: 30%; font-size: 14px;'
                           u' padding-right: 10px;padding-left: 15px')


class TableWidget(QWidget):
    def __init__(self, parent=None, headers=None, with_clear=True):
        QWidget.__init__(self, parent)
        self.__row_count = 0
        self.box = QGridLayout(self)
        self.table = QTableWidget(parent)
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

        # TODO: move to separate styles
        # header_css = u'border-radius: 1px; border: 1px dashed blue;'
        # self.table.horizontalHeader().setStyleSheet(header_css)
        # self.table.verticalHeader().setStyleSheet(header_css + u'padding:-2px')
        self.table.setStyleSheet(default_table)

    def add_span_row(self, text, span=True):
        self.__row_count += 1
        self.setRowCount(self.__row_count)
        time_label = TableLabel(text)
        time_label.setStyleSheet(u'color: #D3D3D3; background-color: #323C3D;font-size: 14px;'
                           u'border-top-left-radius: 30%; padding-right: 15px;padding-left: 15px')
        self.setCellWidget(self.__row_count-1, 0, time_label)
        if span:
            time_label.setAlignment(Qt.AlignCenter)
            time_label.setMinimumHeight(20)
            self.setSpan(self.__row_count-1, 0, 1, self.columnCount())

    def add_logging_row(self, row_li, time_label=None):
        if not time_label:
            time_label = time.strftime(u"%H:%M:%S  \n%d.%m.%y")
        self.add_span_row(time_label, False)
        for i, cell in enumerate(row_li):
            self.setCellWidget(self.__row_count-1, i+1, TableLabel(cell))

    def add_row(self, row_li):
        self.__row_count += 1
        self.setRowCount(self.__row_count)
        for i, cell in enumerate(row_li):
            self.setItem(self.__row_count-1, i, QTableWidgetItem(cell))

    def add_widgets_row(self, widgets_row):
        self.__row_count += 1
        self.setRowCount(self.__row_count)
        for i, cell in enumerate(widgets_row):
            self.setCellWidget(self.__row_count-1, i, cell)

    def clear_table(self):
        self.__row_count = 0
        self.table.reset()
        self.table.clearSpans()
        self.table.setRowCount(1)
