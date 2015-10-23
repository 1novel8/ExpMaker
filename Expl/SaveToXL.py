#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import openpyxl

def add_values_cells(data, cells):
    zips =  zip(data, cells)
    for row in zips:
        for v,c in zip(row[0], row[1]):
            c.value = v

def get_max_xl_letter(row_len):
    if row_len<17:      return u'U'
    elif row_len<27:    return u'AE'
    else:               return u'AZ'

def exp_svodn_fa(matrix, save_as):
    w_book = openpyxl.load_workbook(u'XL_forms\\FA_svod.xlsx')
    sheet = w_book.active
    max_letter = get_max_xl_letter(len(matrix[0]))
    cells_tmp =  tuple(sheet.iter_rows(u'A3:%s%d' % (max_letter,len(matrix)+3)))
    add_values_cells(matrix,cells_tmp)
    w_book.save(save_as)
    os.system(u'start excel.exe %s' % save_as)

def exp_single_fa(fa_data, f22_ind, obj_name, expl_file):
    excel_path = os.path.dirname(expl_file)+ u'\\%s_xlsx_files' % os.path.basename(expl_file)[4:-4]
    if not os.path.exists(excel_path): os.makedirs(excel_path)
    dest_filename = u'%s\\%s.xlsx'%(excel_path, f22_ind)
    w_book = openpyxl.load_workbook(u'XL_forms\\FA.xlsx')
    sheet = w_book.active
    sheet.title = u'Выборочная экспликация'
    sheet[u'M4'] = obj_name
    xl_letter = get_max_xl_letter(len(fa_data[0]))
    cells_temp =  tuple(sheet.iter_rows(u'F15:%s%d' % (xl_letter, 14+len(fa_data))))
    add_values_cells(fa_data,cells_temp)
    w_book.save(dest_filename)
    os.system(u'start excel.exe %s' %  dest_filename)

def export_toxl_fb(data_dict, save_as):
    list_1_fields = [u'f_1', u'f_2', u'f_3', u'f_4', u'f_5', u'f_6',u'f_7', u'f_row09', u'f_row10']
    list_2_fields = [u'f_8', u'f_9', u'f_10', u'f_11', u'f_12', u'f_13',u'f_14', u'f_15', u'f_16']
    list_3_fields = [u'f_melio1', u'f_melio2', u'f_servtype', u'f_state02',u'f_state03', u'f_state04', u'f_state05', u'f_state06', u'f_state07', u'f_state08']
    sh_1_data, sh_2_data, sh_3_data = [], [], []
    sh_1_p1, sh_2_p1, sh_3_p1 = [], [], []
    int_f22_keys = map(lambda x: [int(x), x],data_dict)
    for i in sorted(int_f22_keys):
        if i[0] == 29:
            sh_1_p1, sh_2_p1, sh_3_p1 = sh_1_data, sh_2_data, sh_3_data
            sh_1_data, sh_2_data, sh_3_data = [], [], []
        f22_key = i[1]
        l1_row, l2_row, l3_row = [],[],[]
        for key in list_1_fields:
            l1_row.append(data_dict[f22_key][key])
        sh_1_data.append(l1_row)
        for key in list_2_fields:
            l2_row.append(data_dict[f22_key][key])
        sh_2_data.append(l2_row)
        for key in list_3_fields:
            l3_row.append(data_dict[f22_key][key])
        sh_3_data.append(l3_row)
    w_book = openpyxl.load_workbook(u'XL_forms\\FB.xlsx')

    def write_to_sheet(data_1, data_2, sh_num):
        if sh_num == 1: ex_f1, ex_f2 = u'E', u'M'
        elif sh_num == 2: ex_f1, ex_f2 = u'C', u'K'
        else: ex_f1, ex_f2 = u'C', u'L'
        sheet = w_book.get_sheet_by_name(u'Лист %d' % sh_num)
        cells_tmp =  tuple(sheet.iter_rows(u'%s5:%s32' %( ex_f1, ex_f2)))
        add_values_cells(data_1,cells_tmp)
        cells_tmp =  tuple(sheet.iter_rows(u'%s34:%s48' %( ex_f1, ex_f2)))
        add_values_cells(data_2,cells_tmp)

    write_to_sheet(sh_1_p1, sh_1_data, 1)
    write_to_sheet(sh_2_p1, sh_2_data, 2)
    write_to_sheet(sh_3_p1, sh_3_data, 3)
    w_book.save(save_as)
    os.system(u'start excel.exe %s' % save_as)
