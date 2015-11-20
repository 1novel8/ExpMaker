#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import openpyxl

def get_max_xl_letter(row_len):
    if row_len<17:      return u'U'
    elif row_len<27:    return u'AE'
    else:               return u'AZ'

def add_values_cells(data, cells):
    zips =  zip(data, cells)
    for row in zips:
        for v,c in zip(row[0], row[1]):
            c.value = v

def exp_matrix(matrix, save_as = False, start_f = u'A', start_r = 3, templ_name = u'FA_svod'):
    w_book = openpyxl.load_workbook(u'XL_forms\\%s.xlsx'%templ_name)
    sheet = w_book.active
    max_letter = get_max_xl_letter(len(matrix[0]))
    cells_tmp =  tuple(sheet.iter_rows(u'%s%d:%s%d' % (start_f, start_r, max_letter,len(matrix)+start_r)))
    add_values_cells(matrix,cells_tmp)
    if save_as:
        w_book.save(save_as)
        os.system(u'start excel.exe %s' % save_as)
        return
    else: return w_book

def exp_single_fa(fa_data, f22_ind, obj_name, expl_file):
    excel_path = os.path.dirname(expl_file)+ u'\\%s_xlsx_files' % os.path.basename(expl_file)[4:-4]
    if not os.path.exists(excel_path): os.makedirs(excel_path)
    dest_filename = u'%s\\%s.xlsx'%(excel_path, f22_ind)
    w_book = exp_matrix(fa_data, start_f = u'F', start_r = 15, templ_name = u'FA')
    sheet = w_book.active
    sheet.title = u'Выборочная экспликация'
    sheet[u'M4'] = obj_name
    w_book.save(dest_filename)
    os.system(u'start excel.exe %s' %  dest_filename)
