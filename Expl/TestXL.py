#!/usr/bin/env python
# -*- coding: utf-8 -*-
import openpyxl
from xlrd import open_workbook
from xlutils.copy import copy
import os
# def a_test():
#     a = []
#     for i in range(11):
#         q = []
#         for e in range(16):
#             q.append(e+i)
#         a.append(q)
#     return a
# # Runfor xlsx format
#
# dest_filename = 'test.xlsx'
# wb = openpyxl.load_workbook('FB.xlsx')
# ws1 = wb.get_sheet_by_name(u'Лист 1')
# # ws1.title = u'Выборочная экспликация'
# a = a_test()
# cells_temp =  ws1.iter_rows('F15:U30')
# zips =  zip(a, cells_temp)
# for row in zips:
#     for v,c in zip(row[0], row[1]):
#         c.value = v
# wb.save(dest_filename)
#
# os.system('start excel.exe %s' % dest_filename)

#Run for xls format
#
# rb = open_workbook('FA.xls',formatting_info=True)
# # rs = rb.sheet_by_index(0)
# wb = copy(rb)
# ws = wb.get_sheet(0)
# a = a_test()
# for ind, item in zip(range(14, len(a)+14), a):
#     for i, v in zip(range(5, len(item)+5), item):
#         ws.write(ind, i, v)
#
#
# wb.save('output.xls')
# os.system('start excel.exe output.xls')
#
#

import os, sys

print sys.argv
# print os.environ
print sys.path
print os.path.dirname(__file__)









