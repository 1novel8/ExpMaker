#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from DbTools import DBConn



class OptionsProvider(DBConn):
    def __init__(self, db_path):
        self.db_path = db_path
        self.error = None
        self.raions_names = {}
        self.shz_names = {}
        self.tables_names = {}



        self.obl_name = ''
        self.default_src_db_path = ''
        self.default_out_xls_dir = ''
        self.tables_structure = {}
        if not path.isfile(db_path):
            return
        super(OptionsProvider, self).__init__(db_path)

        self.primary_requirements = [
            {'tab_name': '_DEFAULT_SETTINGS', 'fields': ['Key', 'Value']},
            {'tab_name': '_TABLE_INPUT_NAMES', 'fields': ['Num_Tab', 'Name_Tab_mdb', 'Name_xls_file']}
        ]

        self.secondary_requirements = [
            {'tab_name': '_SOATO_RAYON_NAMES', 'fields': ['SOATO', 'Name_rayon']},
            {'tab_name': '_USERS_SHZ_NAMES', 'fields': ['SOATO', 'CHOZ', 'NHOZ']},
        ]

        try:
            self.validate_structure()
        except Exception as err:
            self.error = {
                'err_type': 'unhandled',
                'err': err
            }
        if self.error:
            return
        self.update_tables_names()
        self.update_raion_names()
        if len(self.raions_names):
            first_raion = sorted(self.raions_names.keys())[0]
            self.update_shz_names(self.raions_names[first_raion])


    def get_all_tab_names(self):
        all_tabs = []
        for tab_key in self.tables_names:
            all_tabs.append(self.tables_names[tab_key]['tab_name'])
        return all_tabs


    def validate_structure(self):
        if not DBConn.is_valid_mdb_file(self.db_path):
            self.error = {'err_type': 'file_not_valid'}
            return
        test = DBConn.test_connection_to_file(self.db_path)
        if test != 'OK':
            self.error = {'err_type': 'failed_to_connect'}
            return
        self.tables_structure = self.get_tabs_with_field_names()
        try:
            self.check_primary_requirements()
        except Exception as err:
            self.error = {'err_type': 'primary_req_failed', 'err': err}
            return
        try:
            self.check_secondary_requirements()
        except Exception as err:
            self.error = {'err_type': 'secondary_req_failed', 'err': err}


    def check_primary_requirements(self):
        for tab_requirement in self.primary_requirements:
            tab_name = tab_requirement['tab_name']
            if tab_name not in self.tables_structure:
                raise Exception('No required table: ' + tab_name)

            for filed_required in tab_requirement['fields']:
                if filed_required not in self.tables_structure[tab_name]:
                    raise Exception('No required field %s in table %s' % (filed_required, tab_name))
            if tab_name == '_DEFAULT_SETTINGS':
                try:
                    self.set_defaults()
                except Exception as err:
                    raise Exception('failed to set defaults')

    def set_defaults(self):
        query = 'Select Key, Value from _DEFAULT_SETTINGS'
        defaults = {}
        for row in self.exec_sel_query(query):
            defaults[row[0]] = row[1]
        if '_CURRENT_OBL_' in defaults:
            self.obl_name = defaults['_CURRENT_OBL_']
            db_path_key = self.obl_name + '_DB_PATH'
            if db_path_key in defaults:
                self.default_src_db_path = defaults[db_path_key]
            xls_path_key = self.obl_name + '_XLS_PATH'
            if xls_path_key in defaults:
                self.default_out_xls_dir = defaults[xls_path_key]
        else:
            raise Exception('failed to set defaults')


    def check_secondary_requirements(self):
        for tab_requirement in self.secondary_requirements:
            tab_name = self.obl_name + tab_requirement['tab_name']
            if tab_name not in self.tables_structure:
                raise Exception('No required table: ' + tab_name)

            for filed_required in tab_requirement['fields']:
                if filed_required not in self.tables_structure[tab_name]:
                    raise Exception('No required field %s in table %s' % (filed_required, tab_name))


    def update_raion_names(self):
        self.raions_names = {}
        if self.error:
            return
        query = 'Select Name_rayon, SOATO from %s_SOATO_RAYON_NAMES' % self.obl_name
        try:
            result = self.exec_sel_query(query)
            for (raion, code) in result:
                self.raions_names[raion] = code
        except Exception as err:
            print err


    def update_shz_names(self, soato_code):
        self.shz_names = {}
        if self.error or not soato_code:
            return
        query = "Select CHOZ, NHOZ from %s_USERS_SHZ_NAMES where SOATO = '%s';" % (self.obl_name, soato_code)
        try:
            # self.make_connection()
            result = self.exec_sel_query(query)
            for (choz, nhoz) in result:
                self.shz_names[choz] = nhoz
        except Exception as err:
            print err


    def update_tables_names(self):
        self.tables_names = {}
        if self.error:
            return
        query = 'Select Num_Tab, description, Name_Tab_mdb, Name_xls_file from _TABLE_INPUT_NAMES'
        try:
            result = self.exec_sel_query(query)
            for (num_tab, tab_descr, tab_name, out_name) in result:
                self.tables_names[num_tab] = {
                    'tab_name': tab_name,
                    'tab_descr': tab_descr,
                    'out_name': out_name
                }

        except Exception as err:
            print err


    def get_sorted_talble_names(self):
        sorted_tables = [u'Экспортировать все',]
        if len(self.tables_names):
            sorted_nums = sorted(self.tables_names.keys())
            for key in sorted_nums:
                sorted_tables.append(str(key) + '. ' + self.tables_names[key]['tab_descr'])
        return sorted_tables


    def get_tab_name_by_item(self, item):
        if item == u'Экспортировать все':
            return 'all', 'All'
        try:
            num_key = int(item.split('.')[0])
        except ValueError:
            print 'Warning. Provided with failed options'
            num_key = 1
        if self.tables_names.has_key(num_key):
            return self.tables_names[num_key]['tab_name'], self.tables_names[num_key]['out_name']
        else:
            return '', ''