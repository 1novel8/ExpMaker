from os import getcwd
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QHBoxLayout, QFileDialog)
from PyQt5.QtCore import Qt, QSize
from .styles import SourceWidgetStyles as Styles
from .buttons import PrimaryButton
from locales import titleLocales
base_dir = getcwd()


class SrcFrame(QFrame):
    def __init__(self, parent=None, title='...', on_select=lambda x: x, get_dir=False, placeholder=''):
        QFrame.__init__(self, parent)
        self.title = title
        self.is_dir_required = get_dir
        self.on_select = on_select
        self.setMinimumSize(QSize(240, 80))
        self.grid = QVBoxLayout(self)
        self.h_box = QHBoxLayout()
        self.src_btn = PrimaryButton(self, title=titleLocales.src_frame_select_file_btn)
        self.src_lbl = QLabel(placeholder, self)
        self.src_lbl.setStyleSheet(Styles.src_lbl)
        self.src_btn.setStyleSheet(Styles.src_btn)
        self.src_lbl.setAlignment(Qt.AlignRight)
        self.src_btn.setFixedHeight(40)
        self.src_lbl.setFixedHeight(40)
        self.h_box.addWidget(self.src_lbl, 2)
        self.h_box.addWidget(self.src_btn)
        if title:
            title_lbl = QLabel(title)
            title_lbl.setFixedHeight(20)
            title_lbl.setStyleSheet(Styles.title_lbl)
            self.grid.addWidget(title_lbl)
        self.grid.addItem(self.h_box)
        self.src_btn.clicked.connect(self.__open_src_dialog)
        self.selected_file = ''

    def click_file_selection(self):
        self.src_btn.click()

    def __open_src_dialog(self):
        if not self.is_dir_required:
            src = QFileDialog(self)\
                .getOpenFileName(self, self.title, base_dir,
                                 'Valid media files (*.mdb *.pkl);; All files (*)',
                                 options=QFileDialog.DontUseNativeDialog)
            src = str(src[0]).replace('/', '\\')
        else:
            src = QFileDialog(self)\
                .getExistingDirectory(self, self.title, base_dir,
                                      options=QFileDialog.DontUseNativeDialog)
            src = str(src).replace('/', '\\')
        if src:
            self.selected_file = src
            self.on_select(self.selected_file)
        # else:
        #     self.selected_file = ''
        #     self.src_lbl.setText('No file chosen')
        #

    def get_selected_file(self):
        return self.selected_file

    def set_src_text(self, collapse_len=40):
        """
        В строке text делается перенос относительно \ если длина превышает 40 символов
        # :param text: new source label text
        :param collapse_len: len to split text
        :return:
        """
        path_parts = self.selected_file.split('\\')
        text = path_parts.pop(0)
        if path_parts:
            temp_text = ''
            for part in path_parts:
                part = '\\%s' % part
                if len(part) + len(temp_text) > collapse_len:
                    text += '%s\n' % temp_text
                    temp_text = part
                else:
                    temp_text += part
            text += temp_text
        self.src_lbl.setText(text)
        self.src_lbl.repaint()
