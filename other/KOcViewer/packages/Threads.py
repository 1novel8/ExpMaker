#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Aleksei Konkov'

import os
import sys
from  shutil import copyfile as shutil_copyfile

from PyQt4 import QtGui, QtCore

# from packages.collector import run_collection
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


#
# class CollectorThread(QtCore.QThread):
#     def __init__(self, parent = None):
#         super(CollectorThread, self).__init__(parent)
#         self.dbf_fls_path = ''
#         self.mdb_out_file = ''
#
#
#     def run_collecting(self, dbf_fls_path, mdb_out_file):
#         self.dbf_fls_path = dbf_fls_path
#         self.mdb_out_file = mdb_out_file
#         self.start()
#
#
#     def run(self):
#         if not self.dbf_fls_path or not self.mdb_out_file:
#             self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), error_titles.not_enough_data)
#             return
#         try:
#             failed_dbfs, not_executed_queries = run_collection(self.dbf_fls_path, self.mdb_out_file)
#         except Exception as err:
#             self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), str(err))
#             raise err
#         if len(failed_dbfs):
#             self.emit(QtCore.SIGNAL(u'some_dbf_failed(PyQt_PyObject)'), failed_dbfs)
#         if len(not_executed_queries):
#             self.emit(QtCore.SIGNAL(u'some_inserts_failed(PyQt_PyObject)'), not_executed_queries)
#         else:
#             self.emit(QtCore.SIGNAL(u'successfully_completed(const QString&)'), 'OK')
        # else:
        #     if err_li:
        #         self.emit(QtCore.SIGNAL(u'contr_failed(PyQt_PyObject)'), err_li)
        #     else:
        #         self.emit(QtCore.SIGNAL(u'control_passed()'))
