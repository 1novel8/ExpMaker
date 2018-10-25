#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Alex Konkov'

import os.path
import shutil
import pyodbc
from ..errors import DbError
from .db_decorators import try_make_conn, catch_db_exception


class DbConnector(object):
    def __init__(self, db_path, do_conn=True):
        self.db_f_path = db_path
        self.db_access = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' % db_path
        self.__conn = None
        self.__dbc = None
        self.reconnect = False
        if do_conn:
            self.make_connection()

    @property
    def get_dbc(self):
        return self.__dbc

    @property
    def has_dbc(self):
        return True if self.__dbc else False

    def make_connection(self):
        if not self.__dbc:
            try:
                self.__conn = pyodbc.connect(self.db_access, autocommit=True, unicode_results=True)
                self.__dbc = self.__conn.cursor()
            except pyodbc.Error:
                self.__dbc = None

    def close_conn(self):
        try:
            self.__dbc.close()
            self.__conn.close()
        except Exception:
            pass

    def run_db(self):
        os.system(u'start %s' % self.db_f_path)

    @try_make_conn
    def get_tab_names(self):
        return [row[2] for row in self.__dbc.tables(tableType='TABLE')]

    @try_make_conn
    def __get_columns(self, table_name):
        return self.__dbc.columns(table=table_name)

    @try_make_conn
    def get_f_names(self, table_name):
        f_names = []
        for f_info in self.__get_columns(table_name):
            f_names.append(f_info[3])
        return f_names

    @try_make_conn
    def get_f_names_types(self, table_name):
        f_name_type = {}
        try:
            for f_info in self.__get_columns(table_name):
                f_name_type[f_info[3]] = f_info[5]
            return f_name_type
        except TypeError:
            raise Exception(u'Ошибка соединения с базой данных')

    def get_common_selection(self, table, fields, where_case=u''):
        query = u'select '
        query += u', '.join(fields)
        query += u' from %s %s' % (table, where_case)
        rc_rows = self.exec_sel_query(query)
        result = []
        for row in rc_rows:
            row_dict = {}
            for ind in range(len(fields)):
                row_dict[fields[ind]] = row[ind]
            result.append(row_dict)
        return result

    @try_make_conn
    @catch_db_exception
    def exec_sel_query(self, query):
        return [row for row in self.__dbc.execute(query).fetchall()]

    @try_make_conn
    @catch_db_exception
    def select_single_f(self, query):
        return [row[0] for row in self.__dbc.execute(query).fetchall()]

    @try_make_conn
    @catch_db_exception
    def exec_covered_query(self, query, covered_args):
        return self.__dbc.execute(query, covered_args)

    @try_make_conn
    @catch_db_exception
    def exec_query(self, query):
        return self.__dbc.execute(query)

    # def insert_row(self, tab_name, fields, vals):
    #     if len(fields) == len(vals):
    #         ins_query = u'insert into %s(' % tab_name
    #         f_count = len(fields)-1
    #         ins_query+=u'?,'*f_count+u'?) values (' + u'?,'*f_count +u'?);'
    #         args = tuple(fields+vals)
    #         self.exec_covered_query(ins_query, args)
    #     return False

    def get_tab_dict(self, query):
        """Вернет словарь на основе данных полученных в результате выполнения запроса.
            :key - первый параметр запроса
            :value - список оставшихся параметров"""
        rc_dict = {}
        rc_rows = self.exec_sel_query(query)
        if isinstance(rc_rows, list):
            for row in rc_rows:
                rc_dict[row[0]] = list(row[1:])
            return rc_dict
        else:
            return {}

    def get_tab_list(self, query):
        result = self.exec_sel_query(query)
        if isinstance(result, list):
            return result
        else:
            return []

    def guarantee_dbf_exists(self, template):
        if not os.path.isfile(self.db_f_path):
            # templ = os.path.join(templ_path, 'template.mdb')
            if os.path.isfile(template):
                try:
                    shutil.copyfile(template, self.db_f_path)
                except Exception:
                    raise DbError('err_create_file', self.db_f_path)
            else:
                raise DbError('tmpl_empty', template)

    def run_db_process(self):
        self.close_conn()
        os.system(u'start %s' % self.db_f_path)

    def __del__(self):
        self.close_conn()
