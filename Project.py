#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Aleksei Konkov'

import time
import sys
import os.path
import cPickle as Pickle

from PyQt4 import QtGui, QtCore

from Packages import Control, Convert, ExpA, FormB, Sprav
from Packages.Exports import ToXL, ToMdb, Balance
from Packages.Titles import LoadMessg, WidgNames, Events, ToolTip, ErrMessage
from Packages.Settings import Settings

Expl = 2
project_dir = os.getcwd()
spr_dir = os.path.join(project_dir, 'Spr')
spr_default_path = os.path.join(spr_dir, 'DefaultSpr.pkl')
tempDB_path = os.path.join(spr_dir, 'tempDbase.mdb')
xls_templates_dir = os.path.join(spr_dir, 'xls_forms')
templ_db_path = os.path.join(spr_dir, 'template.mdb')

def rm_temp_db(file_rm = tempDB_path):
    if os.path.isfile(file_rm):
        os.remove(file_rm)

class MainActiveThread(QtCore.QThread):
    def __init__(self, parent = None):
        super(MainActiveThread, self).__init__(parent)
        self.s_h = Sprav.SpravHolder()
        self.current_sprav_dict = None
        self.__op = None
        self.__file_path = None
        self.spr_path_info = None
        self.settings_dict = None
        self.__args = []

    def change_op(self, file_path, num_op, args):
        """
        :param file_path:
        :param num_op: int num of sprav menu exits
        :param args: if need
        """
        self.__op = num_op
        if file_path:
            self.__file_path = file_path
        self.__args = args

    def update_settings_dict(self, settings_dict):
        self.settings_dict = settings_dict

    def run(self):
        """
        You should call change_op before thread starts
        """
        if self.__op == 0:
            self.load_work_db()
        elif self.__op in [1,2]:      #loading .pkl sprav
            self.load_pkl_op1_2()
        elif self.__op == 3:        # loading .mdb sprav
            self.load_mdb_op3()
        elif self.__op == 4:        # saving .mdb sprav
            self.save_pkl_op4()
        elif self.__op == 5:
            self.load_work_pkl()
        elif self.__op == 6:
            self.save_work_pkl()
        else:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), u'Operation not found')

    def load_work_pkl(self):
        try:
            with open(self.__file_path, 'rb') as inp:
                exp_data = Pickle.load(inp)
                inp.close()
            loading_password = exp_data.pop()
        except Exception as err:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), ErrMessage.wrong_session+err.message)
        else:
            if loading_password == u'Salt':
                self.emit(QtCore.SIGNAL(u'session_loaded(PyQt_PyObject)'), exp_data)
            else:
                self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), ErrMessage.wrong_session)

    def save_work_pkl(self):
        try:
            with open(self.__file_path,u'wb') as output:
                Pickle.dump(self.__args[0], output, 2)
            self.__args = []
            self.emit(QtCore.SIGNAL(u'successfully_saved(const QString&)'), Events.session_saved % self.__file_path)
        except:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), ErrMessage.bad_session)

    def load_work_db(self):
        message = self.pre_control()
        if message:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), message)
        else:
            self.emit(QtCore.SIGNAL(u'db_file_opened()'))

    def pre_control(self):
        try:
            contr = Control.CtrControl(self.__file_path, tempDB_path)
            # if not contr.can_connect():
            #     return ErrMessage.no_db_conn % self.__file_path
            failed_table = contr.contr_tables()
            if failed_table:
                failed_table = ', '.join(failed_table)
                return ErrMessage.empty_tables%failed_table
            failed_table = contr.is_tables_empty()
            if failed_table:
                failed_table = ', '.join(failed_table)
                return ErrMessage.empty_table_data % failed_table
            failed_fields = contr.contr_field_types()
            if failed_fields:
                for tab, fields in failed_fields.items():
                    msg= ErrMessage.lost_fields(tab, fields)
                    self.emit(QtCore.SIGNAL(u'control_warning(const QString&)'), msg)
                return ErrMessage.field_control_failed
            empty_pref_ids = contr.is_empty_f_pref()
            if empty_pref_ids:
                self.emit(QtCore.SIGNAL(u'control_warning(const QString&)'), ErrMessage.warning_no_pref % unicode(empty_pref_ids))
            return False
        except Exception as err:
            return err.message


    def set_spr_changes(self, change_di):
        if self.s_h.set_parameters(change_di):
            self.current_sprav_dict = change_di
            if self.__op == 1:
                self.spr_path_info = u'Default'
            else:
                self.spr_path_info = self.__file_path
            self.emit(QtCore.SIGNAL(u'sprav_holder(PyQt_PyObject)'), self.s_h)
        else:
            if self.current_sprav_dict:
                self.s_h.set_parameters(self.current_sprav_dict)
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.sh_not_changed)
            else:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_wrong_default)

    def set_settings_changes(self, loaded_settings):
        self.emit(QtCore.SIGNAL(u'new_settings_loaded(PyQt_PyObject)'), loaded_settings)

    def load_pkl_op1_2(self):
        try:
            with open(self.__file_path, 'rb') as inp:
                loaded_data = Pickle.load(inp)
                inp.close()
            loading_password = loaded_data[-1]
            if loading_password == u'Sprav':
                self.set_spr_changes(loaded_data[0])
                self.set_settings_changes(loaded_data[1])
            else:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_not_valid)
        except IOError:
            if self.__op == 1:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_default_io_error)
            else:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_io_error)
        except:
            #TODO: rename error message and add exceptions
            self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_err_in_data)


    def load_mdb_op3(self):
        if self.control_spr_db():
            try:
                sprav_data = self.s_h.get_data_from_db(self.__file_path)
                sprav_data[u"create_time"] = time.strftime(u"%H:%M__%d.%m.%Y")
                self.set_spr_changes(sprav_data)
            except Sprav.SpravError as err:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), unicode(err.message))

    def save_pkl_op4(self):
        if self.__file_path:
            if self.__file_path[-4:] != u'.pkl':
                self.__file_path+= u'.pkl'
            try:
                with open(self.__file_path,u'wb') as output:
                    Pickle.dump([self.current_sprav_dict, self.settings_dict, u"Sprav"], output, 2)
                    self.emit(QtCore.SIGNAL(u'successfully_saved(const QString&)'), Events.spr_saved)
            except:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_not_saved)


    def control_spr_db(self, full=True):
        sprav_contr = Sprav.SprControl(self.__file_path, full)
        if not sprav_contr.is_connected:
            self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.no_db_conn % self.__file_path)
            return False
        bad_tbls = sprav_contr.contr_tables()
        if bad_tbls:
            self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.empty_spr_tabs(bad_tbls))
            return False
        bad_fields = sprav_contr.contr_field_types()
        if bad_fields:
            msg = u''
            for tbl, fails in bad_fields.items():
                msg += u'\n%s' % ErrMessage.lost_fields(tbl, fails)
            self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), msg)
            return False
        else:
            #TODO: call exp structure control here. {f_num : not Null; Expa_f_str.f_num : LandCodes.NumberGRAF WHERE f_num is NUll
            return True


class ControlThread(QtCore.QThread):
    def __init__(self, sprav, db_path, parent = None):
        super(ControlThread, self).__init__(parent)
        self.db_file = db_path
        self.sprav_holder = sprav

    def run(self):
        contr = Control.DataControl(self.sprav_holder, self.db_file, tempDB_path)
        try:
            err_li = contr.run_field_control()
        except Exception as Err:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), Err.message)
        else:
            if err_li:
                self.emit(QtCore.SIGNAL(u'contr_failed(PyQt_PyObject)'), err_li)
            else:
                self.emit(QtCore.SIGNAL(u'control_passed()'))

class ConvertThread(QtCore.QThread):

    def __init__(self, sprav, settings, parent = None):
        super(ConvertThread, self).__init__(parent)
        self.conditions_settings = settings.conditions
        self.sprav_holder = sprav


    def run(self):
        try:
            converted_data = Convert.convert(self.sprav_holder, tempDB_path, self.conditions_settings)
        except Exception as err:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), err.message)
        else:
            if isinstance(converted_data, dict):
                self.emit(QtCore.SIGNAL(u'conv_failed(PyQt_PyObject)'), converted_data)
            elif isinstance(converted_data, list):
                self.emit(QtCore.SIGNAL(u'convert_passed(PyQt_PyObject)'), converted_data)
            else:
                self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), ErrMessage.empty_crostab)


class ExpAThread(QtCore.QThread):
    def __init__(self, e_db_f, rows, sprav_holder, settings, parent = None):
        super(ExpAThread, self).__init__(parent)
        self.exp_db_file = e_db_f
        self.expsA = ExpA.ExpFA(rows, sprav_holder)
        self.exp_tree = self.expsA.make_exp_tree()
        self.rnd_settings = settings.rnd
        self.xl_settings = settings.xls
        self.balance_settings = settings.balance
        self.sprav_holder = sprav_holder
        self.__out_to_xl = True
        self.__single_exp = None
        self.__args = []

    def run_single_exp(self, selected_exp, *dop_args):
        self.__single_exp = selected_exp
        self.__args = dop_args
        self.start()

    def set_xl_output(self, is_xls):
        self.__out_to_xl = is_xls

    def get_sv_data(self):
        sv_data = self.expsA.calc_all_exps(self.rnd_settings)
        errs_occured = self.expsA.errors_occured
        if errs_occured:
            for key in errs_occured:
                msg = ErrMessage.expa_errors[key] % errs_occured[key]
                self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), msg)
            if self.isRunning():
                self.quit()
        else:
            return sv_data

    def do_s_balance(self, e_dict):
        Balance.run_as_balancer(e_dict, self.sprav_holder.expa_f_str, self.sprav_holder.expa_r_str)



    def do_sv_balance(self, e_dict):
        Balance.run_asv_balancer(e_dict, self.sprav_holder.expa_f_str, self.sprav_holder.expa_r_str)

    def run(self):
        if self.__single_exp:
            self.__single_exp.add_data(self.sprav_holder)
            counted_exp = self.__single_exp.round_expl_data(self.rnd_settings)
            if self.balance_settings.include_a_balance:
                self.do_s_balance(counted_exp)
            matrix = self.prepare_s_matr(counted_exp)
            self.export_s_to_xl(matrix[1:])
            self.__single_exp = None
        else:
            sv_data = self.get_sv_data()
            if self.balance_settings.include_a_sv_balance:
                self.do_sv_balance(sv_data)
            matrix = self.prepare_sv_matr(sv_data)
            if self.__out_to_xl:
                self.export_sv_to_xl(matrix)
            else:
                self.export_to_mdb(matrix)

    def prepare_s_matr(self, s_dict):
        """
        Caution! The first row contains field Names in order to export!
        :return : list, matrix to export
        """
        f_at_order = self.sprav_holder.str_orders['a_f']
        matr = [f_at_order,]
        for row in self.sprav_holder.str_orders['a_r']:
            digits =  map(lambda x: s_dict[row][x]['val'], f_at_order)
            matr.append(digits)
        return matr

    def prepare_sv_matr(self, sv_dict):
        """
        Caution! The first row contains field Names in order to export!
        :return : tuple, matrix to export
        """
        f_orders = self.sprav_holder.str_orders['sv_f']
        r_order_base = sv_dict['texts']
        matr = []

        self.n = 1
        def push_to_matr(first, second, remain, skip_num = False):
            row = []
            if self.__out_to_xl:
                row = [self.n, ]
                if skip_num:
                    row = ['', ]
                else:
                    self.n+=1
            row.extend([first, second])
            row.extend(remain)
            matr.append(row)

        push_to_matr(u'F22_id', u'description', f_orders, True)
        for f22_key in sorted(r_order_base.keys()):
            if self.__out_to_xl:
                push_to_matr('','', ['', ] * (len(f_orders)+2), True)
                push_to_matr(f22_key, self.sprav_holder.f22_notes[f22_key], ['',]*len(f_orders), True)

            vals_keys = map(lambda (x, y): (y, x), r_order_base[f22_key].items())
            n = 1
            for row_name, row_key in sorted(vals_keys):
                digits = map(lambda x: sv_dict[f22_key][row_key][x]['val'], f_orders)
                push_to_matr('%s.%d' % (f22_key, n), row_name, digits)
                n+=1
            digits = map(lambda x: sv_dict[f22_key]['total'][x]['val'], f_orders)
            push_to_matr(f22_key+u'*', u'Итого:', digits)
        # добавление итоговой строки total
        digits = map(lambda x: sv_dict['total'][x]['val'], f_orders)
        push_to_matr(u'**', u'Всего:', digits)
        # добовление информационной строки Shape_area
        digits = map(lambda x: sv_dict['sh_sum'][x]['val'], f_orders)
        push_to_matr(u'***', u'Shape_Area (для сравнения):', digits)
        del self.n
        return matr

    def export_s_to_xl(self, matrix):
        try:
            ToXL.exp_single_fa(matrix, self.__args[0], self.__single_exp.obj_name, self.exp_db_file, **self.xl_settings.__dict__)
        except ToXL.XlsIOError as err:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), ErrMessage.xl_io_error[err.err_type](err.file_name))
        else:
            self.emit(QtCore.SIGNAL(u'exp_s_success()'))

    def export_sv_to_xl(self, matrix):
        exl_file_name = u'fA_%s_%s.xlsx' % (os.path.basename(self.exp_db_file)[4:-4],time.strftime(u"%d-%m-%Y"))
        exl_file_path = os.path.join(os.path.dirname(self.exp_db_file), exl_file_name)
        xl_s = self.xl_settings
        try:
            ToXL.exp_matrix(matrix, save_as = exl_file_path, start_f = xl_s.a_sv_l, start_r = xl_s.a_sv_n, sh_name = xl_s.a_sv_sh_name, is_xls_start= xl_s.is_xls_start, templ_path = xl_s.a_sv_path)
        except ToXL.XlsIOError as err:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), ErrMessage.xl_io_error[err.err_type](err.file_name))
        else:
            self.emit(QtCore.SIGNAL(u'exp_sv_success()'))

    def export_to_mdb(self, matrix):
        fields = ['f_'+f for f in matrix[0]]
        t_name = u'ExpA_%s' % time.strftime(u"%d\%m\%Y_%H:%M")
        f_str = {fields[0]: 'TEXT(8)', fields[1]: 'TEXT(150)'}
        for f in fields[2:]:
            f_str[f] = 'DOUBLE NULL'
        try:
            export_db = ToMdb.DbExporter(self.exp_db_file, templ_db_path)
            export_db.create_table(t_name, f_str, fields)
            export_db.run_export(t_name, matrix[1:], fields)
        except Exception as err:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), err.message)
        else:
            self.emit(QtCore.SIGNAL(u'exp_sv_success()'))
            if self.xl_settings.is_mdb_start:
                export_db.run_db()

class ExpBThread(QtCore.QThread):
    def __init__(self, edbf, rows, sprav, settings, parent = None):
        super(ExpBThread, self).__init__(parent)
        self.sprav = sprav
        self.exp_file = edbf
        self.rows = rows
        self.out_xl_mode = True
        self.xl_settings = settings.xls
        self.round_settings = settings.rnd
        self.balance_settings = settings.balance
        self.got_result = None

    def set_output_mode(self, is_xls):
        self.out_xl_mode = is_xls

    def prepare_b_matr(self, b_dict):
        """
        Caution! The first row contains field Names in order to export!
        :return : tuple, matrix to export
        """
        f_orders = self.sprav.str_orders['b_f']
        r_orders = self.sprav.str_orders['b_r']
        matr = []
        def push_to_matr(first, second, remain):
            row = [first, second]
            row.extend(remain)
            matr.append(row)
        push_to_matr(u'F22', u'description', f_orders)
        for r_key in r_orders:
            digits = map(lambda x: b_dict[r_key][x]['val'], f_orders)
            push_to_matr(r_key, self.sprav.expb_r_str[r_key]['r_name'], digits)

        digits = map(lambda x: b_dict['by_SHAPE'][x]['val'], f_orders)
        push_to_matr('Total', 'By_Shape', digits)
        return matr

    def do_balance(self, e_dict):
        if self.balance_settings.include_b_balance:
            Balance.run_b_balancer(e_dict, self.sprav.expb_f_str, self.sprav.expb_r_str, self.round_settings.b_accuracy)

    def run(self):
        if not self.got_result:
            expB = FormB.ExpFormaB(self.rows, self.sprav)
            exp_dict = expB.create_exp_dict(self.round_settings)
        else:
            exp_dict = self.got_result
        # if self.round_settings['balance']:
        self.do_balance(exp_dict)
        exp_matr = self.prepare_b_matr(exp_dict)
        if self.out_xl_mode:
            self.run_xl_export(exp_matr)
        else:
            self.run_mdb_export(exp_matr)

    def run_xl_export(self, fb_matr):
        exl_file_name = u'fB_%s_%s.xlsx' % (os.path.basename(self.exp_file)[4:-4],time.strftime(u"%d-%m-%Y"))
        exl_file_path = os.path.join(os.path.dirname(self.exp_file), exl_file_name)
        xls = self.xl_settings
        try:
            ToXL.exp_matrix(fb_matr, save_as = exl_file_path, start_f = xls.b_l, start_r = xls.b_n, sh_name = xls.b_sh_name, is_xls_start = xls.is_xls_start, templ_path = xls.b_path)
        except ToXL.XlsIOError as err:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), ErrMessage.xl_io_error[err.err_type](err.file_name))
        else:
            self.emit(QtCore.SIGNAL(u'success()'))

    def run_mdb_export(self, fb_matr):
        fields = ['f_'+f for f in fb_matr[0]]
        t_name = u'ExpB_%s' % time.strftime(u"%d\%m\%Y_%H:%M")
        f_str = {fields[0]: 'TEXT(8)', fields[1]: 'TEXT(150)'}
        for f in fields[2:]:
            f_str[f] = 'DOUBLE NULL'
        try:
            export_db = ToMdb.DbExporter(self.exp_file, templ_db_path)
            export_db.create_table(t_name, f_str, fields)
            export_db.run_export(t_name, fb_matr[1:], fields)
        except Exception as err:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), err.message)
        else:
            self.emit(QtCore.SIGNAL(u'success()'))
            if self.xl_settings.is_mdb_start:
                export_db.run_db()


class LoadingThread(QtCore.QThread):
    def __init__(self, parent = None):
        super(LoadingThread, self).__init__(parent)

    def run(self):
        dots = [u' ',]*5
        count = 0
        is_dot = True
        while True:
            if count == len(dots):
                count = 0
                is_dot = not is_dot
            self.emit(QtCore.SIGNAL(u's_loading(const QString&)'), u' '.join(dots))
            self.msleep(700)
            if is_dot:  dots[count] = u'.'
            else:       dots[count] = u' '
            count+=1

class SettingsWindow(QtGui.QMainWindow):
    def __init__(self, parent = None, title = u'', width = 710, height = 450):
        super(SettingsWindow, self).__init__(parent)
        self.setWindowTitle(title)
        self.resize(width, height)
        self.main_frame = QtGui.QFrame(self)
        self.main_layout = QtGui.QGridLayout(self.main_frame)
        self.main_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.main_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.setCentralWidget(self.main_frame)
        self.colored_blocks = {}

    def add_widget(self, widget, *args):
        self.main_layout.addWidget(widget, *args)

class ColoredBlock(QtGui.QFrame):
    def __init__(self, block_name = '', color = '#01A6D3', parent = None, ):
        super(ColoredBlock, self).__init__(parent)
        self.box = QtGui.QGridLayout(self)
        self.setLayout(self.box)
        self.name_lbl = QtGui.QLabel(block_name, self)
        self.box.addWidget(self.name_lbl, 0,0,1,3)
        self.setStyleSheet(u'background-color: %s; color: white; border-radius: 13;'%color)

    def add_widget(self, widget, *args):
        if args:
            args = list(args)
            args[0] +=1
        self.box.addWidget(widget, *args)





# class SettingsDeprecated(object):
#     def __init__(self):
#
#
#         self.__xls_default = {
#             'a_sv_l':u'A',
#             'a_sv_n':6,
#             'a_l':u'F',
#             'a_n':16,
#             'a_obj_l':u'M',
#             'a_obj_n':4,
#             'b_l':u'B',
#             'b_n':7,
#             'a_path': u'%s\\FA.xlsx' % xls_templates_dir,
#             'a_sv_path': u'%s\\FA_svod.xlsx' % xls_templates_dir,
#             'b_path': u'%s\\FB.xlsx' % xls_templates_dir,
#             'a_sh_name': u'RB экспликация А',
#             'a_sv_sh_name': u'Активный',
#             'b_sh_name': u'Активный',   #RB Форма22 зем.
#         }
#         self.__round_default = {
#             'a_s_accuracy': 4,
#             'b_accuracy': 0,
#             'small_accur': 3,
#             'a_sv_accuracy': 4,
#             'show_small': True
#         }
#         self.set_xls(self.__xls_default)
#         self.set_round(self.__round_default)
#
#     @property
#     def xls(self):
#         return self.__xls
#     @property
#     def rnd(self):
#         return self.__round
#
#     def set_xls(self, new_setts):
#         if len(new_setts) == len(set(new_setts.keys()+self.__xls_default.keys())):
#             self.__xls = new_setts
#         else:
#             self.__xls = self.__xls_default
#             raise Exception(u'Not enough settings')
#
#     def set_round(self, new_rnd_setts):
#         if len(new_rnd_setts) == len(set(new_rnd_setts.keys()+self.__round_default.keys())):
#             self.__round = new_rnd_setts
#         else:
#             self.__round = self.__round_default
#             raise Exception(u'Not enough settings')


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle(WidgNames.main_name)
        self.resize(1300, 640)
        self.central_widget = QtGui.QFrame(self)
        self.central_widget.setFrameShape(QtGui.QFrame.StyledPanel)
        self.central_widget.setFrameShadow(QtGui.QFrame.Raised)
        self.gridLayout = QtGui.QGridLayout(self.central_widget)
        self.l1 = QtGui.QLabel(WidgNames.l1_title,self.central_widget)
        self.l2 = QtGui.QLabel(WidgNames.l2_title,self.central_widget)
        self.l3 = QtGui.QLabel(WidgNames.l3_title,self.central_widget)
        self.l4 = QtGui.QLabel(WidgNames.l4_title,self.central_widget)
        self.sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.control_btn = QtGui.QPushButton(WidgNames.btn_control,self.central_widget)
        self.control_btn.setToolTip(ToolTip.btn_control)
        self.control_btn.setSizePolicy(self.sizePolicy)
        self.convert_btn = QtGui.QPushButton(WidgNames.btn_control,self.central_widget)
        self.convert_btn.setToolTip(ToolTip.btn_convert)
        self.convert_btn.setSizePolicy(self.sizePolicy)
        self.exp_a_btn = QtGui.QPushButton(WidgNames.btn_exp,self.central_widget)
        self.exp_a_btn.setToolTip(ToolTip.btn_exp_a)
        self.exp_a_btn.setSizePolicy(self.sizePolicy)
        self.btn_a_all = QtGui.QPushButton(WidgNames.btn_a_sv,self.central_widget)
        self.btn_a_all.setToolTip(ToolTip.btn_a_sv)
        self.btn_a_tree = QtGui.QPushButton(WidgNames.btn_a_ch,self.central_widget)
        self.btn_a_tree.setToolTip(ToolTip.btn_a_ch)
        self.btn_a_tree.setSizePolicy(self.sizePolicy)
        self.btn_a_all.setSizePolicy(self.sizePolicy)
        self.btn_a_all.setHidden(True)
        self.btn_a_tree.setHidden(True)
        self.exp_b_btn = QtGui.QPushButton(WidgNames.btn_exp,self.central_widget)
        self.exp_b_btn.setToolTip(ToolTip.btn_exp_b)
        self.exp_b_btn.setSizePolicy(self.sizePolicy)
        self.event_table = TableWidget(WidgNames.event_table_head, self.central_widget)
        self.event_table.show()
        self.event_table.table.set_event_ss()
        self.control_table = TableWidget(WidgNames.control_table_head, self.central_widget)
        self.convert_table = TableWidget(WidgNames.convert_table_head, self.central_widget)
        self.treeView = QtGui.QTreeView()
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.treeView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.treeView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.treeView.setHidden(True)
        self.group_box = GroupBox(self)
        self.group_box.hide()
        self.expa_widget = QtGui.QWidget(self)
        self.expa_box = QtGui.QGridLayout(self.expa_widget)

        # self.setStyleSheet(u'background-color: #959BA8; border-radius: 15%;')
        self.filter_frame = QtGui.QFrame(self)
        self.filter_frame.setHidden(True)
        self.filter_box = QtGui.QHBoxLayout(self.filter_frame)
        self.filter_btn = QtGui.QToolButton(self)
        self.filter_btn.setText(u'...')
        self.filter_btn.setAutoRaise(True)
        self.filter_btn.setStyleSheet(u'color: white; background-color: #2558FF; border-radius: 8%; border: 1px solid white')

        self.filter_activation = QtGui.QCheckBox(u'Фильтр', self)
        self.filter_activation.setChecked(True)

        self.filter_activation.setFont(QtGui.QFont('Segoe Print', 9))
        self.filter_activation.stateChanged.connect( lambda x: self.filter_changed())
        # self.lbl.setAlignment(QtCore.Qt.AlignRight)
        self.filter_box.addWidget(self.filter_activation)
        self.filter_box.addWidget(self.filter_btn)


        self.expa_box.addWidget(self.filter_frame, 0, 0, 1, 5)
        self.expa_box.addWidget(self.treeView,1,0,21,21)
        self.expa_box.addWidget(self.group_box,0,5,1,16)

        self.splitter = QtGui.QSplitter(self)
        self.splitter.addWidget(self.expa_widget)
        self.splitter.addWidget(self.control_table)
        self.splitter.addWidget(self.convert_table)
        self.splitter.addWidget(self.event_table)
        self.tree_text_widg = QtGui.QWidget()
        self.tree_text_box = QtGui.QHBoxLayout(self.tree_text_widg)
        self.tree_text_box.addWidget(self.splitter)

        self.gridLayout.addWidget(self.l1, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.l2, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.l3, 4, 0, 1, 1)
        self.gridLayout.addWidget(self.l4, 7, 0, 1, 1)
        self.gridLayout.addWidget(self.control_btn, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.convert_btn, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.exp_a_btn, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.btn_a_tree,  4, 1, 1, 1)
        self.gridLayout.addWidget(self.btn_a_all,  5, 1, 1, 1)
        self.gridLayout.addWidget(self.exp_b_btn, 7, 1, 1, 1)
        self.gridLayout.addWidget(self.tree_text_widg, 0, 2, 15, 11)
        # self.clearbutton.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Minimum)
        self.setWindowIcon(QtGui.QIcon(u'%s\\Images\\exp.png' % project_dir))
        self.setCentralWidget(self.central_widget)
        self.setFocus()
        self.set_menu_properties()
        self.hide_props()
        self.sprav_holder = None
        self.bold_font = QtGui.QFont()
        self.normal_font = QtGui.QFont()
        self.set_fonts_properties()
        self.set_widgets_font()
        self.set_sources_widgets()
        self.__is_session = False
        self.init_data_params()
        self.load_thr = LoadingThread()
        self.db_file = None
        self.main_load_save_thr = MainActiveThread()
        self._load_message = ''
        def set_status(dots):
            mes = self._load_message+dots
            self.statusBar().showMessage(mes)
        self.__is_xls_mode = True
        self._not_filtered_data = []
        # self.settings = SettingsDeprecated()
        self.settings = Settings(xls_templates_dir, spr_default_path)

        self.connect(self.control_btn, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"click_control_btn()"))
        self.connect(self.convert_btn, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"click_convert_btn()"))
        self.connect(self.exp_a_btn, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"click_exp_a_btn()"))
        self.connect(self.btn_a_all, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"click_a_svodn_btn()"))
        self.connect(self.btn_a_tree, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"click_a_tree_btn()"))
        self.connect(self.exp_b_btn, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"click_exp_b_btn()"))
        self.connect(self.filter_btn, QtCore.SIGNAL(u"clicked()"), self.show_filtering_window)

        self.connect(self.load_thr, QtCore.SIGNAL(u's_loading(const QString&)'), set_status)
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'sprav_holder(PyQt_PyObject)'), self.set_sprav_holder)
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'new_settings_loaded(PyQt_PyObject)'), self.settings_loaded)
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'spr_error_occured(const QString&)'), self.show_sprav_error)
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), self.load_save_db_err)
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'control_warning(const QString&)'), self.show_error)
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'successfully_saved(const QString&)'), self.say_saved)
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'session_loaded(PyQt_PyObject)'), self.session_loaded)
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'db_file_opened()'), self.db_file_opened)
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'finished()'), self.stop_loading)
        self.connect(self.treeView, QtCore.SIGNAL(u"activated(const QModelIndex &)"),self.click_tree_cell)
        self.connect(self.group_box.first_cmb, QtCore.SIGNAL(u'currentIndexChanged (const QString&)'), self.first_combo_changed)
        self.connect(self.group_box.second_cmb, QtCore.SIGNAL(u'currentIndexChanged (const QString&)'), self.second_combo_changed)

        self.show()
        self.run_main_thr()
        try:
            self.setStyleSheet((open(u'%s\\Style\\ss.css' % project_dir).read()))
        except IOError:
            self.show_warning(ErrMessage.no_css)

    def reset_params(self):
        # self.__a_thr_reset = False
        # if not self.__is_session:
        del self.e_db_file, \
            self.explication_data, \
            self.current_exp_data,\
            self.ate_expl_data_dict,\
            self.control_thr, \
            self.convert_thr, \
            self.exp_a_thr, \
            self.exp_b_thr
        self.init_data_params()

    def init_data_params(self):
        self.e_db_file = None
        self.explication_data = None
        self.current_exp_data = None
        self.ate_expl_data_dict = None
        self.control_thr = None
        self.convert_thr = None
        self.exp_a_thr = None
        self.exp_b_thr = None

    def reset_parameters(self):
        self.hide_props(False)
        self.btn_a_all.hide()
        self.btn_a_tree.hide()
        self.treeView.hide()
        self.treeView.reset()
        self.control_btn.setDisabled(self.__is_session)
        self.convert_btn.setDisabled(True)            # !!! Here you can enable or disable convert button
        self.exp_a_btn.setEnabled(self.__is_session)
        self.exp_b_btn.setEnabled(self.__is_session)
        self.filter_frame.setHidden(not self.__is_session)
        self.export_frame.hide()
        self.save_widget.hide()
        self.src_widget.set_lbl_text(self.db_file)
        self.group_box.setHidden(True)
        self.group_box.first_cmb.clear()
        self.group_box.second_cmb.clear()
        # self.src_widget.lbl.repaint()

    def set_sources_widgets(self):
        self.export_frame = ExportFrame()
        self.src_widget = SrcFrame()
        self.gridLayout.addWidget(self.src_widget, 0,0,1,2)
        self.src_widget.set_lbl_text(WidgNames.src_widg)
        self.export_frame.hide()
        self.gridLayout.addWidget(self.export_frame, 9,0,1,2)
        self.save_widget = SrcFrame(u'#9556FF')
        self.save_widget.set_lbl_text(WidgNames.save_widg)
        self.save_widget.hide()
        self.gridLayout.addWidget(self.save_widget, 10,0,1,2)
        self.connect(self.export_frame.rbtn_mdb, QtCore.SIGNAL(u'clicked()'), self.set_mdb_mode)
        self.connect(self.export_frame.rbtn_xls, QtCore.SIGNAL(u'clicked()'), self.set_xls_mode)
        self.connect(self.src_widget.btn, QtCore.SIGNAL(u'clicked()'), self.open_file)
        self.connect(self.export_frame.e_src_widget.btn, QtCore.SIGNAL(u'clicked()'), self.change_edb_file)
        self.connect(self.save_widget.btn, QtCore.SIGNAL(u'clicked()'), self.save_session)

    def set_widgets_font(self):
        self.l1.setFont(self.normal_font)
        self.l2.setFont(self.normal_font)
        self.l3.setFont(self.normal_font)
        self.l4.setFont(self.normal_font)
        self.btn_a_tree.setFont(self.bold_font)
        self.btn_a_all.setFont(self.bold_font)
        self.control_btn.setFont(self.bold_font)
        self.convert_btn.setFont(self.bold_font)
        self.exp_a_btn.setFont(self.bold_font)
        self.exp_b_btn.setFont(self.bold_font)

    def set_fonts_properties(self):
        self.normal_font.setPointSize(10)
        self.bold_font.setPointSize(10)
        self.bold_font.setBold(True)
        self.normal_font.setFamily(u'Dutch801 XBd Bt')       #'Narkisim',
        self.bold_font.setFamily(u'Times New Roman')

    def hide_props(self, hide = True):
        self.l1.setHidden(hide)
        self.l2.setHidden(hide)
        self.l3.setHidden(hide)
        self.l4.setHidden(hide)
        self.control_btn.setHidden(hide)
        self.convert_btn.setHidden(hide)
        self.exp_a_btn.setHidden(hide)
        self.exp_b_btn.setHidden(hide)
        # self.filter_frame.setHidden(hide)


    def block_btns(self, blocked = True):
        self.control_btn.blockSignals(blocked)
        self.convert_btn.blockSignals(blocked)
        self.exp_a_btn.blockSignals(blocked)
        self.exp_b_btn.blockSignals(blocked)
        self.filter_frame.blockSignals(blocked)
        self.btn_a_all.blockSignals(blocked)
        self.treeView.blockSignals(blocked)
        self.group_box.setDisabled(blocked)
        self.src_widget.setDisabled(blocked)
        self.export_frame.setDisabled(blocked)
        self.save_widget.setDisabled(blocked)

    def set_menu_properties(self):
        main_exit1 = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\db.png' % project_dir), WidgNames.exit_main_1, self)
        main_exit2 = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\stop1.png' % project_dir), WidgNames.exit_main_2, self)
        main_exit1.setShortcut(u'Ctrl+O')
        main_exit1.setStatusTip(ToolTip.exit_main_1)
        main_exit2.setShortcut(u'Ctrl+Q')
        main_exit2.setStatusTip(ToolTip.exit_main_2)

        spr_default = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\refresh.png' % project_dir), WidgNames.exit_spr_1, self)
        spr_choose_pkl = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\refresh.png' % project_dir), WidgNames.exit_spr_2, self)
        spr_choose_mdb = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\refresh.png' % project_dir), WidgNames.exit_spr_3, self)
        spr_save_spr = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\save.png' % project_dir), WidgNames.exit_spr_4, self)
        spr_info = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\info.ico' % project_dir), WidgNames.exit_spr_5, self)
        spr_default.setStatusTip(ToolTip.exit_spr_1)
        spr_choose_pkl.setStatusTip(ToolTip.exit_spr_2)
        spr_choose_mdb.setStatusTip(ToolTip.exit_spr_3)
        spr_save_spr.setStatusTip(ToolTip.exit_spr_4)
        spr_info.setStatusTip(ToolTip.exit_spr_5)

        spr_default.setShortcut(u'Ctrl+D')
        spr_choose_pkl.setShortcut(u'Ctrl+P')
        spr_choose_mdb.setShortcut(u'Ctrl+M')
        spr_save_spr.setShortcut(u'Ctrl+S')
        spr_info.setShortcut(u'Ctrl+I')

        settings_xls = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\excel.ico' % project_dir), WidgNames.exit_settings_1, self)
        settings_xls.setStatusTip(ToolTip.settings_xls)
        settings_xls.setShortcut(u'Ctrl+E')
        settings_balance = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\excel.ico' % project_dir), WidgNames.exit_settings_2, self)
        settings_balance.setStatusTip(ToolTip.settings_balance)
        settings_balance.setShortcut(u'Ctrl+B')
        settings_accuracy= QtGui.QAction(QtGui.QIcon(u'%s\\Images\\excel.ico' % project_dir), WidgNames.exit_settings_3, self)
        settings_accuracy.setStatusTip(ToolTip.settings_accuracy)
        settings_accuracy.setShortcut(u'Ctrl+N')
        settings_conditions = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\excel.ico' % project_dir), WidgNames.exit_settings_4, self)
        settings_conditions.setStatusTip(ToolTip.settings_conditions)
        settings_conditions.setShortcut(u'Ctrl+G')

        self.connect(main_exit2, QtCore.SIGNAL(u'triggered()'), QtGui.qApp, QtCore.SLOT(u'quit()'))
        self.connect(main_exit1, QtCore.SIGNAL(u'triggered()'), self.open_file)

        self.connect(spr_default, QtCore.SIGNAL(u'triggered()'), self.run_main_thr)
        self.connect(spr_choose_pkl, QtCore.SIGNAL(u'triggered()'), lambda: self.load_sprav(True))
        self.connect(spr_choose_mdb, QtCore.SIGNAL(u'triggered()'), self.load_sprav)
        self.connect(spr_save_spr, QtCore.SIGNAL(u'triggered()'), self.save_sprav)
        self.connect(spr_info, QtCore.SIGNAL(u'triggered()'), self.show_spr_info)

        self.connect(settings_xls, QtCore.SIGNAL(u'triggered()'), self.show_xl_settings_window)
        self.connect(settings_balance, QtCore.SIGNAL(u'triggered()'), self.show_balance_settings_window)
        self.connect(settings_accuracy, QtCore.SIGNAL(u'triggered()'), self.show_accuracy_settings_window)
        self.connect(settings_conditions, QtCore.SIGNAL(u'triggered()'), self.show_conditions_settings_window)

        menu = self.menuBar()
        menu_file = menu.addMenu(WidgNames.menu_1)
        menu_sprav = menu.addMenu(WidgNames.menu_2)
        menu_settings = menu.addMenu(WidgNames.menu_3)
        menu_file.addAction(main_exit1)
        menu_file.addAction(main_exit2)
        menu_sprav.addAction(spr_default)
        menu_sprav.addAction(spr_choose_pkl)
        menu_sprav.addAction(spr_choose_mdb)
        menu_sprav.addAction(spr_save_spr)
        menu_sprav.addAction(spr_info)
        menu_settings.addAction(settings_xls)
        menu_settings.addAction(settings_balance)
        menu_settings.addAction(settings_accuracy)
        menu_settings.addAction(settings_conditions)

    def show_xl_settings_window(self):
        xl_settings = self.settings.xls
        color1 = u'#35B953'
        color2 = u'#51D04C'
        self.xls_window = SettingsWindow(self, u'Настройки выгрузки в Excel')
        block_1 = ColoredBlock(u'Экспорт выборочной экспликации А', parent=self.xls_window, color =color1)
        block_2 = ColoredBlock(u'Экспорт сводной экспликации А', parent = self.xls_window, color =color2)
        block_3 = ColoredBlock(u'Экспорт экспликации по форме 22.Зем', parent = self.xls_window, color=color2)
        # lbl_2.setAlignment(QtCore.Qt.AlignCenter)
        letters = lambda x: [x,]+[unicode(chr(x)) for x in range(65,91)]
        digits = lambda x: [unicode(x),]+[unicode(i) for i in range(1,100)]
        self.sh_edit_ea = QtGui.QLineEdit(xl_settings.a_sh_name)
        self.sh_edit_easv = QtGui.QLineEdit(xl_settings.a_sv_sh_name)
        self.sh_edit_eb = QtGui.QLineEdit(xl_settings.b_sh_name)
        self.sh_edit_ea.setMinimumWidth(150)
        self.sh_edit_easv.setMinimumWidth(150)
        self.sh_edit_eb.setMinimumWidth(150)
        self.cmb_let_ea = CombBox(data=letters(xl_settings.a_l))
        self.cmb_let_ea_obj = CombBox(data=letters(xl_settings.a_obj_l))
        self.cmb_let_ea_sv = CombBox(data=letters(xl_settings.a_sv_l))
        self.cmb_let_eb = CombBox(data=letters(xl_settings.b_l))
        self.cmb_num_ea = CombBox(data=digits(xl_settings.a_n))
        self.cmb_num_ea_obj = CombBox(data=digits(xl_settings.a_obj_n))
        self.cmb_num_ea_sv = CombBox(data=digits(xl_settings.a_sv_n))
        self.cmb_num_eb = CombBox(data=digits(xl_settings.b_n))
        table_1 = SettingsTable(WidgNames.xls_table_header, self.xls_window)
        table_2 = SettingsTable(WidgNames.xls_table_header, self.xls_window)
        table_3 = SettingsTable(WidgNames.xls_table_header, self.xls_window)
        table_1.add_span_row(WidgNames.out_matrix)
        table_2.add_span_row(WidgNames.out_matrix)
        table_3.add_span_row(WidgNames.out_matrix)
        table_1.add_widgets_row([self.sh_edit_ea, self.cmb_let_ea, self.cmb_num_ea])
        table_2.add_widgets_row([self.sh_edit_easv, self.cmb_let_ea_sv, self.cmb_num_ea_sv])
        table_3.add_widgets_row([self.sh_edit_eb, self.cmb_let_eb, self.cmb_num_eb])
        table_1.add_span_row(WidgNames.out_object)
        table_1.add_widgets_row([None, self.cmb_let_ea_obj, self.cmb_num_ea_obj])
        block_1.add_widget(table_1)
        block_2.add_widget(table_2)
        block_3.add_widget(table_3)

        self.edit_xls_start = QtGui.QCheckBox(u'Запуск .xls файлов по завершению расчетов')
        self.edit_xls_start.setChecked(xl_settings.is_xls_start)

        self.edit_mdb_start = QtGui.QCheckBox(u'Запуск .mdb файлов по завершению расчетов')
        self.edit_mdb_start.setChecked(xl_settings.is_mdb_start)


        btn = QtGui.QPushButton(u"Сохранить изменения", self.xls_window.main_frame)
        # btn.setStyleSheet(u'background-color: %s;color: white; border-radius: 5%; padding:0px'%color1)
        # btn.setFixedHeight(90)
        # btn.setFixedWidth(90)
        self.xls_window.add_widget(block_1, 0,0,5,5)
        self.xls_window.add_widget(block_2, 5,0,5,5)
        self.xls_window.add_widget(block_3, 0,5,5,5)
        self.xls_window.add_widget(self.edit_xls_start, 6,6,1,4)
        self.xls_window.add_widget(self.edit_mdb_start, 7,6,1,4)
        self.xls_window.add_widget(btn, 9,7,1,3)
        self.connect(btn, QtCore.SIGNAL(u'clicked()'), self.update_xl_data)
        self.xls_window.show()

    def show_balance_settings_window(self):
        balance_settings = self.settings.balance

        self.balance_window = SettingsWindow(self, u'Настройки балансировки', 400, 250)
        self.edit_b_balance = QtGui.QCheckBox(u'Включить баланс в расчет экспликации Ф22зем')
        self.edit_b_balance.setChecked(balance_settings.include_b_balance)
        self.edit_a_balance = QtGui.QCheckBox(u'Включить баланс в расчет одиночной экспликации А (Not yet implemented)')
        self.edit_a_balance.setChecked(balance_settings.include_a_balance)
        self.edit_a_sv_balance = QtGui.QCheckBox(u'Включить баланс в расчет сводной экспликации А (Not yet implemented)')
        self.edit_a_sv_balance.setChecked(balance_settings.include_a_sv_balance)

        btn = QtGui.QPushButton(u"Сохранить изменения", self.balance_window.main_frame)
        self.connect(btn, QtCore.SIGNAL(u'clicked()'), self.update_balance_settings)

        self.balance_window.add_widget(self.edit_a_balance, 0,0,3,3)
        self.balance_window.add_widget(self.edit_a_sv_balance, 1,0,3,3)
        self.balance_window.add_widget(self.edit_b_balance, 2,0,3,3)
        self.balance_window.add_widget(btn, 4,2,1,1)
        self.balance_window.show()

    def show_filtering_window(self):
        filter_settings = self.settings.filter
        print filter_settings.__dict__
        self.filter_window = SettingsWindow(self, u'Настройки фильтра',300, 150)

        self.melio_filter_used = QtGui.QRadioButton(u'Вкючить фильтр по полю MELIOCODE', self.filter_window)
        self.servtype_filter_used = QtGui.QRadioButton(u'Вкючить фильтр по полю SERVTYPE', self.filter_window)
        # self.melio_filter_used.setChecked(bool(filter_settings.enable_melio))
        # self.servtype_filter_used.setChecked(bool(filter_settings.enable_servtype))

        self.melio_filter_used.setChecked(filter_settings.enable_melio)
        self.servtype_filter_used.setChecked(not filter_settings.enable_melio)


        # self.melio_filter = QtGui.QTextEdit(self)
        # self.melio_filter.setText(filter_settings.melio)
        # self.servtype_filter = QtGui.QTextEdit(self)
        # self.servtype_filter.setText(filter_settings.servtype)

        btn = QtGui.QPushButton(u"Применить фильтр", self.filter_window.main_frame)
        self.connect(btn, QtCore.SIGNAL(u'clicked()'), lambda: self.filter_changed(True))

        self.filter_window.add_widget(self.melio_filter_used, 0,0,1,2)
        self.filter_window.add_widget(self.servtype_filter_used, 1,0,1,2)
        # self.filter_window.add_widget(self.melio_filter, 0,2,1,2)
        # self.filter_window.add_widget(self.servtype_filter, 1,2,1,2)

        self.filter_window.add_widget(btn, 4,3,1,1)
        self.filter_window.show()

    def show_accuracy_settings_window(self):
        accuracy_settings = self.settings.rnd

        self.accuracy_window = SettingsWindow(self, u'Настройки точности', 400, 250)

        self.edit_a_accuracy = CombBox(self.accuracy_window, '01234')
        self.edit_a_sv_accuracy = CombBox(self.accuracy_window, '01234')
        self.edit_b_accuracy = CombBox(self.accuracy_window, '01234')
        self.edit_a_accuracy.setCurrentIndex(int(accuracy_settings.a_s_accuracy))
        self.edit_a_sv_accuracy.setCurrentIndex(int(accuracy_settings.a_sv_accuracy))
        self.edit_b_accuracy.setCurrentIndex(int(accuracy_settings.b_accuracy))
        self.lbl_a_accuracy = QtGui.QLabel(u'Точность округления формы А', self.accuracy_window)
        self.lbl_a_sv_accuracy = QtGui.QLabel(u'Точность округления формы А сводная', self.accuracy_window)
        self.lbl_b_accuracy = QtGui.QLabel(u'Точность округления формы B', self.accuracy_window)

        btn = QtGui.QPushButton(u"Сохранить изменения", self.accuracy_window.main_frame)
        self.connect(btn, QtCore.SIGNAL(u'clicked()'), self.update_accuracy_settings)

        self.accuracy_window.add_widget(self.lbl_a_accuracy, 0,0,1,5)
        self.accuracy_window.add_widget(self.edit_a_accuracy, 0,5,1,1)
        self.accuracy_window.add_widget(self.lbl_a_sv_accuracy, 1,0,1,5)
        self.accuracy_window.add_widget(self.edit_a_sv_accuracy, 1,5,1,1)
        self.accuracy_window.add_widget(self.lbl_b_accuracy, 2,0,1,5)
        self.accuracy_window.add_widget(self.edit_b_accuracy, 2,5,1,1)
        self.accuracy_window.add_widget(btn, 4,3,1,2)
        self.accuracy_window.show()

    def show_conditions_settings_window(self):
        conditions_settings = self.settings.conditions
        self.conditions_window = SettingsWindow(self, u'Настройки условий выборки из crostab', 400, 150)
        self.include_melio = QtGui.QCheckBox(u'Расчет мелиоративных земель')
        self.include_melio.setChecked(bool(conditions_settings.melio))
        btn = QtGui.QPushButton(u"Сохранить изменения", self.conditions_window.main_frame)
        self.connect(btn, QtCore.SIGNAL(u'clicked()'), self.update_conditions_settings)

        self.conditions_window.add_widget(self.include_melio, 0, 0, 3, 3)
        self.conditions_window.add_widget(btn, 4, 2, 1, 1)
        self.conditions_window.show()

    def update_balance_settings(self):
        self.settings.balance.include_a_balance = bool(self.edit_a_balance.isChecked())
        self.settings.balance.include_a_sv_balance = bool(self.edit_a_sv_balance.isChecked())
        self.settings.balance.include_b_balance  = bool(self.edit_b_balance.isChecked())

        self.add_event_log(u'Установлены новые настройки запуска баланса')
        self.balance_window.close()
        self.update_settings()

    def update_accuracy_settings(self):
        self.settings.rnd.a_s_accuracy = int(self.edit_a_accuracy.get_current_item())
        self.settings.rnd.a_sv_accuracy = int(self.edit_a_sv_accuracy.get_current_item())
        self.settings.rnd.b_accuracy = int(self.edit_b_accuracy.get_current_item())
        self.add_event_log(u'Установлены новые настройки округления')
        self.accuracy_window.close()
        self.update_settings()


    def filter_changed(self, is_details_changed = False):
        self.block_btns()
        self.statusBar().showMessage(u'Фильтрация данных')
        self.settings.filter.enabled = bool(self.filter_activation.isChecked())
        if is_details_changed:
            self.settings.filter.enable_melio = self.melio_filter_used.isChecked()

            # self.settings.filter.enable_servtype = self.servtype_filter_used.isChecked()
            # self.settings.filter.melio = self.melio_filter.toPlainText()
            # self.settings.filter.servtype = self.servtype_filter.toPlainText()
            self.filter_window.close()
            self.add_event_log(u'Изменены условия фильтрации данных для экспликации')
            self.update_settings()
        self.apply_exp_data_filter()

    def apply_exp_data_filter(self):
        if self.settings.filter.enabled:
            filtered_rows = filter(self.filter_item, self._not_filtered_data)
        else:
            if len(self.explication_data[0]) == len(self._not_filtered_data):
                return
            else:
                filtered_rows = self._not_filtered_data[:]
        self.explication_data[0] = filtered_rows
        self.current_exp_data = self.explication_data[:]
        print len(self.explication_data[0])
        self.show_first_combo()
        self.stop_loading()

    def filter_item(self, item):
        if self.settings.filter.enable_melio:
            param = item.get_el_by_fkey('mc')
        else:
            param = item.get_el_by_fkey('srvtype')
        if param:
            return True
        else:
            return False
        #
        # if self.settings.filter.enable_servtype:
        #     if item['structure']['mc'] != self.settings.filter.melio:
        #         return False
        # if self.settings.filter.enable_melio:
        #     if item['structure']['srvtype'] != self.settings.filter.servtype:
        #         return False
        # TODO: fix conditions
        # return True


    def update_conditions_settings(self):
        if self.include_melio.isChecked():
            self.settings.conditions.melio = u'MELIOCODE = 1'
        else:
            self.settings.conditions.melio = u''
        self.add_event_log(u'Установлены новые настройки выборки данных из crostab')
        self.conditions_window.close()
        self.update_settings()

    def update_xl_data(self):
        self.settings.xls.a_sh_name = unicode(self.sh_edit_ea.text())
        self.settings.xls.a_sv_sh_name = unicode(self.sh_edit_easv.text())
        self.settings.xls.b_sh_name = unicode(self.sh_edit_eb.text())
        self.settings.xls.a_l = unicode(self.cmb_let_ea.currentText())
        self.settings.xls.a_obj_l = unicode(self.cmb_let_ea_obj.currentText())
        self.settings.xls.a_sv_l = unicode(self.cmb_let_ea_sv.currentText())
        self.settings.xls.b_l = unicode(self.cmb_let_eb.currentText())
        self.settings.xls.a_n = int(self.cmb_num_ea.currentText())
        self.settings.xls.a_obj_n = int(self.cmb_num_ea_obj.currentText())
        self.settings.xls.a_sv_n = int(self.cmb_num_ea_sv.currentText())
        self.settings.xls.b_n = int(self.cmb_num_eb.currentText())
        self.settings.xls.is_xls_start = bool(self.edit_xls_start.isChecked())
        self.settings.xls.is_mdb_start = bool(self.edit_mdb_start.isChecked())

        self.add_event_log(u'Установлены новые настройки выгрузки в Excel')
        self.xls_window.close()
        self.update_settings()

    def open_file(self):
        db_f = unicode(QtGui.QFileDialog(self).getOpenFileName(self, WidgNames.open_file, project_dir, u'Valid files (*.mdb *.pkl);; All files (*)', options=QtGui.QFileDialog.DontUseNativeDialog))
        self.db_file = db_f.replace('/', '\\')


        if db_f:
            if db_f[-4:] == u'.mdb':
                self.run_main_thr(self.db_file, op = 0)
            elif db_f[-4:] == u'.pkl':
                self.run_main_thr(self.db_file, op = 5)
            else:
                self.show_error(ErrMessage.wrong_file)

    def db_file_opened(self):
        self.__is_session = False
        self.reset_params()
        self.reset_parameters()
        self.add_event_log(Events.opened_file % self.db_file)
        self.add_event_log(Events.db_has_data % os.path.basename(self.db_file), False)

    def session_loaded(self, exp_data):
        self.__is_session = True
        self.reset_params()
        self.reset_parameters()
        e_db_f = exp_data.pop()
        if not self.set_export_src(os.path.dirname(e_db_f), os.path.basename(e_db_f)):
            self.show_warning(ErrMessage.session_path_not_found % e_db_f)
            self.change_edb_file()
        self.enable_explications(exp_data)
        self.add_event_log(Events.session_loaded % self.db_file)

    def save_session(self):
        default_name = os.path.basename(self.e_db_file)[4:-4]+time.strftime(u'_%d_%m_%y') + u'.pkl'
        save_file = unicode(QtGui.QFileDialog(self).getSaveFileName(self, WidgNames.save_dialog, default_name, options=QtGui.QFileDialog.DontUseNativeDialog))
        if save_file:
            if save_file[-4:] != u'.pkl':
                save_file+= u'.pkl'


            exp_data = self.explication_data[:]
            exp_data[0] = self._not_filtered_data
            exp_data.extend([self.e_db_file, u'Salt'])
            self.run_main_thr(save_file, 6, exp_data)


    def say_convert_success(self):
        self.convert_thr = None
        self.convert_table.clear_all()
        self.convert_table.hide()
        self.add_event_log(Events.convert_passed)

    def enable_explications(self, converted_data):
        self.exp_a_btn.setEnabled(True)
        self.exp_b_btn.setEnabled(True)
        self.explication_data = converted_data
        self._not_filtered_data = converted_data[0][:]
        self.current_exp_data = self.explication_data[:]
        self.show_expl_export()
        if not self.__is_session:
            self.change_edb_file()

        self.filter_frame.setHidden(False)
        self.settings.filter.enabled = False
        self.filter_activation.setChecked(False)

        self.stop_loading()

    def get_edb_path(self):
        exp_path = unicode(QtGui.QFileDialog(self).getExistingDirectory(self, WidgNames.save_exp_dialog, project_dir, options=QtGui.QFileDialog.DontUseNativeDialog))
        exp_path = exp_path.replace('/', '\\')
        if exp_path:
            return  exp_path
        current_path = os.path.dirname(unicode(self.e_db_file))
        if os.path.isdir(current_path):
            return current_path
        else:
            return self.get_edb_path()

    def set_export_src(self, exp_path, base_name):
        if os.path.isdir(exp_path):
            self.export_frame.e_src_widget.set_lbl_text(exp_path)
            self.e_db_file = os.path.join(exp_path, base_name)
            return True
        else:
            return False

    def change_edb_file(self):
        if self.__is_session and self.e_db_file:
            base_name = os.path.basename(self.e_db_file)
        else:
            base_name = u'Exp_' + os.path.basename(self.db_file)
        got_path = self.get_edb_path()
        self.set_export_src(got_path, base_name)


    def show_expl_export(self):
        self.export_frame.show()
        self.save_widget.show()

    def set_xls_mode(self):
        self.__is_xls_mode= True

    def set_mdb_mode(self):
        self.__is_xls_mode = False

    def ask_question(self, messag):
        reply = QtGui.QMessageBox.question(self, WidgNames.ask_exit, messag,
                                           QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.statusBar().showMessage(LoadMessg.ready)
        else:
            sys.exit()

    def enable_convert(self):
        self.control_thr = None
        self.add_event_log(Events.control_passed)
        self.control_table.hide()
        self.convert_btn.setEnabled(True)

    def show_first_combo(self):
        self.group_box.show()
        group_soatos = self.make_soato_group(self.explication_data[2].keys())
        soato_names_d = self.explication_data[2]
        ate_expl_data = dict.fromkeys(group_soatos.keys(), None)
        for expl in self.current_exp_data[0]:
            try:
                ate_expl_data[expl.soato[:-3]].append(expl)
            except AttributeError:
                ate_expl_data[expl.soato[:-3]] = [expl,]
            except KeyError:
                try:
                    ate_expl_data[nongrouped].append(expl)
                except AttributeError:
                    ate_expl_data[nongrouped] = [expl,]
        for k, v in ate_expl_data.items():
            if v is None:
                del ate_expl_data[k]
                del group_soatos[k]
        self.ate_expl_data_dict = ate_expl_data
        names = []
        for key in group_soatos:
            names.append((soato_names_d[key+u'000'], key))
        cmb1_data, self.cmb1_recover_d, ate_len = self._count_cmb_data_recovery(names)
        self.group_soatos = group_soatos
        # self.group_box.first_cmb.set_width(ate_len*7)
        self.group_box.change_first_cmb(cmb1_data)

    def show_second_combo(self, ate_soato):
        soato_names_d = self.explication_data[2]
        # soatos = self.group_soatos[ate_soato]
        expl_data = {}
        u'''
        Далее заполняем словарь expl_data(keys: SOATO codes) экземплярами класса CtrRow
        '''
        for expl in self.current_exp_data[0]:
            try:
                expl_data[expl.soato].append(expl)
            except KeyError:
                expl_data[expl.soato] = [expl,]
        self.second_expl_data_dict = expl_data
        ate_names = []
        for s in expl_data:
            try:
                ate_name = soato_names_d[s]
            except KeyError:
                ate_name=u'-'
            ate_names.append((ate_name, s))
        cmb2_data, self.cmb2_recover_d, ate_len = self._count_cmb_data_recovery(ate_names, u'Вся АТЕ', ate_kod = ate_soato)
        self.group_box.change_second_cmb(cmb2_data)
        self.group_box.second_cmb.show()
        # self.group_box.second_cmb.set_width(ate_len*7)

    def first_combo_changed(self):
        curr_ind = self.group_box.get_first_index()
        self.group_box.second_cmb.hide()
        if curr_ind != -1:
            if curr_ind == 0:
                self.current_exp_data = self.explication_data[:]
            else:
                curr_soato = self.cmb1_recover_d[curr_ind]
                self.current_exp_data[0] = self.ate_expl_data_dict[curr_soato]
                if self.group_soatos[curr_soato]:
                    self.show_second_combo(curr_soato)

            #self.click_exp_a_btn(False)
            self.reset_expa_thread()
            self.click_a_tree_btn()


    def second_combo_changed(self):
        curr_ind = self.group_box.get_second_index()
        if curr_ind != -1:
            curr_soato = self.cmb2_recover_d[curr_ind]
            if curr_ind == 0:
                self.current_exp_data[0] = self.ate_expl_data_dict[curr_soato]
            else:
                self.current_exp_data[0] = self.second_expl_data_dict[curr_soato]
            #self.click_exp_a_btn(False)
            self.reset_expa_thread()
            self.click_a_tree_btn()

    @staticmethod
    def _count_cmb_data_recovery(names, first_combo_row = u'Весь район', ate_kod = None):
        """ Input: names - list of tuples (name, soato)
            returns combo_box data , recovery dictionary to catch, which combo row was checked , max item length
        """
        if ate_kod:
            recovery_soato_d = {0:ate_kod}
        else:
            if len(names):
                recovery_soato_d = {0:names[0][1][:-3]}
            else:
                recovery_soato_d = {0:'not found'}
        combo_data = [u'* ' + first_combo_row]
        sorted_names = sorted(names)
        max_len = 0
        for i in sorted_names:
            if len(i[0]) > max_len:
                max_len = len(i[0])
            combo_data.append(i[0])
            recovery_soato_d[sorted_names.index(i)+1] = i[1]
        return combo_data, recovery_soato_d, max_len

    def make_soato_group(self, s_kods):
        soato_group = {}
        for s in s_kods:
            ate_key = s[:-3]
            if s[-3:] == u'000':
                soato_group[ate_key] = []
        nongrouped_soatos = []
        for s in s_kods:
            ate_key = s[:-3]
            try:
                soato_group[ate_key].append(s)
            except KeyError:
                nongrouped_soatos.append(s)
        if nongrouped_soatos:
            self.show_error(u'WARNING! \nДанные коды не возможно сгруппировать  %s\nУчастки с такими кодами будут размещены в NonGrouped'% unicode(nongrouped_soatos))
            global nongrouped
            nongrouped = u'xxxxxxx'
            soato_group[nongrouped] = nongrouped_soatos
            self.explication_data[2][u'%s000'%nongrouped ]= u'NonGrouped!'
        return soato_group

    def stop_loading(self, unlock_btns = True):
        self.load_thr.terminate()
        if unlock_btns:
            self.block_btns(False)
        self.statusBar().showMessage(LoadMessg.ready)

    def add_loading(self, load_message):
        self.block_btns()
        self._load_message = load_message
        self.load_thr.start()

    def show_sprav_error(self, err_text):
        self.show_main_thr_error(err_text)
        if self.sprav_holder:
            self.add_event_log(Events.set_previous_spr)
        else:
            self.add_event_log(Events.spr_default_failed)

    def load_save_db_err(self, err_text):
        self.show_main_thr_error(err_text)
        self.add_event_log(err_text)

    def show_main_thr_error(self, err_msg):
        self.main_load_save_thr.terminate()
        self.load_thr.terminate()
        self.show_error(err_msg)
        self.statusBar().showMessage(LoadMessg.ready)

    def load_sprav(self, from_pkl = False):
        if from_pkl:
            file = unicode(QtGui.QFileDialog(self).getOpenFileName(self, WidgNames.load_sprav+ u'*.pkl', project_dir, options=QtGui.QFileDialog.DontUseNativeDialog))
            op = 2
        else:
            file = unicode(QtGui.QFileDialog(self).getOpenFileName(self, WidgNames.load_sprav+ u'*.mdb', project_dir, options=QtGui.QFileDialog.DontUseNativeDialog))
            op = 3
        if file:
            self.run_main_thr(file, op)

    def run_main_thr(self, sprav_path = spr_default_path, op = 1, *dop_args):
        if sprav_path:
            if op == 0:
                self.add_loading(LoadMessg.load_db)
            elif op <= 3:
                self.add_loading(LoadMessg.spr_loading)
            elif op == 5:
                self.add_loading(LoadMessg.load_session_pkl)
            elif op == 6:
                self.add_loading(LoadMessg.save_session_pkl)
            self.main_load_save_thr.change_op(sprav_path, op, dop_args)
            self.main_load_save_thr.start()

    def set_sprav_holder(self, sprav):
        self.stop_loading(False)
        self.sprav_holder = sprav
        self.add_event_log(Events.load_sprav_success)

    def save_sprav(self):
        save_file = unicode(QtGui.QFileDialog(self).getSaveFileName(self, WidgNames.save_dialog, options=QtGui.QFileDialog.DontUseNativeDialog))
        if save_file:
            self.add_loading(LoadMessg.spr_saving)
            self.main_load_save_thr.update_settings_dict(self.settings.get_settings_dict())
            self.settings.last_hold_pkl_dir = save_file
            self.run_main_thr(save_file,4)

    def update_settings(self):
        self.main_load_save_thr.update_settings_dict(self.settings.get_settings_dict())
        self.run_main_thr(self.settings.last_hold_pkl_dir, 4)

    def settings_loaded(self, settings_dict):
        self.settings.update_settings(settings_dict)

    def say_saved(self, msg):
        self.stop_loading(False)
        self.add_event_log(msg)

    def show_spr_info(self):
        csd = self.main_load_save_thr.current_sprav_dict
        if csd:
            s_date = csd[u'create_time']
            s_file = self.main_load_save_thr.spr_path_info
            message = Events.spr_info(s_date, s_file)
        else:
            message = ErrMessage.spr_not_loaded
        QtGui.QMessageBox.information(self, WidgNames.sprav_info_box,message, u'Ok')

    @QtCore.pyqtSlot()
    def click_control_btn(self):
        self.convert_btn.setDisabled(True)
        self.add_event_log(Events.run_control)
        self.add_loading(LoadMessg.loading_control)
        self.control_thr = ControlThread(self.sprav_holder, self.db_file)
        self.connect(self.control_thr, QtCore.SIGNAL(u'control_passed()'), self.enable_convert)
        self.connect(self.control_thr, QtCore.SIGNAL(u'contr_failed(PyQt_PyObject)'), self.add_control_protocol)
        self.connect(self.control_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), self.show_error)
        self.connect(self.control_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), lambda:self.add_event_log(
            ErrMessage.control_failed))
        self.connect(self.control_thr, QtCore.SIGNAL(u'finished()'), self.stop_loading)
        self.control_thr.start()

    @QtCore.pyqtSlot()
    def click_convert_btn(self):
        self.add_event_log(Events.run_convert)
        self.convert_thr = ConvertThread(self.sprav_holder, self.settings)
        self.add_loading(LoadMessg.loading_convert)
        self.connect(self.convert_thr, QtCore.SIGNAL(u'convert_passed(PyQt_PyObject)'), self.enable_explications)
        self.connect(self.convert_thr, QtCore.SIGNAL(u'convert_passed(PyQt_PyObject)'), lambda:self.add_event_log(Events.convert_passed))
        self.connect(self.convert_thr, QtCore.SIGNAL(u'conv_failed(PyQt_PyObject)'), self.add_convert_protocol)
        self.connect(self.convert_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), self.show_error)
        self.connect(self.convert_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), lambda:self.add_event_log(
            ErrMessage.convert_failed))
        self.connect(self.convert_thr, QtCore.SIGNAL(u'finished()'), self.stop_loading)
        self.convert_thr.start()

    @QtCore.pyqtSlot()
    def click_exp_a_btn(self):
        self.block_btns()
        self.btn_a_all.setHidden(False)
        self.btn_a_tree.setHidden(False)
        self.exp_a_btn.setHidden(True)
        self.show_first_combo()
        self.block_btns(False)

    def reset_expa_thread(self):
        self.exp_a_thr = None
        self.exp_a_thr = ExpAThread(self.e_db_file, self.current_exp_data, self.sprav_holder, self.settings)
        self.connect(self.exp_a_thr, QtCore.SIGNAL(u'finished()'), self.stop_loading)
        self.connect(self.exp_a_thr, QtCore.SIGNAL(u'exp_sv_success()'), lambda: self.add_event_log(Events.finished_exp_a_sv))
        self.connect(self.exp_a_thr, QtCore.SIGNAL(u'exp_s_success()'), lambda: self.add_event_log(Events.finished_exp_a_s))
        self.connect(self.exp_a_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), self.show_error)
        self.connect(self.exp_a_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), lambda: self.add_event_log(Events.exp_a_finished_with_err))

    @QtCore.pyqtSlot()
    def click_a_svodn_btn(self):
        self.add_loading(LoadMessg.wait_exp_a)
        self.add_event_log(Events.started_sv_exp_a)
        self.exp_a_thr.set_xl_output(self.__is_xls_mode)
        self.exp_a_thr.start()

    def run_single_exp_a(self, pressed_exp, exp_ind):
        self.add_loading(LoadMessg.wait_exp_a)
        exp_name = exp_ind + '. ' + pressed_exp.obj_name
        self.add_event_log(Events.started_s_exp_a % exp_name)
        self.exp_a_thr.run_single_exp(pressed_exp, exp_ind)

    @QtCore.pyqtSlot()
    def click_a_tree_btn(self):
        self.model = self.make_tree_model(self.exp_a_thr.exp_tree)
        self.model.setHorizontalHeaderLabels([WidgNames.tree_header])
        self.treeView.setModel(self.model)
        self.treeView.setHidden(False)
        # self.disconnect(self.treeView, QtCore.SIGNAL(u"activated(const QModelIndex &)"),self.click_tree_cell)
        # self.connect(self.treeView, QtCore.SIGNAL(u"activated(const QModelIndex &)"),self.click_tree_cell)

    @QtCore.pyqtSlot()
    def click_exp_b_btn(self):
        self.add_loading(LoadMessg.wait_exp_b)
        self.add_event_log(Events.run_exp_b)
        self.exp_b_thr = ExpBThread(self.e_db_file, self.explication_data[0], self.sprav_holder, self.settings)
        self.connect(self.exp_b_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), self.show_error)
        self.connect(self.exp_b_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), lambda:self.add_event_log(Events.exp_b_finished_with_err))
        self.connect(self.exp_b_thr, QtCore.SIGNAL(u'finished()'), self.stop_loading)
        self.connect(self.exp_b_thr, QtCore.SIGNAL(u'success()'), lambda:self.add_event_log(Events.finish_exp_b))
        self.exp_b_thr.set_output_mode(self.__is_xls_mode)
        self.exp_b_thr.start()

    def make_tree_model(self, all_exps):
        model = QtGui.QStandardItemModel()
        forms22 = all_exps.keys()
        f22_notes = self.sprav_holder.f22_notes
        self.tree_index_dict = {}
        for key in sorted(forms22):
            f22_item = QtGui.QStandardItem(key+u' '+f22_notes[key])
            f22_item_font = QtGui.QFont()
            f22_item_font.setBold(True)
            f22_item_font.setFamily('Cursive')
            f22_item_font.setPointSize(10)
            f22_item.setFont(f22_item_font)
            model.appendRow(f22_item)
            item_names = [i.full_obj_name for i in all_exps[key]]
            index_li = []
            ch_item_count = 1
            for exp_item in sorted(item_names):
                index_li.append(item_names.index(exp_item))     #заполняет позициями элементов до сортировки, для дальнейшего определения инстанса в data[key]
                child_item = QtGui.QStandardItem(u'%d. ' % ch_item_count + exp_item)
                child_item.setFont(QtGui.QFont('Serif', 10))
                f22_item.appendRow(child_item)
                ch_item_count+=1
            self.tree_index_dict[key] = index_li
        return model

    def click_tree_cell(self, qindex):
        if qindex.parent().isValid():
            data = self.exp_a_thr.exp_tree
            pressed_f22_ind = qindex.parent().row()
            pressed_exp_ind = qindex.row()
            pressed_f22 = sorted(data.keys())[pressed_f22_ind]
            indexes_before_sort = self.tree_index_dict[pressed_f22]
            exp_index = indexes_before_sort[pressed_exp_ind]
            pressed_exp = data[pressed_f22][exp_index]
            self.run_single_exp_a(pressed_exp, u'%s.%d' % (pressed_f22, pressed_exp_ind+1))


    def add_event_log(self, text, with_time = True):
        if with_time:
            self.event_table.table.add_action_row([text])
        else: self.event_table.table.add_action_row([text],u'- // -')

    def add_control_protocol(self, data_li):
        self.control_thr = None
        self.add_event_log(Events.control_failed)
        self.control_table.show()
        event_time = time.strftime(u"%d.%m.%y  %H:%M:%S"  )
        self.control_table.table.add_span_row(event_time)
        err_descriptions = ErrMessage.control_protocol
        for err in data_li:
            if len(err[u'err_ids'])> 100:
                errors = unicode(tuple(err[u'err_ids'][:100]))
                add_warning = u'!!! '
            else:
                errors = unicode(tuple(err[u'err_ids']))
                add_warning = u''
            err_code = err[u'err_msg']
            if err[u'dyn_param']:
                err_msg = err_descriptions[err_code](err[u'dyn_param'])
            else:
                err_msg = err_descriptions[err_code]
            self.control_table.table.add_row([err[u'table'],err[u'field'], u'OBJECTID in %s' % errors, add_warning+err_msg])

    def add_convert_protocol(self, data_di):
        self.convert_btn.setDisabled(True)
        self.convert_thr = None
        self.add_event_log(Events.convert_failed)
        self.stop_loading()
        self.convert_table.show()
        event_time = time.strftime(u"%d.%m.%y  %H:%M:%S"  )
        self.convert_table.table.add_span_row(event_time)
        for err_type in data_di:
            for part in data_di[err_type]:
                errors = data_di[err_type][part]
                if len(errors)> 100:
                    errors = unicode(tuple(errors[:100]))
                    add_warning = u'!!! '
                else:
                    errors = unicode(tuple(errors))
                    add_warning = u' '
                self.convert_table.table.add_row([part, u'OBJECTID in %s' % errors, add_warning + ErrMessage.convert_errors[err_type]])

    def show_warning(self, warn_text):
        QtGui.QMessageBox.critical(self, WidgNames.warning, u"%s" % warn_text,u'Закрыть')

    def show_error(self, err_text):
        QtGui.QMessageBox.critical(self, WidgNames.error, u"%s" % err_text,u'Закрыть')


class ExportFrame(QtGui.QFrame):
    def __init__(self, parent = None):
        QtGui.QFrame.__init__(self, parent)
        self.color = u'#D3D120'
        self.setStyleSheet(u'background-color: #959BA8; border-radius: 15%;')
        self.rbtn_xls = QtGui.QRadioButton(u'*.xls',self)
        self.rbtn_xls.setIcon(QtGui.QIcon(u'%s\\Images\\xls.ico' % project_dir))
        self.rbtn_xls.setChecked(True)
        self.rbtn_xls.setFont(QtGui.QFont('Verdana',10))
        self.rbtn_mdb = QtGui.QRadioButton(u'*.mdb',self)
        self.rbtn_mdb.setIcon(QtGui.QIcon(u'%s\\Images\\mdb.ico' % project_dir))
        self.rbtn_mdb.setFont(QtGui.QFont('Verdana',10))
        self.rbtn_style = u'background-color: white; color: green;' \
                          u' border-top-right-radius: 3%;' \
                          u'border-bottom-left-radius: 3%; padding: 3px;' \
                          u'border: 2px solid' + self.color
        self.lbl_style = u'background-color: #49586B; color: white;' \
                          u'border-top-left-radius: 23%;' \
                          u'border-top-right-radius: 23%;' \
                          u'border-bottom-left-radius: 23%;' \
                          u'border-bottom-right-radius: 3%;' \
                          u'padding-left: 10px;' \
                          u'border: 2px solid '+self.color
        self.lbl = QtGui.QLabel(u'Экспорт \n данных', self)
        # self.lbl.setStyleSheet(u'color: white; background-color: #49586B; border-radius: 8%; border: 2px solid' + border_color)
        self.lbl.setFont(QtGui.QFont('Segoe Print',10))
        self.e_src_widget = SrcFrame(self.color)
        self.box = QtGui.QGridLayout(self)
        self.box.addWidget(self.rbtn_xls, 0, 1, 1, 1)
        self.box.addWidget(self.rbtn_mdb, 1, 1, 1, 1)
        self.box.addWidget(self.lbl, 0, 0, 2, 1)
        self.box.addWidget(self.e_src_widget, 2, 0, 1, 2)
        self.rbtn_xls.setStyleSheet(self.rbtn_style)
        self.rbtn_mdb.setStyleSheet(self.rbtn_style)
        self.lbl.setStyleSheet(self.lbl_style)


class SrcFrame(QtGui.QFrame):
    def __init__(self, border_color = u'#00BA4A',parent = None):
        QtGui.QFrame.__init__(self, parent)
        self.setStyleSheet(u'background-color: #959BA8; border-radius: 15%;')
        self.h_box = QtGui.QHBoxLayout(self)
        self.btn = QtGui.QToolButton(self)
        self.btn.setText(u'...')
        self.btn.setStyleSheet(u'background-color: white ; border-radius: 8% ; border: 1px solid '+ border_color)
        self.btn.setAutoRaise(True)
        self.lbl = QtGui.QLabel(u' ', self)
        self.lbl.setStyleSheet(u'color: white; background-color: #49586B; border-radius: 8%; border: 2px solid' + border_color)
        self.lbl.setFont(QtGui.QFont('Segoe Print',9))
        self.lbl.setAlignment(QtCore.Qt.AlignRight)
        self.h_box.addWidget(self.lbl)
        self.h_box.addWidget(self.btn)


    def change_border_color(self, color):
        self.btn.setStyleSheet(u'border: 1px solid %s;' % color)
        self.lbl.setStyleSheet(u'border: 2px solid %s;' % color)

    def set_lbl_text(self, text, collapse_len = 40):
        """
        В строке text делается перенос относительно \ если длина превышает 40 символов
        """
        path_parts = text.split(u'\\')
        text = path_parts.pop(0)
        if path_parts:
            temp_text = u''
            for part in path_parts:
                part = u'\\%s' % part
                if len(part) + len(temp_text) >collapse_len:
                    text+=u'%s\n'% temp_text
                    temp_text = part
                else:
                    temp_text+=part
            text+=temp_text
        # path_parts = text.split(u'\\')
        # path_parts = map(lambda x: x+'\\', path_parts)
        # if path_parts:
        #     text = path_parts[0]
        #     temp_text = ''
        #     for part in path_parts[1:]:
        #         if len(part)+len(temp_text)<collapse_len:
        #             temp_text+=part
        #         else:
        #             text+=temp_text+'\n'
        #             temp_text = part
        #     text+=temp_text[:2]
        self.lbl.setText(text)
        self.lbl.repaint()

class CombBox(QtGui.QComboBox):
    def __init__(self, parent = None, data = [], width = 60):
        QtGui.QComboBox.__init__(self, parent)
        self.data = data
        self.change_data(data)
        self.setStyleSheet(u'font-size: 12px')
        self.set_min_width(width)
        self.setMaxVisibleItems(30)

    def set_min_width(self, width):
        self.setMinimumWidth(width)

    def change_data(self, new_data):
        self.clear()
        self.addItems(new_data)
        self.data = new_data

    def get_current_item(self):
        if len(self.data):
            cur_ind = self.currentIndex()
            return self.data[cur_ind]



class SelectionBox(QtGui.QComboBox):
    def __init__(self, parent=None, data=None, width=60):
        QtGui.QComboBox.__init__(self, parent)
        self.data = []
        if data is not None:
            self.change_data(data)
        self.set_min_width(width)
        self.setMaxVisibleItems(20)
        self.applyStyles()
        self.setAutoCompletion(True)

    def set_min_width(self, width):
        # self.scroll(1,3)
        self.setMinimumWidth(width)

    def change_data(self, new_data):
        self.clear()
        self.addItems(new_data)
        self.data = new_data

class GroupBox(QtGui.QFrame):
    def __init__(self, parent = None, border_color = u'#C3FFF1'):
        QtGui.QFrame.__init__(self, parent)
        self.setMaximumHeight(33)
        self.setStyleSheet(u'background-color: #2558FF; border-top-left-radius: 30%;border-bottom-right-radius: 30%; padding-right: 5px;padding-left: 5px')
        self.h_box = QtGui.QHBoxLayout(self)
        self.first_cmb = CombBox(self, width = 180)
        self.second_cmb = CombBox(self, width = 180)
        self.second_cmb.hide()
        self.first_cmb.setStyleSheet(u'border-radius: 5% ; border: 1px solid '+ border_color)
        self.second_cmb.setStyleSheet(u'border-radius: 5% ; border: 2px solid '+ border_color)
        self.lbl = QtGui.QLabel(WidgNames.lbl_group, self)
        self.lbl.setStyleSheet(u'color: #C3FFF1;')
        self.lbl.setFont(QtGui.QFont('Segoe Print',9))
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
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

class Table(QtGui.QTableWidget):
    def __init__(self, header_text_li, parent = None):
        QtGui.QTableWidget.__init__(self, parent)
        self.__row_count = 0
        # qsize =QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        # self.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        # self.horizontalHeader().setOffsetToSectionPosition(0)
        # self.horizontalHeader().resizeSection(0, self.horizontalHeader().sectionSize(0)+20)
        self.horizontalHeader().setCascadingSectionResizes(True)
        self.verticalHeader().setCascadingSectionResizes(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setMinimumSectionSize(50)
        header_css = u'border-radius: 1px; border: 1px dashed blue;'
        self.horizontalHeader().setStyleSheet(header_css)
        self.verticalHeader().setStyleSheet(header_css+u'padding:-2px')
        self.setColumnCount(len(header_text_li))
        self.setHorizontalHeaderLabels(header_text_li)
        self.setAlternatingRowColors(True)
        self.setAutoScroll(True)
        self.setStyleSheet(u'alternate-background-color: #ADADAD; background-color: silver;'
                           u'border-radius: 10%; border: 1px solid #1E54B1; color: #1E54B1; font-size: 13px')
    def set_event_ss(self):
        self.setAlternatingRowColors(False)
        self.setStyleSheet(u'alternate-background-color: #0688FF; background-color: #1A1A1B;'
                           u'border-radius: 10%; border: 1px solid #1E54B1; color: #1E54B1')
    def add_span_row(self, text, span = True):
        self.__row_count+=1
        self.setRowCount(self.__row_count)
        time_label = TableLabel(text)
        time_label.setStyleSheet(u'color: #D3D3D3; background-color: #323C3D;font-size: 14px;'
                           u'border-top-left-radius: 30%; padding-right: 15px;padding-left: 15px')
        self.setCellWidget(self.__row_count-1,0, time_label)
        if span:
            time_label.setAlignment(QtCore.Qt.AlignCenter)
            time_label.setMinimumHeight(20)
            self.setSpan(self.__row_count-1,0,1,self.columnCount())

    def add_action_row(self, row_li, time_ = True):
        if time_:
            time_ = time.strftime(u"%H:%M:%S  \n%d.%m.%y")
        self.add_span_row(time_, False)
        for i, cell in enumerate(row_li):
            self.setCellWidget(self.__row_count-1,i+1, TableLabel(cell))
    def add_widgets_row(self, widgets_row):
        self.__row_count+=1
        self.setRowCount(self.__row_count)
        for i, cell in enumerate(widgets_row):
            self.setCellWidget(self.__row_count-1,i, cell)
    def add_row(self, row_li):
        self.__row_count+=1
        self.setRowCount(self.__row_count)
        for i, cell in enumerate(row_li):
            self.setItem(self.__row_count-1,i, QtGui.QTableWidgetItem(cell))

    def clear_all(self):
        self.__row_count = 0
        # self.clearContents()
        self.reset()
        self.clearSpans()
        self.setRowCount(1)


class SettingsTable(Table):
    def __init__(self, header_li, parent = None):
        Table.__init__(self, header_li, parent)
        self.horizontalHeader().resizeSection(0, self.horizontalHeader().sectionSize(0)+80)
        self.horizontalHeader().setResizeMode(1, True)
        self.verticalHeader().setHidden(True)
        self.setMinimumWidth(40)

class TableLabel(QtGui.QTextEdit):
    def __init__(self, data):
        QtGui.QTextEdit.__init__(self)
        self.setText(data)
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.setMinimumHeight(40)
        self.setMinimumWidth(200)
        self.setStyleSheet(u'color: #AAAAAA; background-color: #22232F; border: 1.5px solid #C10000;'
                           u'border-bottom-right-radius: 30%; font-size: 14px;'
                           u' padding-right: 10px;padding-left: 15px')

class StyledButton(QtGui.QPushButton):
    def __init__(self, title, parent = None):
        QtGui.QPushButton.__init__(self,title, parent)
        self.setMaximumHeight(30)
        self.setStyleSheet(u'background-color: #A0A0A0; border: 1.5px dotted #C10000; margin:2px;'
                           u'border-top-left-radius: 20%;border-top-right-radius: 20%; padding:0px;'
                           u'border-bottom-left-radius: 1%;border-bottom-right-radius: 1%;'
                           u'padding-right: 20px; padding-left: 20px;font-size: 12px;')

class TableWidget(QtGui.QWidget):
    def __init__(self, title, parent = None, with_clear = True):
        QtGui.QWidget.__init__(self, parent)
        self.table = Table(title, parent)
        self.box = QtGui.QGridLayout(self)
        self.box.addWidget(self.table,0,0,21,21)
        if with_clear:
            self.clear_btn = StyledButton(WidgNames.btn_clear, parent)
            self.box.addWidget(self.clear_btn,19,10,2,2)
            self.connect(self.clear_btn, QtCore.SIGNAL(u"clicked()"), self.table.clear_all)
            self.hide()
    def clear_all(self):
        self.table.clear_all()




if __name__ == u'__main__':
    app = QtGui.QApplication(sys.argv)
    exp_maker = MainWindow()
    app.exec_()
    rm_temp_db()
