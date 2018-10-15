#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Alex Konkov'

import sys
from os import path, getcwd
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter)
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from uiWidgets import TableWidget, SrcFrame, PrimaryButton, LoadingLabel, ProgressBar
from uiCustomWidgets import LogoFrame, ControlsFrame
from locales import titleLocales
from uiWidgets.styles import splitter as splitter_styles
project_dir = getcwd()


class ExpWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setMinimumSize(QSize(640, 480))
        self.resize(1400, 840)
        self.setWindowTitle("Explication 2.0")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.controls_frame = ControlsFrame(self)
        self.log_table = TableWidget(central_widget, headers=titleLocales.log_table_head)
        self.control_table = TableWidget(central_widget, headers=titleLocales.control_table_head)
        self.convert_table = TableWidget(central_widget, headers=titleLocales.convert_table_head)
        self.src_frame = SrcFrame(self, title=titleLocales.src_frame_default, on_select=self.on_file_opened)
        self.init_widgets_positions(central_widget)
        self.setWindowIcon(QIcon(path.join(project_dir, 'Images\exp.png')))
        self.__from_session = False

        # self.media_src_widget = SrcFrame(self, title="Please, select source file", on_select=self.on_file_selected)
        # main_grid.addWidget(self.media_src_widget, 1, 1, QtCore.Qt.AlignLeft)

    def init_widgets_positions(self, central_widget):
        main_grid = QGridLayout(central_widget)
        central_widget.setLayout(main_grid)
        splitter = self.init_splitter()
        logo = LogoFrame(self, titleLocales.logo)
        main_grid.addWidget(logo, 0, 0, 1, 11)
        main_grid.addWidget(self.src_frame, 1, 0, 1, 2)
        main_grid.addWidget(self.controls_frame, 2, 0, 6, 2)
        main_grid.addWidget(self.controls_frame, 2, 0, 6, 2)
        main_grid.addWidget(splitter, 1, 2, 15, 11)

    def init_splitter(self):
        splitter = QSplitter(self)
        splitter.setStyleSheet(splitter_styles)
        # splitter.addWidget(self.expa_widget)
        splitter.addWidget(self.control_table)
        # splitter.addWidget(self.convert_table)
        splitter.addWidget(self.log_table)
        return splitter


    def on_file_opened(self, file_path):
        print(file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = ExpWindow()
    mainWin.show()
    sys.exit(app.exec_())