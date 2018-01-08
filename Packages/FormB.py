#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ExpA import round_and_modify, sum_dict_values

class ExpFormaB(object):
    def __init__(self, ctr_rows, sprav_holder):
        self.r_structure = sprav_holder.expb_r_str
        self.f_structure = sprav_holder.expb_f_str
        self.filtered_rows = self.filter_by_r_str(ctr_rows, sprav_holder.attr_config.keys())

    def filter_by_r_str(self, ct_rows, aliases):
        """
            return fbrow_dict: f22(key_of_row_in_formB) -> [(area, LANDCODE, MELIOCODE, ServType08, State_1),...]
        """
        fbrow_dict = {u'by_SHAPE': []}
        for key in self.r_structure:
            fbrow_dict[key] = []
        keys_not_used = ('ctr_structure', 'id', 'usern_sad', 'part', 'usern')
        need_keys = [k for k in aliases if k not in keys_not_used]
        r_str = self.r_structure.items()

        for row in ct_rows:
            for n in range(row.n):
                need_params = row.simplify_to_d(n, need_keys)
                fbrow_dict[u'by_SHAPE'].append(need_params)
                for key, fb_row in r_str:
                    try:
                        if row.check_filter_match(n, fb_row[u'sort_filter']):
                            fbrow_dict[key].append(need_params)
                    except KeyError:
                        fb_row[u'sort_filter'] = {}

        self.r_structure[u'by_SHAPE'] = {u'r_name': u'Всего:', u'sort_filter': {}}
        return fbrow_dict

    def make_fbr_params(self, rows):
        f_str = self.f_structure
        r_params_d = dict.fromkeys(f_str.keys(), 0)
        if rows:
            ready_fields = []
            for f_key, f_val in f_str.items():
                if f_val.has_key(u'alias_codes'):
                    s = 0
                    for row in rows:
                        passed = True
                        for als, cds in f_val[u'alias_codes'].items():
                            if row[als] not in cds:
                                passed = False
                                break
                        if passed:
                            s+=row[u'area']
                    r_params_d[f_key] = s
                if not f_val[u'sum_f']:
                    ready_fields.append(f_key)
            while len(f_str)>len(ready_fields):
                l = len(ready_fields)
                for f, value in f_str.items():
                    if f in ready_fields:
                        continue
                    add_fields = value[u'sum_f']
                    check_li = ready_fields[:]
                    check_li.extend(add_fields)
                    if len(ready_fields) == len(set(check_li)):        #проверка входят ли все элементы value[u'sum_f'] в число уже сформированных полей
                        for a_f in add_fields:
                            r_params_d[f]+=r_params_d[a_f]
                        ready_fields.append(f)
                if len(ready_fields) == l: break
        return r_params_d

    def create_exp_dict(self, round_setts):
        exp_dict = self.filtered_rows
        count_ready = 0
        for key in exp_dict:
            exp_dict[key] = self.make_fbr_params(exp_dict[key])
            if self.r_structure[key].has_key(u'conds'):
                exp_dict[key][u'ready'] = False
            else:
                count_ready += 1
                exp_dict[key][u'ready'] = True

        while count_ready < len(exp_dict):
            cr_old = count_ready
            for key in exp_dict:
                r_spr = self.r_structure[key]
                if not exp_dict[key][u'ready']:
                    new_row = exp_dict[key].copy()
                    row_ready = True
                    for cond_k, cond_v in r_spr[u'conds'].items():
                        if cond_k in (u'add', u'sub'):
                            is_add = True if cond_k == u'add' else False
                            if self.all_ready(exp_dict, cond_v):
                                add_rows = map(lambda x: exp_dict[x], cond_v)
                                new_row = sum_dict_values(new_row, add_rows, add_ok = is_add)
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
        round_setts.accuracy = round_setts.b_accuracy
        self.__round_fb(exp_dict, round_setts)
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
    def __round_fb(fb_dict, round_setts):
        print round_setts
        round_setts = round_setts.copy() if isinstance(round_setts, dict) else round_setts.__dict__
        round_setts['show_small'] = False
        for key1, data_d in fb_dict.items():
            fb_dict[key1] = round_and_modify(data_d, round_setts)

if __name__ == u'__main__':
    print u'Призываю этот модуль рассчитать экспликацию по форме В'










