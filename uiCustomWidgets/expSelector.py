__author__ = 'Alex Konkov'

from PyQt5.QtWidgets import (
    QWidget, QFrame, QGridLayout, QHBoxLayout, QLabel, QCheckBox, QRadioButton, QTreeView,
    QAbstractItemView
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from uiWidgets import Dropdown, PrimaryButton, SettingsWindow
from uiWidgets.styles import SourceWidgetStyles as Styles
from locales import titleLocales


class GroupHeader(QFrame):
    def __init__(self, parent=None, on_cmb1_changes=lambda x: x, on_cmb2_changes=lambda x: x):
        QFrame.__init__(self, parent)
        border_color = '#C3FFF1'
        self.setMaximumHeight(33)
        self.setStyleSheet(
            'background-color: #2558FF; '
            'border-radius: 4%;'
            'padding-right: 5px;'
            'padding-left: 5px')
        self.h_box = QHBoxLayout(self)
        self.first_cmb = Dropdown(self, width=180)
        self.second_cmb = Dropdown(self, width=180)
        self.first_cmb.activated.connect(on_cmb1_changes)
        self.second_cmb.activated.connect(on_cmb2_changes)
        self.second_cmb.hide()
        self.first_cmb.setStyleSheet('border-radius: 2% ; border: 1px solid ' + border_color)
        self.second_cmb.setStyleSheet('border-radius: 2% ; border: 1px solid ' + border_color)
        self.lbl = QLabel(titleLocales.group_box_title, self)
        self.lbl.setStyleSheet('color: #C3FFF1;')
        self.lbl.setAlignment(Qt.AlignCenter)
        self.h_box.addWidget(self.lbl)
        self.h_box.addWidget(self.first_cmb)
        self.h_box.addWidget(self.second_cmb)

    def change_first_cmb(self, data):
        self.first_cmb.change_data(data)

    def change_second_cmb(self, data):
        self.second_cmb.change_data(data)

    def get_first_index(self):
        return self.first_cmb.currentIndex()

    def get_second_index(self):
        return self.second_cmb.currentIndex()


class ExpFilter(QFrame):
    def __init__(self, parent=None, filter_settings=None, on_changes=lambda x: x):
        QFrame.__init__(self, parent)
        self.filter_settings = filter_settings
        self.on_changes = on_changes
        self.h_box = QHBoxLayout(self)
        self.filter_btn = PrimaryButton(self, title='...')
        self.filter_btn.clicked.connect(self.show_filter_setup)
        self.activation_switcher = QCheckBox('Фильтр', self)
        self.activation_switcher.setChecked(True)
        self.activation_switcher.stateChanged.connect(on_changes)
        self.h_box.addWidget(self.activation_switcher)
        self.h_box.addWidget(self.filter_btn)
        self.filter_window = None

    def show_filter_setup(self):
        filter_window = SettingsWindow(self, 'Настройки фильтра', 300, 150)
        melio_filter_used = QRadioButton('Вкючить фильтр по полю MELIOCODE', filter_window)
        servtype_filter_used = QRadioButton('Вкючить фильтр по полю SERVTYPE', filter_window)
        change_btn = PrimaryButton(filter_window, title='Применить фильтр')
        change_btn.clicked.connect(self.on_settings_selected)
        melio_filter_used.setChecked(self.filter_settings.enable_melio)
        servtype_filter_used.setChecked(not self.filter_settings.enable_melio)
        melio_filter_used.melio_filter_used = melio_filter_used
        filter_window.add_widget(melio_filter_used, 0, 0, 1, 2)
        filter_window.add_widget(servtype_filter_used, 1, 0, 1, 2)
        filter_window.add_widget(change_btn, 4, 3, 1, 1)
        self.filter_window = filter_window
        self.filter_window.show()

    def on_settings_selected(self):
        if self.filter_window:
            is_melio_selected = bool(self.filter_window.melio_filter_used.isChecked())
            settings_changed = self.filter_settings.enable_melio != is_melio_selected
            if settings_changed:
                self.filter_settings.enable_melio = is_melio_selected
            self.filter_window.close()
            self.on_changes(settings_changed)


not_groupped_key = 'not_groupped'


class ExpSelector(QWidget):
    def __init__(self, parent=None, settings=None, sprav=None, reinit_exp_hook=lambda x: x, handle_exp_click=lambda x: x):
        QWidget.__init__(self, parent)
        self.settings = settings
        self.sprav_holder = sprav
        self.reload_exp = reinit_exp_hook
        self.grid = QGridLayout(self)
        self.header = GroupHeader(self, on_cmb1_changes=self.handle_cmb1_click, on_cmb2_changes=self.handle_cmb2_click)
        self.filter = ExpFilter(self, filter_settings=settings.filter, on_changes=self.handle_filter_changes)
        self.treeView = QTreeView()
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tree_index_dict = {}
        self.grid.addWidget(self.header, 0, 0, 1, 15)
        self.grid.addWidget(self.filter, 0, 16, 1, 5)
        self.grid.addWidget(self.treeView, 1, 0, 21, 21)
        self.grid.setSpacing(1)
        self.current_exp_rows = []
        self.soato_titles = None
        self._exp_valuables_link = None
        self.exp_data_by_ate = None
        self.exp_data_by_soato = None
        self.cmb1_recovery = None
        self.cmb2_recovery = None
        self.groupped_soatos = None

    def handle_filter_changes(self, settings_changed=False):
        self.settings.filter.enabled = bool(self.filter.activation_switcher.isChecked())
        if settings_changed:
            self.settings.save()

    def enable(self, exp_valuables, exp_tree):
        self.show()
        self._exp_valuables_link = exp_valuables
        self.current_exp_rows = exp_valuables['rows']
        self.soato_titles = exp_valuables['soato']
        self.show_first_combo()
        self.remake_tree(exp_tree)

    def disable(self):
        self.current_exp_rows = []
        self.soato_titles = None
        self._exp_valuables_link = None
        self.exp_data_by_ate = None
        self.exp_data_by_soato = None
        self.cmb1_recovery = None
        self.cmb2_recovery = None
        self.groupped_soatos = None

    def show_first_combo(self):
        group_soatos = self.make_soato_groups()
        ate_expl_data = dict.fromkeys(list(group_soatos.keys()), None)
        for expl in self.current_exp_rows:
            try:
                ate_expl_data[expl.soato[:-3]].append(expl)
            except AttributeError:
                ate_expl_data[expl.soato[:-3]] = [expl]
            except KeyError:
                try:
                    ate_expl_data[not_groupped_key].append(expl)
                except AttributeError:
                    ate_expl_data[not_groupped_key] = [expl]
        for k, v in ate_expl_data.items():
            if v is None:
                del ate_expl_data[k]
                del group_soatos[k]
        self.exp_data_by_ate = ate_expl_data
        names = []
        for key in group_soatos:
            names.append((self.soato_titles[key + '000'], key))
        cmb1_data, self.cmb1_recovery = self._count_cmb_data_recovery(names)
        self.groupped_soatos = group_soatos
        self.header.change_first_cmb(cmb1_data)

    def show_second_combo(self, ate_soato):
        expl_data = {}
        ''''
        Далее заполняем словарь expl_data(keys: SOATO codes) экземплярами класса CtrRow
        '''
        for expl in self.current_exp_rows:
            try:
                expl_data[expl.soato].append(expl)
            except KeyError:
                expl_data[expl.soato] = [expl]
        self.exp_data_by_soato = expl_data
        ate_names = []
        for s in expl_data:
            try:
                ate_name = self.soato_titles[s]
            except KeyError:
                ate_name = '-'
            ate_names.append((ate_name, s))
        cmb2_data, self.cmb2_recovery = self._count_cmb_data_recovery(ate_names, 'Вся АТЕ', ate_kod=ate_soato)
        self.header.change_second_cmb(cmb2_data)
        self.header.second_cmb.show()

    def handle_cmb1_click(self):
        curr_ind = self.header.get_first_index()
        self.header.second_cmb.hide()
        if curr_ind != -1:
            if curr_ind == 0:
                self.current_exp_rows = self._exp_valuables_link['rows']
                self.set_shape_sum_enabled(True)
            else:
                curr_soato = self.cmb1_recovery[curr_ind]
                self.current_exp_rows = self.exp_data_by_ate[curr_soato]
                self.set_shape_sum_enabled(False)
                if self.groupped_soatos[curr_soato]:
                    self.show_second_combo(curr_soato)
            self.reload_exp(self.current_exp_rows)

    def handle_cmb2_click(self):
        curr_ind = self.header.get_second_index()
        if curr_ind != -1:
            curr_soato = self.cmb2_recovery[curr_ind]
            if curr_ind == 0:
                self.current_exp_rows = self.exp_data_by_ate[curr_soato]
            else:
                self.current_exp_rows = self.exp_data_by_soato[curr_soato]
            self.reload_exp(self.current_exp_rows)

    def set_shape_sum_enabled(self, val):
        if "options" in self._exp_valuables_link:
            self._exp_valuables_link["options"]['shape_sum_enabled'] = val

    def remake_tree(self, current_exps):
        model = QStandardItemModel()
        forms22 = current_exps.keys()
        f22_notes = self.sprav_holder.f22_notes
        tree_index_dict = {}
        for key in sorted(forms22):
            f22_item = QStandardItem(key + ' ' + f22_notes[key])
            f22_item_font = QFont()
            f22_item_font.setBold(True)
            f22_item_font.setFamily('Cursive')
            f22_item_font.setPointSize(10)
            f22_item.setFont(f22_item_font)
            model.appendRow(f22_item)
            item_names = [i.full_obj_name for i in current_exps[key]]
            index_li = []
            ch_item_count = 1
            for exp_item in sorted(item_names):
                index_li.append(item_names.index(exp_item))
                # заполняет позициями элементов до сортировки, для дальнейшего определения инстанса в data[key]
                child_item = QStandardItem('%d. ' % ch_item_count + exp_item)
                child_item.setFont(QFont('Serif', 10))
                f22_item.appendRow(child_item)
                ch_item_count += 1
            tree_index_dict[key] = index_li
        self.tree_index_dict = tree_index_dict
        model.setHorizontalHeaderLabels([titleLocales.exp_tree_header_title])
        self.treeView.setModel(model)

    def on_tree_cell_click(self, qindex):
        if qindex.parent().isValid():
            data = self.exp_a_thr.exp_tree
            pressed_f22_ind = qindex.parent().row()
            pressed_exp_ind = qindex.row()
            pressed_f22 = sorted(data.keys())[pressed_f22_ind]
            indexes_before_sort = self.tree_index_dict[pressed_f22]
            exp_index = indexes_before_sort[pressed_exp_ind]
            pressed_exp = data[pressed_f22][exp_index]
            self.handle_exp_click(pressed_exp)

    def make_soato_groups(self):
        s_kods = self.soato_titles.keys()
        soato_group = {}
        for s in s_kods:
            ate_key = s[:-3]
            if s[-3:] == '000':
                soato_group[ate_key] = []
        for s in s_kods:
            ate_key = s[:-3]
            try:
                soato_group[ate_key].append(s)
            except KeyError:
                soato_group[not_groupped_key].append(s)
        if not_groupped_key in soato_group:
            self.show_error('WARNING! \n'
                            'Данные коды не были сгруппированы %s\n'
                            'Участки с такими кодами отображены как "Не сгруппированы"'
                            % str(soato_group[not_groupped_key]))
            self.soato_titles['not_groupped'] = 'Не сгруппированы'
        return soato_group

    @staticmethod
    def _count_cmb_data_recovery(names, first_combo_row='Весь район', ate_kod=None):
        """ Input: names - list of tuples (name, soato)
            returns combo_box data , recovery dictionary to catch, which combo row was checked , max item length
        """
        if ate_kod:
            recovery_soato_d = {0: ate_kod}
        else:
            if len(names):
                recovery_soato_d = {0: names[0][1][:-3]}
            else:
                recovery_soato_d = {0: 'not found'}
        combo_data = ['* ' + first_combo_row]
        sorted_names = sorted(names)
        max_len = 0
        for i in sorted_names:
            if len(i[0]) > max_len:
                max_len = len(i[0])
            combo_data.append(i[0])
            recovery_soato_d[sorted_names.index(i)+1] = i[1]
        return combo_data, recovery_soato_d
