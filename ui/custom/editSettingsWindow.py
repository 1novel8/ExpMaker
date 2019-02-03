from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QFrame, QGridLayout, QLabel, QLineEdit, QCheckBox, QMessageBox, QRadioButton)
from constants import settingsActions
from locales import titleLocales
from ui.components import ModalWindow, Dropdown, TableWidget, PrimaryButton, SrcFrame
from constants import coreFiles


def prepare_xl_letters(initial_val):
    return [initial_val, ] + [str(chr(x)) for x in range(65, 91)]


def prepare_xl_digits(initial_val):
    return [str(initial_val), ] + [str(i) for i in range(1, 100)]


class SettingsBlock(QFrame):
    def __init__(self, parent=None, title='', color='#01A6D3'):
        super(SettingsBlock, self).__init__(parent)
        self.box = QGridLayout(self)
        self.setLayout(self.box)
        self.name_lbl = QLabel(title, self)
        self.box.addWidget(self.name_lbl, 0, 0, 1, 3)
        self.setStyleSheet('background-color: %s; color: white; border-radius: 13;' % color)

    def add_widget(self, widget, *args):
        if args:
            args = list(args)
            args[0] += 1
        self.box.addWidget(widget, *args)


class EditSettingsWindow(ModalWindow):
    def __init__(self, initial_settings, sprav_holder, parent=None, edit_action_type=None, on_save=lambda x: x):
        self.settings = initial_settings
        self.sprav_holder = sprav_holder
        self.setts_type = edit_action_type
        if edit_action_type == settingsActions.SHOW_XLS:
            init_params = (titleLocales.edit_settings_xls_title, 800, 530)
            init_method = self.init_xl_widgets
        elif edit_action_type == settingsActions.SHOW_BALANCE:
            init_params = (titleLocales.edit_settings_balance_title, 300, 150)
            init_method = self.init_balance_widgets
        elif edit_action_type == settingsActions.SHOW_ACCURACY:
            init_params = (titleLocales.edit_settings_accuracy_title, 400, 250)
            init_method = self.init_accuracy_widgets
        elif edit_action_type == settingsActions.SHOW_CONDITIONS:
            init_params = (titleLocales.edit_settings_conditions_title, 300, 300)
            init_method = self.init_conditions_widgets
        else:
            raise Exception('Unsupported params provided!')
        super(EditSettingsWindow, self).__init__(parent, *init_params)
        init_method()

    def init_xl_widgets(self):
        settings = self.settings.xls
        block_a = SettingsBlock(self, titleLocales.edit_settings_xls_block_a, '#35B953')
        block_a_sv = SettingsBlock(self, titleLocales.edit_settings_xls_block_a_sv, '#51D04C')
        block_b = SettingsBlock(self, titleLocales.edit_settings_xls_block_b, '#35B953')
        self.sh_edit_ea = QLineEdit(settings.a_sh_name)
        self.sh_edit_easv = QLineEdit(settings.a_sv_sh_name)
        self.sh_edit_eb = QLineEdit(settings.b_sh_name)
        self.sh_edit_ea.setMinimumWidth(250)
        self.sh_edit_easv.setMinimumWidth(250)
        self.sh_edit_eb.setMinimumWidth(250)
        self.cmb_let_ea = Dropdown(self, data=prepare_xl_letters(settings.a_l))
        self.cmb_let_ea_obj = Dropdown(self, data=prepare_xl_letters(settings.a_obj_l))
        self.cmb_let_ea_sv = Dropdown(self, data=prepare_xl_letters(settings.a_sv_l))
        self.cmb_let_eb = Dropdown(self, data=prepare_xl_letters(settings.b_l))
        self.cmb_num_ea = Dropdown(self, data=prepare_xl_digits(settings.a_n))
        self.cmb_num_ea_obj = Dropdown(self, data=prepare_xl_digits(settings.a_obj_n))
        self.cmb_num_ea_sv = Dropdown(self, data=prepare_xl_digits(settings.a_sv_n))
        self.cmb_num_eb = Dropdown(self, data=prepare_xl_digits(settings.b_n))
        table_a = TableWidget(self, titleLocales.edit_xls_table_header)
        table_a.add_representation_row(titleLocales.edit_xls_table_out_matrix)
        table_a.add_widgets_row([self.sh_edit_ea, self.cmb_let_ea, self.cmb_num_ea])
        table_a.add_representation_row(titleLocales.edit_xls_table_out_object)
        table_a.add_widgets_row([None, self.cmb_let_ea_obj, self.cmb_num_ea_obj])
        block_a.add_widget(table_a)
        table_a_sv = TableWidget(self, titleLocales.edit_xls_table_header)
        table_a_sv.add_representation_row(titleLocales.edit_xls_table_out_matrix)
        table_a_sv.add_widgets_row([self.sh_edit_easv, self.cmb_let_ea_sv, self.cmb_num_ea_sv])
        block_a_sv.add_widget(table_a_sv)
        table_b = TableWidget(self, titleLocales.edit_xls_table_header)
        table_b.add_representation_row(titleLocales.edit_xls_table_out_matrix)
        table_b.add_widgets_row([self.sh_edit_eb, self.cmb_let_eb, self.cmb_num_eb])
        block_b.add_widget(table_b)

        self.xl_a_src_widget = SrcFrame(title=titleLocales.edit_xls_a_src_title,
                                        default_dir=coreFiles.xls_templates_dir,
                                        valid_files="*.xls *.xlsx",
                                        on_select=lambda f: self.set_xls_path('a', f))
        self.xl_a_sv_src_widget = SrcFrame(title=titleLocales.edit_xls_a_sv_src_title,
                                           default_dir=coreFiles.xls_templates_dir,
                                           valid_files="*.xls *.xlsx",
                                           on_select=lambda f: self.set_xls_path('a_sv', f))
        self.xl_b_src_widget = SrcFrame(title=titleLocales.edit_xls_b_src_title,
                                        default_dir=coreFiles.xls_templates_dir,
                                        valid_files="*.xls *.xlsx",
                                        on_select=lambda f: self.set_xls_path('b', f))
        self.xl_b_src_widget.set_selected_file(settings.b_path)
        self.xl_a_src_widget.set_selected_file(settings.a_path)
        self.xl_a_sv_src_widget.set_selected_file(settings.a_sv_path)

        self.edit_xls_start = QCheckBox(titleLocales.edit_xls_run_mode_title)
        self.edit_mdb_start = QCheckBox(titleLocales.edit_mdb_run_mode_title)
        self.edit_xls_start.setChecked(settings.is_xls_start)
        self.edit_mdb_start.setChecked(settings.is_mdb_start)

        save_btn = PrimaryButton(self, titleLocales.save_edited_settings, on_click=self.update_settings)
        self.add_widget(block_a, 0, 0, 10, 6)
        self.add_widget(block_a_sv, 10, 0, 4, 6)
        self.add_widget(block_b, 14, 0, 4, 6)
        self.add_widget(self.xl_a_src_widget, 4, 8, 1, 5)
        self.add_widget(self.xl_a_sv_src_widget, 7, 8, 1, 5)
        self.add_widget(self.xl_b_src_widget, 11, 8, 1, 5)
        self.add_widget(self.edit_xls_start, 13, 8, 1, 5)
        self.add_widget(self.edit_mdb_start, 14, 8, 1, 5)
        self.add_widget(save_btn, 17, 10, 1, 2)

    def set_xls_path(self, expl_type, templ_path):
        if templ_path and 'xls' in templ_path:
            if expl_type == 'a':
                self.settings.xls.a_path = templ_path
            elif expl_type == 'a_sv':
                self.settings.xls.a_sv_path = templ_path
            elif expl_type == 'b':
                self.settings.xls.b_path = templ_path
        else:
            QMessageBox.warning(self, titleLocales.error_modal_warning, titleLocales.edit_xls_src_warning, QMessageBox.Ok)

    def init_balance_widgets(self):
        balance_settings = self.settings.balance
        self.edit_b_balance = QCheckBox(titleLocales.edit_settings_enable_b_balance_title)
        self.edit_b_balance.setChecked(balance_settings.include_b_balance)
        # self.edit_a_balance = QtGui.QCheckBox('Включить баланс в расчет одиночной экспликации А (Not yet implemented)')
        # self.edit_a_balance.setChecked(balance_settings.include_a_balance)
        # self.edit_a_sv_balance = QtGui.QCheckBox('Включить баланс в расчет сводной экспликации А (Not yet implemented)')
        # self.edit_a_sv_balance.setChecked(balance_settings.include_a_sv_balance)
        save_btn = PrimaryButton(self, titleLocales.save_edited_settings, on_click=self.update_settings)
        self.add_widget(self.edit_b_balance, 1, 0, 3, 3)
        self.add_widget(save_btn, 4, 2, 1, 1)

    def init_accuracy_widgets(self):
        accuracy_settings = self.settings.rnd
        possible_vals = ['-2', '-1', '0', '1', '2', '3', '4']
        self.edit_a_accuracy = Dropdown(self, data=possible_vals)
        self.edit_a_sv_accuracy = Dropdown(self, data=possible_vals)
        self.edit_b_accuracy = Dropdown(self, data=possible_vals)
        if str(accuracy_settings.a_s_accuracy) not in possible_vals:
            accuracy_settings.a_s_accuracy = 0
        if str(accuracy_settings.a_sv_accuracy) not in possible_vals:
            accuracy_settings.a_sv_accuracy = 0
        if str(accuracy_settings.b_accuracy) not in possible_vals:
            accuracy_settings.b_accuracy = 0
        self.edit_a_accuracy.setCurrentIndex(possible_vals.index(str(accuracy_settings.a_s_accuracy)))
        self.edit_a_sv_accuracy.setCurrentIndex(possible_vals.index(str(accuracy_settings.a_sv_accuracy)))
        self.edit_b_accuracy.setCurrentIndex(possible_vals.index(str(accuracy_settings.b_accuracy)))
        lbl_a_accuracy = QLabel(titleLocales.edit_settings_accuracy_a_title, parent=self)
        lbl_a_sv_accuracy = QLabel(titleLocales.edit_settings_accuracy_a_sv_title, parent=self)
        lbl_b_accuracy = QLabel(titleLocales.edit_settings_accuracy_b_title, parent=self)
        save_btn = PrimaryButton(self, titleLocales.save_edited_settings, on_click=self.update_settings)
        self.add_widget(lbl_a_accuracy, 0, 0, 1, 5)
        self.add_widget(self.edit_a_accuracy, 0, 5, 1, 1)
        self.add_widget(lbl_a_sv_accuracy, 1, 0, 1, 5)
        self.add_widget(self.edit_a_sv_accuracy, 1, 5, 1, 1)
        self.add_widget(lbl_b_accuracy, 2, 0, 1, 5)
        self.add_widget(self.edit_b_accuracy, 2, 5, 1, 1)
        self.add_widget(save_btn, 4, 3, 1, 2)

    def init_conditions_widgets(self):
        conditions_settings = self.settings.conditions
        select_options = self.sprav_holder.select_conditions
        self.selection_options_radio = {}
        grid_y = 1
        for option in select_options:
            op_id = option['Id']
            self.selection_options_radio[op_id] = QRadioButton(option['Title'], parent=self)
            if op_id == conditions_settings.active_cond:
                self.selection_options_radio[op_id].setChecked(True)
            self.add_widget(self.selection_options_radio[op_id], grid_y, 1, 1, 4)
            grid_y += 1

        self.group_by_cc_activated = QCheckBox(titleLocales.edit_settings_conditions_gr_by_cc, parent=self)
        # self.group_by_np_activated = QtGui.QRadioButton('Группировать по населенным пунктам', self)
        # self.group_not_activated = QtGui.QRadioButton('Без группировки', self)
        # if conditions_settings.groupping_by == 'cc':
        #     self.group_by_cc_activated.setChecked(True)
        # elif conditions_settings.groupping_by == 'np':
        #     self.group_by_np_activated.setChecked(True)
        # else:
        #     self.group_not_activated.setChecked(True)
        if conditions_settings.groupping_by == 'cc':
            self.group_by_cc_activated.setChecked(True)
        else:
            self.group_by_cc_activated.setChecked(False)

        selection_title_lbl = QLabel(titleLocales.edit_settings_conditions_ctr_filter, parent=self)
        groupping_title_lbl = QLabel(titleLocales.edit_settings_conditions_sv_exp_groupping, parent=self)
        save_btn = PrimaryButton(self, titleLocales.save_edited_settings, on_click=self.update_settings)
        self.add_widget(selection_title_lbl, 0, 0, 1, 6)
        self.add_widget(groupping_title_lbl, grid_y, 0, 1, 6)
        self.add_widget(self.group_by_cc_activated, grid_y + 1, 1, 1, 5)
        self.add_widget(save_btn, grid_y + 3, 6, 1, 2)

    def update_settings(self):
        print(self.setts_type)
        pass
