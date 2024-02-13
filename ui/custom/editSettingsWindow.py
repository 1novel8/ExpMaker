from PyQt5.QtWidgets import (QCheckBox, QFrame, QLabel, QLineEdit, QMessageBox,
                             QRadioButton, QVBoxLayout)

from constants import coreFiles, settingsActions
from locales import titleLocales
from ui.components import (Dropdown, ModalWindow, PrimaryButton, SrcFrame,
                           TableWidget)
from ui.styles import representation_xls_table_label, title_label
from ui.styles import xls_table as xls_table_styles


def prepare_xl_letters(initial_val):
    return [initial_val, ] + [str(chr(x)) for x in range(65, 91)]


def prepare_xl_digits(initial_val):
    return [str(initial_val), ] + [str(i) for i in range(1, 100)]


class SettingsBlock(QFrame):
    def __init__(self, parent=None, title=''):
        super(SettingsBlock, self).__init__(parent)
        self.box = QVBoxLayout(self)
        self.setLayout(self.box)
        if title:
            self.name_lbl = QLabel(title, self)
            self.name_lbl.setStyleSheet(title_label)
            self.box.addWidget(self.name_lbl)

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
        self.emit_settings_updated = on_save
        if edit_action_type == settingsActions.SHOW_XLS:
            init_params = (titleLocales.edit_settings_xls_title, 960, 710)
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
        elif edit_action_type == settingsActions.SHOW_EXP_FILTER:
            init_params = (titleLocales.edit_settings_exp_filter_title, 300, 300)
            init_method = self.init_exp_filter_settings
        else:
            raise Exception('Unsupported params provided!')
        super(EditSettingsWindow, self).__init__(parent, *init_params)
        init_method()

    def init_xl_widgets(self):
        settings = self.settings.xls
        tables_box = SettingsBlock(self, title='')
        sources_box = SettingsBlock(self, title='')
        tables_box.setMinimumWidth(450)
        block_a = SettingsBlock(tables_box, titleLocales.edit_settings_xls_block_a)
        block_a_sv = SettingsBlock(tables_box, titleLocales.edit_settings_xls_block_a_sv)
        block_b = SettingsBlock(tables_box, titleLocales.edit_settings_xls_block_b)
        tables_box.add_widget(block_a, 3)
        tables_box.add_widget(block_a_sv, 2)
        tables_box.add_widget(block_b, 2)
        self.sh_edit_ea = QLineEdit(settings.a_sh_name)
        self.sh_edit_easv = QLineEdit(settings.a_sv_sh_name)
        self.sh_edit_eb = QLineEdit(settings.b_sh_name)
        self.cmb_let_ea = Dropdown(self, data=prepare_xl_letters(settings.a_l))
        self.cmb_let_ea_obj = Dropdown(self, data=prepare_xl_letters(settings.a_obj_l))
        self.cmb_let_ea_sv = Dropdown(self, data=prepare_xl_letters(settings.a_sv_l))
        self.cmb_let_eb = Dropdown(self, data=prepare_xl_letters(settings.b_l))
        self.cmb_num_ea = Dropdown(self, data=prepare_xl_digits(settings.a_n))
        self.cmb_num_ea_obj = Dropdown(self, data=prepare_xl_digits(settings.a_obj_n))
        self.cmb_num_ea_sv = Dropdown(self, data=prepare_xl_digits(settings.a_sv_n))
        self.cmb_num_eb = Dropdown(self, data=prepare_xl_digits(settings.b_n))
        table_a = TableWidget(self, titleLocales.edit_xls_table_header, styles=xls_table_styles)
        table_a.add_representation_row(titleLocales.edit_xls_table_out_matrix, styles=representation_xls_table_label)
        table_a.add_widgets_row([self.sh_edit_ea, self.cmb_let_ea, self.cmb_num_ea])
        table_a.add_representation_row(titleLocales.edit_xls_table_out_object, styles=representation_xls_table_label)
        table_a.add_widgets_row([None, self.cmb_let_ea_obj, self.cmb_num_ea_obj])
        block_a.add_widget(table_a)
        table_a_sv = TableWidget(self, titleLocales.edit_xls_table_header, styles=xls_table_styles)
        table_a_sv.add_representation_row(titleLocales.edit_xls_table_out_matrix, styles=representation_xls_table_label)
        table_a_sv.add_widgets_row([self.sh_edit_easv, self.cmb_let_ea_sv, self.cmb_num_ea_sv])
        block_a_sv.add_widget(table_a_sv)
        table_b = TableWidget(self, titleLocales.edit_xls_table_header, styles=xls_table_styles)
        table_b.add_representation_row(titleLocales.edit_xls_table_out_matrix, styles=representation_xls_table_label)
        table_b.add_widgets_row([self.sh_edit_eb, self.cmb_let_eb, self.cmb_num_eb])
        block_b.add_widget(table_b)

        self.xl_a_src_widget = SrcFrame(title=titleLocales.edit_xls_a_src_title,
                                        default_dir=coreFiles.xls_templates_dir,
                                        valid_files="*.xls *.xlsx")
        self.xl_a_sv_src_widget = SrcFrame(title=titleLocales.edit_xls_a_sv_src_title,
                                           default_dir=coreFiles.xls_templates_dir,
                                           valid_files="*.xls *.xlsx")
        self.xl_b_src_widget = SrcFrame(title=titleLocales.edit_xls_b_src_title,
                                        default_dir=coreFiles.xls_templates_dir,
                                        valid_files="*.xls *.xlsx")
        self.xl_b_src_widget.set_selected_file(settings.b_path)
        self.xl_a_src_widget.set_selected_file(settings.a_path)
        self.xl_a_sv_src_widget.set_selected_file(settings.a_sv_path)
        sources_box.add_widget(self.xl_a_src_widget)
        sources_box.add_widget(self.xl_a_sv_src_widget)
        sources_box.add_widget(self.xl_b_src_widget)

        self.edit_xls_start = QCheckBox(titleLocales.edit_xls_run_mode_title)
        #self.edit_mdb_start = QCheckBox(titleLocales.edit_mdb_run_mode_title)
        self.edit_xls_start.setChecked(settings.is_xls_start)
        #self.edit_mdb_start.setChecked(settings.is_mdb_start)

        save_btn = PrimaryButton(self, titleLocales.save_edited_settings, on_click=self.update_settings)
        self.add_widget(tables_box, 0, 0, 12, 7)
        self.add_widget(sources_box, 0, 7, 7, 5)
        self.add_widget(self.edit_xls_start, 9, 8, 1, 3)
        #self.add_widget(self.edit_mdb_start, 10, 8, 1, 3)
        self.add_widget(save_btn, 11, 9, 1, 1)

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
        self.add_widget(save_btn, 5, 4, 1, 2)

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
        selection_title_lbl.setStyleSheet(title_label)
        groupping_title_lbl.setStyleSheet(title_label)
        save_btn = PrimaryButton(self, titleLocales.save_edited_settings, on_click=self.update_settings)
        self.add_widget(selection_title_lbl, 0, 0, 1, 6)
        self.add_widget(groupping_title_lbl, grid_y, 0, 1, 6)
        self.add_widget(self.group_by_cc_activated, grid_y + 1, 1, 1, 5)
        self.add_widget(save_btn, grid_y + 3, 6, 1, 2)

    def init_exp_filter_settings(self):
        filter_settings = self.settings.filter
        self.melio_filter_used = QRadioButton('Выбрать МЕЛИОРИРУЕМЫЕ земли', self)
        self.servtype_filter_used = QRadioButton('Выбрать земли ЗАГРЯЗНЕННЫЕ РАДИОНУКЛИДАМИ', self)
        self.melio_filter_used.setChecked(filter_settings.enable_melio)
        self.servtype_filter_used.setChecked(not filter_settings.enable_melio)
        save_btn = PrimaryButton(self, titleLocales.save_edited_settings, on_click=self.update_settings)
        self.add_widget(self.melio_filter_used, 0, 0, 1, 2)
        self.add_widget(self.servtype_filter_used, 1, 0, 1, 2)
        self.add_widget(save_btn, 4, 3, 1, 1)

    def update_settings(self):
        upd_successfull = False
        params = {'setts_type': self.setts_type}
        if self.setts_type == settingsActions.SHOW_XLS:
            upd_successfull = self._change_xls_setts()
        elif self.setts_type == settingsActions.SHOW_BALANCE:
            upd_successfull = self._change_balance_setts()
        elif self.setts_type == settingsActions.SHOW_ACCURACY:
            upd_successfull = self._change_accuracy_setts()
            QMessageBox.information(self, titleLocales.error_modal_warning, "После изменений параметров необходимо заново запустить КОНВЕРТАЦИЮ", QMessageBox.Ok)
        elif self.setts_type == settingsActions.SHOW_CONDITIONS:
            upd_successfull = self._change_conditions_setts()
            params['active_condition_changed'] = upd_successfull and upd_successfull['active_condition_changed']
        elif self.setts_type == settingsActions.SHOW_EXP_FILTER:
            params['has_changes'] = self.__change_exp_filter_settings()
            upd_successfull = True
        if upd_successfull:
            self.emit_settings_updated(params)

    def get_xls_templates(self):
        a_path = self.xl_a_src_widget.get_selected_file()
        a_sv_path = self.xl_a_sv_src_widget.get_selected_file()
        b_path = self.xl_b_src_widget.get_selected_file()
        for p in (a_path, a_sv_path, b_path):
            if not p or 'xls' not in p:
                QMessageBox.warning(self, titleLocales.error_modal_warning, titleLocales.edit_xls_src_warning,
                                    QMessageBox.Ok)
                return
        return a_path, a_sv_path, b_path

    def _change_xls_setts(self):
        if not hasattr(self, 'sh_edit_ea'):
            raise Exception("Unable to retrieve new settings; unexpected method call")
        xls_setts = self.settings.xls
        selected_templates = self.get_xls_templates()
        if not selected_templates:
            return False
        xls_setts.a_path, xls_setts.a_sv_path, xls_setts.b_path = selected_templates
        xls_setts.a_sh_name = str(self.sh_edit_ea.text())
        xls_setts.a_sv_sh_name = str(self.sh_edit_easv.text())
        xls_setts.b_sh_name = str(self.sh_edit_eb.text())
        xls_setts.a_l = str(self.cmb_let_ea.currentText())
        xls_setts.a_obj_l = str(self.cmb_let_ea_obj.currentText())
        xls_setts.a_sv_l = str(self.cmb_let_ea_sv.currentText())
        xls_setts.b_l = str(self.cmb_let_eb.currentText())
        xls_setts.a_n = int(self.cmb_num_ea.currentText())
        xls_setts.a_obj_n = int(self.cmb_num_ea_obj.currentText())
        xls_setts.a_sv_n = int(self.cmb_num_ea_sv.currentText())
        xls_setts.b_n = int(self.cmb_num_eb.currentText())
        xls_setts.is_xls_start = bool(self.edit_xls_start.isChecked())
        #xls_setts.is_mdb_start = bool(self.edit_mdb_start.isChecked())
        return True

    def _change_balance_setts(self):
        # self.settings.balance.include_a_balance = bool(self.edit_a_balance.isChecked())
        # self.settings.balance.include_a_sv_balance = bool(self.edit_a_sv_balance.isChecked())
        balance_settings = self.settings.balance
        balance_settings.include_b_balance = bool(self.edit_b_balance.isChecked())
        return True

    def _change_accuracy_setts(self):
        accuracy_settings = self.settings.rnd
        accuracy_settings.a_s_accuracy = int(self.edit_a_accuracy.get_current_item())
        accuracy_settings.a_sv_accuracy = int(self.edit_a_sv_accuracy.get_current_item())
        accuracy_settings.b_accuracy = int(self.edit_b_accuracy.get_current_item())
        #self.show_modal("После изменений параметров необходимо заново запустить КОНВЕРТАЦИЮ", modal_type='information')
        return True

    def _change_conditions_setts(self):
        try:
            selected_condition = list(filter(lambda x: self.selection_options_radio[x].isChecked(), self.selection_options_radio.keys()))[0]
            prev_condition = self.settings.conditions.active_cond
            self.settings.conditions.active_cond = selected_condition
        except Exception as err:
            print(err)
            QMessageBox.warning(self, titleLocales.error_modal_warning, "Invalid data selected",
                                QMessageBox.Ok)
            return
        if self.group_by_cc_activated.isChecked():
            self.settings.conditions.groupping_by = 'cc'
        # elif self.group_by_np_activated.isChecked():
        #     self.settings.conditions.groupping_by = u'np'
        else:
            self.settings.conditions.groupping_by = 'np'
        return {'active_condition_changed': selected_condition != prev_condition}

    def __change_exp_filter_settings(self,):
        filter_settings = self.settings.filter
        is_melio_selected = bool(self.melio_filter_used.isChecked())
        #settings_changed = filter_settings.enable_melio != is_melio_selected
        filter_settings.enable_melio = is_melio_selected
        return True
