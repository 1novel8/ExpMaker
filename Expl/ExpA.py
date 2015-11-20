#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from Sprav import DBConn

def round_row_data(data, accuracy = 4):
    try:
        return map(lambda x: round(x/10000, accuracy), data)
    except TypeError:
        return round(data/10000, accuracy)

class DataComb(object):
    def __init__(self, f22, user_soato, nusname, datali, inform = u''):
        self.f22 = f22
        self.us_soato = user_soato
        self.nusname = nusname
        self.data = datali[1:]
        self.exp_a_rows = []
        self.obj_name = inform
        info_is_null = lambda x: x if x else ''
        self.info = info_is_null(datali[0])+u' '+inform

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
                except (IndexError, TypeError): continue
            self.exp_a_rows.append(round_row_data(e_row))

    def prepare_svodn_data(self):
        if self.exp_a_rows:
            try:
                temp = list(self.exp_a_rows[0])
                for row in self.exp_a_rows[1:]:
                    # row.pop(-2)
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
        self.datadict = self.make_dict_of_dict(input_data[0])     #Main Dict :keys F22>>Dict with keys UserN/SOATo >> list of tuples with data from ctr for ExpA
        self.usersInfo, self.soatoInfo = input_data[-2:]
        self.expsdict = self.make_comb_data()     #Exp Dict :keys F22>>Dict with keys UserN/SOATo >> combdata instanse

    @staticmethod
    def make_f22_dict(rows_ok):
        """
        Rows which passed convert are grouped by F22
        """
        f22_dict = dict()
        for row in rows_ok:
            for n in range(row.n):
                row_params = [row.usern[n], row.soato, row.nusname[n], row.area[n], row.lc, row.mc, row.st08, row.state]
                            # NewF22_%(N)d, UserN_%(N)d, SOATO, NEWUSNAME_%(N)d, Area_%(N)d,LANDCODE, MELIOCODE, ServType08, State_1, NPType, DOPNAME_%(N)d,
                row_params.extend(row.dop_args)
                row_params.append(row.dopname[n])
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
        :return: dict with dicts, keys: f22 >> usern | soato >> rows(newusname_n, dopname_n, (Area_n,LANDCODE, MELIOCODE, ServType08, State, *dop_args))
        """
        f22_groups = self.make_f22_dict(rows)
        ct_dict = dict()
        for f22 in f22_groups:
            ct_dict[f22] = dict()
            for row in f22_groups[f22]:
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
                self.expsdict[key1][key2].add_data(self.sprav_holder)

    def prepare_svodn_xl(self):
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

            f22_head = [n, f22_k, self.sprav_holder.f22_notes[f22_k]]
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

    def fill_razv_edb(self, matrix):
        self.__expname = u'ExpA_%s' % time.strftime(u"%d\%m\%Y_%H:%M")
        created_fields = self.create_edb_table(True)
        if created_fields:
            if len(created_fields) == len(matrix[0])-1:
                self.__exp_conn.make_connection()
                joined_f = u','.join(created_fields)
                for row in matrix:
                    row = row[1:]
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
        created_fields = [u'f_F22', u'f_UsN']
        def add_fields(f_dict, f_name_ki):
            query_part = u''
            for f_k, f_v in sorted(f_dict.items()):
                if f_v[f_name_ki]:
                    query_part+= u'%s DOUBLE NULL, ' % f_v[f_name_ki]
                    created_fields.append(u'%s' % f_v[f_name_ki])
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