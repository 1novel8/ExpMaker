from os import getcwd
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QHBoxLayout, QFileDialog)
from PyQt5.QtCore import Qt, QSize
from .styles import SourceWidgetStyles as Styles
from .buttons import PrimaryButton
base_dir = getcwd()


class SrcFrame(QFrame):
    def __init__(self, parent=None, title="", on_select=lambda x: x):
        QFrame.__init__(self, parent)
        self.title = title
        self.on_select = on_select
        self.setMinimumSize(QSize(240, 80))
        self.grid = QVBoxLayout(self)
        self.h_box = QHBoxLayout()
        self.src_btn = PrimaryButton(self)
        self.src_btn.setText("Select File")
        self.src_lbl = QLabel("No file chosen", self)
        self.src_lbl.setStyleSheet(Styles.src_lbl)
        self.src_btn.setStyleSheet(Styles.src_btn)
        self.src_lbl.setAlignment(Qt.AlignRight)
        self.src_btn.setFixedHeight(40)
        self.src_lbl.setFixedHeight(40)
        self.h_box.addWidget(self.src_lbl)
        self.h_box.addWidget(self.src_btn)
        if title:
            title_lbl = QLabel(title)
            title_lbl.setFixedHeight(20)
            title_lbl.setStyleSheet(Styles.title_lbl)
            self.grid.addWidget(title_lbl)
        self.grid.addItem(self.h_box)
        self.src_btn.clicked.connect(self.__open_src_dialog)
        self.selected_file = ""

    def __open_src_dialog(self):
        db_f = QFileDialog(self)\
            .getOpenFileName(self,
                             "open file",
                             base_dir,
                             "Valid media files (*.mdb *.pkl);; All files (*)",
                             options=QFileDialog.DontUseNativeDialog)
        if db_f[0]:
            self.selected_file = str(db_f[0])
            self.src_lbl.setText("Selected file: %s" % self.selected_file)
            self.on_select(self.selected_file)
        # else:
        #     self.selected_file = ""
        #     self.src_lbl.setText("No file chosen")
        #
