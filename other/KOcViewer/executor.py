#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Aleksei Konkov'

import os
import sys
from time import gmtime, strftime
import re
from PyQt4 import QtGui, QtCore
from packages.Threads import *
from packages.titles import *
from packages.OptionsProvider import OptionsProvider
from packages.Threads import RedefinerThread, LoadingThread
from packages.DbTools import DBConn

widget_titles = WidgetTitles()
error_titles = ErrorTitles()
status_titles = StatusTitles()
message_titles = MessageTitles()


Expl = 2
project_dir = os.getcwd()
default_xls_template = os.path.join(project_dir, u'conf\\template.xlsx')
default_base_mdb = os.path.join(project_dir, u'conf\\settingsProvider.mdb')
# spr_dir = os.path.join(project_dir, 'Spr')
# spr_default_path = os.path.join(spr_dir, 'DefaultSpr.pkl')
# tempDB_path = os.path.join(spr_dir, 'tempDbase.mdb')
# xls_templates_dir = os.path.join(spr_dir, 'xls_forms')
# templ_db_path = os.path.join(spr_dir, 'template.mdb')

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle(widget_titles.main_name)
        self.resize(1000, 600)
        self.central_widget = QtGui.QFrame(self)
        self.central_widget.setFrameShape(QtGui.QFrame.StyledPanel)
        self.central_widget.setFrameShadow(QtGui.QFrame.Raised)
        self.gridLayout = QtGui.QGridLayout(self.central_widget)

        self.lbl_src = QtGui.QLabel(widget_titles.base_mdb_file_lbl, self.central_widget)
        self.src_mdb_widget = SrcFrame('#2894FF')
        self.gridLayout.addWidget(self.lbl_src, 13, 0, 1, 5)
        self.gridLayout.addWidget(self.src_mdb_widget, 14, 0, 1, 5)

        self.lbl_out = QtGui.QLabel(widget_titles.choose_out_dir_lbl, self.central_widget)
        self.out_xls_widget = SrcFrame()
        self.gridLayout.addWidget(self.lbl_out, 13, 7, 1, 5)
        self.gridLayout.addWidget(self.out_xls_widget, 14, 7, 1, 5)

        self.lbl_raion = QtGui.QLabel(widget_titles.choose_raion_lbl, self.central_widget)
        self.lbl_land = QtGui.QLabel(widget_titles.choose_land_lbl, self.central_widget)
        self.lbl_table = QtGui.QLabel(widget_titles.choose_table_lbl, self.central_widget)
        self.empty_lbl = QtGui.QLabel(' ', self.central_widget)
        self.empty_lbl2 = QtGui.QLabel(' ', self.central_widget)

        self.gridLayout.addWidget(self.lbl_raion, 0, 0, 1, 4)
        self.gridLayout.addWidget(self.lbl_land, 0, 4, 1, 4)
        self.gridLayout.addWidget(self.lbl_table, 0, 8, 1, 4)

        self.cmb_rayon = CombBox(self.central_widget, [])
        self.cmb_shz = CombBox(self.central_widget, [])
        self.cmb_table = CombBox(self.central_widget, [])

        self.gridLayout.addWidget(self.cmb_rayon, 1, 0, 1, 4)
        self.gridLayout.addWidget(self.cmb_shz, 1, 4, 1, 4)
        self.gridLayout.addWidget(self.cmb_table, 1, 8, 1, 4)

        self.gridLayout.addWidget(self.empty_lbl, 4, 0, 4, 12)
        self.gridLayout.addWidget(self.empty_lbl2, 8, 0, 4, 12)

        self.run_btn = QtGui.QPushButton(widget_titles.btn_run, self.central_widget)
        self.run_btn.setToolTip(widget_titles.tooltip_run)
        # self.run_btn.setSizePolicy(self.sizePolicy)
        self.gridLayout.addWidget(self.run_btn, 5, 5, 1, 2)

        # self.clearbutton.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Minimum)
        self.setWindowIcon(QtGui.QIcon(u'%s\\Images\\KO.png' % project_dir))
        self.setCentralWidget(self.central_widget)
        self.setFocus()
        self.bold_font = QtGui.QFont()
        self.normal_font = QtGui.QFont()
        self.set_fonts_properties()
        self.set_widgets_font()

        try:
            self.setStyleSheet((open(u'%s\\Style\\ss.css' % project_dir).read()))
        except IOError:
            self.show_error_message(error_titles.no_css, error_titles.no_css)
        self.loading_thr = LoadingThread(self)
        self.current_loading_message = ''
        # self.connect(self.loading_thr, QtCore.SIGNAL(u's_loading(const QString&)'), set_status)
        self.run_loading_status_bar(u'Загрузка данных')
        self.show()
        self.redefine_thr = RedefinerThread(default_xls_template)
        # self.copy_file_thr = FileCopyThread()
        self.connect(self.run_btn, QtCore.SIGNAL(u'clicked()'), self.run_redefiner)
        self.connect(self.loading_thr, QtCore.SIGNAL(u's_loading(const QString&)'), self._set_status)
        self.connect(self.src_mdb_widget.btn, QtCore.SIGNAL(u'clicked()'), self.get_src_mdb_file)
        self.connect(self.cmb_rayon, QtCore.SIGNAL(u'currentIndexChanged (const QString&)'), self.raion_changed)
        self.connect(self.out_xls_widget.btn, QtCore.SIGNAL(u'clicked()'), self.get_out_xls_dir)
        self.enable_redefiner_connections(True)

        self.src_mdb_path = ''
        # self.out_xls_dir = project_dir
        self.out_xls_dir = ''

        self.options = None
        self.initialize_options()
        self.set_default_paths()
        self.require_object = {
            'raion_code': '',
            'rab_land_code': '',
            'out_table': ''
        }
        self.stop_loading_status_bar(status_titles.ready)

    def initialize_options(self):
        del self.options
        self.options = OptionsProvider(default_base_mdb)
        if self.options.error:
            err_message = self.options.error['err_type']
            self.show_error_message(error_titles.options_error, err_message)
            self.clear_combos_data()
        else:
            self.set_combos_data()

    def set_default_paths(self):
        self.src_mdb_widget.set_lbl_text(widget_titles.src_mdb_folder)
        if os.path.isfile(self.options.default_src_db_path):
            self.src_mdb_path = self.options.default_src_db_path
            result = self.redefine_thr.update_db_loader(self.src_mdb_path, self.options.get_all_tab_names())
            if result == 'OK':
                self.src_mdb_widget.set_lbl_text(self.options.default_src_db_path)
            else:
                self.src_mdb_path = ''


        if os.path.isdir(self.options.default_out_xls_dir):
            self.out_xls_dir = self.options.default_out_xls_dir
            self.out_xls_widget.set_lbl_text(self.options.default_out_xls_dir)
        else:
            self.show_error_message(error_titles.warning, error_titles.no_out_xls)
            self.out_xls_widget.set_lbl_text(widget_titles.choose_out_dir)


    def set_combos_data(self, shz_only = False):
        if not shz_only:
            self.cmb_rayon.change_data(sorted(self.options.raions_names.keys()))
            self.cmb_table.change_data(self.options.get_sorted_talble_names())
        self.cmb_shz.change_data(sorted(self.options.shz_names.keys()))


    def clear_combos_data(self):
        self.cmb_rayon.change_data([])
        self.cmb_table.change_data([])
        self.cmb_shz.change_data([])


    def raion_changed(self):
        if not len(self.options.raions_names):
            return
        curr_item = self.cmb_rayon.get_current_item()
        if curr_item is not None:
            soato_code = self.options.raions_names[curr_item]
            self.options.update_shz_names(soato_code)
            self.set_combos_data(True)



    def get_required_cmb_params(self):
        curr_rayon_item = self.cmb_rayon.get_current_item()
        curr_shz_item = self.cmb_shz.get_current_item()
        curr_tab_item = self.cmb_table.get_current_item()
        tab_name, out_name = self.options.get_tab_name_by_item(curr_tab_item)

        # rayon_name = self.options.raions_names[curr_rayon_item]
        shz_code = self.options.shz_names[curr_shz_item]
        if tab_name == 'all':
            tab_name = self.options.get_all_tab_names()
        return {
            'current_rayon': curr_rayon_item,
            'current_shz': curr_shz_item,
            'current_shz_code': shz_code,
            'current_tab': tab_name,
            'out_tab_name': out_name
        }


    def reset_parameters(self):
        self.export_frame.hide()
        self.save_widget.hide()
        self.out_xls_widget.set_lbl_text(self.db_file)



    def set_widgets_font(self):
        self.lbl_src.setFont(self.normal_font)
        self.lbl_out.setFont(self.normal_font)
        self.lbl_raion.setFont(self.bold_font)
        self.lbl_land.setFont(self.bold_font)
        self.lbl_table.setFont(self.bold_font)

    def set_fonts_properties(self):
        self.normal_font.setPointSize(12)
        self.bold_font.setPointSize(11)
        self.bold_font.setBold(True)
        self.normal_font.setFamily(u'Narkisim')  #u'Dutch801 XBd Bt'     #'Narkisim',
        self.bold_font.setFamily(u'Narkisim')  #Times New Roman u'Segoe Print'


    def get_src_mdb_file(self):
        if self.src_mdb_path:
            start_dir = os.path.dirname(self.src_mdb_path)
        else:
            start_dir = project_dir
        file_path = unicode(QtGui.QFileDialog(self).getOpenFileName(self, widget_titles.choose_src_mdb, start_dir, u'Valid files (*.mdb);; All files (*)', options=QtGui.QFileDialog.DontUseNativeDialog))
        if os.path.isfile(file_path):
            self.src_mdb_path = file_path.replace('/', '\\')
            print self.src_mdb_path
            result = self.redefine_thr.update_db_loader(self.src_mdb_path, self.options.get_all_tab_names())
            if result == 'OK':
                self.src_mdb_widget.set_lbl_text(self.src_mdb_path)
            else:
                self.src_mdb_path = ''


    def get_out_xls_dir(self):
        dir_path = unicode(QtGui.QFileDialog(self).getExistingDirectory(self, widget_titles.choose_out_dir, project_dir, options=QtGui.QFileDialog.DontUseNativeDialog))
        if os.path.isdir(dir_path):
            self.out_xls_dir = dir_path.replace('/', '\\')
            self.out_xls_widget.set_lbl_text(self.out_xls_dir)


    def run_redefiner(self):
        if not os.path.isfile(self.src_mdb_path) or DBConn.test_connection_to_file(self.src_mdb_path) != 'OK':
            self.handle_redefiner_error(error_titles.src_mdb_connection_failed)
            self.src_mdb_path = ''
            self.src_mdb_widget.set_lbl_text(widget_titles.src_mdb_folder)
            return
        if not self.out_xls_dir or not os.path.isdir(self.out_xls_dir):
            self.out_xls_dir = ''
            self.out_xls_widget.set_lbl_text(widget_titles.choose_out_dir)
            self.handle_redefiner_error(error_titles.no_out_xls)
            return

        self.run_btn.setDisabled(True)
        self.run_loading_status_bar(status_titles.redefining_running)
        # self.options.close_conn()
        if self.options.error:
            # TODO: Handle options error
            self.handle_redefiner_error(self.options.error)
            return

        required_params = self.get_required_cmb_params()

        out_name = "_".join(re.findall(ur'(?u)\w+', required_params['current_shz']))
        print out_name
        out_xls_file_name = u'%s_%s_%s.xlsx' % (out_name ,strftime("%d-%m-%Y", gmtime()), required_params['out_tab_name'])

        self.redefine_thr.update_xls_work_file(os.path.join(self.out_xls_dir, out_xls_file_name))
        self.redefine_thr.run_redefiner(required_params)


    def enable_redefiner_connections(self, make_active = True):
        # self.run_btn.setDisabled(make_active)
        if make_active:
            self.connect(self.redefine_thr, QtCore.SIGNAL(u'error_occurred(PyQt_PyObject)'), self.handle_redefiner_error)
            self.connect(self.redefine_thr, QtCore.SIGNAL(u'xls_error_occurred(PyQt_PyObject)'), self.handle_redefiner_error)
            self.connect(self.redefine_thr, QtCore.SIGNAL(u'successfully_completed(const QString&)'), self.handle_redefiner_success)
        else:
            self.disconnect(self.redefine_thr, QtCore.SIGNAL(u'error_occurred(PyQt_PyObject)'), lambda x: x)
            self.disconnect(self.redefine_thr, QtCore.SIGNAL(u'xls_error_occurred(PyQt_PyObject)'), lambda x: x)
            self.disconnect(self.redefine_thr, QtCore.SIGNAL(u'successfully_completed(const QString&)'), lambda x: x)


    def handle_redefiner_error(self, err_object):

        self.stop_loading_status_bar(status_titles.ready)
        self.clear_redefiner()
        if isinstance(err_object, XlsError):
            self.show_error_message(error_titles.has_error, err_object.message)
        elif isinstance(err_object, Exception):
            self.show_error_message(error_titles.has_error, err_object.message)
        elif isinstance(err_object, (unicode, str)):
            self.show_error_message(error_titles.has_error, unicode(err_object))
        self.statusBar().showMessage(status_titles.ready)


    def handle_redefiner_success(self):
        self.stop_loading_status_bar(status_titles.ready)
        self.clear_redefiner()
        self.show_success_message(message_titles.success, message_titles.successfully_collected)
        self.statusBar().showMessage(status_titles.ready)


    def clear_redefiner(self):
        # self.enable_redefiner_connections(False)
        self.run_btn.setDisabled(False)
        self.redefine_thr.terminate()
        # del self.redefine_thr
        # self.redefine_thr = RedefinerThread(default_xls_template)


    def _set_status(self, dots):
        if self.current_loading_message:
            mes = self.current_loading_message + dots
            self.statusBar().showMessage(mes)

    def run_loading_status_bar(self, message):
        self.current_loading_message = message
        # self.connect(self.loading_thr, QtCore.SIGNAL(u's_loading(const QString&)'), self._set_status)
        self.loading_thr.start()


    def stop_loading_status_bar(self, message):
        self.current_loading_message = ''
        self.loading_thr.terminate()
        self.loading_thr.running = False
        # self.disconnect(self.loading_thr, QtCore.SIGNAL(u's_loading(const QString&)'), lambda x: self.statusBar().showMessage(message))
        self.statusBar().showMessage(message)

    def show_error_message(self, warn_title, warn_text):
        QtGui.QMessageBox.critical(self, warn_title, u"%s" % warn_text, u'Закрыть')


    def show_success_message(self, success_title, success_text):
        # information || question || warning || about
        QtGui.QMessageBox.information(self, success_title, u"%s" % success_text, u'Закрыть')




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


class CombBox(QtGui.QComboBox):
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

    def get_current_item(self):
        if len(self.data):
            cur_ind = self.currentIndex()
            return self.data[cur_ind]


    def applyStyles(self):
        self.autoFillBackground()
        styles = '''
            background-color: #D3D3D3;
            border-radius: 4px;
            border: 1.2px solid #2558FF;
            color: #165596;
            padding: 2px;
            font-family: Helvetica Neue;
            font-size: 14px;
        '''
        self.setStyleSheet(styles)


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

    def set_lbl_text(self, text, collapse_len = 60):
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
        self.lbl.setText(text)
        self.lbl.repaint()


class StyledButton(QtGui.QPushButton):
    def __init__(self, title, parent = None):
        QtGui.QPushButton.__init__(self,title, parent)
        self.setMaximumHeight(30)
        self.setStyleSheet(u'background-color: #A0A0A0; border: 1.5px dotted #C10000; margin:2px;'
                           u'border-top-left-radius: 20%;border-top-right-radius: 20%; padding:0px;'
                           u'border-bottom-left-radius: 1%;border-bottom-right-radius: 1%;'
                           u'padding-right: 20px; padding-left: 20px;font-size: 12px;')



if __name__ == u'__main__':
    app = QtGui.QApplication(sys.argv)
    exp_maker = MainWindow()
    app.exec_()
