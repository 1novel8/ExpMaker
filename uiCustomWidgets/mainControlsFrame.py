from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel, QSizePolicy
from locales import titleLocales, tooltipsLocales
from uiWidgets import PrimaryButton
from uiWidgets.styles import title_label


class ControlsFrame(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.exp_tree_initialized = False
        self.mainSizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.controls_box = QGridLayout(parent)
        self.control_lbl = QLabel(titleLocales.control_lbl, self)
        self.convert_lbl = QLabel(titleLocales.convert_lbl, self)
        self.exp_a_lbl = QLabel(titleLocales.exp_a_lbl, self)
        self.exp_b_lbl = QLabel(titleLocales.exp_b_lbl, self)
        self.control_btn = PrimaryButton(self, titleLocales.run_btn)
        self.convert_btn = PrimaryButton(self, titleLocales.run_btn)
        self.exp_single_btn = PrimaryButton(self, titleLocales.exp_single_btn)
        self.exp_sv_btn = PrimaryButton(self, titleLocales.exp_sv_btn)
        self.exp_b_btn = PrimaryButton(self, titleLocales.calc_btn)
        # self.exp_sv_btn.setHidden(True)
        # self.exp_single_btn.setHidden(True)
        self._set_size_policy()
        self._set_tooltips()
        self._set_styles()
        self.controls_box = QGridLayout(self)
        self._locate_components()

    def _locate_components(self):
        self.controls_box.addWidget(self.control_lbl, 0, 0, 1, 1)
        self.controls_box.addWidget(self.convert_lbl, 2, 0, 1, 1)
        self.controls_box.addWidget(self.exp_a_lbl, 3, 0, 1, 1)
        self.controls_box.addWidget(self.exp_b_lbl, 6, 0, 1, 1)
        self.controls_box.addWidget(self.control_btn, 0, 1, 1, 1)
        self.controls_box.addWidget(self.convert_btn, 2, 1, 1, 1)
        self.controls_box.addWidget(self.exp_single_btn, 3, 1, 1, 1)
        self.controls_box.addWidget(self.exp_sv_btn,  4, 1, 1, 1)
        self.controls_box.addWidget(self.exp_b_btn, 6, 1, 1, 1)

    def _set_tooltips(self):
        self.control_btn.setToolTip(tooltipsLocales.btn_control)
        self.convert_btn.setToolTip(tooltipsLocales.btn_convert)
        self.exp_single_btn.setToolTip(tooltipsLocales.exp_single_btn)
        self.exp_sv_btn.setToolTip(tooltipsLocales.exp_sv_btn)
        self.exp_b_btn.setToolTip(tooltipsLocales.exp_b_btn)

    def _set_size_policy(self):
        pass
        # self.convert_btn.setSizePolicy(self.mainSizePolicy)
        # self.control_btn.setSizePolicy(self.mainSizePolicy)
        # self.exp_single_btn.setSizePolicy(self.mainSizePolicy)
        # self.exp_sv_btn.setSizePolicy(self.mainSizePolicy)
        # self.exp_b_btn.setSizePolicy(self.mainSizePolicy)

    def _set_styles(self):
        self.control_lbl.setStyleSheet(title_label)
        self.convert_lbl.setStyleSheet(title_label)
        self.exp_a_lbl.setStyleSheet(title_label)
        self.exp_b_lbl.setStyleSheet(title_label)