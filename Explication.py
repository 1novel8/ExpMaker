#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Alex Konkov'

import sys
from os import path, getcwd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter)
from PyQt5.QtCore import QSize, QCoreApplication
from PyQt5.QtGui import QIcon
from uiWidgets import TableWidget, SrcFrame, LoadingLabel, ProgressBar
from uiCustomWidgets import LogoFrame, ControlsFrame
from menu import MenuBar, MenuConf
from locales import titleLocales
from uiWidgets.styles import splitter as splitter_styles
from constants import sprActions, settingsActions
from threads import BaseActivityThread
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
        self.controls_frame.hide()
        self.log_table = TableWidget(central_widget, headers=titleLocales.log_table_head)
        self.control_table = TableWidget(central_widget, headers=titleLocales.control_table_head)
        self.convert_table = TableWidget(central_widget, headers=titleLocales.convert_table_head)
        self.src_frame = SrcFrame(self, title=titleLocales.src_frame_default, on_select=self.on_file_opened)
        self.init_widgets_positions(central_widget)
        self.init_menu_bar()

        self.setWindowIcon(QIcon(path.join(project_dir, 'Images\exp.png')))
        self.__from_session = False
        self.baseThread = BaseActivityThread(
            self, error_handler=self.base_activity_error_handler,
            success_handler=self.base_activity_success_handler)

        # self.media_src_widget = SrcFrame(self, title="Please, select source file", on_select=self.on_file_selected)
        # main_grid.addWidget(self.media_src_widget, 1, 1, QtCore.Qt.AlignLeft)

    def base_activity_success_handler(self, result):
        print(result)

    def base_activity_error_handler(self, result):
        print(result)

    def init_menu_bar(self):
        menu = MenuBar(self)
        file_section_key = menu.create_section(titleLocales.menu_1, 1)
        sprav_section_key = menu.create_section(titleLocales.menu_2, 2)
        settings_section_key = menu.create_section(titleLocales.menu_3, 3)
        menu.init_sections()
        menu.add_section_action(
            file_section_key, MenuConf.open_file,
            self.src_frame.click_file_selection)
        menu.add_section_action(
            file_section_key, MenuConf.quit_app,
            QCoreApplication.instance().quit)
        menu.add_section_action(
            sprav_section_key, MenuConf.spr_default,
            lambda x: self.run_sprav_action(sprActions.SET_DEFAULT))
        menu.add_section_action(
            sprav_section_key, MenuConf.spr_pkl,
            lambda x: self.run_sprav_action(sprActions.CHOOSE_PKL))
        menu.add_section_action(
            sprav_section_key, MenuConf.spr_mdb,
            lambda x: self.run_sprav_action(sprActions.CHOOSE_MDB))
        menu.add_section_action(
            sprav_section_key, MenuConf.spr_save,
            lambda x: self.run_sprav_action(sprActions.SAVE))
        menu.add_section_action(
            sprav_section_key, MenuConf.spr_info,
            lambda x: self.run_sprav_action(sprActions.INFO))
        menu.add_section_action(
            settings_section_key, MenuConf.settings_xls,
            lambda x: self.run_sprav_action(settingsActions.SHOW_XLS))
        menu.add_section_action(
            settings_section_key, MenuConf.settings_balance,
            lambda x: self.run_sprav_action(settingsActions.SHOW_BALANCE))
        menu.add_section_action(
            settings_section_key, MenuConf.settings_accuracy,
            lambda x: self.run_sprav_action(settingsActions.SHOW_ACCURACY))
        menu.add_section_action(
            settings_section_key, MenuConf.settings_conditions,
            lambda x: self.run_sprav_action(settingsActions.SHOW_CONDITIONS))

    def run_sprav_action(self, action_type):
        print(action_type)

    def run_settings_action(self, action_type):
        print(action_type)

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