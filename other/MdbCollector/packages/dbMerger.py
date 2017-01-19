#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import listdir
from os import path
import shutil
from DbTools import DBConn, DbError



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