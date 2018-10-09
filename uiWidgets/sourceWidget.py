from PyQt5 import QtCore, QtWidgets
from os import getcwd
base_dir = getcwd()

styles = {
    "src_lbl":  """
        color: white; 
        margin: 0; 
        padding: 4px; 
        background-color: #115f50; 
        border-top-left-radius: 8%;
        border-bottom-left-radius: 8%;
        border: 1px solid #00BA4A
    """,
    "title_lbl":  """
        color: #115f50;
        padding: 4px;
        font-size: 12px;
        font-weight: bold;
    """,
    "src_btn": """
        background-color: #00BA4A; 
        padding: 5px; 
        color: white;
        font-size: 15px;
        border-top-right-radius: 8%;
        border-bottom-right-radius: 8%;
    """,
}


class SrcFrame(QtWidgets.QFrame):
    def __init__(self, parent=None, title="", on_select=lambda x: x):
        QtWidgets.QFrame.__init__(self, parent)
        self.title = title
        self.on_select = on_select
        self.setMinimumSize(QtCore.QSize(240, 80))
        self.grid = QtWidgets.QVBoxLayout(self)
        self.h_box = QtWidgets.QHBoxLayout()
        self.src_btn = QtWidgets.QToolButton(self)
        self.src_btn.setText("Select File")
        self.src_lbl = QtWidgets.QLabel("No file chosen", self)
        self.src_btn.setStyleSheet(styles["src_btn"])
        self.src_lbl.setStyleSheet(styles["src_lbl"])
        self.src_lbl.setAlignment(QtCore.Qt.AlignRight)
        self.src_btn.setFixedHeight(40)
        self.src_lbl.setFixedHeight(40)
        self.h_box.addWidget(self.src_lbl)
        self.h_box.addWidget(self.src_btn)
        self.h_box.setSpacing(0)
        self.grid.setSpacing(0)
        self.grid.addStretch(1)
        if title:
            title_lbl = QtWidgets.QLabel(title)
            title_lbl.setFixedHeight(40)
            title_lbl.setStyleSheet(styles["title_lbl"])
            self.grid.addWidget(title_lbl)
        self.grid.addItem(self.h_box)
        self.src_btn.clicked.connect(self.__open_src_dialog)
        self.selected_file = ""

    def __open_src_dialog(self):
        db_f = QtWidgets.QFileDialog(self)\
            .getOpenFileName(self,
                             "open file",
                             base_dir,
                             "Valid media files (*.mp4 *.mkv);; All files (*)",
                             options=QtWidgets.QFileDialog.DontUseNativeDialog)
        if db_f[0]:
            self.selected_file = str(db_f[0])
            self.src_lbl.setText("Selected file: %s" % self.selected_file)
            self.on_select(self.selected_file)
        # else:
        #     self.selected_file = ""
        #     self.src_lbl.setText("No file chosen")
        #
