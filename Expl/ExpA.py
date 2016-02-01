#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from Sprav import DBConn

def round_row_data(data, accuracy = 4, simple_round = True):
    to_ga = 10000.0
    if simple_round:
        try:
            return map(lambda x: round(x/to_ga, accuracy), data)
        except TypeError:
            return round(data/to_ga, accuracy)
    else:
        if hasattr(data, '__iter__'):
            return map(lambda x: complex_round(x/to_ga, accuracy), data)
        else:
            return complex_round(data/to_ga, accuracy)

def complex_round(digit, n_digits):
    min_normal_round = 10**-n_digits
    try:
        rounded = round(digit, n_digits)
    except TypeError as err:
        raise Exception(u'Возникла ошибка при попытке округления %s.\n%s' % (unicode(digit),err.message))
    else:
        if rounded < min_normal_round:
            return round(digit, n_digits+3)
        else:
            return rounded

class DataComb(object):
    def __init__(self, datali, info, dop_info, soato_inf):
        self.soato_inf = soato_inf
        self.data = datali
        self.exp_a_rows = []
        self.obj_name = info
        self.info = u'%s %s' % (dop_info, info)
        self.errors = {}

    def add_data(self, sprav):
        """
        :param sprav: sprav_holder instance
        Makes ordered list of explication rows
        work with expa_row_structure
        """
        self.exp_a_rows = []
        for key in sorted(sprav.expa_r_str):
            r_params = sprav.expa_r_str[key]
            if r_params[2] in (0,1):            #index of the sort parameter, by which row is filtered
                e_row = self.sum_by_lc(self.data, sprav.expa_f_str)
            else:
                r_par = r_params[1]
                if not hasattr(r_par, '__iter__'): continue
                try:
                    e_row = self.sum_by_lc([row for row in self.data if row[r_params[2]] in r_par], sprav.expa_f_str)
                except (IndexError, TypeError):
                    try:
                        self.errors[1]+= u', %s' % r_params[0]
                    except KeyError:
                        self.errors[1] = r_params[0]
                    e_row = [0]*len(sprav.expa_f_str)
            self.exp_a_rows.append(round_row_data(e_row, False))

    def prepare_svodn_data(self):
        if self.exp_a_rows:
            try:
                temp = list(self.exp_a_rows[0])
                for row in self.exp_a_rows[1:]:
                    temp.append(row[0])
                return temp
            except IndexError:
                pass
        return []

    def sum_by_lc(self, rowsli, f_str):
        c = u'codes'
        if rowsli:
            f_values = {}
            for key in f_str:
                if f_str[key][c]:
                    f_values[key] = 0
                    for row in rowsli:
                        if row[1] in f_str[key][c]: f_values[key] += row[0]
            # while f_value key is empty ...
            while len(f_str) > len(f_values):
                f_len = len(f_values)
                for key in f_str:
                    if f_values.has_key(key): continue
                    sum_f_li = f_str[key][u'sum_f']
                    if hasattr(sum_f_li, '__iter__'):
                        f_sum = self.try_get_sum(sum_f_li, f_values)
                        if f_sum == -1:
                            continue
                        else:
                            f_values[key] = f_sum
                    else: break
                if f_len == len(f_values):
                    break
            return_li = []
            for key in sorted(f_str):
                try:
                    return_li.append(f_values[key])
                except KeyError: return_li.append(0)
            return return_li
        else:
            return [0]*len(f_str)

    @staticmethod
    def try_get_sum(key_li, sum_di):
        """If sum_di has all keys from key_li, function returns this sum else returns False"""
        r_sum = 0
        for f_key in key_li:
            try:
                r_sum += sum_di[f_key]
            except KeyError: return -1
        return r_sum


class ExpFA(object):
    def __init__(self, expdb, input_data, sprav_holder):
        self.sprav_holder = sprav_holder
        self.__errors = []
        self.__exp_conn =  DBConn(expdb, False)
        self.usersInfo, self.soatoInfo = input_data[-2:]
        self.cc_soato_d = self.get_cc_soato_d()
        self.datadict = self.make_datadict(input_data[0])     #Main Dict :keys F22>>Dict with keys UserN/SOATo >> list of tuples with data from ctr for ExpA
        self.exps_dict = self.make_comb_data()     #Exp Dict :keys F22>>Dict with keys UserN/SOATo >> combdata instanse

    def get_cc_soato_d(self):
        cc_soato_d = {}
        for soato in self.soatoInfo:
            if soato[-3:] == u'000':
                cc_soato_d[soato[:-3]] = self.soatoInfo[soato]
        return cc_soato_d

    def get_cc_name(self, soato):
        soato = unicode(soato)
        if soato[-3:] == u'000':
            return u''
        else:
            try:
                return self.cc_soato_d[soato[:-3]] +u'  '
            except KeyError:
                return u'! '
    def has_error(self):
        if not self.__errors:
            return False
        if 1 in self.__errors:
            return self.__expname

    def make_datadict(self, rows):
        f22_dict = {}
        for row in rows:
            for n in range(row.n):
                f22_key = row.f22[n]
                if row.nusname[n] == 1: #группировка по User_N
                    group_key = row.usern[n]
                    info = self.usersInfo[group_key]
                else:                   #группировка по SOATo
                    group_key = row.soato
                    info = self.soatoInfo[group_key]
                dop_info = row.dopname[n] if row.dopname[n] else u''
                row_params = [row.area[n], row.lc, row.mc, row.st08, row.state]# NEWUSNAME_%(N)d, Area_%(N)d, LANDCODE, MELIOCODE, ServType08, State_1
                row_params.extend(row.dop_args) #ADD Dop args with Dop_* in field name
                try:
                    f22_dict[f22_key][group_key][u'r_params'].append(row_params)
                except KeyError:
                    if not f22_dict.has_key(f22_key):
                        f22_dict[f22_key] = {}
                    f22_dict[f22_key][group_key] = {
                        u'r_params': [row_params, ],
                        u'info': info,
                        u'dop_info': dop_info,
                        u'soato_inf': self.get_cc_name(row.soato)
                    }
        return f22_dict

    def make_exp_tree(self):
        """ Returns dictionary:
            keys: F22, values: combdata instanses
        """
        tree_dict = dict.fromkeys(self.exps_dict)
        for key1 in self.exps_dict:
            tree_dict[key1] = []
            for key2 in self.exps_dict[key1]:
                tree_dict[key1].append(self.exps_dict[key1][key2])
        return tree_dict

    def make_comb_data(self):
        comb_dicts = dict.fromkeys(self.datadict.keys())
        for key1 in comb_dicts:
            comb_dicts[key1] = dict.fromkeys(self.datadict[key1].keys())
            for key2 in comb_dicts[key1]:
                comb_li = self.datadict[key1][key2]
                comb_dicts[key1][key2] = DataComb(comb_li[u'r_params'], comb_li[u'info'], comb_li[u'dop_info'], comb_li[u'soato_inf'])
        return comb_dicts

    def calc_all_exps(self):
        ask_err = True
        if self.exps_dict:
            for key1 in self.exps_dict:
                for key2 in self.exps_dict[key1]:
                    self.exps_dict[key1][key2].add_data(self.sprav_holder)
                    if ask_err:
                        ask_err = False
                        errors = self.exps_dict[key1][key2].errors
            return errors
        return {1: u'Lost Data!'}

    def prepare_svodn_xl(self):
        xl_f22_dict = {}
        return_xl_matrix = []
        n = 1
        total_row = [0]*150
        for f22_k  in sorted(self.exps_dict.keys()):
            itogo_row = [0]*150
            data_matrix = []
            for group_k in self.exps_dict[f22_k]:
                zem_obj = self.exps_dict[f22_k][group_k]
                row_data = zem_obj.prepare_svodn_data()
                itogo_row = map(lambda x: sum(x), zip(itogo_row,row_data))
        #   Add cc name to zem_obj.info
                cc_kod = unicode(group_k)[:-3]
                if len(cc_kod)>6:
                    try:
                        cc_name = self.cc_soato_d[cc_kod] +u' '
                    except KeyError:
                        cc_name = u''
                else:
                    cc_name = u''
                cc_name += zem_obj.info
        #   --------------------------------
                row_data.insert(0, cc_name)
                data_matrix.append(row_data)

            f22_head = [n, f22_k, self.sprav_holder.f22_notes[f22_k]]
            f22_head.extend([None]*len(itogo_row))
            xl_f22_dict[f22_k] = [f22_head,]
            n+=1
            f22_row_num = 1
            for li in sorted(data_matrix):
                li[0:0] = [n, u'%s. %d' % (f22_k, f22_row_num)]
                f22_row_num+=1
                n += 1
                xl_f22_dict[f22_k].append(li)
            total_row = map(lambda x: sum(x), zip(itogo_row,total_row))
            itogo_row[0:0] = [n, u'%s. i' % f22_k, u'Итого:']
            n+=1
            xl_f22_dict[f22_k].append(itogo_row)
            return_xl_matrix.extend(list(xl_f22_dict[f22_k]))
        total_row[0:0] = [n, u'', u'Всего:']
        return_xl_matrix.append(total_row)
        #Do Shape_sum
        conv_rows = []
        for k1 in self.datadict:
            for k2 in self.datadict[k1]:
                conv_rows.extend(self.datadict[k1][k2][u'r_params'])
        shape_comb = DataComb(conv_rows, u'Shape_sum:', u'', u'')
        shape_comb.add_data(self.sprav_holder)
        shape_row = shape_comb.prepare_svodn_data()
        shape_row[:0] = [n+1, u'', u'Shape_sum:']
        return_xl_matrix.append(shape_row)
        return return_xl_matrix

    def fill_razv_edb(self, matrix):
        self.__expname = u'ExpA_%s' % time.strftime(u"%d\%m\%Y_%H:%M")
        created_fields = self.create_edb_table(True)
        if created_fields:
            if len(created_fields) == len(matrix[0]):
                self.__exp_conn.make_connection()
                joined_f = u','.join(created_fields)
                for row in matrix:
                    # row = row[1:]
                    row = map(lambda x: u"'%s'" % x if isinstance(x, unicode) else x, row)
                    row = map(lambda x: (u'Null' if x is None else unicode(x)), row)
                    f_values = u','.join(row)
                    ins_query = u'insert into %s(%s) values (%s);' % (self.__expname, joined_f, f_values)
                    row_insert = self.__exp_conn.exec_query(ins_query)
                    if not row_insert: break
                self.__exp_conn.close_conn()
            self.__exp_conn.run_db()

    def create_edb_table(self, razv = False):
        """
        :param razv: Makes tab structure like xls if parameter is true
        :return: list of created fields if create table operation finished with success, else returns false
        """
        create_fa = u'create table %s(ID AUTOINCREMENT, f_F22 text(8) Null, f_UsN text(100), ' % self.__expname
        created_fields = [u'ID', u'f_F22', u'f_UsN']
        def add_fields(f_dict, f_name_ki):
            query_part = u''
            for f_k, f_v in sorted(f_dict.items()):
                if f_v[f_name_ki]:
                    query_part+= u'f_%s DOUBLE NULL, ' % f_v[f_name_ki]
                    created_fields.append(u'f_%s' % f_v[f_name_ki])
            return query_part
        create_fa += add_fields(self.sprav_holder.expa_f_str, u'f_name')
        if razv:
            create_fa += add_fields(self.sprav_holder.expa_r_str, 0)
        create_fa += u'PRIMARY KEY(ID));'
        self.__exp_conn.make_connection()
        if self.__exp_conn.exec_query(create_fa):
            self.__exp_conn.close_conn()
            return created_fields
        else: return False

if __name__ == u'__main__':
    print unicode(round_row_data([324242,3223, 0.2,345], 3, False))