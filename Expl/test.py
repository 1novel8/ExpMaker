__author__ = 'Aliaksandr'


import cPickle as pickle
import Control
import os
import shutil
import pyodbc
# a = [1,2,3]
# with open(u'D:/workspace/GitProject/testDB.pkl','wb') as output:
#     pickle.dump(a, output, 2)
#
#
# with open(u'D:/workspace/GitProject/testDB.pkl', u'rb') as inp:
#     q = pickle.load(inp)
#     print q
#-*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
import sys
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(QtGui.QFrame):
    def __init__(self, parent = None):
        QtGui.QFrame.__init__(self, parent)
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(20, 20, 61, 21))
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
#    self.comboBox.addItem(_fromUtf8(""))
#    self.comboBox.addItem(_fromUtf8(""))
#    self.comboBox.addItem(_fromUtf8(""))

    # self.comboBox.addItem(_translate("Form", ".60", None))
    # self.comboBox.addItem(_translate("Form", ".45", None))
    # self.comboBox.addItem(_translate("Form", ".19", None))

        self.pushButton = QtGui.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(20, 50, 100, 50))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
    #QtCore.QObject.connect(self.comboBox, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.pushButton.click)
  #
  # def retranslateUi(self, Form):
  #   #index;
  #   Form.setWindowTitle(_translate("Form", "Form", None))
  #
  #   self.pushButton.setText(_translate("Form", "SEND!", None))
  #   self.pushButton.clicked.connect(self.sendIndexFromComboBox)
  #
  # def sendIndexFromComboBox(self,index):
  #
  #   index = self.comboBox.currentIndex()
  #   print index
  #
  #   text = self.comboBox.currentText()
  #   print text

#    if index == 0: print ("Send to .45")
#    elif index == 1: print ("Send to .19")
#    elif index == 2: print ("Send to .60")
#    elif index == 3: print ("Send other stand")


if __name__ == '__main__':
  app = QtGui.QApplication(sys.argv)
  ex = Ui_Form()
  ex.show()
  sys.exit(app.exec_())