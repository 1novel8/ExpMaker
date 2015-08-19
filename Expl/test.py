from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys

def main():
    app 	= QApplication(sys.argv)
    table 	= QTableWidget()
    tableItem 	= QTableWidgetItem()

    table.setWindowTitle("Set QWidget for Entire QTableWidget Column")
    table.resize(400, 250)
    table.setRowCount(4)
    table.setColumnCount(3)

    table.setHorizontalHeaderLabels(QString("HEADER 1;HEADER 2;HEADER 3;HEADER 4").split(";"))

    table.setItem(0,0, QTableWidgetItem("ITEM 1_1"))
    table.setItem(0,1, QTableWidgetItem("ITEM 1_2"))

    table.setItem(1,0, QTableWidgetItem("ITEM 2_1"))
    table.setItem(1,1, QTableWidgetItem("ITEM 2_2"))

    table.setItem(2,0, QTableWidgetItem("ITEM 3_1"))
    table.setItem(2,1, QTableWidgetItem("ITEM 3_2"))

    table.setItem(3,0, QTableWidgetItem("ITEM 4_1"))
    table.setItem(3,1, QTableWidgetItem("ITEM 4_2"))

    #Add Widget to the rightmost Element of First Row
    table.setItem(0,2,tableItem)

    #Add QPushButton to the rightmost QTableWidgetItem on first row
    table.setCellWidget(0,2, QPushButton("Cell Widget"));

    #Span Right-Most Item of First Row Here
    table.setSpan(1,0,1,table.columnCount())
    table.show()
    return app.exec_()

if __name__ == '__main__':
    main()












# from PyQt4.QtGui import QWidget, QApplication, QTreeView, QListView, QTextEdit, \
#                         QSplitter, QHBoxLayout
#
# import sys
#
# class MainWindow(QWidget):
#     def __init__(self):
#         QWidget.__init__(self)
#
#         treeView = QTreeView()
#         listView = QListView()
#         textEdit = QTextEdit()
#         splitter = QSplitter(self)
#
#         splitter.addWidget(treeView)
#         splitter.addWidget(listView)
#         splitter.addWidget(textEdit)
#
#         layout = QHBoxLayout()
#         layout.addWidget(splitter)
#         self.setLayout(layout)
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     mainWindow = MainWindow()
#     mainWindow.show()
#     sys.exit(app.exec_())