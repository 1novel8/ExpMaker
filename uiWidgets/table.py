from PyQt5.QtWidgets import QWidget, QTableWidget


class TableWidget(QtGui.QWidget):
    def __init__(self, title, parent = None, with_clear = True):
        QtGui.QWidget.__init__(self, parent)
        self.table = Table(title, parent)
        self.box = QtGui.QGridLayout(self)
        self.box.addWidget(self.table,0,0,21,21)
        if with_clear:
            self.clear_btn = StyledButton(WidgNames.btn_clear, parent)
            self.box.addWidget(self.clear_btn,19,10,2,2)
            self.connect(self.clear_btn, QtCore.SIGNAL(u"clicked()"), self.table.clear_all)
            self.hide()

    def clear_all(self):
        self.table.clear_all()