#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from DbTools import DBConn


class DbLoader(DBConn):
    def __init__(self, db_path):
        self.db_path = db_path
        self.error = {}
        self.raions_names = {}
        self.shz_names = {}
        self.tables_names = {}
        self.tables_structure = None
        if not path.isfile(db_path):
            return
        super(DbLoader, self).__init__(db_path)
        self.validate_db()
        if self.check_error():
            return


    def validate_db(self):
        if not DBConn.is_valid_mdb_file(self.db_path):
            self.error['notValid'] = True
            return
        test = DBConn.test_connection_to_file(self.db_path)
        if test != 'OK':
            self.error['notValid'] = test
            return

    def check_table_structure(self, tab_name, tab_fields):
        if self.tables_structure is None:
            self.tables_structure = self.get_tabs_with_field_names()
        if tab_name not in self.tables_structure:
            raise Exception(u'В базе данных источнике отутствует таблица ' + unicode(tab_name))
        failed_fields = []
        for f in  tab_fields:
            if f not in self.tables_structure[tab_name]:
                failed_fields.append(f)
        if len(failed_fields):
            raise Exception(u'В базе данных источнике в таблице %s отсутствуют поля %s' % (tab_name, failed_fields))

    def check_error(self):
        err_message = ''
        if len(self.error.keys()):
            print self.error
            err_message = self.error[self.error.keys()[0]]
        return err_message

    def load_data_to_config(self, table_name, shz_code, config):
        for task in config:
            fields = ', '.join(task['db_fields'])
            where_cases = ["%s = '%s'" % ('UserN_CO', shz_code)]

            for where_obj in task['where_cases']:
                value = where_obj['value']
                field = where_obj['field']
                if isinstance(value, (str, unicode)):
                    value = u"'%s'" % value
                    where_cases.append("(%s = %s)" % (field, value))
                else:
                    where_cases.append("(%s = %d)" % (field, value))

            where_cases = ' AND '.join(where_cases)

            query = 'SELECT %s FROM %s WHERE %s' % (fields, table_name, where_cases)

            try:
                load_result = self.exec_sel_query(query)
                for row in load_result:
                    task['loaded_data'].append(row)
            except Exception as err:
                print err
                task['loaded_data'] = u'Failed to get data'