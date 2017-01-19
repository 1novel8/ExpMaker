#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import listdir
from os import path
import shutil
from DbTools import DBConn, DbError



class OptionsProvider(DBConn):
    def __init__(self, db_path):
        self.db_path = db_path
        self.error = {}
        self.raions_names = {}
        self.shz_names = {}
        self.tables_names = {}
        if not path.isfile(db_path):
            return

        super(OptionsProvider, self).__init__(db_path)
        self.required_structure = {
            '_SOATO_RAYON_NAMES': ['SOATO', 'Name_rayon'],
            '_TABLE_INPUT_NAME': ['Num_Tab', 'Name_Tab_mdb', 'description'],
            '_USERS_SHZ_NAMES': ['SOATO', 'CHOZ', 'NHOZ']
        }
        self.validate_structure()
        if self.check_error():
            return
        self.update_tables_names()
        self.update_raion_names()
        if len(self.raions_names):
            first_raion = sorted(self.raions_names.keys())[0]
            self.update_lands_names(self.raions_names[first_raion])




    def validate_structure(self):
        if not DBConn.is_valid_dbf_file(self.db_path):
            self.error['notValid'] = True
            return
        test = DBConn.test_connection_to_file(self.db_path)
        if test != 'ok':
            self.error['notValid'] = test
            return
        tabs_fields = self.get_tabs_with_field_names()
        for tab_name in self.required_structure:
            if not tabs_fields.has_key(tab_name):
                self.error['noTable'] = tab_name
                return
            for req_field in self.required_structure[tab_name]:
                if not tabs_fields[tab_name].has_key(req_field):
                    self.error['noField'] = (tab_name, req_field)
                    return

    def check_error(self):
        err_message = ''
        if len(self.error.keys()):
            print self.error
            err_message = self.error[self.error.keys()[0]]
        return err_message

    def update_raion_names(self):
        self.raions_names = {}
        if len(self.error.keys()):
            return
        query = 'Select Name_rayon, SOATO from _SOATO_RAYON_NAMES'
        try:
            result = self.exec_sel_query(query)
            for (raion, code) in result:
                self.raions_names[raion] = code
        except Exception as err:
            print err


    def update_lands_names(self, soato_code):
        self.shz_names = {}
        if len(self.error.keys()) or not soato_code:
            return
        query = "Select CHOZ, NHOZ from _USERS_SHZ_NAMES where SOATO = '%s';" % soato_code
        try:
            result = self.exec_sel_query(query)
            for (choz, nhoz) in result:
                self.shz_names[choz] = nhoz
        except Exception as err:
            print err


    def update_tables_names(self):
        self.tables_names = {}
        if len(self.error.keys()):
            return
        query = 'Select Num_Tab, description, Name_Tab_mdb from _TABLE_INPUT_NAME'
        try:
            result = self.exec_sel_query(query)
            for (num_tab, tab_descr, tab_name) in result:
                self.tables_names[num_tab] = {
                    'tab_name': tab_name,
                    'tab_descr': tab_descr
                }

        except Exception as err:
            print err


    def get_sorted_talble_names(self):
        sorted_tables = []
        if len(self.tables_names):
            sorted_nums = sorted(self.tables_names.keys())
            for key in sorted_nums:
                sorted_tables.append(str(key) + '. ' + self.tables_names[key]['tab_descr'])
        return sorted_tables

    def get_tab_name_by_item(self, item):
        try:
            num_key = int(item.split('.')[0])
        except ValueError:
            print 'Warning. Provided with failed options'
            num_key = 1
        if self.tables_names.has_key(num_key):
            return self.tables_names[num_key]['tab_name']
        else:
            return ''


def get_mdb_file_names(fls_path):

    def is_valid_dbf_file(f):
        if not path.isfile(path.join(fls_path, f)):
            return False
        if not f.lower()[-3:] == u'mdb':
            return False
        return True

    return [f for f in listdir(fls_path ) if is_valid_dbf_file(f)]


def test_connection_to_file(mdb_path):
    try:
        mdb_db = DBConn(mdb_path)
        mdb_out_structure = mdb_db.get_tabs_with_field_names()
        del mdb_db
        if len(mdb_out_structure):
            return 'ok'
        else:
            raise Exception('Database is empty')
    except Exception as err:
        return err


def generate_out_template_name(file_dir):
    default_name = 'output.mdb'
    while True:
        if path.isfile(path.join(file_dir, default_name)):
            default_name = '_' + default_name
        else:
            break
    return default_name


out_template_name = 'output.mdb'
def make_template_by_first_valid_mdb(all_mdbs, files_dir):
    errors = []
    for mdb_name in all_mdbs:
        mdb_file_path = path.join(files_dir, mdb_name)

        test_result = test_connection_to_file(mdb_file_path)
        if test_result == 'ok':
            try:
                global out_template_name
                out_template_name = generate_out_template_name(files_dir)
                shutil.copyfile(mdb_file_path, path.join(files_dir, out_template_name))
            except shutil.Error:
                raise DbError('shutil_err', mdb_file_path, {})
            break
        else:
            errors.append(test_result)
    return errors


def merge_structure_to_template(template_db, tmpl_str, update_str):
    for tab_name in update_str:
        if tmpl_str.has_key(tab_name):
            for field_name in update_str[tab_name]:
                template_db.add_field_if_not_exists(tab_name, field_name, update_str[tab_name][field_name])
        else:
            template_db.create_table(tab_name, update_str[tab_name])




def merge_all_mdbs_in_folder(fls_dir):
    all_mdbs = get_mdb_file_names(fls_dir)
    errors_before_tmp_created = make_template_by_first_valid_mdb(all_mdbs, fls_dir)
    errs_len = len(errors_before_tmp_created)
    if errs_len:
        if errs_len == len(all_mdbs) - 1:
            raise Exception('Operation failed. No connection to 2 or more files to merge')

    all_mdbs = all_mdbs[errs_len + 1 :]

    template_db = DBConn(path.join(fls_dir, out_template_name))
    tmpl_structure = template_db.get_tabs_with_field_names()

    failed_mdbs = {}
    for mdb_name in all_mdbs:
        if 'output' in mdb_name:
            continue
        mdb_path = path.join(fls_dir, mdb_name)
        try:
            test_connection_to_file(mdb_path)
        except Exception as err:
            failed_mdbs[mdb_name] = 'Connection Error: ' + str(err)
            continue

        mdb_db = DBConn(mdb_path)
        update_structure = mdb_db.get_tabs_with_field_names()
        try:
            merge_structure_to_template(template_db, tmpl_structure, update_structure)
        except Exception as err:
            print unicode(err)
            failed_mdbs[mdb_name] = 'Merging Structure Error: ' + str(err)
            continue

        exec_errors = {
            'loadAll': [],
            'insert': []
        }
        for table_name in update_structure:
            all_fields = update_structure[table_name].keys()
            try:
                all_data = mdb_db.select_all(table_name, all_fields)
            except Exception:
                exec_errors['loadAll'].append(table_name)
                continue
            for row in all_data:
                try:
                    template_db.insert_row(table_name, all_fields, row)
                except Exception:
                    exec_errors['insert'].append(table_name)
                    break

        if len(exec_errors['loadAll']):
            failed_mdbs[mdb_name] = {'loadAllErrors': exec_errors['loadAll']}
        if len(exec_errors['insert']):
            failed_mdbs[mdb_name] = {'typeErrors': exec_errors['insert']}
    print failed_mdbs
    return failed_mdbs



if __name__ == '__main__':
    test_files_dir = '../../mergeTest'
    merge_all_mdbs_in_folder(test_files_dir)