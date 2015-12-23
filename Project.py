#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Aleksei Konkov'

import time
import sys
import shutil
import os.path
import cPickle as pickle
import pyodbc

from PyQt4 import QtGui, QtCore

from Expl import Control, Convert, ExpA, FormB, Sprav, SaveToXL
from Titles import Events, ToolTip, WName, ErrMessage, LoadMessg

project_dir = os.getcwd()
spr_dir = u'%s\\Spr\\'% project_dir
spr_default_path = u'%sDefaultSpr.pkl'%spr_dir
tempDB_path = u'%stempDbase.mdb' % spr_dir
xls_templates_dir = u'%sxls_forms' % spr_dir

def rm_temp_db(file_rm = tempDB_path):
    if os.path.isfile(file_rm):
        os.remove(file_rm)

class MainActiveThread(QtCore.QThread):
    def __init__(self, parent = None):
        super(MainActiveThread, self).__init__(parent)
        self.sh = Sprav.SpravHolder()
        self.current_sprav_dict = None
        self.__op = None
        self.__file_path = None
        self.spr_path_info = None
        self.__args = []

    def change_op(self, file_path, num_op, args):
        """
        :param file_path:
        :param num_op: int num of sprav menu exits
        :param args: if need
        """
        self.__op = num_op
        self.__file_path = file_path
        self.__args = args

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
                exp_data = pickle.load(inp)
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
                pickle.dump(self.__args[0], output, 2)
            self.__args = []
            self.emit(QtCore.SIGNAL(u'successfully_saved(const QString&)'),Events.session_saved % self.__file_path)
        except:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'),ErrMessage.bad_session)

    def load_work_db(self):
        message = self.pre_control()
        if message:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), message)
        else:
            self.emit(QtCore.SIGNAL(u'db_file_opened()'))

    def pre_control(self):
        try:
            contr = Control.DbControl(self.__file_path, tempDB_path)
        except shutil.Error:
            return ErrMessage.shutil_err
        if not contr.can_connect():
            return ErrMessage.no_db_conn % self.__file_path
        try:
            failed_table = contr.is_tables_exist()
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
                    msg=ErrMessage.bgd_lost_fields(tab, fields)
                    self.emit(QtCore.SIGNAL(u'control_warning(const QString&)'), msg)
                return ErrMessage.field_control_failed
            if contr.is_empty_f_pref():
                self.emit(QtCore.SIGNAL(u'control_warning(const QString&)'), ErrMessage.warning_no_pref)
            return False
        except Exception as err:
            return err


    def set_spr_changes(self, change_di):
        if self.sh.set_parameters(change_di):
            self.current_sprav_dict = change_di
            if self.__op == 1:
                self.spr_path_info = u'Default'
            else:
                self.spr_path_info = self.__file_path
            self.emit(QtCore.SIGNAL(u'sprav_holder(PyQt_PyObject)'), self.sh)
        else:
            if self.current_sprav_dict:
                self.sh.set_parameters(self.current_sprav_dict)
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.sh_not_changed)
            else:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_wrong_default)

    def load_pkl_op1_2(self):
        try:
            with open(self.__file_path, 'rb') as inp:
                loaded_data = pickle.load(inp)
                inp.close()
            loading_password = loaded_data.pop()
            if loading_password == u'Sprav':
                new_spr_di = loaded_data[0]
                self.set_spr_changes(new_spr_di)
            else:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'),ErrMessage.spr_not_valid)
        except IOError:
            if self.__op == 1:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_default_io_error)
            else:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_io_error)
        except Exception as ex:
            #TODO: rename error message and add exceptions
            print ex
            self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_err_in_data)


    def load_mdb_op3(self):
        try:
            self.control_db()
            sprav_data = self.sh.get_data_from_db(self.__file_path)
            sprav_data[u"create_time"] = time.strftime(u"%H:%M__%d.%m.%Y")
            self.set_spr_changes(sprav_data)
        except Sprav.SpravError as se:
            print se.text
            self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), unicode(se.text))

    def save_pkl_op4(self):
        if self.__file_path:
            if self.__file_path[-4:] != u'.pkl':
                self.__file_path+= u'.pkl'
            try:
                with open(self.__file_path,u'wb') as output:
                    pickle.dump([self.current_sprav_dict, u"Sprav"], output, 2)
                    self.emit(QtCore.SIGNAL(u'successfully_saved(const QString&)'), Events.spr_saved)
            except:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_not_saved)



    def control_db(self, full=True):
        sprav_contr = Sprav.SpravControl(self.__file_path, full)
        if sprav_contr.s_conn.has_dbc:
            if sprav_contr.losttables:
                pos = u'ет таблица' if len(sprav_contr.losttables) == 1 else u'ют таблицы'
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.bdg_lost_tables % (pos,unicode(sprav_contr.losttables)[1:-1]))
            elif sprav_contr.badfields:
                for key, failes in sprav_contr.badfields.items():
                    self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.bgd_lost_fields(key, failes))
            else:
                pass
                #TODO: make exp structure control here. {f_num : not Null; Expa_f_str.f_num : LandCodes.NumberGRAF WHERE f_num is NUll
        else:
            self.emit(QtCore.SIGNAL(u'failure_conn(const QString&)'), ErrMessage.no_db_conn % self.__file_path)

class ControlThread(QtCore.QThread):
    def __init__(self, sprav, db_path, parent = None):
        super(ControlThread, self).__init__(parent)
        self.db_file = db_path
        self.sprav_holder = sprav

    def run(self):
        try:
            contr = Control.DataControl(self.sprav_holder, self.db_file, tempDB_path)
        except Exception as Err:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), Err.message)
        else:
            err_li = contr.run_field_control()
            if err_li:
                self.emit(QtCore.SIGNAL(u'contr_failed(PyQt_PyObject)'), err_li)
            else:
                self.emit(QtCore.SIGNAL(u'control_passed()'))

class ConvertThread(QtCore.QThread):
    def __init__(self, sprav, parent = None):
        super(ConvertThread, self).__init__(parent)
        self.sprav_holder = sprav
    def run(self):
        try:
            converted_data = Convert.convert(self.sprav_holder, tempDB_path)
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
    def __init__(self, edbf, rows, sprav_holder, xl_settings, parent = None):
        super(ExpAThread, self).__init__(parent)
        self.exp_file = edbf
        self.expsA = ExpA.ExpFA(self.exp_file, rows, sprav_holder)
        self.exp_tree = self.expsA.make_exp_tree()
        self.output_mode = True
        self.xl_settings = xl_settings

    def set_output_mode(self, is_xls):
        self.output_mode = is_xls

    def run(self):
        errs_occured = self.expsA.calc_all_exps()
        if errs_occured:
            for key in errs_occured:
                msg = ErrMessage.expa_errors[key] % errs_occured[key]
                self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), msg)
        xl_matrix = self.expsA.prepare_svodn_xl()
        exl_file_name = u'fA_%s_%s.xlsx' % (os.path.basename(self.exp_file)[4:-4],time.strftime(u"%d-%m-%Y"))
        exl_file_path = os.path.dirname(self.exp_file)+'\\'+ exl_file_name
        if self.output_mode:
            try:
                SaveToXL.exp_matrix(xl_matrix, save_as = exl_file_path, start_f = self.xl_settings[u'a_sv_l'], start_r = self.xl_settings[u'a_sv_n'],templ_path = self.xl_settings[u'a_sv_path'])
            except SaveToXL.XlsIOError as err:
                if err.err_type == 1:
                    self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), ErrMessage.xl_template_not_found %err.args[0][0] )
                elif err.err_type == 2:
                    self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), ErrMessage.xl_already_opened % exl_file_path)
            else:
                self.emit(QtCore.SIGNAL(u'success()'))
        else:
            self.expsA.fill_razv_edb(xl_matrix)
            err_message = self.expsA.has_error()
            if err_message:
                self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), ErrMessage.e_table_exist % err_message)
            else:
                self.emit(QtCore.SIGNAL(u'success()'))


class ExpBThread(QtCore.QThread):
    def __init__(self, edbf, rows, sprav, xl_settings, parent = None):
        super(ExpBThread, self).__init__(parent)
        self.sprav = sprav
        self.exp_file = edbf
        self.rows = rows
        self.out_xl_mode = True
        self.xl_settings = xl_settings

    def set_output_mode(self, is_xls):
        self.out_xl_mode = is_xls

    def prepare_b_matr(self, b_dict):
        matr = []
        fields_d = {}
        for key, val in self.sprav.expb_f_str.items():
            fields_d[val[u'f_num']] = key
        srt_fields = map(lambda x: fields_d[x], sorted(fields_d))
        for r_key in sorted(b_dict):
            m_row  = []
            for f_key in srt_fields:
                m_row.append(b_dict[r_key][f_key])
            matr.append(m_row)
            if r_key == u'28':
                matr.append([u'',]*len(m_row))
        return matr

    def run(self):
        ExpB = FormB.ExpFormaB(self.exp_file, self.rows, self.sprav )
        b_rows_dict = ExpB.create_exp_dict()
        if self.out_xl_mode:
            exl_file_name = u'fB_%s_%s.xlsx' % (os.path.basename(self.exp_file)[4:-4],time.strftime(u"%d-%m-%Y"))
            exl_file_path = os.path.dirname(self.exp_file)+u'\\'+ exl_file_name
            b_rows_dict = self.prepare_b_matr(b_rows_dict)
            try:
                SaveToXL.exp_matrix(b_rows_dict, save_as = exl_file_path, start_f = self.xl_settings[u'b_l'], start_r = self.xl_settings[u'b_n'],templ_path = self.xl_settings[u'b_path'])
            except SaveToXL.XlsIOError as err:
                if err.err_type == 1:
                    self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), ErrMessage.xl_template_not_found %err.args[0][0] )
                elif err.err_type == 2:
                    self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), ErrMessage.xl_already_opened % exl_file_path)
            else:
                self.emit(QtCore.SIGNAL(u'success()'))
        else:
            created_fields = ExpB.create_e_table()
            if created_fields:
                ExpB.run_mdb_exp(b_rows_dict, created_fields)
                self.emit(QtCore.SIGNAL(u'success()'))
            else:
                self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), ErrMessage.table_add_failed)


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

class MyWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle(WName.main_name)
        self.resize(1300, 640)
        self.central_widget = QtGui.QFrame(self)
        self.central_widget.setFrameShape(QtGui.QFrame.StyledPanel)
        self.central_widget.setFrameShadow(QtGui.QFrame.Raised)
        self.gridLayout = QtGui.QGridLayout(self.central_widget)
        self.l1 = QtGui.QLabel(WName.l1_title,self.central_widget)
        self.l2 = QtGui.QLabel(WName.l2_title,self.central_widget)
        self.l3 = QtGui.QLabel(WName.l3_title,self.central_widget)
        self.l4 = QtGui.QLabel(WName.l4_title,self.central_widget)
        self.sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.control_btn = QtGui.QPushButton(WName.btn_control,self.central_widget)
        self.control_btn.setToolTip(ToolTip.btn_control)
        self.control_btn.setSizePolicy(self.sizePolicy)
        self.convert_btn = QtGui.QPushButton(WName.btn_control,self.central_widget)
        self.convert_btn.setToolTip(ToolTip.btn_convert)
        self.convert_btn.setSizePolicy(self.sizePolicy)
        self.exp_a_btn = QtGui.QPushButton(WName.btn_exp,self.central_widget)
        self.exp_a_btn.setToolTip(ToolTip.btn_exp_a)
        self.exp_a_btn.setSizePolicy(self.sizePolicy)
        self.btn_a_all = QtGui.QPushButton(WName.btn_a_sv,self.central_widget)
        self.btn_a_all.setToolTip(ToolTip.btn_a_sv)
        self.btn_a_tree = QtGui.QPushButton(WName.btn_a_ch,self.central_widget)
        self.btn_a_tree.setToolTip(ToolTip.btn_a_ch)
        self.btn_a_tree.setSizePolicy(self.sizePolicy)
        self.btn_a_all.setSizePolicy(self.sizePolicy)
        self.btn_a_all.setHidden(True)
        self.btn_a_tree.setHidden(True)
        self.exp_b_btn = QtGui.QPushButton(WName.btn_exp,self.central_widget)
        self.exp_b_btn.setToolTip(ToolTip.btn_exp_b)
        self.exp_b_btn.setSizePolicy(self.sizePolicy)
        self.event_table = TableWidget(WName.event_table_head, self.central_widget)
        self.event_table.show()
        self.event_table.table.set_event_ss()
        self.control_table = TableWidget(WName.control_table_head, self.central_widget)
        self.convert_table = TableWidget(WName.convert_table_head, self.central_widget)
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
        self.expa_box.addWidget(self.treeView,1,0,21,21)
        self.expa_box.addWidget(self.group_box,0,20,1,1)

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
        self.connect(self.control_btn, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"click_control_btn()"))
        self.connect(self.convert_btn, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"click_convert_btn()"))
        self.connect(self.exp_a_btn, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"click_exp_a_btn()"))
        self.connect(self.btn_a_all, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"click_a_svodn_btn()"))
        self.connect(self.btn_a_tree, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"click_a_tree_btn()"))
        self.connect(self.exp_b_btn, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"click_exp_b_btn()"))
        self.sprav_holder = None
        self.bold_font = QtGui.QFont()
        self.normal_font = QtGui.QFont()
        self.set_fonts_properties()
        self.set_widgets_font()
        self.set_sources_widgets()
        self.__is_session = False
        self.set_default_params()
        self.load_thr = LoadingThread()
        self.db_file = None

        self.main_load_save_thr = MainActiveThread()
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'sprav_holder(PyQt_PyObject)'), self.set_sprav_holder)
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'spr_error_occured(const QString&)'), self.show_sprav_error)
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), self.load_save_db_err)
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'control_warning(const QString&)'), self.show_error)
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'successfully_saved(const QString&)'), self.say_saved)
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'session_loaded(PyQt_PyObject)'), self.session_loaded)
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'db_file_opened()'), self.db_file_opened)
        self.connect(self.main_load_save_thr, QtCore.SIGNAL(u'finished()'), self.on_finished)
        self.__is_xls_mode = True
        self.show()
        self.run_main_thr()
        self.xls_settings_d = {
            'a_sv_l':u'A',
            'a_sv_n':1,
            'a_l':u'A',
            'a_n':2,
            'a_obj_l':u'A',
            'a_obj_n':1,
            'b_l':u'C',
            'b_n':3,
            'a_path': u'%s\\FA.xlsx' % xls_templates_dir,
            'a_sv_path': u'%s\\FA_svod.xlsx' % xls_templates_dir,
            'b_path': u'%s\\FB.xlsx' % xls_templates_dir
        }
        try:
            self.setStyleSheet((open(u'%s\\Style\\ss.css' % project_dir).read()))
        except IOError:
            self.show_error(ErrMessage.no_css)

    def set_default_params(self):
        self.__a_thr_reinit = False
        if not self.__is_session:
            self.e_db_file = None
            self.explication_data = None
        self.current_exp_data = None
        self.ate_expl_data_dict = None
        self.control_thr =None
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
        self.export_frame.hide()
        self.save_widget.hide()
        self.src_widget.set_lbl_text(self.db_file)
        # self.src_widget.lbl.repaint()
        self.group_box.setHidden(not self.__is_session)

    def set_sources_widgets(self):
        self.export_frame = ExportFrame()
        self.src_widget = SrcFrame()
        self.gridLayout.addWidget(self.src_widget, 0,0,1,2)
        self.src_widget.set_lbl_text(WName.src_widg)
        self.export_frame.hide()
        self.gridLayout.addWidget(self.export_frame, 9,0,1,2)
        self.save_widget = SrcFrame(u'#9556FF')
        self.save_widget.set_lbl_text(WName.save_widg)
        self.save_widget.hide()
        self.gridLayout.addWidget(self.save_widget, 10,0,1,2)
        self.connect(self.export_frame.rbtn_mdb, QtCore.SIGNAL(u'clicked()'), self.set_mdb_mode)
        self.connect(self.export_frame.rbtn_xls, QtCore.SIGNAL(u'clicked()'), self.set_xls_mode)
        self.connect(self.src_widget.btn, QtCore.SIGNAL(u'clicked()'), self.open_file)
        self.connect(self.export_frame.e_src_widget.btn, QtCore.SIGNAL(u'clicked()'), self.get_edbf_name)
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

    def block_btns(self, blocked = True):
        self.control_btn.blockSignals(blocked)
        self.convert_btn.blockSignals(blocked)
        self.exp_a_btn.blockSignals(blocked)
        self.exp_b_btn.blockSignals(blocked)
        self.btn_a_all.blockSignals(blocked)
        self.group_box.setDisabled(blocked)
        self.src_widget.setDisabled(blocked)
        self.export_frame.setDisabled(blocked)
        self.save_widget.setDisabled(blocked)

    def set_menu_properties(self):
        main_exit1 = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\add.png' % project_dir), WName.exit_main_1, self)
        main_exit2 = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\stop1.png' % project_dir), WName.exit_main_2, self)
        main_exit1.setShortcut(u'Ctrl+O')
        main_exit1.setStatusTip(ToolTip.exit_main_1)
        main_exit2.setShortcut(u'Ctrl+Q')
        main_exit2.setStatusTip(ToolTip.exit_main_2)

        spr_default = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\refresh.png' % project_dir), WName.exit_spr_1, self)
        spr_choose_pkl = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\refresh.png' % project_dir), WName.exit_spr_2, self)
        spr_choose_mdb = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\exclamation.png' % project_dir), WName.exit_spr_3, self)
        spr_save_spr = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\exclamation.png' % project_dir), WName.exit_spr_4, self)
        spr_info = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\exclamation.png' % project_dir), WName.exit_spr_6, self)
        spr_default.setStatusTip(ToolTip.exit_spr_1)
        spr_choose_pkl.setStatusTip(ToolTip.exit_spr_2)
        spr_choose_mdb.setStatusTip(ToolTip.exit_spr_3)
        spr_save_spr.setStatusTip(ToolTip.exit_spr_4)
        spr_info.setStatusTip(ToolTip.exit_spr_5)

        spr_default.setShortcut(u'Ctrl+D')
        spr_choose_pkl.setShortcut(u'Ctrl+P')
        spr_choose_mdb.setShortcut(u'Ctrl+M')
        spr_save_spr.setShortcut(u'Ctrl+S')

        self.connect(main_exit2, QtCore.SIGNAL(u'triggered()'), QtGui.qApp, QtCore.SLOT(u'quit()'))
        self.connect(main_exit1, QtCore.SIGNAL(u'triggered()'), self.open_file)

        self.connect(spr_default, QtCore.SIGNAL(u'triggered()'), self.run_main_thr)
        self.connect(spr_choose_pkl, QtCore.SIGNAL(u'triggered()'), lambda: self.load_sprav(True))
        self.connect(spr_choose_mdb, QtCore.SIGNAL(u'triggered()'), self.load_sprav)
        self.connect(spr_save_spr, QtCore.SIGNAL(u'triggered()'), self.save_sprav)
        self.connect(spr_info, QtCore.SIGNAL(u'triggered()'), self.show_spr_info)
        menu = self.menuBar()
        menu_file = menu.addMenu(WName.menu_1)
        menu_sprav = menu.addMenu(WName.menu_2)
        menu_file.addAction(main_exit1)
        menu_file.addAction(main_exit2)
        menu_sprav.addAction(spr_default)
        menu_sprav.addAction(spr_choose_pkl)
        menu_sprav.addAction(spr_choose_mdb)
        menu_sprav.addAction(spr_save_spr)
        menu_sprav.addAction(spr_info)

    def open_file(self):
        self.db_file = unicode(QtGui.QFileDialog(self).getOpenFileName(self, WName.open_file, project_dir, options=QtGui.QFileDialog.DontUseNativeDialog))
        if self.db_file:
            if self.db_file[-4:] == u'.mdb':
                self.run_main_thr(self.db_file, op = 0)
            elif self.db_file[-4:] == u'.pkl':
                self.run_main_thr(self.db_file, op = 5)
            else:
                self.show_error(ErrMessage.wrong_file)

    def db_file_opened(self):
        self.__is_session = False
        self.set_default_params()
        self.reset_parameters()
        self.add_event_log(Events.opened_file % self.db_file)
        self.add_event_log(Events.db_has_data % self.db_file.split(u'/')[-1], False)

    def session_loaded(self, exp_data):
        self.__is_session = True
        self.set_default_params()
        self.reset_parameters()
        loaded_path = exp_data.pop()
        self.explication_data = exp_data
        self.current_exp_data = exp_data[:]
        self.add_event_log(Events.session_loaded % self.db_file)
        self.e_db_file = loaded_path
        e_src_dir =  u'\\'.join(self.e_db_file.split(u'\\')[:-1])
        if os.path.isdir(e_src_dir):
            self.export_frame.e_src_widget.set_lbl_text(e_src_dir)
        else:
            self.show_error(ErrMessage.session_path_not_found%loaded_path)
            self.get_edbf_name()
        self.show_first_combo()

    def save_session(self):
        default_name = self.e_db_file.split(u'\\')[-1][4:-4]+time.strftime(u'_%d_%m_%y') + u'.pkl'
        save_file = unicode(QtGui.QFileDialog(self).getSaveFileName(self, WName.save_dialog, default_name, options=QtGui.QFileDialog.DontUseNativeDialog))
        if save_file:
            if save_file[-4:] != u'.pkl':
                save_file+= u'.pkl'
            exp_data = self.explication_data[:]
            exp_data.extend([self.e_db_file, u'Salt'])
            self.run_main_thr(save_file, 6, exp_data)

    def set_xls_mode(self):
        self.__is_xls_mode= True

    def set_mdb_mode(self):
        self.__is_xls_mode = False

    def ask_question(self, messag):
        reply = QtGui.QMessageBox.question(self, WName.ask_exit, messag,
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

    def enable_explications(self, converted_data):
        self.convert_thr = None
        self.on_finished()
        self.add_event_log(Events.convert_passed)
        self.convert_table.hide()
        self.exp_a_btn.setEnabled(True)
        self.exp_b_btn.setEnabled(True)
        self.explication_data = converted_data
        self.current_exp_data = self.explication_data[:]

    def show_first_combo(self):
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
        self.disconnect(self.group_box.first_cmb, QtCore.SIGNAL(u'currentIndexChanged (const QString&)'), self.first_combo_changed)
        self.connect(self.group_box.first_cmb, QtCore.SIGNAL(u'currentIndexChanged (const QString&)'), self.first_combo_changed)

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
        # self.group_box.second_cmb.set_width(ate_len*7)
        self.group_box.second_cmb.show()
        self.disconnect(self.group_box.second_cmb, QtCore.SIGNAL(u'currentIndexChanged (const QString&)'), self.second_combo_changed)
        self.connect(self.group_box.second_cmb, QtCore.SIGNAL(u'currentIndexChanged (const QString&)'), self.second_combo_changed)

    def first_combo_changed(self):
        curr_ind = self.group_box.get_first_index()
        self.hide_second_combo()
        if curr_ind != -1:
            if curr_ind == 0:
                self.current_exp_data = self.explication_data[:]
            else:
                curr_soato = self.cmb1_recover_d[curr_ind]
                self.current_exp_data[0] = self.ate_expl_data_dict[curr_soato]
                if self.group_soatos[curr_soato]:
                    self.show_second_combo(curr_soato)
            self.click_exp_a_btn(False)
            self.click_a_tree_btn()

    def hide_second_combo(self):
        self.group_box.second_cmb.hide()

    def second_combo_changed(self):
        curr_ind = self.group_box.get_second_index()
        if curr_ind != -1:
            curr_soato = self.cmb2_recover_d[curr_ind]
            if curr_ind == 0:
                self.current_exp_data[0] = self.ate_expl_data_dict[curr_soato]
            else:
                self.current_exp_data[0] = self.second_expl_data_dict[curr_soato]
            self.click_exp_a_btn(False)
            self.click_a_tree_btn()

    @staticmethod
    def _count_cmb_data_recovery(names, first_combo_row = u'Весь район', ate_kod = None):
        """ Input: names - list of tuples (name, soato)
            returns combo_box data , recovery dictionary to catch, which combo row was checked , max item length
        """
        if ate_kod:
            recovery_soato_d = {0:ate_kod}
        else:
            recovery_soato_d = {0:names[0][1][:-3]}
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

    def on_finished(self):
        self.load_thr.terminate()
        self.block_btns(False)
        self.statusBar().showMessage(LoadMessg.ready)

    def add_loading(self, load_message):
        self.block_btns()
        def set_status(dots):
            mes = load_message+dots
            self.statusBar().showMessage(mes)
        self.connect(self.load_thr, QtCore.SIGNAL(u's_loading(const QString&)'), set_status)
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
            file = unicode(QtGui.QFileDialog(self).getOpenFileName(self, WName.load_sprav+ u'*.pkl', project_dir, options=QtGui.QFileDialog.DontUseNativeDialog))
            op = 2
        else:
            file = unicode(QtGui.QFileDialog(self).getOpenFileName(self, WName.load_sprav+ u'*.mdb', project_dir, options=QtGui.QFileDialog.DontUseNativeDialog))
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
        self.load_thr.terminate()
        self.sprav_holder = sprav
        self.statusBar().showMessage(LoadMessg.ready)
        self.add_event_log(Events.load_sprav_success)

    def save_sprav(self):
        save_file = unicode(QtGui.QFileDialog(self).getSaveFileName(self, WName.save_dialog, options=QtGui.QFileDialog.DontUseNativeDialog))
        if save_file:
            self.add_loading(LoadMessg.spr_saving)
            self.run_main_thr(save_file,4)

    def say_saved(self, msg):
        self.load_thr.terminate()
        self.add_event_log(msg)
        self.statusBar().showMessage(LoadMessg.ready)

    def show_spr_info(self):
        csd = self.main_load_save_thr.current_sprav_dict
        if csd:
            s_date = csd[u'create_time']
            s_file = self.main_load_save_thr.spr_path_info
            message = Events.spr_info(s_date, s_file)
        else:
            message = ErrMessage.spr_not_loaded
        QtGui.QMessageBox.information(self, WName.sprav_info_box,message, u'Ok')


    @QtCore.pyqtSlot()
    def click_control_btn(self):
        self.add_event_log(Events.run_control)
        self.add_loading(LoadMessg.loading_control)
        self.control_thr = ControlThread(self.sprav_holder, self.db_file)
        self.connect(self.control_thr, QtCore.SIGNAL(u'control_passed()'), self.enable_convert)
        self.connect(self.control_thr, QtCore.SIGNAL(u'contr_failed(PyQt_PyObject)'), self.add_control_protocol)
        self.connect(self.control_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), self.show_error)
        self.connect(self.control_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), lambda:self.add_event_log(ErrMessage.control_failed))
        self.connect(self.control_thr, QtCore.SIGNAL(u'finished()'), self.on_finished)
        self.control_thr.start()

    @QtCore.pyqtSlot()
    def click_convert_btn(self):
        self.add_event_log(Events.run_convert)
        self.convert_thr = ConvertThread(self.sprav_holder)
        self.add_loading(LoadMessg.loading_convert)
        self.connect(self.convert_thr, QtCore.SIGNAL(u'convert_passed(PyQt_PyObject)'), self.enable_explications)
        self.connect(self.convert_thr, QtCore.SIGNAL(u'conv_failed(PyQt_PyObject)'), self.add_convert_protocol)
        self.connect(self.convert_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), self.show_error)
        self.convert_thr.start()

    def get_edbf_name(self):
        exp_dir = unicode(QtGui.QFileDialog(self).getExistingDirectory(self, WName.save_exp_dialog, project_dir, options=QtGui.QFileDialog.DontUseNativeDialog))
        if exp_dir:
            if self.__is_session:
                e_dbf = exp_dir + u'\\' + self.e_db_file.split(u'\\')[-1]
            else:
                e_dbf = exp_dir + u'\\Exp_' + self.db_file.split(u'/')[-1]
            if not self.__is_xls_mode:
                self.try_create_edb_file(e_dbf)
            self.export_frame.e_src_widget.set_lbl_text(exp_dir)
            self.e_db_file = e_dbf

    def try_create_edb_file(self, e_dbf):
        templ = u"%s\\template.mdb" % spr_dir
        if not os.path.isfile(e_dbf):
            if os.path.isfile(templ):
                try:
                    shutil.copyfile(templ, e_dbf)
                except IOError:
                    self.show_error(ErrMessage.wrong_file_path % e_dbf)
                except:
                    self.show_error(ErrMessage.err_create_file% e_dbf)
            else:
                self.show_error(ErrMessage.tmpl_empty)

    @QtCore.pyqtSlot()
    def click_a_svodn_btn(self):
        if self.try_has_edbf():
            self.add_loading(LoadMessg.wait_exp_a)
            self.add_event_log(Events.run_exp_a)
            if self.__a_thr_reinit:
                self.exp_a_thr = ExpAThread(self.e_db_file, self.current_exp_data,  self.sprav_holder, self.xls_settings_d)
            else: self.__a_thr_reinit = True
            self.connect(self.exp_a_thr, QtCore.SIGNAL(u'finished()'), self.on_finished)
            self.connect(self.exp_a_thr, QtCore.SIGNAL(u'success()'), lambda: self.add_event_log(Events.finish_exp_a))
            self.connect(self.exp_a_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), self.show_error)
            self.connect(self.exp_a_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), lambda: self.add_event_log(Events.exp_a_finished_with_err))
            self.exp_a_thr.set_output_mode(self.__is_xls_mode)
            self.exp_a_thr.start()


    @QtCore.pyqtSlot()
    def click_a_tree_btn(self):
        self.model = self.make_tree_model(self.exp_a_thr.exp_tree)
        self.model.setHorizontalHeaderLabels([WName.tree_header])
        self.treeView.setModel(self.model)
        self.treeView.setHidden(False)
        self.disconnect(self.treeView, QtCore.SIGNAL(u"activated(const QModelIndex &)"),self.tree_edit_cell)
        self.connect(self.treeView, QtCore.SIGNAL(u"activated(const QModelIndex &)"),self.tree_edit_cell)

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
            item_names = [u'%s%s' % (i.soato_inf, i.info) for i in all_exps[key]]
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

    def tree_edit_cell(self, qindex):
        if qindex.parent().isValid():
            data = self.exp_a_thr.exp_tree
            pressed_f22 = qindex.parent().row()
            pressed_exp = qindex.row()
            pressed_f22 = sorted(data.keys())[pressed_f22]
            indexes_before_sort = self.tree_index_dict[pressed_f22]
            exp_index = indexes_before_sort[pressed_exp]
            pressed_exp = data[pressed_f22][exp_index]
            pressed_exp.add_data(self.sprav_holder)
            SaveToXL.exp_single_fa(pressed_exp.exp_a_rows, u'%s_%s' % (pressed_f22, qindex.row()+1), pressed_exp.info, self.e_db_file, **self.xls_settings_d)

    @QtCore.pyqtSlot()
    def click_exp_a_btn(self, after_click = True):
        self.block_btns()
        self.__a_thr_reinit = False
        if not self.e_db_file:
            self.get_edbf_name()
        if self.e_db_file:
            self.exp_a_thr = ExpAThread(self.e_db_file, self.current_exp_data, self.sprav_holder, self.xls_settings_d)
            if self.export_frame.isHidden():
                self.export_frame.show()
                self.save_widget.show()
                self.group_box.show()
            self.btn_a_all.setHidden(False)
            self.btn_a_tree.setHidden(False)
            self.exp_a_btn.setHidden(True)
            if after_click:
                self.show_first_combo()
        self.block_btns(False)

    @QtCore.pyqtSlot()
    def click_exp_b_btn(self):
        if not self.e_db_file:
            self.get_edbf_name()
        if self.e_db_file and self.try_has_edbf():
            if self.export_frame.isHidden():
                self.export_frame.show()
                self.save_widget.show()
            self.add_loading(LoadMessg.wait_exp_b)
            self.add_event_log(Events.run_exp_b)
            self.exp_b_thr = ExpBThread(self.e_db_file, self.explication_data[0], self.sprav_holder, self.xls_settings_d)
            self.connect(self.exp_b_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), self.show_error)
            self.connect(self.exp_b_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), lambda:self.add_event_log(Events.exp_b_finished_with_err))
            self.connect(self.exp_b_thr, QtCore.SIGNAL(u'finished()'), self.on_finished)
            self.connect(self.exp_b_thr, QtCore.SIGNAL(u'success()'), lambda:self.add_event_log(Events.finish_exp_b))
            self.exp_b_thr.set_output_mode(self.__is_xls_mode)
            self.exp_b_thr.start()

    def add_event_log(self, text, with_time = True):
        if with_time:
            self.event_table.table.add_action_row([text])
        else: self.event_table.table.add_action_row([text],u'- // -')

    def add_control_protocol(self, data_li):
        self.control_thr = None
        self.control_table.show()
        event_time = time.strftime(u"%d.%m.%y  %H:%M:%S"  )
        self.add_event_log(Events.control_failed)
        self.control_table.table.add_span_row(event_time)
        err_descriptions = ErrMessage.control_protocol
        for err in data_li:
            errors = unicode(tuple(err[u'err_ids']))
            err_code = err['err_msg']
            if err[u'dyn_param']:
                err_msg = err_descriptions[err_code](err[u'dyn_param'])
            else:
                err_msg = err_descriptions[err_code]
            self.control_table.table.add_row([err[u'table'],err[u'field'], u'OBJECTID in %s' % errors, err_msg])

    def add_convert_protocol(self, data_di):
        self.convert_btn.setDisabled(True)
        self.on_finished()
        self.convert_table.show()
        event_time = time.strftime(u"%d.%m.%y  %H:%M:%S"  )
        self.add_event_log(Events.convert_failed)
        self.convert_table.table.add_span_row(event_time)
        for key in data_di:
            errors = unicode(tuple(data_di[key]))
            self.convert_table.table.add_row([unicode(key), u'OBJECTID in %s' % errors, ErrMessage.convert_errors[key]])

    def try_has_edbf(self):
        if self.__is_xls_mode or self.try_to_connect(self.e_db_file):
            return True
        self.try_create_edb_file(self.e_db_file)
        if self.try_to_connect(self.e_db_file):
            return True
        else:
            self.show_error(ErrMessage.failed_edb_conn)
            return False

    @staticmethod
    def try_to_connect(db_file):
        try:
            db = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' % db_file
            conn = pyodbc.connect(db, autocommit = True, unicode_results = True)
            dbc = conn.cursor()
            dbc.close()
            conn.close()
            return True
        except pyodbc.Error :
            return False

    def show_error(self, err_text):
        QtGui.QMessageBox.critical(self, WName.error, u"%s" % err_text,u'Закрыть')

class ExportFrame(QtGui.QFrame):
    def __init__(self, parent = None):
        QtGui.QFrame.__init__(self, parent)
        self.color = u'#D3D120'
        self.setStyleSheet(u'background-color: #959BA8; border-radius: 15%;')
        self.rbtn_xls = QtGui.QRadioButton(u'*.xls',self)
        self.rbtn_xls.setIcon(QtGui.QIcon(u'%s\\Images\\excel.ico' % project_dir))
        self.rbtn_xls.setChecked(True)
        self.rbtn_xls.setFont(QtGui.QFont('Verdana',10))
        self.rbtn_mdb = QtGui.QRadioButton(u'*.mdb',self)
        self.rbtn_mdb.setIcon(QtGui.QIcon(u'%s\\Images\\access.ico' % project_dir))
        self.rbtn_mdb.setFont(QtGui.QFont('Verdana',10))
        self.rbtn_style = u'background-color: white; color: green;' \
                          u' border-top-right-radius: 3%;' \
                          u'border-bottom-left-radius: 3%; padding: 3px;' \
                          u' border: 2px solid' + self.color
        self.lbl_style = u'background-color: #49586B; color: white;' \
                          u' border-top-left-radius: 23%;' \
                          u' border-top-right-radius: 23%;' \
                          u' border-bottom-left-radius: 23%;' \
                          u' border-bottom-right-radius: 3%;' \
                          u' padding-left: 10px;' \
                          u' border: 2px solid '+self.color
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

    def set_lbl_text(self, text):
        """
        В строке text делается перенос относительно / если длина превышает 40 символов
        """
        path_parts = text.split(u'/')
        text = path_parts.pop(0)
        if path_parts:
            text+=u''
            temp_text = u''
            for part in path_parts:
                part = u'\\%s' % part
                if len(part) + len(temp_text) >40:
                    text+=u'%s\n'% temp_text
                    temp_text = part
                else:
                    temp_text+=part
            text+=temp_text
        self.lbl.setText(text)
        self.lbl.repaint()

class CombBox(QtGui.QComboBox):
    def __init__(self, parent = None, width = 160, data = u'A'):
        QtGui.QComboBox.__init__(self, parent)
        self.change_data(data)
        self.hide()
        self.setStyleSheet(u'font-size: 12px')
        self.set_width(width)
        self.setMaxVisibleItems(30)
    def set_width(self, width):
        self.setFixedWidth(width)
    def change_data(self, new_data):
        self.clear()
        self.addItems(new_data)

class GroupBox(QtGui.QFrame):
    def __init__(self, parent = None, border_color = u'#C3FFF1'):
        QtGui.QFrame.__init__(self, parent)
        self.setMaximumHeight(33)
        self.setStyleSheet(u'background-color: #2558FF; border-top-left-radius: 30%;border-bottom-right-radius: 30%; padding-right: 5px;padding-left: 5px')
        self.h_box = QtGui.QHBoxLayout(self)
        self.first_cmb = CombBox(self)
        self.first_cmb.show()
        self.second_cmb = CombBox(self)
        self.first_cmb.setStyleSheet(u'border-radius: 5% ; border: 1px solid '+ border_color)
        self.second_cmb.setStyleSheet(u'border-radius: 5% ; border: 2px solid '+ border_color)
        self.lbl = QtGui.QLabel(WName.lbl_group, self)
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
        self.horizontalHeader().setStretchLastSection(True)
        # qsize =QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        # self.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.horizontalHeader().setOffsetToSectionPosition(1)
        self.horizontalHeader().setCascadingSectionResizes(True)
        self.horizontalHeader().setMinimumSectionSize(130)
        header_css = u'border-radius: 1px; border: 1px dashed blue;'
        self.horizontalHeader().setStyleSheet(header_css)
        self.verticalHeader().setStyleSheet(header_css+u'padding:-2px')
        self.verticalHeader().setCascadingSectionResizes(True)
        # self.setWindowTitle(u"Text LOG")
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
        time_label.setStyleSheet(u'color: #AAAAAA; background-color: #22232F;font-size: 14px;'
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
    def __init__(self, title, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.table = Table(title, parent)
        self.clear_btn = StyledButton(WName.btn_clear, parent)
        self.box = QtGui.QGridLayout(self)
        self.box.addWidget(self.table,0,0,21,21)
        self.box.addWidget(self.clear_btn,19,10,2,2)
        self.connect(self.clear_btn, QtCore.SIGNAL(u"clicked()"), self.table.clear_all)
        self.hide()
if __name__ == u'__main__':
    app = QtGui.QApplication(sys.argv)
    exp_maker = MyWindow()
    app.exec_()
    rm_temp_db()
