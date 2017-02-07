#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Aleksei Konkov'

from PyQt4 import QtCore
from OutHardcodeSettings import OutSettings
from DbDataLoader import DbLoader
from XLExporter import *

class LoadingThread(QtCore.QThread):
    def __init__(self, parent = None):
        super(LoadingThread, self).__init__(parent)
        self.running = False


    def run(self):
        dots = [u' ',]*5
        count = 0
        is_dot = True
        self.running = True
        while self.running:
            if count == len(dots):
                count = 0
                is_dot = not is_dot
            self.emit(QtCore.SIGNAL(u's_loading(const QString&)'), u' '.join(dots))
            self.msleep(700)
            if is_dot:  dots[count] = u'.'
            else:       dots[count] = u' '
            count+=1


class RedefinerThread(QtCore.QThread):
    def __init__(self, main_xls_tamplate_path, src_db_path = None, parent = None):
        super(RedefinerThread, self).__init__(parent)
        self.out_settings = OutSettings()
        self.db_loader = DbLoader('')
        self.xl_exporter = ExcelExporter('', main_xls_tamplate_path)
        self.current_rayon = ''
        # self.current_rayon_code = ''
        self.current_shz = ''
        self.current_shz_code = ''
        self.current_tab = ''

        if src_db_path is not None:
            self.update_db_loader(src_db_path)


    def run(self):
        self.db_loader.validate_db()
        if self.db_loader.check_error():
            self.emit(QtCore.SIGNAL(u'error_occurred(PyQt_PyObject)'), self.db_loader.check_error())
            return
        if isinstance(self.current_tab, (str, unicode)):
            res = self.run_covered_table_loader(self.current_tab)
            if res == 'Ok':
                print 'SUCCESS'
                self.emit(QtCore.SIGNAL(u'successfully_completed(const QString&)'), res)
        elif isinstance(self.current_tab, list):
            err_results = []
            for table_name in self.current_tab:
                res = self.run_covered_table_loader(table_name)
                if res != 'Ok':
                    err_results.append(res)
            if not len(err_results):
                print 'SUCCESS'
                self.emit(QtCore.SIGNAL(u'successfully_completed(const QString&)'), u'Ok')
            else:
                self.emit(QtCore.SIGNAL(u'error_occurred(PyQt_PyObject)'), err_results)
        else:
            self.emit(QtCore.SIGNAL(u'error_occurred(PyQt_PyObject)'), u'Wrong input data')


    def run_covered_table_loader(self, tab_name, with_signals = True):
        try:
            if tab_name == 'all':
                pass
            else:
                self.run_table_loader(tab_name)
            return 'Ok'
        except XlsError as err:
            if with_signals:
                self.emit(QtCore.SIGNAL(u'xls_error_occurred(PyQt_PyObject)'), err)
            return err
        except Exception as err:
            print err
            if with_signals:
                self.emit(QtCore.SIGNAL(u'error_occurred(PyQt_PyObject)'), u'Unhandled error occurred. \n%s\nPlease contact support' % unicode(err))
            return err

    def update_db_loader(self, new_src_db_path, tables_to_check=None):
        if self.db_loader.db_path != new_src_db_path:
            del self.db_loader
            self.db_loader = DbLoader(new_src_db_path)
            if tables_to_check is None:
                return 'OK'
            try:
                for check_tab in tables_to_check:
                    tab_structure = self.out_settings.get_table_settings(check_tab)
                    print check_tab
                    self.db_loader.check_table_structure(check_tab, tab_structure.fields_to_validate)
                return 'OK'
            except Exception as err:
                self.emit(QtCore.SIGNAL(u'error_occurred(PyQt_PyObject)'), err)
                return 'failed'

    def update_xls_work_file(self, new_xls_work_file):
        self.xl_exporter.change_work_file(new_xls_work_file)


    def run_redefiner(self, required_params):
        self.out_settings = OutSettings()
        self.current_rayon = required_params['current_rayon']
        # self.current_rayon_code = required_params['current_rayon_code']
        self.current_shz = required_params['current_shz']
        self.current_shz_code = required_params['current_shz_code']
        self.current_tab = required_params['current_tab']
        self.start()


    def run_table_loader(self, table_name):
        dynamic_settings = {
            'rayon_name': self.current_rayon,
            'shz_name': self.current_shz
        }
        tab_settings = self.out_settings.get_table_settings(table_name, dynamic_settings)
        self.db_loader.load_data_to_config(table_name, self.current_shz_code, tab_settings.data_configure_list)
        self.export_to_excel(tab_settings)


    def export_to_excel(self, tab_settings):
        self.xl_exporter.run_table_export(tab_settings)


                # try:
        #     failed_dbfs, not_executed_queries = run_collection(self.dbf_fls_path, self.mdb_out_file)
        # except Exception as err:
        #     self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), str(err))
        #     raise err
        # if len(failed_dbfs):
        #     self.emit(QtCore.SIGNAL(u'some_dbf_failed(PyQt_PyObject)'), failed_dbfs)
        # if len(not_executed_queries):
        #     self.emit(QtCore.SIGNAL(u'some_inserts_failed(PyQt_PyObject)'), not_executed_queries)
        # else:
        #     self.emit(QtCore.SIGNAL(u'successfully_completed(const QString&)'), 'OK')
        # else:
        #     if err_li:
        #         self.emit(QtCore.SIGNAL(u'contr_failed(PyQt_PyObject)'), err_li)
        #     else:
        #         self.emit(QtCore.SIGNAL(u'control_passed()'))


#
#
# class FileCopyThread(QtCore.QThread):
#     def __init__(self, parent = None):
#         super(FileCopyThread, self).__init__(parent)
#         self.file_src = ''
#         self.file_destination = ''
#
#
#     def copy_file(self, file_src, file_destination):
#         self.file_src = file_src
#         self.file_destination = file_destination
#         self.start()
#
#
#     def run(self):
#         if not self.file_destination or not self.file_src:
#             self.emit(QtCore.SIGNAL(u'error(const QString&)'), error_titles.not_enough_data)
#             return
#         try:
#
#             print self.file_src, self.file_destination
#             shutil_copyfile(self.file_src, self.file_destination)
#         except Exception as err:
#             self.emit(QtCore.SIGNAL(u'success(const QString&)'), self.file_src)
#             # self.emit(QtCore.SIGNAL(u'error(const QString&)'), str(err))
#             return
#
#         new_file_name = os.path.basename(self.file_src)
#         self.emit(QtCore.SIGNAL(u'success(const QString&)'), os.path.join(self.file_destination, new_file_name))
#



