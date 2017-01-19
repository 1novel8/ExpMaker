#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import shutil

import pyodbc

class DbError(Exception):
    def __init__(self, err_type, dynamic_message, data = None):
        self.data = data
        self.message = DbError.concat_message_by_type(err_type, dynamic_message)
        super(DbError, self).__init__(self.message)

    @staticmethod
    def concat_message_by_type(err_type, dynamic_message = ''):
        f = lambda x: x % unicode(dynamic_message)
        msg = {
            'failed': f(u'Ошибка соединения с базой данных %s'),
            'query_stack': f(u'Не удалось выполнить запрос %s'),
            'tmpl_empty': f(u'Не удалось найти шаблонный файл %s либо он поврежден.'),
            'err_create_file': f(u'Ошибка при попытке создания файла %s'),
            'shutil_err': f(u'Ошибка при попытке скопировать файл %s. \nВозможное решение: измените права доступа к файлу.'),
            'create_t_fail': f(u'Не удалось создать таблицу %s'),
            'insert_failed': f(u'failed to insert row into %s. Check input types')
        }
        if err_type in msg:
            return msg[err_type]
        else:
            return dynamic_message


def catch_db_exception(func_runs_query):
    """
    Decorator for functions with connection to database
    decorator is decorated to take parameter self
    """
    def wrapper(self, *args, **kwargs):
        try:
            return func_runs_query(self, *args, **kwargs)
        except pyodbc.ProgrammingError:
            raise DbError(u'query_stack', args)
        except pyodbc.Error:
            raise DbError(u'failed', args)

    return wrapper


def try_make_conn(func_with_connect):
    """
    Decorator for functions with connection to database
    decorator is decorated to take parameter self
    """
    conn_attempt = {1:True}
    def wrapper(self,  *args, **kwargs):
        if self.get_dbc:
            conn_attempt[1] = True
            return func_with_connect(self, *args, **kwargs)
        elif conn_attempt[1]:
            conn_attempt[1] = False
            self.make_connection()
            return wrapper(self, *args, **kwargs)
        else:
            raise Exception(u'Database connection failed')
    return wrapper

class DBConn(object):
    def __init__(self, db_path, do_conn = True):
        self.db_f_path = db_path
        self.db_access = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' % db_path
        self.__conn = None
        self.__dbc = None
        self.reconnect = False
        self.created_tables = {}
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
                self.__conn = pyodbc.connect(self.db_access, autocommit = True, unicode_results = True)
                self.__dbc = self.__conn.cursor()
            except pyodbc.Error:
                self.__dbc = None
                raise DbError('failed', self.db_f_path, {})

    def close_conn(self):
        try:
            self.__dbc.close()
            self.__conn.close()
        except: pass

    def run_db(self):
        os.system(u'start %s' % self.db_f_path)

    @try_make_conn
    def get_tab_names(self):
        return [row[2] for row in self.__dbc.tables(tableType='TABLE')]


    @try_make_conn
    def __get_columns(self, table_name):
        return self.__dbc.columns(table= table_name)


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
        return  self.__dbc.execute(query, covered_args)


    @try_make_conn
    @catch_db_exception
    def exec_query(self, query):
        return  self.__dbc.execute(query)

    # def insert_row(self, tab_name, fields, vals):
    #     if len(fields) == len(vals):
    #         ins_query = u'insert into %s(' % tab_name
    #         f_count = len(fields)-1
    #         ins_query+=u'?,'*f_count+u'?) values (' + u'?,'*f_count +u'?);'
    #         args = tuple(fields+vals)
    #         self.exec_covered_query(ins_query, args)
    #     return False


    def create_table(self, tab_name, field_str, with_id = False, f_order = None):
        create_query = u'create table ' + tab_name + u'('
        if with_id:
            create_query += 'ID AUTOINCREMENT,'
        if not f_order:
            f_order = field_str.keys()

        for f in f_order:
            create_query += '%s %s, ' %(f, field_str[f])

        if with_id:
            create_query += u'PRIMARY KEY(ID));'
        else:
            create_query = create_query[:-2] + u');'
        try:
            self.exec_query(create_query)
        except DbError:
            raise DbError(u'create_t_fail', create_query)
        else:
            self.created_tables[tab_name] = field_str

    def select_all(self, tab_name, fields = None):
        selector = '*'
        if fields:
           selector = ','.join(fields)
        return self.exec_sel_query('SELECT %s FROM %s' % (selector, tab_name))


    def get_tab_dict(self, query):
        """Вернет словарь на основе данных полученных в результате выполнения запроса.
            :key - первый параметр запроса
            :value - список оставшихся параметров"""
        rc_dict ={}
        rc_rows = self.exec_sel_query(query)
        if isinstance(rc_rows, list):
            for row in rc_rows:
                rc_dict[row[0]] = list(row[1:])
            return rc_dict
        else: return {}


    def get_tab_list(self, query):
        result = self.exec_sel_query(query)
        if isinstance(result, list):
            return result
        else: return []


    def guarantee_dbf_exists(self, template):
        if not os.path.isfile(self.db_f_path):
            # templ = os.path.join(templ_path, 'template.mdb')
            if os.path.isfile(template):
                try:
                    shutil.copyfile(template, self.db_f_path)
                except:
                    raise DbError('err_create_file', self.db_f_path)
            else:
                raise DbError('tmpl_empty', template)


    def add_field_if_not_exists(self, tab_name, col_name, col_type):
        if col_name not in self.get_f_names(tab_name):
            self.exec_query(u'ALTER TABLE %s ADD %s %s;' % (tab_name, col_name, col_type))


    def run_db_process(self):
        self.close_conn()
        os.system(u'start %s' % self.db_f_path)



    def get_tabs_with_field_names(self):
        """

        :return: Dict with table names as keys and fields data as values
        """
        tabs_fields = {}
        for tab in self.get_tab_names():
            tabs_fields[tab] = self.get_f_names_types(tab)
        return tabs_fields


    def insert_row(self, t_name, fields, vals):
        if len(fields) != len(vals):
            raise DbError('insert_failed', t_name, 'Count of fields not equal to count of values')
        fields = u','.join(fields)
        vals = map(lambda x: u"'%s'" % x if isinstance(x, (unicode, str)) else unicode(x), vals)
        vals = u','.join(vals)
        ins_query = u'INSERT INTO %s( %s ) VALUES ( %s )' % (t_name, fields, vals)
        try:
            self.exec_query(ins_query)
        except Exception as err:
            print ins_query
            raise DbError('insert_failed', t_name, ins_query)


    def clear_table(self, table_name):
        query = u'DELETE * FROM %s' % table_name
        try:
            self.exec_query(query)
        except Exception as err:
            raise DbError('failed to clear table %s' % table_name)


    def __del__(self):
        self.close_conn()

class DbControl(object):
    def __init__(self, db_path, db_schema_pattern, temp_db_path = None):
        self.db_path = db_path
        self.db_schema = db_schema_pattern
        if temp_db_path:
            try:
                shutil.copyfile(db_path, temp_db_path)
            except shutil.Error:
                raise DbError('shutil_err', db_path)
            self.db_path = temp_db_path
        self.conn = DBConn(self.db_path)

    def __del__(self):
        del self.conn

    @property
    def is_connected(self):
        return self.conn.has_dbc

    def contr_tables(self):
        lost_tables = []
        tab_names = self.conn.get_tab_names()
        for tab in self.db_schema:
            if tab not in tab_names:
                lost_tables.append(tab)
        return lost_tables

    def is_tables_empty(self):
        """
        :return: Tables from __need_tabs that has no any data
        """
        no_data = []
        for tab in self.db_schema:
            if not self.conn.exec_sel_query(u'select * from %s' % tab):
                no_data.append(tab)
        if no_data:
            return no_data
        else:
            return False

    def contr_field_types(self):
        """
        the method compares default db field schema with connected db
        :return: nested dictionary like "tab_name" : "field_name" : [field, (field, type), field, ....]
        """
        fails = {}
        for tab in self.db_schema:
            loaded_tab_schema = self.conn.get_f_names_types(tab)
            bad_fields = []
            for field in self.db_schema[tab]:
                f_name = self.db_schema[tab][field]['name']
                f_types = self.db_schema[tab][field]['type']
                if f_name not in loaded_tab_schema:
                    bad_fields.append(f_name)
                elif loaded_tab_schema[f_name] not in f_types:
                    bad_fields.append((f_name, f_types))
            if bad_fields:
                fails[tab] = tuple(bad_fields)
        return fails

    def get_all_fields(self):
        all_fields = {}
        for tab in self.db_schema:
            all_fields[tab] = self.conn.get_f_names_types(tab)
        return all_fields
