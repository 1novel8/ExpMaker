from os import getcwd, path
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QHBoxLayout, QFileDialog)
from PyQt5.QtCore import Qt, QSize
from ui.styles import SourceWidgetStyles as Styles
from .buttons import PrimaryButton
from locales import titleLocales
base_dir = getcwd()


class SrcFrame(QFrame):
    def __init__(self, parent=None,
                 title="...",
                 on_select=None,
                 get_dir=False,
                 update_self_after_select=False,
                 placeholder="",
                 valid_files="*.mdb *.pkl",
                 default_dir=base_dir):
        QFrame.__init__(self, parent)
        self.title = title
        self.placeholder = placeholder
        self.valid_files = valid_files
        self.default_dir = default_dir
        self.is_dir_required = get_dir
        self.on_select = on_select
        self.force_set_text = update_self_after_select
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
                .getOpenFileName(self, self.title, self.default_dir,
                                 'Valid media files (%s);; All files (*)' % self.valid_files,
                                 options=QFileDialog.DontUseNativeDialog)
            src = str(src[0]).replace('/', '\\')
        else:
            src = QFileDialog(self)\
                .getExistingDirectory(self, self.title, self.default_dir,
                                      options=QFileDialog.DontUseNativeDialog)
            src = str(src).replace('/', '\\')
        if src:
            self.selected_file = src
            if self.on_select:
                if self.force_set_text:
                    self.set_src_text()
                self.on_select(self.selected_file)
            else:
                self.set_src_text()

    def get_selected_file(self, name_only=False):
        if '\\' not in self.selected_file:
            return ''
        if name_only:
            file_name = path.basename(self.selected_file)
            return path.splitext(file_name)[0]
        return self.selected_file

    def set_selected_file(self, new_src):
        if new_src:
            self.selected_file = new_src
            self.set_src_text()

    def clear(self, hide=False):
        self.selected_file = ''
        self.set_src_text(src_text=self.placeholder)
        self.setHidden(hide)

    def set_src_text(self, src_text=None, collapse_len=40):
        """
        В строке text делается перенос относительно \ если длина превышает 40 символов
        :param src_text: new source text
        :param collapse_len: len to split text
        :return:
        """
        if not src_text:
            src_text = str(self.selected_file)
        path_parts = src_text.split('\\')
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
