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

from Titles import Message, ToolTip, WName
from Expl import Control, Convert, ExpA, FormB, Sprav
from Expl.DefaultSprav import default
from Expl.SaveToXL import exp_single_fa, export_toxl_fb, exp_svodn_fa

project_path = os.getcwd()

def rm_temp_db(file_rm = Control.tempDB_path):
    if os.path.isfile(file_rm):
        os.remove(file_rm)



class ControlThread(QtCore.QThread):
    def __init__(self, dbf, sprav, parent = None):
        super(ControlThread, self).__init__(parent)
        self.db_file = dbf
        self.sprav_holder = sprav

    def run(self):
        contr = Control.DataControl(self.db_file, self.sprav_holder)
        if not contr.shutil_err:
            err_li = contr.run_field_control()
            contr.close_conn()
            if err_li:
                self.emit(QtCore.SIGNAL(u'contr_failed(PyQt_PyObject)'), err_li)
            else:
                self.emit(QtCore.SIGNAL(u'controlpassed'))
        # else: pass #TODO: catch error

class ConvertThread(QtCore.QThread):
    def __init__(self, sprav, parent = None):
        super(ConvertThread, self).__init__(parent)
        self.converted_data = []
        self.sprav_holder = sprav
    def run(self):
        dict_with_err, self.converted_data = Convert.convert(self.sprav_holder)
        if dict_with_err:
            self.emit(QtCore.SIGNAL(u'conv_failed(PyQt_PyObject)'), dict_with_err)
        else:
            self.emit(QtCore.SIGNAL(u'convertpassed'))
    def __del__(self):
        rm_temp_db()

class ExpAThread(QtCore.QThread):
    def __init__(self, edbf, rows, sprav_holder, parent = None):
        super(ExpAThread, self).__init__(parent)
        self.exp_file = edbf
        self.expsA = ExpA.ExpFA(self.exp_file, rows, sprav_holder)
        self.exp_tree = self.expsA.make_exp_tree()
        self.output_mode = True

    def set_output_mode(self, is_xls):
        self.output_mode = is_xls
    def run(self):
        self.expsA.calc_all_exps()
        xl_matrix = self.expsA.prepare_svodn_xl()
        exl_file_name = u'fA_%s_%s.xlsx' % (os.path.basename(self.exp_file)[4:-4],time.strftime(u"%d-%m-%Y"))
        exl_file_path = os.path.dirname(self.exp_file)+'\\'+ exl_file_name
        if self.output_mode:
            try:
                exp_svodn_fa(xl_matrix,exl_file_path)
            except IOError:
                self.emit(QtCore.SIGNAL(u'already_opened(const QString&)'), Message.xl_already_opened % exl_file_path)
        else:
            self.expsA.fill_razv_edb(xl_matrix)
            err_message = self.expsA.has_error()
            if err_message: self.emit(QtCore.SIGNAL(u'err1(const QString&)'), Message.e_table_exist % err_message)

class ExpBThread(QtCore.QThread):
    def __init__(self, edbf, rows, sprav, parent = None):
        super(ExpBThread, self).__init__(parent)
        self.sprav = sprav
        self.exp_file = edbf
        self.rows = rows
        self.output_mode = True

    def set_output_mode(self, is_xls):
        self.output_mode = is_xls

    def run(self):
        ExpB = FormB.ExpFormaB(self.exp_file, self.rows, self.sprav )
        b_rows_dict = ExpB.create_exp_dict()
        if self.output_mode:
            exl_file_name = u'fB_%s_%s.xlsx' % (os.path.basename(self.exp_file)[4:-4],time.strftime(u"%d-%m-%Y"))
            exl_file_path = os.path.dirname(self.exp_file)+u'\\'+ exl_file_name
            try:
                export_toxl_fb(b_rows_dict,exl_file_path)
            except IOError:
                self.emit(QtCore.SIGNAL(u'b_already_opened(const QString&)'), Message.xl_already_opened % exl_file_path)
        else:
            created_fs = ExpB.create_e_table()
            if created_fs:
                ExpB.run_mdb_exp(b_rows_dict, created_fs)
            else:
                self.emit(QtCore.SIGNAL(u'b_already_opened(const QString&)'), Message.xl_already_opened % self.exp_file)
                #TODO: catch Error like in E_A


class SpravContrThread(QtCore.QThread):
    def __init__(self, load_from_pkl = False, parent = None):
        super(SpravContrThread, self).__init__(parent)
        self.__pkl = load_from_pkl

    def set_pkl_src(self):
        self.__pkl = True
    def set_mdb_src(self):
        self.__pkl = False

    def run(self):
        sprav_contr = Sprav.SpravControl()
        #TODO: switch to default sprav_contr on if cases
        if self.__pkl:
            self.get_sprav_holder()
        else:
            if sprav_contr.s_conn.has_dbc:
                if sprav_contr.losttables:
                    pos = u'ет таблица' if len(sprav_contr.losttables) == 1 else u'ют таблицы'
                    self.emit(QtCore.SIGNAL(u'lost_table(const QString&)'), Message.bdg_lost_tables % (pos,unicode(sprav_contr.losttables)[1:-1]))
                elif sprav_contr.badfields:
                    for key in sprav_contr.badfields:
                        pos1, pos2 = (u'ет',u'е') if len(sprav_contr.badfields[key]) == 1 else (u'ют',u'я')
                        self.emit(QtCore.SIGNAL(u'lost_field(const QString&)'), Message.bgd_lost_fields % (key,pos1,pos1,pos2,unicode(sprav_contr.badfields[key])[1:-1],key))
                else:
                    try:
                        sh = Sprav.SpravHolder(self.__pkl)
                        self.emit(QtCore.SIGNAL(u'sprav_holder(PyQt_PyObject)'), sh)
                    except Sprav.SpravError as se:
                        print se
                        #TODO: call error window
            else:
                self.emit(QtCore.SIGNAL(u'failure_conn(const QString&)'), Message.no_bgd_conn)

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
# noinspection PyTypeChecker
class MyWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.loadthread = LoadingThread()
        self.__a_thr_reinit = False
        self.db_file = None
        self.e_db_file = None
        self.setWindowTitle(u'Создание экспликации')
        self.resize(1400, 700)
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
        self.expa_box.addWidget(self.group_box,0,20,2,1)

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
        self.setWindowIcon(QtGui.QIcon(u'%s\\Images\\exp.png' % project_path))
        self.setCentralWidget(self.central_widget)
        self.setFocus()
        self.set_menu_properties()
        self.hide_props()

        self.connect(self.control_btn, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"on_clicked_control_btn()"))
        self.connect(self.convert_btn, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"on_clicked_convert_btn()"))
        self.connect(self.exp_a_btn, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"on_clicked_exp_a_btn()"))
        self.connect(self.btn_a_all, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"on_clicked_btn_a_all()"))
        self.connect(self.btn_a_tree, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"on_clicked_btn_a_tree()"))
        self.connect(self.exp_b_btn, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"on_clicked_exp_b_btn()"))
        self.sprav_holder = default
        try:
            self.setStyleSheet((open(u'%s\\Style\\ss.css' % project_path).read()))
        except IOError:
            pass

        self.bold_font = QtGui.QFont()
        self.normal_font = QtGui.QFont()
        self.set_fonts_properties()
        self.set_widgets_font()
        self.set_sources_widgets()
        self.__is_xls_mode = True
        self.explication_data = None
        self.current_exp_data = None
        self.__session_flag = False
        self.recount_bgd()
        self.show()

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
        main_exit1 = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\add.png' % project_path), WName.exit_main_1, self)
        main_exit2 = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\stop1.png' % project_path), WName.exit_main_2, self)
        main_exit1.setShortcut(u'Ctrl+O')
        main_exit1.setStatusTip(ToolTip.exit_main_1)
        main_exit2.setShortcut(u'Ctrl+Q')
        main_exit2.setStatusTip(ToolTip.exit_main_2)
        spr_exit1 = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\refresh.png' % project_path), WName.exit_spr_1, self)
        spr_exit2 = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\refresh.png' % project_path), WName.exit_spr_2, self)
        spr_exit3 = QtGui.QAction(QtGui.QIcon(u'%s\\Images\\exclamation.png' % project_path), WName.exit_spr_3, self)
        spr_exit1.setShortcut(u'Ctrl+U')
        spr_exit1.setStatusTip(ToolTip.exit_spr_1)
        spr_exit2.setShortcut(u'Ctrl+Y')
        spr_exit2.setStatusTip(ToolTip.exit_spr_2)
        spr_exit3.setShortcut(u'Ctrl+Y')
        spr_exit3.setStatusTip(ToolTip.exit_spr_3)
        self.connect(main_exit2, QtCore.SIGNAL(u'triggered()'), QtGui.qApp, QtCore.SLOT(u'quit()'))
        self.connect(main_exit1, QtCore.SIGNAL(u'triggered()'), self.open_file)
        self.connect(spr_exit1, QtCore.SIGNAL(u'triggered()'), self.recount_bgd)
        self.connect(spr_exit2, QtCore.SIGNAL(u'triggered()'), lambda: self.recount_bgd(True))
        self.connect(spr_exit3, QtCore.SIGNAL(u'triggered()'), self.set_b2e_default)
        menu = self.menuBar()
        menu_file = menu.addMenu(WName.menu_1)
        menu_sprav = menu.addMenu(WName.menu_2)
        menu_file.addAction(main_exit1)
        menu_file.addAction(main_exit2)
        menu_sprav.addAction(spr_exit1)
        menu_sprav.addAction(spr_exit2)
        menu_sprav.addAction(spr_exit3)

    def reset_parameters(self, load_session = False):
        if not load_session:
            self.e_db_file = None
        self.hide_props(False)
        self.btn_a_all.hide()
        self.btn_a_tree.hide()
        self.treeView.hide()
        self.treeView.reset()
        self.control_btn.setDisabled(load_session)
        # self.convert_btn.setDisabled(True)
        self.exp_a_btn.setEnabled(load_session)
        self.exp_b_btn.setEnabled(load_session)
        self.export_frame.hide()
        self.save_widget.hide()
        self.src_widget.lbl.setText(self.db_file)
        self.src_widget.lbl.repaint()
        self.group_box.setHidden(not load_session)

    def open_file(self):
        self.db_file = unicode(QtGui.QFileDialog(self).getOpenFileName(self, WName.open_file, project_path, options=QtGui.QFileDialog.DontUseNativeDialog))
        if self.db_file:
            if self.db_file[-4:] == u'.pkl':
                self.load_session()
            elif self.db_file[-4:] == u'.mdb':
                message = self.prepare_control()
                if message:
                    self.show_error(message)
                else:
                    self.__session_flag = False
                    self.add_event_log(Message.opened_file % self.db_file)
                    self.add_event_log(Message.db_has_data % self.db_file.split(u'/')[-1], False)
                    self.reset_parameters()
            else:
                self.show_error(Message.wrong_file)

    def prepare_control(self):
        contr = Control.DataControl(self.db_file, self.sprav_holder)
        if not contr.can_connect():
            return u'Не удалось соединиться с базой данных %s' % self.db_file
        need_table = contr.contr_tables()
        contr.close_conn()
        table_message = u'Отсутствуют таблицы '
        tab_err = 0
        for tabl in need_table:
            if not tabl[1]:
                tab_err = 1
                table_message+= tabl[0] + u', '
        if tab_err == 1:
            return table_message
        else:
            return False

    def load_session(self):
        try:
            with open(self.db_file, 'rb') as inp:
                self.explication_data = pickle.load(inp)
                inp.close()
            loading_password = self.explication_data.pop()
            if loading_password == u'Alex':
                self.__session_flag = True
                self.e_db_file = self.explication_data.pop()
                e_src_text =  u'\\'.join(self.e_db_file.split(u'\\')[:-1])
                self.export_frame.e_src_widget.set_lbl_text(e_src_text)
                self.add_event_log(Message.session_loaded % self.db_file)
                self.reset_parameters(True)
                self.current_exp_data = self.explication_data[:]
                self.show_first_combo()
            else:
                self.show_error(Message.wrong_session)
        except:
            #TODO: rename error message and add exceptions
            self.show_error(Message.wrong_session)

    def save_session(self):
        default_name = self.e_db_file.split(u'\\')[-1][4:-4]+time.strftime(u'_%d_%m_%y') + u'.pkl'
        save_file = unicode(QtGui.QFileDialog(self).getSaveFileName(self, WName.save_dialog, default_name, options=QtGui.QFileDialog.DontUseNativeDialog))
        if save_file:
            if save_file[-4:] != u'.pkl':
                save_file+= u'.pkl'
            try:
                with open(save_file,u'wb') as output:
                    self.explication_data.append(self.e_db_file)
                    self.explication_data.append(u'Alex')
                    pickle.dump(self.explication_data, output, 2)
                self.add_event_log(Message.session_saved % self.db_file)
            except:
                self.show_error(Message.bad_session)
    def set_xls_mode(self):
        self.__is_xls_mode= True

    def set_mdb_mode(self):
        self.__is_xls_mode = False

    def ask_question(self, messag):
        reply = QtGui.QMessageBox.question(self, Message.ask_exit,messag,
                                           QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.statusBar().showMessage(u'Ready')
        else:
            sys.exit()

    def enable_convert(self):
        self.add_event_log(Message.control_passed)
        self.control_table.hide()
        self.convert_btn.setEnabled(True)

    def enable_explications(self):
        # self.control_thr.terminate()
        self.convert_thr.terminate()
        self.on_finished()
        self.add_event_log(Message.convert_passed)
        self.convert_table.hide()
        self.exp_a_btn.setEnabled(True)
        self.exp_b_btn.setEnabled(True)
        self.explication_data = self.convert_thr.converted_data
        self.current_exp_data = self.explication_data[:]
        self.show_first_combo()

    def show_first_combo(self):
        soato_names_d = self.explication_data[2]
        group_soatos = self.make_soato_group(soato_names_d.keys())
        ate_expl_data = dict.fromkeys(group_soatos.keys(), None)
        for expl in self.current_exp_data[0]:
            try:
                ate_expl_data[expl.soato[:-3]].append(expl)
            except AttributeError:
                ate_expl_data[expl.soato[:-3]] = [expl,]
            except KeyError:
                pass
                # This exception can be raised
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
        soatos = self.group_soatos[ate_soato]
        expl_data = dict.fromkeys(soatos, None)
        for expl in self.current_exp_data[0]:
            try:
                expl_data[expl.soato].append(expl)
            except AttributeError:
                expl_data[expl.soato] = [expl,]
            except KeyError:
                pass
                # This exception raised when soato ends '000'

        self.second_expl_data_dict = expl_data
        ate_names = []
        for s in soatos:
            try:
                ate_name = soato_names_d[s]
            except KeyError:
                ate_name=u'-'
            ate_names.append((ate_name, s))
        cmb2_data, self.cmb2_recover_d, ate_len = self._count_cmb_data_recovery(ate_names, u'Вся АТЕ')
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
            self.on_clicked_exp_a_btn()
            self.on_clicked_btn_a_tree()

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
            self.on_clicked_exp_a_btn()
            self.on_clicked_btn_a_tree()

    @staticmethod
    def _count_cmb_data_recovery(names, first_combo_row = u'Весь район'):
        """ Input: names - list of tuples (name, soato)
            returns combo_box data , recovery dictionary to catch, which combo row was checked , max item length
        """
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

    @staticmethod
    def make_soato_group(s_kods):
        soato_group = {}
        ate_soato = []
        for s in s_kods:
            ate_key = s[:-3]
            if not s[-3:] == u'000':
                try:
                    soato_group[ate_key].append(s)
                except KeyError:
                    soato_group[ate_key] = [s]
            else:
                ate_soato.append(ate_key)
            for soato in ate_soato:
                if soato not in soato_group.keys():
                    soato_group[soato] = []
        return soato_group

    def on_finished(self):
        self.block_btns(False)
        self.loadthread.terminate()
        self.statusBar().showMessage(u'Ready')

    def add_loading(self, load_message):
        self.block_btns()
        def set_status(dots):
            mes = load_message+dots
            self.statusBar().showMessage(mes)
        self.connect(self.loadthread, QtCore.SIGNAL(u's_loading(const QString&)'), set_status)
        self.loadthread.start()

    def set_b2e_default(self):
        self.sprav_holder = default
        self.statusBar().showMessage(u'Ready')
        self.add_event_log(Message.set_sprav_default)
    def set_sprav_holder(self, sprav):
        self.sprav_holder = sprav
        self.statusBar().showMessage(u'Ready')
        self.add_event_log(Message.load_sprav_success)

    def recount_bgd(self, bgdparam = False):
        self.sprav_thread = SpravContrThread(bgdparam)
        self.connect(self.sprav_thread, QtCore.SIGNAL(u'sprav_holder(PyQt_PyObject)'), self.set_sprav_holder)
        self.connect(self.sprav_thread, QtCore.SIGNAL(u'failure_conn(const QString&)'), self.show_error)
        self.connect(self.sprav_thread, QtCore.SIGNAL(u'lost_table(const QString&)'), self.show_error)
        self.connect(self.sprav_thread, QtCore.SIGNAL(u'lost_field(const QString&)'), self.show_error)
        self.connect(self.sprav_thread, QtCore.SIGNAL(u'failure_conn(const QString&)'), self.set_b2e_default)
        self.connect(self.sprav_thread, QtCore.SIGNAL(u'lost_table(const QString&)'), self.set_b2e_default)
        self.connect(self.sprav_thread, QtCore.SIGNAL(u'lost_field(const QString&)'), self.set_b2e_default)
        self.sprav_thread.start()
        self.statusBar().showMessage(u'Busy')


    @QtCore.pyqtSlot()
    def on_clicked_control_btn(self):
        self.add_event_log(Message.run_control)
        self.add_loading(Message.loading_control)
        self.control_thr = ControlThread(self.db_file, self.sprav_holder)
        self.connect(self.control_thr, QtCore.SIGNAL(u'controlpassed'), self.enable_convert)
        self.connect(self.control_thr, QtCore.SIGNAL(u'contr_failed(PyQt_PyObject)'), self.add_control_protocol)
        self.connect(self.control_thr, QtCore.SIGNAL(u'finished()'), self.on_finished)
        self.control_thr.start()
        self.statusBar().showMessage(Message.status_busy)

    @QtCore.pyqtSlot()
    def on_clicked_convert_btn(self):
        self.add_event_log(Message.run_convert)
        self.convert_thr = ConvertThread(self.sprav_holder)
        self.add_loading(Message.loading_convert)
        self.connect(self.convert_thr, QtCore.SIGNAL(u'convertpassed'), self.enable_explications)
        self.connect(self.convert_thr, QtCore.SIGNAL(u'conv_failed(PyQt_PyObject)'), self.add_convert_protocol)
        self.convert_thr.start()
        self.statusBar().showMessage(Message.status_busy)

    def get_edbf_name(self):
        exp_dir = unicode(QtGui.QFileDialog(self).getExistingDirectory(self, Message.save_exp_dialog, project_path, options=QtGui.QFileDialog.DontUseNativeDialog))
        if exp_dir:
            if self.__session_flag:
                e_dbf = exp_dir + u'\\' + self.e_db_file.split(u'\\')[-1]
            else:
                e_dbf = exp_dir + u'\\Exp_' + self.db_file.split(u'/')[-1]
            if not self.__is_xls_mode:
                self.try_create_edb_file(e_dbf)
            self.export_frame.e_src_widget.set_lbl_text(exp_dir)
            self.e_db_file = e_dbf

    def try_create_edb_file(self, e_dbf):
        templ = u"%s\\template.mdb" % Sprav.work_dir
        if not os.path.isfile(e_dbf):
            if os.path.isfile(templ):
                try:
                    shutil.copyfile(templ, e_dbf)
                except IOError:
                    self.show_error(Message.wrong_file_path % e_dbf)
                except:
                    self.show_error(Message.err_create_file% e_dbf)
            else:
                self.show_error(Message.tmpl_empty)

    @QtCore.pyqtSlot()
    def on_clicked_exp_a_btn(self):
        self.block_btns()
        self.__a_thr_reinit = False
        if not self.e_db_file:
            self.get_edbf_name()
        if self.e_db_file:
            if self.export_frame.isHidden():
                self.export_frame.show()
                self.save_widget.show()
                self.group_box.show()
            self.exp_a_thr = ExpAThread(self.e_db_file, self.current_exp_data, self.sprav_holder)
            self.btn_a_all.setHidden(False)
            self.btn_a_tree.setHidden(False)
            self.exp_a_btn.hide()
        self.block_btns(False)

    @QtCore.pyqtSlot()
    def on_clicked_btn_a_all(self):
        if self.try_has_edbf():
            self.add_loading(Message.wait_exp_a)
            self.add_event_log(Message.run_exp_a)
            if self.__a_thr_reinit:
                self.exp_a_thr = ExpAThread(self.e_db_file, self.current_exp_data,  self.sprav_holder)
            else: self.__a_thr_reinit = True
            self.connect(self.exp_a_thr, QtCore.SIGNAL(u'finished()'), self.on_finished)
            self.connect(self.exp_a_thr, QtCore.SIGNAL(u'finished()'), lambda: self.add_event_log(Message.finish_exp_a))
            self.connect(self.exp_a_thr, QtCore.SIGNAL(u'already_opened(const QString&)'), self.show_error)
            self.connect(self.exp_a_thr, QtCore.SIGNAL(u'err1(const QString&)'), self.show_error)
            self.exp_a_thr.set_output_mode(self.__is_xls_mode)
            self.exp_a_thr.start()

    @QtCore.pyqtSlot()
    def on_clicked_btn_a_tree(self):
        self.model = self.make_tree_model(self.exp_a_thr.exp_tree)
        self.model.setHorizontalHeaderLabels([WName.tree_header])
        self.treeView.setModel(self.model)
        self.treeView.setHidden(False)
        self.disconnect(self.treeView, QtCore.SIGNAL(u"activated(const QModelIndex &)"),self.tree_edit_cell)
        self.connect(self.treeView, QtCore.SIGNAL(u"activated(const QModelIndex &)"),self.tree_edit_cell)

    def make_tree_model(self, data):
        model = QtGui.QStandardItemModel()
        forms22 = data.keys()
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
            item_names = [i.info for i in data[key]]
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
            exp_single_fa(pressed_exp.exp_a_rows, u'%s_%s' % (pressed_f22, qindex.row()+1), pressed_exp.info, self.e_db_file)

    @QtCore.pyqtSlot()
    def on_clicked_exp_b_btn(self):

        if not self.e_db_file:
            self.get_edbf_name()
        if self.e_db_file and self.try_has_edbf():
            if self.export_frame.isHidden():
                self.export_frame.show()
                self.save_widget.show()
            self.add_loading(Message.wait_exp_b)
            self.add_event_log(Message.run_exp_b)
            self.exp_b_thr = ExpBThread(self.e_db_file, self.explication_data[0], self.sprav_holder)
            self.connect(self.exp_b_thr, QtCore.SIGNAL(u'already_opened(const QString&)'), self.show_error)
            self.connect(self.exp_b_thr, QtCore.SIGNAL(u'finished()'), self.on_finished)
            self.connect(self.exp_b_thr, QtCore.SIGNAL(u'finished()'), lambda:self.add_event_log(Message.finish_exp_b))
            self.exp_b_thr.set_output_mode(self.__is_xls_mode)
            self.exp_b_thr.start()

    def add_event_log(self, text, with_time = True):
        if with_time:
            self.event_table.table.add_action_row([text])
        else: self.event_table.table.add_action_row([text],u'- // -')

    def add_control_protocol(self, data_li):
        self.control_thr.terminate()
        self.control_table.show()
        event_time = time.strftime(u"%d.%m.%y  %H:%M:%S"  )
        self.add_event_log(Message.control_failed)
        self.control_table.table.add_span_row(event_time)
        for row in data_li:
            errors = unicode(tuple(row[2]))
            self.control_table.table.add_row([row[0],row[1], u'OBJECTID in %s' % errors, row[3]])

    def add_convert_protocol(self, data_di):
        self.on_finished()
        self.convert_table.show()
        event_time = time.strftime(u"%d.%m.%y  %H:%M:%S"  )
        self.add_event_log(Message.convert_failed)
        self.convert_table.table.add_span_row(event_time)
        for key in data_di:
            errors = unicode(tuple(data_di[key]))
            self.convert_table.table.add_row([u'UserN_%s' % unicode(key), errors, u'OBJECTID in %s' % errors])


    def try_has_edbf(self):
        if self.__is_xls_mode or self.try_to_connect(self.e_db_file):
            return True
        self.try_create_edb_file(self.e_db_file)
        if self.try_to_connect(self.e_db_file):
            return True
        else:
            self.show_error(Message.failed_edb_conn)
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
        self.rbtn_xls.setIcon(QtGui.QIcon(u'%s\\Images\\excel.ico' % project_path))
        self.rbtn_xls.setChecked(True)
        self.rbtn_xls.setFont(QtGui.QFont('Verdana',10))
        self.rbtn_mdb = QtGui.QRadioButton(u'*.mdb',self)
        self.rbtn_mdb.setIcon(QtGui.QIcon(u'%s\\Images\\access.ico' % project_path))
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
        self.lbl.setText(text)

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
        self.setWindowTitle(u"Text LOG")
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
