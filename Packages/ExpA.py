#!/usr/bin/env python
# -*- coding: utf-8 -*-

def sum_dict_values(basic, add_dicts_li, add_ok = True):
    """
    :param basic: main dict with values you are going to add to
    :param add_dicts_li: list or tuple od additional dicts
    :param add_ok: operation with elements, sum or deduct
    :return: :raise:
    """
    if isinstance(basic, dict):
        resultdict = basic.copy()
        if add_ok:
            def func(key):
                if add_d.get(key) is not None:
                    resultdict[key] += add_d[key]
        else:
            def func(key):
                if add_d.get(key) is not None:
                    resultdict[key] -= add_d[key]
        for add_d in add_dicts_li:
            try:
                map(func, resultdict.keys())
            except KeyError:
                pass
            except Exception:
                raise
        return resultdict
    else:
        raise TypeError('Wrong basic parameter received')

def round_row_data(data, accuracy = 4, show_small = False, small_accur = 3, **kwargs):
    #TODO: Remake inputs without __dict__
    to_ga = 10000.0
    def rnd(digit):
        return round(digit/to_ga, accuracy)
        # if show_small:
        #     return complex_round(digit/to_ga, accuracy, small_accur)
        # else:
        #     return round(digit/to_ga, accuracy)
    try:
        if isinstance(data, dict):
            d = {}
            for k, v in data.items():
                d[k] = rnd(v)
            return d
        elif isinstance(data, (list, tuple)):
            return map(rnd, data)
        elif isinstance(data, (float, int)):
            return rnd(data)
        else:
            raise Exception(u'Передан неверный тип обрабатываемых данных')
    except TypeError as err:
        raise Exception(u'Возникла ошибка при попытке округления %s.\n%s' % (unicode(data),err.message))

def complex_round(digit, accuracy, small_accur):
    min_step = 10**-accuracy
    try:
        rounded = round(digit, accuracy)
    except TypeError as err:
        raise Exception(u'Возникла ошибка при попытке округления %s.\n%s' % (unicode(digit),err.message))
    else:
        if rounded < min_step:
            return round(digit, accuracy+small_accur)
        else:
            return rounded

def round_and_modify(data_dict, settings):
    """
    :param data_dict: dictionary with field keys and their float values
    :param settings: settings instance with parameters that round_row_data def required
    :return: dict with modified structure. after round tails are saved
    """
    modified = data_dict.copy()
    modified = round_row_data(modified, **settings)
    for key, val in modified.items():
        modified[key] = {
            'val': val,
            'tail': data_dict[key]/10000 - val
        }
    return modified

class DataComb(object):
    def __init__(self, data_li, full_inf, main_inf, soato_inf):
        self.soato_inf = soato_inf
        self.__init_data = data_li
        self.expl_data = {}
        self.obj_name = main_inf
        self.full_obj_name = full_inf
        self.errors = {}

    def add_data(self, spr):
        """
        :param spr: sprav_holder instance
        Makes json-style simple explication a in case that it's not counted yet
        """
        if self.expl_data:
            # Data already added
            pass
        else:
            expl_data = dict.fromkeys(spr.str_orders['a_r'])
            for r_key in expl_data:
                if r_key == u'total':
                    filtered_rows = self.__init_data
                else:
                    r_codes = spr.expa_r_str[r_key]['codes']
                    s_alias = spr.expa_r_str[r_key]['sort_alias']
                    filtered_rows = [row for row in self.__init_data if row[s_alias] in r_codes]
                try:
                    expl_data[r_key] = self.sum_by_lc(filtered_rows, spr.expa_f_str)
                except (IndexError, TypeError, AttributeError) as e:
                    self.errors[r_key] = e.message
            self.expl_data = expl_data
            self.__init_data = None


    def round_expl_data(self, round_setts):
        rounded_e_data = {}
        if self.expl_data:
            round_setts.accuracy = round_setts.a_s_accuracy
            for row in self.expl_data:
                rounded_e_data[row] = round_and_modify(self.expl_data[row], round_setts.__dict__)
        return rounded_e_data


    def make_sv_row(self, spr):
        self.add_data(spr)
        if self.expl_data:
            sv_row = {}
            for r_key in self.expl_data:
                if r_key == 'total':
                    sv_row.update(self.expl_data[r_key])
                else:
                    sv_row[r_key] = self.expl_data[r_key]['total']
            return sv_row
        return {}

    def sum_by_lc(self, rows, f_str):
        if rows:
            f_values = {}
            for f_key in f_str:
                if f_str[f_key]['codes']:
                    f_values[f_key] = 0
                    for row in rows:
                        if row['lc'] in f_str[f_key]['codes']:
                            f_values[f_key] += row['area']

            # while f_value key is empty ...
            while len(f_str) > len(f_values):
                f_len = len(f_values)
                for f_key in f_str:
                    if f_values.has_key(f_key):
                        continue
                    sum_f_li = f_str[f_key]['sum_f']
                    f_sum = self.try_get_sum(sum_f_li, f_values)
                    if f_sum == -1:
                        continue
                    else:
                        f_values[f_key] = f_sum
                if f_len == len(f_values):
                    raise Exception(u'Возникла взаимоблокирующая ситуация. Справочник структуры полей содержит некорректные данные в ')

            return f_values
        return dict.fromkeys(f_str, 0)

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
    def __init__(self, input_data, sprav_holder):
        self.sprav_holder = sprav_holder
        self.errors_occured = {}
        self.usersInfo, self.soatoInfo = input_data[-2:]
        self.cc_soato_d = self.get_cc_soato_d()
        self.datadict = self.make_datadict(input_data[0])     #Main Dict :keys F22>>Dict with keys UserN/SOATo >> list of tuples with data from ctr for ExpA
        self.exps_dict = self.make_comb_data()     #Exp Dict :keys F22>>Dict with keys UserN/SOATo >> combdata instance

    def get_cc_soato_d(self):
        cc_soato_d = {}
        for soato in self.soatoInfo:
            if soato[-3:] == u'000':
                cc_soato_d[soato[:-3]] = self.soatoInfo[soato]
        return cc_soato_d

    def get_cc_name(self, soato):
        soato = unicode(soato)
        # if soato[-3:] == u'000':
        #     return u''
        # else:
        try:
            return self.cc_soato_d[soato[:-3]] +u'  '
        except KeyError:
            return u'! '

    def make_datadict(self, rows):
        f22_dict = {}
        keys_not_used = ('ctr_structure', 'id', 'usern_sad', 'part', 'f22', 'usern', 'slnad', 'usertype', 'nptype')
        need_keys = [k for k in self.sprav_holder.attr_config if k not in keys_not_used]
        for row in rows:
            for n in range(row.n):
                f22_key = row.get_el_by_fkey_n('f22', n)
                nusn = row.nusname[n]
                if nusn == 1: #группировка по User_N
                    group_key = row.get_el_by_fkey_n('usern', n)
                else:         #группировка по SOATo
                    group_key = row.soato
                row_params = row.simplify_to_d(n, need_keys)# NEWUSNAME_%(N)d, Area_%(N)d, LANDCODE, MELIOCODE, ServType08, State_1
                try:
                    f22_dict[f22_key][group_key]['r_params'].append(row_params)
                except KeyError:
                    if not f22_dict.has_key(f22_key):
                        f22_dict[f22_key] = {}
                    soato_inf = self.get_cc_name(row.soato)
                    main_inf = self.usersInfo[group_key] if nusn == 1 else self.soatoInfo[group_key]
                    dop_inf = row.dopname[n] if row.dopname[n] else u''
                    f22_dict[f22_key][group_key] = {
                        u'r_params': [row_params, ],
                        u'main_inf': u'%s %s' % (dop_inf, main_inf),
                        u'soato_inf': soato_inf,
                        u'full_inf': self.get_full_e_name(main_inf, dop_inf, soato_inf, nusn),
                    }
        return f22_dict

    def get_full_e_name(self, main_name, dop_name, ss_name, nusn_code):
        if nusn_code == 1:
            return main_name
        if nusn_code == 2:
            return ss_name + ' ' + dop_name + ' ' + main_name
        if nusn_code == 3:
            return main_name + ' ' + dop_name

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
                comb_dicts[key1][key2] = DataComb(comb_li['r_params'], comb_li['full_inf'], comb_li['main_inf'], comb_li['soato_inf'])
        return comb_dicts

    def calc_all_exps(self, round_setts):
        sv_exp = {}
        sv_texts = {}
        if self.exps_dict:
            for key1 in self.exps_dict:
                sv_exp[key1] = {}
                sv_texts[key1] = {}
                for key2 in self.exps_dict[key1]:
                    exp_obj = self.exps_dict[key1][key2]
                    sv_exp[key1][key2] = exp_obj.make_sv_row(self.sprav_holder)
                    sv_texts[key1][key2] = self.__get_sv_row_text(key2, exp_obj.obj_name)
                    if exp_obj.errors:
                        #TODO: Work with exception (get message from exp_obj)
                        self.errors_occured[1] = exp_obj.errors
                        return {}
            self.__add_total_rows(sv_exp)
            sv_exp['sh_sum'] = self.__make_shape_row()
            round_setts.accuracy = round_setts.a_sv_accuracy
            self.__round_sv(sv_exp, round_setts)
            sv_exp['texts'] = sv_texts
            return sv_exp
        else:
            self.errors_occured[0] = u'No data'
            return sv_exp


    @staticmethod
    def __round_sv(sv_nested_di, round_setts):
        """
        use to transform sv_explication_dict. Depends of round settings.
        instead of digits it will paste dicts with value key and tail key
        !Caution! It changes the input object!
        """
        for key1 in sv_nested_di:
            if key1 in ('total', 'sh_sum'):
                sv_nested_di[key1] = round_and_modify(sv_nested_di[key1], round_setts.__dict__)
            else:
                for key2, data_d in sv_nested_di[key1].items():
                    sv_nested_di[key1][key2] = round_and_modify(data_d, round_setts.__dict__)

    def __get_sv_row_text(self, soato_key, obj_text):
        cc_kod = unicode(soato_key)[:-3]
        try:
            return u'%s %s' % (self.cc_soato_d[cc_kod], obj_text)
        except KeyError:
            return obj_text

    def __make_shape_row(self):
        conv_rows = []
        for k1 in self.datadict:
            for k2 in self.datadict[k1]:
                conv_rows.extend(self.datadict[k1][k2]['r_params'])
        shape_comb = DataComb(conv_rows, u'Shape_sum:', u'', u'')
        return shape_comb.make_sv_row(self.sprav_holder)

    def __add_total_rows(self, sv_e):
        """
        Caution! this method changes enter parameter sv_e
        :param sv_e: Sv explication data only
        :return: modified sv_e with total keys
        """
        tmpl = dict.fromkeys(self.sprav_holder.str_orders['sv_f'],0)
        total_all = tmpl.copy()
        for key1 in sv_e:
            total_f22 = tmpl.copy()
            for key2 in sv_e[key1]:
                total_f22 = sum_dict_values(total_f22, (sv_e[key1][key2],))
            sv_e[key1]['total'] = total_f22
            total_all = sum_dict_values(total_all, (total_f22,))
        sv_e['total'] = total_all

if __name__ == u'__main__':
    print unicode(round_row_data([324242,3223, 0.2,345], 3, False))