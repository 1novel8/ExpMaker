#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import pyodbc
import time
from Control import work_dir
# template_db = u'%s\\template.mdb' % workDir
access_dbf = u"%s\\tempDbase.mdb" % work_dir
dependOfCodes = dict(f_3=1, f_4=1, f_5=1, f_6=1, f_8 =1, f_9=1, f_10=1, f_11 =1, f_12=1, f_13 =1,f_15=1, f_16 =1,
                     f_melio1=2, f_melio2=2, f_servtype=3,
                     f_state02=4, f_state03=4, f_state04 =4, f_state05=4, f_state06=4, f_state07=4, f_state08 =4)


def round_row_data(data, accuracy = 4):
    try:
        return map(lambda x: round(x/10000, accuracy), data)
    except TypeError:
        return round(data/10000, accuracy)

def sum_by_lc(rowsli):
    if len(rowsli):
        sum_dict = dict.fromkeys(lcdict,0)
        for key in sum_dict.keys():
            for row in rowsli:
                if row[1] in lcdict[key]:
                    sum_dict[key] += row[0]
        sum_dict[u'f_2'] = sum_dict[u'f_3']+sum_dict[u'f_4']
        sum_dict[u'f_7'] = sum_dict[u'f_2']+sum_dict[u'f_5']+sum_dict[u'f_6']
        sum_dict[u'f_14'] = sum_dict[u'f_15']+sum_dict[u'f_16']
        sum_dict[u'f_1'] = sum(sum_dict[u'f_%d' % i] for i in (7,8,9,10,11,12,13,14))
        a = map(lambda x : sum_dict[u'f_%d' % x], range(1,len(sum_dict.keys())+1))
        return a
    else:
        return [0]*16

def make_expa_params(rowslist):
    fa_params = {u'f_01': sum_by_lc(rowslist)}
    for key in rcdict.keys():
        filtr_rows_li = [row[:2] for row in rowslist if row[dependOfCodes[key]] in rcdict[key]]
        fa_params[key] = sum_by_lc(filtr_rows_li)
    return fa_params

def select_sprav(query):
    __bgd = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s\\Spravochnik.mdb;' % work_dir
    conn = pyodbc.connect(__bgd, autocommit = True, unicode_results = True)
    dbc = conn.cursor()
    selresult = [row for row in dbc.execute(query).fetchall()]
    dbc.close()
    conn.close()
    return selresult

def make_row_codes():
    """
    Makes dictionary with Names of Rows in FormB as keys
    and LandCodes, RowCodes as values
    """
    codsdict ={}
    global rcdict
    rcdict = {}
    lcrows = select_sprav(u'select LandCode, NumberGraf from LandCodes')
    rcrows = select_sprav(u'select Code, RowNames from RowCodes')
    for row in lcrows:
        if u'f_%s' % row[1] in codsdict.keys():
            codsdict[u'f_%s' % row[1]].append(row[0])
        else:
            codsdict[u'f_%s' % row[1]] = [row[0]]
    global lcdict
    lcdict = codsdict.copy()
    for row in rcrows:
        rowli = row[0][1:-1].split(u',')
        rowli = map(lambda x: int(x), rowli)
        rcdict[row[1]] = rowli
    codsdict.update(rcdict)
    codsdict[u'f_7'] = codsdict[u'f_3'] + codsdict[u'f_4'] + codsdict[u'f_5'] + codsdict[u'f_6']
    return codsdict
NumRowsLi = [u'f_01', u'f_state02', u'f_state03', u'f_state04', u'f_state05', u'f_state06', u'f_state07', u'f_state08', u'f_melio1', u'f_melio2', u'f_servtype' ]

class DataComb(object):
    def __init__(self, f22, user_soato, nusname, datali, inform = u''):
        self.f22 = f22
        self.us_soato = user_soato
        self.nusname = nusname
        self.data = datali[1:]
        self.exp_a_rows = []
        self.svodn_row = []
        self.obj_name = inform
        info_is_null = lambda x: x if x else ''
        self.info = info_is_null(datali[0])+u' '+inform

    def add_data(self):
        exp_a_dict = make_expa_params(self.data)
        self.exp_a_rows = []
        for i in NumRowsLi:
            exp_row = round_row_data(exp_a_dict[i])
            self.exp_a_rows.append(exp_row)

    def prepare_svodn_data(self):
        try:
            temp = list(self.exp_a_rows[0])
            for row in self.exp_a_rows[1:]:
                # row.pop(-2)
                temp.append(row[0])
            return temp
        except IndexError:
            return []


class ExpFA(object):
    def __init__(self, expdb, input_data):
        self.__errors = []
        self.__expfile = expdb
        self.__expAccess = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' % self.__expfile
        self.__expconnected = 0
        self.__crtabconnected = 0
        self.datadict = self.make_dict_of_dict(input_data[0])     #Main Dict :keys F22>>Dict with keys UserN/SOATo >> list of tuples with data from ctr for ExpA
        self.usersInfo, self.soatoInfo = input_data[-2:]
        self.remake_codes()
        self.expsdict = self.make_comb_data()     #Exp Dict :keys F22>>Dict with keys UserN/SOATo >> combdata instanse
        self.make_exp_tree()

    @staticmethod
    def make_f22_dict(rows_ok):
        f22_dict = dict()
        for row in rows_ok:
            for n in range(row.n):
                row_params = (row.usern[n], row.soato, row.nusname[n], row.area[n], row.lc, row.mc, row.st08, row.state, row.dopname[n])
                            # NewF22_%(N)d, UserN_%(N)d, SOATO, NEWUSNAME_%(N)d, Area_%(N)d,LANDCODE, MELIOCODE, ServType08, State_1, NPType, DOPNAME_%(N)d,
                try:
                    f22_dict[row.f22[n]].append(row_params)
                except KeyError:
                    f22_dict[row.f22[n]] = [row_params,]
        return f22_dict

    def has_error(self):
        if not self.__errors:
            return False
        if 1 in self.__errors:
            return self.__expname

    def make_dict_of_dict(self, rows):
        """
        :param rows : rows instances (f22, UserN_n, SOATO, NEWUSNAME_n, Area_n,LANDCODE, MELIOCODE, ServType08, State, DOPNAME_n)
        :return: dict with dicts, keys: f22 >> usern | soato >> rows(newusname_n, dopname_n, (Area_n,LANDCODE, MELIOCODE, ServType08, State))
        """
        f22_rows = self.make_f22_dict(rows)
        ct_dict = dict()
        for f22 in f22_rows.keys():
            ct_dict[f22] = dict()
            for row in f22_rows[f22]:
                row_ind = 0 if row[2] == 1 else 1    #NEWUSNAME_%(N)d =1 >> Sort By UserN
                                                    #NEWUSNAME_%(N)d =2|3 >> Sort By SOATO
                try:
                    ct_dict[f22][row[row_ind]].append(row[3:-1])
                except KeyError:
                    ct_dict[f22][row[row_ind]] = [row[2], row[-1], row[3:-1]]
        return ct_dict

    def make_exp_tree(self):
        """ Returns dictionary:
            keys: F22, values: combdata instanses
        """
        tree_dict = dict.fromkeys(self.expsdict)
        for key1 in self.expsdict:
            tree_dict[key1] = []
            for key2 in self.expsdict[key1]:
                tree_dict[key1].append(self.expsdict[key1][key2])
        return tree_dict

    def make_comb_data(self):
        comb_dicts = dict.fromkeys(self.datadict.keys())
        for key1 in comb_dicts:
            comb_dicts[key1] = dict.fromkeys(self.datadict[key1].keys())
            for key2 in comb_dicts[key1]:
                comb_li = self.datadict[key1][key2]
                if comb_li[0] == 1:
                    comb_dicts[key1][key2] = DataComb(key1, key2, comb_li[0], comb_li[1:], self.usersInfo[key2])
                else: comb_dicts[key1][key2] = DataComb(key1, key2, comb_li[0], comb_li[1:], self.soatoInfo[key2])
        return comb_dicts

    def calc_all_exps(self):
        for key1 in self.expsdict:
            for key2 in self.expsdict[key1]:
                self.expsdict[key1][key2].add_data()

    def prepare_svodn_xl(self, f22_note):
        xl_f22_dict = {}
        return_xl_matrix = []
        n = 1
        total_row = [0]*100
        for f22_k  in sorted(self.expsdict.keys()):
            itogo_row = [0]*100
            data_matrix = []
            for group_k in self.expsdict[f22_k]:
                zem_obj = self.expsdict[f22_k][group_k]
                row_data = zem_obj.prepare_svodn_data()
                itogo_row = map(lambda x: sum(x), zip(itogo_row,row_data))
                row_data.insert(0, zem_obj.info)
                data_matrix.append(row_data)

            f22_head = [n, f22_k, f22_note[f22_k]]
            f22_head.extend([None]*len(itogo_row))
            xl_f22_dict[f22_k] = [f22_head,]
            n+=1
            f22_row_num = 1
            for li in sorted(data_matrix):
                li[0:0] = [n, u'%s. %d' % (f22_k, f22_row_num)]
                f22_row_num+=1
                n+=1
                xl_f22_dict[f22_k].append(li)
            total_row = map(lambda x: sum(x), zip(itogo_row,total_row))
            itogo_row[0:0] = [n, u'%s. i' % f22_k, u'Итого:']
            n+=1
            xl_f22_dict[f22_k].append(itogo_row)
            return_xl_matrix.extend(list(xl_f22_dict[f22_k]))
        total_row[0:0] = [n, u'', u'Всего:']
        return_xl_matrix.append(total_row)
        return return_xl_matrix


    def transfer_to_ins(self):
        self.__expname = u'ExpA_%s' % time.strftime(u"%d\%m\%Y_%H:%M")
        if self.create_clear_edb():
            final_dict = self.expsdict
            self.__connect_exp()
            fdk = final_dict.keys()
            fdk.sort()
            for f22key in fdk:
                itogo_row = [0]*16
                for us_so_key in final_dict[f22key].keys():
                    li = final_dict[f22key][us_so_key].exp_a_rows
                    data = final_dict[f22key][us_so_key].info
                    for i in range(1, len(li)+1):
                        if i == 1:
                            self.add_row_exp_a(f22key, data, i, li[i-1])
                            itogo_row = map(lambda x: sum(x), zip(itogo_row, li[i-1]))
                        else:
                            self.add_row_exp_a(f22key, us_so_key, i, li[i-1])
                self.add_row_exp_a(f22key, u'Итого:', 0, itogo_row)
            self.__disconnect_exp()
            os.system(u'start %s' % self.__expfile)
        else: self.__errors.append(1)

    def add_row_exp_a(self, f_f22, f_us_n, f_r_n, params):
        if self.__expconnected ==1:
            ins_args = params
            sql_ins = u'''insert into %s (f_F22, f_UsN, f_RowNumber, f_1, f_2, f_3, f_4, f_5, f_6, f_7, f_8, f_9, f_10,
                        f_11, f_12, f_13, f_14, f_15, f_16) values ( ?, ?, ?, %s);''' % (self.__expname, unicode(ins_args)[1:-1])
            try:
                self.__edbc.execute(sql_ins, (f_f22, f_us_n, f_r_n))
            except pyodbc.DataError: pass

    def create_clear_edb(self):
        create_fa = u''' create table %s(
        ID AUTOINCREMENT    ,
        f_F22 text(3)       ,
        f_UsN text(100)     ,
        f_RowNumber integer NULL,
        f_1  DOUBLE NULL    ,
        f_2  DOUBLE NULL    ,
        f_3  DOUBLE NULL    ,
        f_4  DOUBLE NULL    ,
        f_5  DOUBLE NULL    ,
        f_6  DOUBLE NULL    ,
        f_7  DOUBLE NULL    ,
        f_8  DOUBLE NULL    ,
        f_9  DOUBLE NULL    ,
        f_10 DOUBLE NULL    ,
        f_11 DOUBLE NULL    ,
        f_12 DOUBLE NULL    ,
        f_13 DOUBLE NULL    ,
        f_14 DOUBLE NULL    ,
        f_15 DOUBLE NULL    ,
        f_16 DOUBLE NULL    ,
        PRIMARY KEY(ID));''' % self.__expname
        self.__connect_exp()
        if self.__expconnected == 1:
            try:
                self.__edbc.execute(create_fa)
            except pyodbc.ProgrammingError:
                return False

            self.__disconnect_exp()
        return True

    def __connect_exp(self):
        try:
            self.__econn = pyodbc.connect(self.__expAccess, autocommit = True, unicode_results = True)
            self.__edbc = self.__econn.cursor()
            self.__expconnected = 1
        except:
            self.__expconnected = 0

    def __disconnect_exp(self):
        if self.__expconnected == 1:
            self.__edbc.close()
            self.__econn.close()
            self.__expconnected = 0

    @staticmethod
    def remake_codes():
        make_row_codes()

if __name__ == '__main__':
    print time.ctime()
    test = ExpFA(u'd:\\workspace\\explication.mdb',access_dbf)
    test.transfer_to_ins()
    print time.ctime()

