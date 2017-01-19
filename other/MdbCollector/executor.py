#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Aleksei Konkov'

import os
import sys
from  shutil import copyfile as shutil_copyfile

from PyQt4 import QtGui, QtCore

from packages.collector import run_collection
from packages.titles import *

widget_titles = WidgetTitles()
error_titles = ErrorTitles()
status_titles = StatusTitles()
message_titles = MessageTitles()


Expl = 2
project_dir = os.getcwd()
# spr_dir = os.path.join(project_dir, 'Spr')
# spr_default_path = os.path.join(spr_dir, 'DefaultSpr.pkl')
# tempDB_path = os.path.join(spr_dir, 'tempDbase.mdb')
# xls_templates_dir = os.path.join(spr_dir, 'xls_forms')
# templ_db_path = os.path.join(spr_dir, 'template.mdb')

def rm_temp_db(file_rm):
    if os.path.isfile(file_rm):
        os.remove(file_rm)


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



class FileCopyThread(QtCore.QThread):
    def __init__(self, parent = None):
        super(FileCopyThread, self).__init__(parent)
        self.file_src = ''
        self.file_destination = ''


    def copy_file(self, file_src, file_destination):
        self.file_src = file_src
        self.file_destination = file_destination
        self.start()


    def run(self):
        if not self.file_destination or not self.file_src:
            self.emit(QtCore.SIGNAL(u'error(const QString&)'), error_titles.not_enough_data)
            return
        try:

            print self.file_src, self.file_destination
            shutil_copyfile(self.file_src, self.file_destination)
        except Exception as err:
            self.emit(QtCore.SIGNAL(u'success(const QString&)'), self.file_src)
            # self.emit(QtCore.SIGNAL(u'error(const QString&)'), str(err))
            return

        new_file_name = os.path.basename(self.file_src)
        self.emit(QtCore.SIGNAL(u'success(const QString&)'), os.path.join(self.file_destination, new_file_name))



class CollectorThread(QtCore.QThread):
    def __init__(self, parent = None):
        super(CollectorThread, self).__init__(parent)
        self.dbf_fls_path = ''
        self.mdb_out_file = ''


    def run_collecting(self, dbf_fls_path, mdb_out_file):
        self.dbf_fls_path = dbf_fls_path
        self.mdb_out_file = mdb_out_file
        self.start()


    def run(self):
        if not self.dbf_fls_path or not self.mdb_out_file:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), error_titles.not_enough_data)
            return
        try:
            failed_dbfs, not_executed_queries = run_collection(self.dbf_fls_path, self.mdb_out_file)
        except Exception as err:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), str(err))
            raise err
        if len(failed_dbfs):
            self.emit(QtCore.SIGNAL(u'some_dbf_failed(PyQt_PyObject)'), failed_dbfs)
        if len(not_executed_queries):
            self.emit(QtCore.SIGNAL(u'some_inserts_failed(PyQt_PyObject)'), not_executed_queries)
        else:
            self.emit(QtCore.SIGNAL(u'successfully_completed(const QString&)'), 'OK')
        # else:
        #     if err_li:
        #         self.emit(QtCore.SIGNAL(u'contr_failed(PyQt_PyObject)'), err_li)
        #     else:
        #         self.emit(QtCore.SIGNAL(u'control_passed()'))


class SettingsWindow(QtGui.QMainWindow):
    def __init__(self, parent = None, title = u'' ):
        super(SettingsWindow, self).__init__(parent)
        self.setWindowTitle(title)
        self.resize(690, 450)
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


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle(widget_titles.main_name)
        self.resize(600, 300)
        self.central_widget = QtGui.QFrame(self)
        self.central_widget.setFrameShape(QtGui.QFrame.StyledPanel)
        self.central_widget.setFrameShadow(QtGui.QFrame.Raised)
        self.gridLayout = QtGui.QGridLayout(self.central_widget)
        self.l1 = QtGui.QLabel(widget_titles.l1_title,self.central_widget)
        self.l2 = QtGui.QLabel(widget_titles.l2_title,self.central_widget)
        # self.l3 = QtGui.QLabel(widget_titles.l3_title,self.central_widget)

        self.src_dbf_widget = SrcFrame()
        self.gridLayout.addWidget(self.src_dbf_widget, 3, 0, 1, 2)
        self.src_dbf_widget.set_lbl_text(widget_titles.dbf_folder)


        self.src_mdb_widget = SrcFrame('#2894FF')
        self.gridLayout.addWidget(self.src_mdb_widget, 1, 0, 1, 2)
        self.src_mdb_widget.set_lbl_text(widget_titles.src_mdb_folder)

        #
        # self.out_mdb_widget = SrcFrame('#FF5C1B')
        # self.gridLayout.addWidget(self.out_mdb_widget, 5, 0, 1, 2)
        # self.out_mdb_widget.set_lbl_text(widget_titles.out_mdb_folder)

        self.gridLayout.addWidget(self.l1, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.l2, 2, 0, 1, 1)
        # self.gridLayout.addWidget(self.l3, 4, 0, 1, 1)

        self.run_btn = QtGui.QPushButton(widget_titles.btn_run, self.central_widget)
        self.run_btn.setToolTip(widget_titles.tooltip_run)
        # self.run_btn.setSizePolicy(self.sizePolicy)
        self.gridLayout.addWidget(self.run_btn, 8, 2, 1, 1)
        # self.clearbutton.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Minimum)
        self.setWindowIcon(QtGui.QIcon(u'%s\\Images\\exp.png' % project_dir))
        self.setCentralWidget(self.central_widget)
        self.setFocus()
        self.bold_font = QtGui.QFont()
        self.normal_font = QtGui.QFont()
        self.set_fonts_properties()
        self.set_widgets_font()

        self.load_thr = LoadingThread()
        self.collector_thr = CollectorThread()
        self.copy_file_thr = FileCopyThread()

        self.connect(self.src_dbf_widget.btn, QtCore.SIGNAL(u'clicked()'), self.get_dbf_dir)
        self.connect(self.src_mdb_widget.btn, QtCore.SIGNAL(u'clicked()'), self.get_src_mdb_file)
        # self.connect(self.out_mdb_widget.btn, QtCore.SIGNAL(u'clicked()'), self.get_out_mdb_dir)
        self.connect(self.run_btn, QtCore.SIGNAL(u'clicked()'), self.run_collector)
        self.show()

        self.dbf_files_dir = ''
        self.src_mdb_path = ''
        self.out_mdb_dir = ''
        # self.dbf_files_dir = 'D:\workspace\MdbCollector\dbf_files'
        # self.src_mdb_path = 'D:\workspace\MdbCollector\ProbaCO6258.mdb'
        # self.out_mdb_dir = 'D:\workspace\MdbCollector\\test'


        try:
            self.setStyleSheet((open(u'%s\\Style\\ss.css' % project_dir).read()))
        except IOError:
            self.show_error_message(error_titles.no_css, error_titles.no_css)



    def run_loading_status_bar(self, message):
        def set_status(dots):
            mes = message + dots
            self.statusBar().showMessage(mes)
        self.connect(self.load_thr, QtCore.SIGNAL(u's_loading(const QString&)'), set_status)
        self.load_thr.start()

    def stop_loading_status_bar(self, message):
        self.disconnect(self.load_thr, QtCore.SIGNAL(u's_loading(const QString&)'), lambda x: x)
        self.load_thr.terminate()
        self.statusBar().showMessage(message)

    def reset_parameters(self):
        self.export_frame.hide()
        self.save_widget.hide()
        self.src_dbf_widget.set_lbl_text(self.db_file)


    def set_widgets_font(self):
        self.l1.setFont(self.normal_font)
        self.l2.setFont(self.normal_font)
        # self.l3.setFont(self.normal_font)

    def set_fonts_properties(self):
        self.normal_font.setPointSize(10)
        self.bold_font.setPointSize(10)
        self.bold_font.setBold(True)
        self.normal_font.setFamily(u'Dutch801 XBd Bt')       #'Narkisim',
        self.bold_font.setFamily(u'Times New Roman')

    def get_dbf_dir(self):
        start_dir = self.dbf_files_dir if self.dbf_files_dir else project_dir
        dir_path = unicode(QtGui.QFileDialog(self).getExistingDirectory(self, widget_titles.choose_dbf_dir, start_dir, options=QtGui.QFileDialog.DontUseNativeDialog))
        if os.path.isdir(dir_path):
            self.dbf_files_dir = dir_path.replace('/', '\\')
            self.src_dbf_widget.set_lbl_text(self.dbf_files_dir)

    def get_src_mdb_file(self):
        if self.src_mdb_path:
            start_dir = os.path.dirname(self.src_mdb_path)
        else:
            start_dir = project_dir
        file_path = unicode(QtGui.QFileDialog(self).getOpenFileName(self, widget_titles.choose_src_mdb, start_dir, u'Valid files (*.mdb);; All files (*)', options=QtGui.QFileDialog.DontUseNativeDialog))
        if os.path.isfile(file_path):
            self.src_mdb_path = file_path.replace('/', '\\')
            self.src_mdb_widget.set_lbl_text(self.src_mdb_path)


    # def get_out_mdb_dir(self):
    #     dir_path = unicode(QtGui.QFileDialog(self).getExistingDirectory(self, widget_titles.choose_out_dir, project_dir, options=QtGui.QFileDialog.DontUseNativeDialog))
    #     if os.path.isdir(dir_path):
    #         self.out_mdb_dir = dir_path.replace('/', '\\')
    #         self.out_mdb_widget.set_lbl_text(self.out_mdb_dir)


    def run_collector(self):
        if not self.src_mdb_path:
            self.show_error_message(error_titles.no_src_mdb, error_titles.no_src_mdb)
            return
        if not self.dbf_files_dir:
            self.show_error_message(error_titles.no_dbf_dir, error_titles.no_dbf_dir)
            return
        # if not self.out_mdb_dir:
        #     self.show_error_message(error_titles.no_out_mdb, error_titles.no_out_mdb)
        #     return

        self.run_loading_status_bar(status_titles.collecting_running)
        self.set_collector_thr_connections()
        # self.copy_file_thr.copy_file(self.src_mdb_path, self.out_mdb_dir)
        self.collector_thr.run_collecting(self.dbf_files_dir, self.src_mdb_path)


    def set_collector_thr_connections(self, make_active = True):
        if make_active:
            self.connect(self.collector_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), self.handle_collector_error)
            self.connect(self.collector_thr, QtCore.SIGNAL(u'successfully_completed(const QString&)'), self.handle_collector_success)
            self.connect(self.collector_thr, QtCore.SIGNAL(u'some_inserts_failed(PyQt_PyObject)'), self.handle_failed_inserts)
            self.connect(self.collector_thr, QtCore.SIGNAL(u'some_dbf_failed(PyQt_PyObject)'), self.handle_failed_dbfs)
        else:
            self.disconnect(self.collector_thr, QtCore.SIGNAL(u'some_inserts_failed(PyQt_PyObject)'),
                         self.handle_collector_error)
            self.disconnect(self.collector_thr, QtCore.SIGNAL(u'some_dbf_failed(PyQt_PyObject)'),
                         self.handle_failed_dbfs)
            self.disconnect(self.collector_thr, QtCore.SIGNAL(u'error_occured(const QString&)'), lambda x: x)
            self.disconnect(self.collector_thr, QtCore.SIGNAL(u'successfully_completed(const QString&)'), lambda x: x)


    def handle_failed_inserts(self, fails):
        err_message = error_titles.insert_error
        err_message += u'\n\n'.join(fails)
        self.clear_collector()
        self.stop_loading_status_bar(status_titles.ready)
        self.show_error_message(error_titles.has_error, err_message)
        print fails

    def handle_failed_dbfs(self, fails):
        err_message = error_titles.has_failed_dbfs
        err_message += u'\n\n'.join(fails)
        self.clear_collector()
        self.stop_loading_status_bar(status_titles.ready)
        self.show_error_message(error_titles.has_error, err_message)
        print fails

    def handle_collector_error(self, err_message):
        self.clear_collector()
        self.stop_loading_status_bar(status_titles.ready)
        self.show_error_message(error_titles.has_error, error_titles.collecting_failed + '\n' + err_message)


    def handle_collector_success(self):
        self.clear_collector()
        self.stop_loading_status_bar(status_titles.ready)
        self.show_success_message(message_titles.success, message_titles.successfully_collected)


    def clear_collector(self):
        self.set_collector_thr_connections(False)
        self.collector_thr.terminate()
        del self.collector_thr
        self.collector_thr = CollectorThread()


    def set_copy_file_thr_connections(self, make_active = True):
        if make_active:
            self.connect(self.copy_file_thr, QtCore.SIGNAL(u'error(const QString&)'), self.handle_copy_file_error)
            self.connect(self.copy_file_thr, QtCore.SIGNAL(u'success(const QString&)'), self.handle_copy_file_success)
        else:
            self.disconnect(self.copy_file_thr, QtCore.SIGNAL(u'error(const QString&)'), lambda x: x)
            self.disconnect(self.copy_file_thr, QtCore.SIGNAL(u'success(const QString&)'), lambda x: x)


    def handle_copy_file_error(self, message):
        self.stop_loading_status_bar(status_titles.ready)
        self.show_error_message(error_titles.has_error, error_titles.collecting_failed + '\n ' + message)
        self.clear_copy_file_thr()


    def handle_copy_file_success(self, out_file_path):
        self.clear_copy_file_thr()

        self.set_collector_thr_connections()
        self.collector_thr.run_collecting(self.dbf_files_dir, out_file_path)



    def clear_copy_file_thr(self):
        self.set_copy_file_thr_connections(False)
        self.copy_file_thr.terminate()
        del self.copy_file_thr
        self.copy_file_thr = FileCopyThread()





    def ask_question(self, messag):
        reply = QtGui.QMessageBox.question(self, status_titles.ready, messag,
                                           QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.statusBar().showMessage(status_titles.ready)
        else:
            sys.exit()


    def show_error_message(self, warn_title, warn_text):
        QtGui.QMessageBox.critical(self, warn_title, u"%s" % warn_text, u'Закрыть')


    def show_success_message(self, success_title, success_text):
        # information || question || warning || about
        QtGui.QMessageBox.information(self, success_title, u"%s" % success_text, u'Закрыть')

# class ExportFrame(QtGui.QFrame):
#     def __init__(self, parent = None):
#         QtGui.QFrame.__init__(self, parent)
#         self.color = u'#D3D120'
#         self.setStyleSheet(u'background-color: #959BA8; border-radius: 15%;')
#         self.rbtn_xls = QtGui.QRadioButton(u'*.xls',self)
#         self.rbtn_xls.setIcon(QtGui.QIcon(u'%s\\Images\\xls.ico' % project_dir))
#         self.rbtn_xls.setChecked(True)
#         self.rbtn_xls.setFont(QtGui.QFont('Verdana',10))
#         self.rbtn_mdb = QtGui.QRadioButton(u'*.mdb',self)
#         self.rbtn_mdb.setIcon(QtGui.QIcon(u'%s\\Images\\mdb.ico' % project_dir))
#         self.rbtn_mdb.setFont(QtGui.QFont('Verdana',10))
#         self.rbtn_style = u'background-color: white; color: green;' \
#                           u' border-top-right-radius: 3%;' \
#                           u'border-bottom-left-radius: 3%; padding: 3px;' \
#                           u'border: 2px solid' + self.color
#         self.lbl_style = u'background-color: #49586B; color: white;' \
#                           u'border-top-left-radius: 23%;' \
#                           u'border-top-right-radius: 23%;' \
#                           u'border-bottom-left-radius: 23%;' \
#                           u'border-bottom-right-radius: 3%;' \
#                           u'padding-left: 10px;' \
#                           u'border: 2px solid '+self.color
#         self.lbl = QtGui.QLabel(u'Экспорт \n данных', self)
#         # self.lbl.setStyleSheet(u'color: white; background-color: #49586B; border-radius: 8%; border: 2px solid' + border_color)
#         self.lbl.setFont(QtGui.QFont('Segoe Print',10))
#         self.e_src_widget = SrcFrame(self.color)
#         self.box = QtGui.QGridLayout(self)
#         self.box.addWidget(self.rbtn_xls, 0, 1, 1, 1)
#         self.box.addWidget(self.rbtn_mdb, 1, 1, 1, 1)
#         self.box.addWidget(self.lbl, 0, 0, 2, 1)
#         self.box.addWidget(self.e_src_widget, 2, 0, 1, 2)
#         self.rbtn_xls.setStyleSheet(self.rbtn_style)
#         self.rbtn_mdb.setStyleSheet(self.rbtn_style)
#         self.lbl.setStyleSheet(self.lbl_style)

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

# class CombBox(QtGui.QComboBox):
#     def __init__(self, parent = None, data = [], width = 60):
#         QtGui.QComboBox.__init__(self, parent)
#         self.change_data(data)
#         self.setStyleSheet(u'font-size: 12px')
#         self.set_min_width(width)
#         self.setMaxVisibleItems(30)
#
#     def set_min_width(self, width):
#         self.setMinimumWidth(width)
#     def change_data(self, new_data):
#         self.clear()
#         self.addItems(new_data)

# class GroupBox(QtGui.QFrame):
#     def __init__(self, parent = None, border_color = u'#C3FFF1'):
#         QtGui.QFrame.__init__(self, parent)
#         self.setMaximumHeight(33)
#         self.setStyleSheet(u'background-color: #2558FF; border-top-left-radius: 30%;border-bottom-right-radius: 30%; padding-right: 5px;padding-left: 5px')
#         self.h_box = QtGui.QHBoxLayout(self)
#         self.first_cmb = CombBox(self, width = 180)
#         self.second_cmb = CombBox(self, width = 180)
#         self.second_cmb.hide()
#         self.first_cmb.setStyleSheet(u'border-radius: 5% ; border: 1px solid '+ border_color)
#         self.second_cmb.setStyleSheet(u'border-radius: 5% ; border: 2px solid '+ border_color)
#         self.lbl = QtGui.QLabel(WidgNames.lbl_group, self)
#         self.lbl.setStyleSheet(u'color: #C3FFF1;')
#         self.lbl.setFont(QtGui.QFont('Segoe Print',9))
#         self.lbl.setAlignment(QtCore.Qt.AlignCenter)
#         self.h_box.addWidget(self.lbl)
#         self.h_box.addWidget(self.first_cmb)
#         self.h_box.addWidget(self.second_cmb)
#
#     def change_first_cmb(self, data):
#         self.first_cmb.change_data(data)
#     def change_second_cmb(self, data):
#         self.second_cmb.change_data(data)
#     def get_first_index(self):
#         return self.first_cmb.currentIndex()
#     def get_second_index(self):
#         return self.second_cmb.currentIndex()
# #
# class Table(QtGui.QTableWidget):
#     def __init__(self, header_text_li, parent = None):
#         QtGui.QTableWidget.__init__(self, parent)
#         self.__row_count = 0
#         # qsize =QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
#         # self.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
#         # self.horizontalHeader().setOffsetToSectionPosition(0)
#         # self.horizontalHeader().resizeSection(0, self.horizontalHeader().sectionSize(0)+20)
#         self.horizontalHeader().setCascadingSectionResizes(True)
#         self.verticalHeader().setCascadingSectionResizes(True)
#         self.horizontalHeader().setStretchLastSection(True)
#         self.horizontalHeader().setMinimumSectionSize(50)
#         header_css = u'border-radius: 1px; border: 1px dashed blue;'
#         self.horizontalHeader().setStyleSheet(header_css)
#         self.verticalHeader().setStyleSheet(header_css+u'padding:-2px')
#         self.setColumnCount(len(header_text_li))
#         self.setHorizontalHeaderLabels(header_text_li)
#         self.setAlternatingRowColors(True)
#         self.setAutoScroll(True)
#         self.setStyleSheet(u'alternate-background-color: #ADADAD; background-color: silver;'
#                            u'border-radius: 10%; border: 1px solid #1E54B1; color: #1E54B1; font-size: 13px')
#     def set_event_ss(self):
#         self.setAlternatingRowColors(False)
#         self.setStyleSheet(u'alternate-background-color: #0688FF; background-color: #1A1A1B;'
#                            u'border-radius: 10%; border: 1px solid #1E54B1; color: #1E54B1')
#     def add_span_row(self, text, span = True):
#         self.__row_count+=1
#         self.setRowCount(self.__row_count)
#         time_label = TableLabel(text)
#         time_label.setStyleSheet(u'color: #D3D3D3; background-color: #323C3D;font-size: 14px;'
#                            u'border-top-left-radius: 30%; padding-right: 15px;padding-left: 15px')
#         self.setCellWidget(self.__row_count-1,0, time_label)
#         if span:
#             time_label.setAlignment(QtCore.Qt.AlignCenter)
#             time_label.setMinimumHeight(20)
#             self.setSpan(self.__row_count-1,0,1,self.columnCount())
#
#     def add_action_row(self, row_li, time_ = True):
#         if time_:
#             time_ = time.strftime(u"%H:%M:%S  \n%d.%m.%y")
#         self.add_span_row(time_, False)
#         for i, cell in enumerate(row_li):
#             self.setCellWidget(self.__row_count-1,i+1, TableLabel(cell))
#     def add_widgets_row(self, widgets_row):
#         self.__row_count+=1
#         self.setRowCount(self.__row_count)
#         for i, cell in enumerate(widgets_row):
#             self.setCellWidget(self.__row_count-1,i, cell)
#     def add_row(self, row_li):
#         self.__row_count+=1
#         self.setRowCount(self.__row_count)
#         for i, cell in enumerate(row_li):
#             self.setItem(self.__row_count-1,i, QtGui.QTableWidgetItem(cell))
#
#     def clear_all(self):
#         self.__row_count = 0
#         # self.clearContents()
#         self.reset()
#         self.clearSpans()
#         self.setRowCount(1)
#
#
# class SettingsTable(Table):
#     def __init__(self, header_li, parent = None):
#         Table.__init__(self, header_li, parent)
#         self.horizontalHeader().resizeSection(0, self.horizontalHeader().sectionSize(0)+80)
#         self.horizontalHeader().setResizeMode(1, True)
#         self.verticalHeader().setHidden(True)
#         self.setMinimumWidth(40)
#
# class TableLabel(QtGui.QTextEdit):
#     def __init__(self, data):
#         QtGui.QTextEdit.__init__(self)
#         self.setText(data)
#         self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
#         self.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
#         self.setMinimumHeight(40)
#         self.setMinimumWidth(200)
#         self.setStyleSheet(u'color: #AAAAAA; background-color: #22232F; border: 1.5px solid #C10000;'
#                            u'border-bottom-right-radius: 30%; font-size: 14px;'
#                            u' padding-right: 10px;padding-left: 15px')

class StyledButton(QtGui.QPushButton):
    def __init__(self, title, parent = None):
        QtGui.QPushButton.__init__(self,title, parent)
        self.setMaximumHeight(30)
        self.setStyleSheet(u'background-color: #A0A0A0; border: 1.5px dotted #C10000; margin:2px;'
                           u'border-top-left-radius: 20%;border-top-right-radius: 20%; padding:0px;'
                           u'border-bottom-left-radius: 1%;border-bottom-right-radius: 1%;'
                           u'padding-right: 20px; padding-left: 20px;font-size: 12px;')

# class TableWidget(QtGui.QWidget):
#     def __init__(self, title, parent = None, with_clear = True):
#         QtGui.QWidget.__init__(self, parent)
#         self.table = Table(title, parent)
#         self.box = QtGui.QGridLayout(self)
#         self.box.addWidget(self.table,0,0,21,21)
#         if with_clear:
#             self.clear_btn = StyledButton(WidgNames.btn_clear, parent)
#             self.box.addWidget(self.clear_btn,19,10,2,2)
#             self.connect(self.clear_btn, QtCore.SIGNAL(u"clicked()"), self.table.clear_all)
#             self.hide()
#     def clear_all(self):
#         self.table.clear_all()



if __name__ == u'__main__':
    app = QtGui.QApplication(sys.argv)
    exp_maker = MainWindow()
    app.exec_()
