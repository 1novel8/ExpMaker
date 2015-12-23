#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
from ExpA import round_row_data
from Sprav import DBConn

class ExpFormaB(object):
    def __init__(self, exp_db, ctr_rows, sprav_holder):
        self.exp_db = exp_db
        self.__exp_conn =  DBConn(exp_db, False)
        self.sprav_holder = sprav_holder
        self.ctr_rows = ctr_rows        #dict: F22 > (UserN_%(N)d, SOATO, NEWUSNAME_%(N)d, Area_%(N)d,LANDCODE, MELIOCODE, ServType08, State_1, nptype, DOPNAME_%(N)d)
        self.exp_name = u'ExpB_%s' % time.strftime(u"%d\%m\%Y_%H:%M")

    @staticmethod
    def sum_dict_values(basic, add_dicts, add = True):
        resultdict = {}
        resultdict.update(basic)
        if add:
            def func(key):
                if add_d.get(key) is not None:
                    resultdict[key] += add_d[key]
        else:
            def func(key):
                if add_d.get(key) is not None:
                    resultdict[key] -= add_d[key]
        for add_d in add_dicts:
            try:
                map(func, resultdict.keys())
            except KeyError:
                pass
        return resultdict

    def sort_for_fbrows(self):
        """
            return fbrow_dict: f22(key_of_row_in_formB) -> [(area, LANDCODE, MELIOCODE, ServType08, State_1),...]
        """
        fbrow_dict = {}
        r_structure = self.sprav_holder.expb_r_str
        for key, fb_row in r_structure.items():
            passed_rows = []
            if fb_row[u's_by']:
                for row in self.ctr_rows:   #(row.usern[n], row.soato, row.nusname[n], row.area[n], row.lc, row.mc, row.st08, row.state, row.slnad, row.np_type, row.dopname[n])
                    for n in range(row.n):
                        if row.has_code(n, fb_row[u's_by'], fb_row[u's_p']):
                            need_params = [row.area[n], row.lc, row.mc, row.st08, row.state]
                            need_params.extend(row.dop_args)
                            passed_rows.append(need_params)
            fbrow_dict[key] = passed_rows
        return fbrow_dict

    def make_fbr_params(self, rows):
        f_str = self.sprav_holder.expb_f_str
        r_params_d = dict.fromkeys(f_str.keys(), 0)
        if rows:
            ready_f_nums = {}
            for f_key, f_val in f_str.items():
                if f_val.has_key(u'codes'):
                    sort_rows = rows[:]
                    s = 0
                    codes = f_val[u'codes']
                    for c_i in range(len(codes)):
                        c = f_val[u'codes'][c_i]
                        c_ind = f_val[u'sort_i'][c_i]
                        if c_i == len(codes)-1:
                            for r_i in range(len(sort_rows)):
                                if sort_rows[r_i][c_ind] in c:
                                    s += sort_rows[r_i][0]
                        else:
                            new_srt_li = []
                            for r_i in range(len(sort_rows)):
                                if sort_rows[r_i][c_ind] in c:
                                    new_srt_li.append(sort_rows[r_i])
                            sort_rows = new_srt_li
                        r_params_d[f_key] = s
                    if not f_val[u'sum_f']:
                        ready_f_nums[f_val[u'f_num']] = f_key
            while len(f_str)>len(ready_f_nums):
                l = len(ready_f_nums)
                for key, value in f_str.items():
                    if value[u'f_num'] in ready_f_nums:
                        continue
                    elif value[u'sum_f']:
                        check_li = ready_f_nums.keys()
                        check_li.extend(value[u'sum_f'])
                        if len(ready_f_nums) == len(set(check_li)):        #проверка входят ли все элементы value[u'sum_f'] в число уже сформированных полей
                            ready_f_nums[value[u'f_num']] = key
                            for i in value[u'sum_f']:
                                add_f_key = ready_f_nums[i]
                                r_params_d[key]+=r_params_d[add_f_key]
                if len(ready_f_nums) == l: break
        return r_params_d

    def create_exp_dict(self):
        exp_dict = self.sort_for_fbrows()
        count_ready = 0
        for key in exp_dict:
            exp_dict[key] = self.make_fbr_params(exp_dict[key])
            if self.sprav_holder.expb_r_str[key].has_key(u'conds'):
                exp_dict[key][u'ready'] = False
            else:
                count_ready += 1
                exp_dict[key][u'ready'] = True
        while count_ready < len(exp_dict):
            cr_old = count_ready
            for key in exp_dict:
                r_spr = self.sprav_holder.expb_r_str[key]
                if not exp_dict[key][u'ready']:
                    new_row = exp_dict[key].copy()
                    row_ready = True
                    for cond_k, cond_v in r_spr[u'conds'].items():
                        if cond_k in (u'add', u'sub'):
                            is_add = True if cond_k == u'add' else False
                            if self.all_ready(exp_dict, cond_v):
                                add_rows = map(lambda x: exp_dict[x], cond_v)
                                new_row = self.sum_dict_values(new_row, add_rows, add = is_add)
                            else:
                                row_ready = False
                                break

                        elif cond_k == u'eq_f':
                            for eq_i in cond_v:
                                take_r = eq_i[u'take_r']
                                if  exp_dict[take_r][u'ready']:
                                    take_f = eq_i[u'take_f']
                                    upd_f = eq_i[u'upd_f']
                                    op = eq_i[u'op']
                                    if op == u'=':
                                        new_row[upd_f] = exp_dict[take_r][take_f]
                                    elif op == u'-':
                                        new_row[upd_f] -= exp_dict[take_r][take_f]
                                    elif op == u'+':
                                        new_row[upd_f] += exp_dict[take_r][take_f]
                                else:
                                    row_ready = False
                                    break
                    if row_ready:
                        exp_dict[key] = new_row
                        exp_dict[key][u'ready'] = True
                        count_ready += 1
            if cr_old == count_ready: break
        for key in exp_dict:
            exp_dict[key].pop(u'ready')
        # Add Itogo row to explication
        all_rows = []
        for row in self.ctr_rows:   #(row.usern[n], row.soato, row.nusname[n], row.area[n], row.lc, row.mc, row.st08, row.state, row.slnad, row.np_type, row.dopname[n])
            for n in range(row.n):
                need_params = [row.area[n], row.lc, row.mc, row.st08, row.state]
                need_params.extend(row.dop_args)
                all_rows.append(need_params)
        exp_dict[u'by_SHAPE'] = self.make_fbr_params(all_rows)

        self.round_fb(exp_dict)
        return exp_dict

    @staticmethod
    def all_ready(e_dict, keys, ready_key = u'ready'):
        for key in keys:
            try:
                if not e_dict[key][ready_key] == True:
                    return False
            except KeyError:
                return False
        return True

    @staticmethod
    def round_fb(data_di):
        for key1 in data_di:
            for key2 in data_di[key1]:
                data_di[key1][key2] = round_row_data(data_di[key1][key2],0)

    def run_mdb_exp(self, exp_dict, cr_fields):
        if not exp_dict:
            exp_dict = self.create_exp_dict()
        r_str = self.sprav_holder.expb_r_str
        self.__exp_conn.make_connection()
        for key in sorted(exp_dict.keys()):
            try:
                f_values = [key, r_str[key][u'row_name']]
            except KeyError as err:
                if key == u'by_SHAPE':
                    f_values = [key, u'Всего:']
                else: raise err
            for field_name in cr_fields[2:]:
                f_v = exp_dict[key][field_name]
                f_values.append(f_v if f_v else 0)
            inserted = self.insert_row(cr_fields, f_values)
            if not inserted: break
        self.__exp_conn.close_conn()
        os.system(u'start %s' % self.exp_db)

    def insert_row(self, fields, vals):
        fields = u','.join(fields)
        vals = map(lambda x: u"'%s'" % x if isinstance(x, unicode) else unicode(x), vals)
        vals = u','.join(vals)
        ins_query = u'INSERT into %s(%s) values (%s)' % (self.exp_name, fields, vals)
        inserted = self.__exp_conn.exec_query(ins_query)
        if inserted: return True
        else: return False

    def create_e_table(self):
        """
        :return: list of created fields if create table operation finished with success, else returns false
        """
        create_fb = u'create table %s(ID AUTOINCREMENT, f_F22 text(8) Null, f_description text(150), ' % self.exp_name
        created_fields = [u'f_F22', u'f_description']
        sort_f_d = {}
        f_str = self.sprav_holder.expb_f_str
        for key in f_str:
            sort_key = f_str[key].get(u'f_num')
            if sort_key:
                sort_f_d[sort_key] = key
        for key in sorted(sort_f_d):
            create_fb+= u'%s DOUBLE NULL, ' % sort_f_d[key]
            created_fields.append(sort_f_d[key])
        create_fb += u'PRIMARY KEY(ID));'
        self.__exp_conn.make_connection()
        if self.__exp_conn.exec_query(create_fb):
            self.__exp_conn.close_conn()
            return created_fields
        else: return False

if __name__ == u'__main__':
    print u'Призываю этот модуль рассчитать экспликацию по форме В'










