from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel, QSizePolicy

from constants import controlsStates, expActions, extractionActions
from locales import titleLocales, tooltipsLocales
from ui.components import PrimaryButton
from ui.styles import title_label


class ControlsFrame(QFrame):
    def __init__(self, parent=None, on_click=lambda x: x):
        QFrame.__init__(self, parent)
        self.previous_state = None
        self.current_state = None
        self.exp_tree_initialized = False
        self.mainSizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.controls_box = QGridLayout(parent)
        self.control_lbl = QLabel(titleLocales.control_lbl, self)
        self.convert_lbl = QLabel(titleLocales.convert_lbl, self)
        self.exp_a_lbl = QLabel(titleLocales.exp_a_lbl, self)
        self.exp_b_lbl = QLabel(titleLocales.exp_b_lbl, self)
        self.control_btn = PrimaryButton(self, titleLocales.run_btn)
        self.convert_btn = PrimaryButton(self, titleLocales.run_btn)
        # self.exp_single_btn = PrimaryButton(self, titleLocales.exp_single_btn)
        self.exp_sv_btn = PrimaryButton(self, titleLocales.exp_sv_btn)
        self.exp_b_btn = PrimaryButton(self, titleLocales.calc_btn)
        self.control_btn.clicked.connect(lambda x: on_click(extractionActions.CONTROL))
        self.convert_btn.clicked.connect(lambda x: on_click(extractionActions.CONVERTATION))
        self.exp_sv_btn.clicked.connect(lambda x: on_click(expActions.EXP_A_SV))
        self.exp_b_btn.clicked.connect(lambda x: on_click(expActions.EXP_B))
        # self.exp_sv_btn.setHidden(True)
        # self.exp_single_btn.setHidden(True)
        self._set_tooltips()
        self._set_styles()
        self.controls_box = QGridLayout(self)
        self._locate_components()

    def _locate_components(self):
        self.controls_box.addWidget(self.control_lbl, 0, 0, 1, 1)
        self.controls_box.addWidget(self.convert_lbl, 2, 0, 1, 1)
        self.controls_box.addWidget(self.exp_a_lbl, 4, 0, 1, 1)
        self.controls_box.addWidget(self.exp_b_lbl, 6, 0, 1, 1)
        self.controls_box.addWidget(self.control_btn, 0, 1, 1, 1)
        self.controls_box.addWidget(self.convert_btn, 2, 1, 1, 1)
        # self.controls_box.addWidget(self.exp_single_btn, 3, 1, 1, 1)
        self.controls_box.addWidget(self.exp_sv_btn,  4, 1, 1, 1)
        self.controls_box.addWidget(self.exp_b_btn, 6, 1, 1, 1)

    def _set_tooltips(self):
        self.control_btn.setToolTip(tooltipsLocales.btn_control)
        self.convert_btn.setToolTip(tooltipsLocales.btn_convert)
        # self.exp_single_btn.setToolTip(tooltipsLocales.exp_single_btn)
        self.exp_sv_btn.setToolTip(tooltipsLocales.exp_sv_btn)
        self.exp_b_btn.setToolTip(tooltipsLocales.exp_b_btn)

    def _set_styles(self):
        self.control_lbl.setStyleSheet(title_label)
        self.convert_lbl.setStyleSheet(title_label)
        self.exp_a_lbl.setStyleSheet(title_label)
        self.exp_b_lbl.setStyleSheet(title_label)

    def set_all_disabled(self, state):
        self.control_btn.setDisabled(state)
        self.convert_btn.setDisabled(state)
        self.exp_sv_btn.setDisabled(state)
        self.exp_b_btn.setDisabled(state)

    def set_state(self, state):
        self.previous_state = self.current_state
        self.current_state = state
        if state == controlsStates.INITIAL:
            self.hide()
            return
        if state == controlsStates.LOADING:
            return
        self.show()
        if state == controlsStates.CONVERTATION_PASSED:
            self.set_all_disabled(False)
            return
        self.set_all_disabled(True)

        if state == controlsStates.DB_LOADED \
                or state == controlsStates.CONVERTATION_FAILED \
                or state == controlsStates.CONTROL_FAILED:
            self.control_btn.setEnabled(True)
            return
        if state == controlsStates.CONTROL_PASSED:
            self.control_btn.setEnabled(True)
            self.convert_btn.setEnabled(True)
            return
        if state == controlsStates.SESSION_LOADED:
            self.exp_sv_btn.setEnabled(True)
            self.exp_b_btn.setEnabled(True)

    def set_previous_state(self):
        self.set_state(self.previous_state)
