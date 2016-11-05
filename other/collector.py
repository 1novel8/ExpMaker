#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import openpyxl
import pyodbc
from dbfread import DBF

from os import listdir
from os.path import isfile, join
project_dir = os.getcwd()

def is_valid_xl_file(f):
    if not isfile(join(project_dir, f)):
        return False
    if not (f.lower()[-4:] == u'xlsx' or f.lower()[-3:] == u'xls'):
        return False
    return True

xls_files = [f for f in listdir(project_dir) if is_valid_xl_file(f)]

def run_searched_files(searched_files):
    for f in searched_files:
        if isinstance(f, str):
           get_w_sheets(f)


def get_wb(xls_file_path):
    return openpyxl.load_workbook(filename=xls_file_path, use_iterators=True)


def get_w_sheets(xls_file_path):
    wb = get_wb(xls_file_path)
    return wb.get_sheet_names()


default_sheet_name = u'sheet_1'
def get_sheet_by_name(work_book, sh_name = None):
    sh_name = unicode(sh_name)
    if sh_name in work_book.sheetnames:
        sheet_name = sh_name
    else:
        sheet_name = sh_name if sh_name else default_sheet_name
        work_book.create_sheet(title=sheet_name, index=0)
    return work_book.get_sheet_by_name(sheet_name)


def get_dbf_table(file_path):
    try:
        db = DBF(file_path)
        print db
    except Exception as err:
        print err
        raise err


    out_table = []
    for rec in db:
        new_rec = {}
        for key in rec:
            if key[0] != '_':
                new_rec[key] = rec[key]
        out_table.append(new_rec)

    return out_table


def getMdbStructureFromXls(xls_file_path):

    available_types = {
        'Long': 'INTEGER',
        'Floa': 'DOUBLE',
        'Shor': 'SMALLINT',
        'Text': 'VARCHAR',

    }

    wb = get_wb(xls_file_path)
    shts = wb.get_sheet_names()
    structure_doc = {}
    for sh_name in shts:

        sheet = get_sheet_by_name(wb, sh_name)
        structure_doc[sh_name] = {
            'tab_name': sheet.cell(u'B1').value,
            'NPRIZNAK': {
                'dbf_field': 'NPRIZNAK',
                'mdb_type': 'VARCHAR'
            },
            'CTITLE': {
                'dbf_field': 'CTITLE',
                'mdb_type': 'VARCHAR'
            }
        }

        f_cell_num = 3
        while True:
            try:
                field_name = sheet.cell(u'C%d' % f_cell_num).value
            except Exception:
                break
            if not field_name:
                break
            dbf_field = sheet.cell(u'D%d' % f_cell_num).value
            dbf_type = sheet.cell(u'E%d' % f_cell_num).value
            try:
                mdb_type = available_types[dbf_type[:4]]
            except KeyError:
                mdb_type = 'VARCHAR'
            except TypeError:
                print 'warning on table' + sh_name
                mdb_type = 'VARCHAR'
            structure_doc[sh_name][field_name] = {
                'dbf_field': dbf_field,
                'mdb_type': mdb_type
            }
            f_cell_num += 1
    return structure_doc


def getDbfFileNames(fls_path):

    def is_valid_dbf_file(f):
        if not isfile(join(project_dir, f)):
            return False
        if not f.lower()[-3:] == u'dbf':
            return False
        return True

    return[f for f in listdir(fls_path ) if is_valid_dbf_file(f)]


def collectDataToMdb(dbf_path, mdb_str):
    dbf_files = getDbfFileNames(dbf_path)
    print dbf_files


if __name__ == u'__main__':
    xls_str_file = project_dir + '\\structure.xlsx'
    mdb_out_file = project_dir + '\\ProbaCO6258.mdb'
    dbf_fls_path = project_dir + '\\dbf_files'
    xls_str = getMdbStructureFromXls(xls_str_file)
    collectDataToMdb(dbf_fls_path, xls_str)
    # get_dbf_table(project_dir + '\\t02_6258000005.dbf')
    # run_searched_files(xls_files)
