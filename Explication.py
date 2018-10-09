#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Alex Konkov'

import sys
from os import path
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout)
from PyQt5.QtCore import QSize
from uiWidgets import SrcFrame, PrimaryButton, LoadingLabel, ProgressBar
from uiCustomWidgets import LogoFrame, ControlsFrame
from locales import titleLocales

class ExpWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setMinimumSize(QSize(640, 480))
        self.resize(1400, 840)
        self.setWindowTitle("Explication 2.0")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_grid = QGridLayout(central_widget)
        central_widget.setLayout(main_grid)
        logo = LogoFrame(self, titleLocales.logo)
        self.controls_frame = ControlsFrame(self)
        main_grid.addWidget(logo, 0, 0, 1, 11)
        main_grid.addWidget(self.controls_frame, 2, 0, 6, 2)




        # self.media_src_widget = SrcFrame(self, title="Please, select source file", on_select=self.on_file_selected)
        # main_grid.addWidget(self.media_src_widget, 1, 1, QtCore.Qt.AlignLeft)

    def on_file_selected(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = ExpWindow()
    mainWin.show()
    sys.exit(app.exec_())