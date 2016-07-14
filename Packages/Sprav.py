#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DbTools import DBConn, DbControl
import DbStructures

class SprControl(DbControl):
    def __init__(self, db_path, is_full):
        self.schema = DbStructures.str_db_cfg.copy()
        if is_full:
            self.schema.update(DbStructures.spr_db_cfg)
        super(SprControl, self).__init__(db_path, self.schema)
    #TODO: You can add exp structure control here

class SpravError(Exception):
    def __init__(self, e_type, *args):
        err_head = u'Ошибка в справочниках! \n'
        args_err = u'Переданы неверные аргументы. \nПожалуйста зафиксируйте условия возникновения данной ошибки и обратитесь к разработчику:)'
        args = map(lambda x: unicode(x), args)
        errors = {
            -1: lambda: args[0],
            0: lambda: err_head + unicode(args[0]) if len(args) >= 1 else args_err,
            1: lambda: err_head + u'Не удалось выполнить запрос: < %s >. Проверьте корректность базы данных' % unicode(args[0]) if len(args)>=1 else args_err,
            #errors[2] used when error occured in row, so [args] must contain table_name and row_name as first 2 parameters
            2: lambda: err_head + u'Проверьте строку %s в таблице %s. ' % (args[1], args[0]) if len(args)>=2 else args_err,
            3: lambda: errors[2]() + args[2]  if len(args)>=3 else args_err,
            4: lambda: errors[2]() + u'Отсутствует соответствующее значение %s, на которое произведена ссылка.' % args[2] if len(args)>=3 else args_err,
            5: lambda: errors[2]() + u'Не указана ссылка на суммарную строку.' if len(args)>=2 else args_err,
        }
        super(SpravError, self).__init__(errors[e_type]())

def catch_ex_as_sprav_err(decor_method):
    def wrapper(*args, **kwargs):
        try:
            return decor_method(*args, **kwargs)
        except SpravError:
            raise
        except Exception as err:
            raise SpravError(-1, err.message)
    return wrapper

class SpravHolder(object):
    def __init__(self):
        self._s_conn = None
        self.expa_f_str = None
        self.expa_r_str = None
        self.expb_f_str = None
        self.expb_r_str = None
        self.soato_npt = None
        self.bgd2ekp =   None
        self.f22_notes = None
        self.bgd2ekp_1 = None
        self.bgd2ekp_2 = None
        self.user_types = None
        self.slnad_codes =None
        self.state_codes =None
        self.melio_codes =None
        self.land_codes =None
        self.max_n = None
        self.crtab_columns = None
        self.str_orders = None
        self.__sorted_keys = None
        self.reset_sorted_keys()

    def reset_sorted_keys(self):
        self.__sorted_keys = {'a_f':[], 'a_r':[], 'sv_f':[], 'b_f':[], 'b_r':[]}

    def set_parameters(self, sprav_dict):
        self.__sorted_keys = None
        try:
            self.attr_config = sprav_dict['attr_depnd']
            self.expa_f_str = sprav_dict['expa_f_str']
            self.expa_r_str = sprav_dict['expa_r_str']
            self.expb_f_str = sprav_dict['expb_f_str']
            self.expb_r_str = sprav_dict['expb_r_str']
            self.str_orders = sprav_dict['str_orders']
            self.soato_npt = sprav_dict['soato_npt']
            self.f22_notes = sprav_dict['f22_notes']
            self.bgd2ekp_1 = self.bgd_to_dicts(sprav_dict['bgd2ekp'][0])
            self.bgd2ekp_2 = self.bgd_to_dicts(sprav_dict['bgd2ekp'][1])
            self.user_types = sprav_dict['user_types']
            self.slnad_codes = sprav_dict['slnad_codes']
            self.state_codes = sprav_dict['state_codes']
            self.melio_codes = sprav_dict['melio_codes']
            self.land_codes = sprav_dict['land_codes']
            return True
        except KeyError:
            return False

    @catch_ex_as_sprav_err
    def get_data_from_db(self, spr_path):
        self._s_conn = DBConn(spr_path, False)
        data_dict = {}
        self._s_conn.make_connection()
        if not self._s_conn.has_dbc:
            raise SpravError(0)
        self.reset_sorted_keys()
        data_dict['land_codes'] = self.get_l_codes()
        attr_config = self.make_attr_dependencies()
        data_dict['expa_f_str'] = self.get_expa_f_str(data_dict['land_codes'])
        data_dict['expa_r_str'] = self._get_expa_r_str(attr_config)
        data_dict['expb_f_str'] = self.get_expb_f_str(data_dict['land_codes'], attr_config)
        data_dict['expb_r_str'] = self.get_expb_r_str(attr_config)

        data_dict['attr_depnd'] = self.remake_attr_conf(attr_config)
        data_dict['str_orders'] = self.make_orders()
        data_dict['soato_npt'] = self.get_np_type()
        data_dict['bgd2ekp'] = self.remake_bgd2()
        data_dict['f22_notes'] = self.get_f22_names()
        spr_cfg = DbStructures.spr_db_cfg
        table = DbStructures.s_ustype
        data_dict['user_types'] = self.select_to_str(u'select %s from %s' % (spr_cfg[table]['user_type']['name'], table))
        table = DbStructures.s_slnad
        data_dict['slnad_codes'] = self.select_to_str(u'select %s from %s' %(spr_cfg[table]['sl_nad_code']['name'], table))
        table = DbStructures.s_state
        data_dict['state_codes'] = self.select_to_str(u'select %s from %s'%(spr_cfg[table]['state_code']['name'], table))
        table = DbStructures.s_mc
        data_dict['melio_codes'] = self.select_to_str(u'select %s from %s'%(spr_cfg[table]['mc']['name'], table))
        self._s_conn.close_conn()
        return data_dict

    @staticmethod
    def remake_attr_conf(attr_conf):
        for k, v in attr_conf.items():
            if isinstance(v, dict):
                attr_conf[k] = v['f_index']
        return attr_conf


    def select_sprav(self, query):
        try:
            return self._s_conn.get_tab_list(query)
        except Exception:
            raise SpravError(1, query)

    @catch_ex_as_sprav_err
    def select_to_str(self, query):
        codes_list = self._s_conn.exec_sel_query(query)
        codes_list = map(lambda x : u'\'%s\'' % x[0] if isinstance(x[0], unicode) else str(x[0]), codes_list)
        codes_list = ', '.join(codes_list)
        return codes_list

    def make_attr_dependencies(self):
        """
        Caution! Very important method!

        Here we save the list of fields in specific order to tuple and
        also put the index of that field to r_attr key
        * means that field is multiple

        Silensed:
        in these method UserType field silenced because its appears after data convertation
        as 'nptype' attribute we save SOATO field here, but after convert it becomes nptype in ctrow instance.

        Important:
        ctr_structure hold fields in order like the crostab_razv row structure will be(it's going to be nested)
        """
        check_aliases = [u'lc', u'mc', u'area', u'usertype', u'usern_sad', u'id', u'f22', u'state', u'part', u'slnad', u'usern', u'nptype']
        #check_aliases are resolved key-names, they got info about Field_Names (their indexes)
        tab_name = DbStructures.s_r_alias
        tab_str = DbStructures.str_db_cfg[tab_name]
        format_d = {
            't': tab_name,
            'alias':    tab_str['alias']['name'],
            'match_f':  tab_str['match_f']['name'],
            'f_type' :  tab_str['f_type']['name']
        }
        query = u'select %(alias)s, %(match_f)s, %(f_type)s from %(t)s' % format_d
        try:
            attr_config = self._s_conn.get_tab_dict(query)
            if not attr_config:
                raise Exception()
        except Exception:
            raise SpravError(1, query)
        ctr_attr_structure = []
        for r_attr, field in attr_config.items():
            f_ctr = unicode(field[0])
            f_type = unicode(field[1])
            if r_attr == 'usertype':
                f_ctr = u'UserType_*'
                f_type = 'int'
            if ' ' in f_ctr: # Небольшая подстраховка  :)
                raise SpravError(3, tab_name, f_ctr, u'Названия полей не должны содержать пробелов!')
            ctr_attr_structure.append(f_ctr)
            attr_config[r_attr] = {
                'f_type' :  f_type,
                'f_index':    ctr_attr_structure.index(f_ctr)
            }
        attr_config['ctr_structure'] = tuple(ctr_attr_structure)
        all_aliases = attr_config.keys()
        all_aliases.extend(check_aliases)
        if len(attr_config) == len(set(all_aliases)):
            return attr_config
        else:
            failed_aliases = []
            for alias in check_aliases:
                if alias not in attr_config:
                    failed_aliases.append(alias)
            raise SpravError(0, u'В таблице %s не заданы используемые в программе соответствия %s' % (tab_name, unicode(failed_aliases)))

    def make_orders(self):
        order = self.__sorted_keys
        sv_order = []
        sv_order.extend(order['a_f'])
        for r_key in order['a_r']:
            if r_key != 'total':
                if r_key in sv_order:
                    raise SpravError(0, u'Названия строк и полей (за исключением "total") не должны совпадать: %s' % r_key)
                sv_order.append(r_key)
        order['sv_f'] = sv_order
        return order

    def get_expa_f_str(self, l_codes):
        tab_name = DbStructures.s_a_f_str
        tab_str = DbStructures.str_db_cfg[tab_name]
        format_d = {
            't': tab_name,
            'f_num':  tab_str['f_num']['name'],
            'f_name':   tab_str['f_name']['name'],
            'sum_fields':  tab_str['sum_fields']['name'],
            'balance_lvl': tab_str['balance_lvl']['name'],
            'balance_by': tab_str['balance_by']['name']
        }
        f_str = self._s_conn.get_tab_dict(u'select %(f_num)s, %(f_name)s, %(sum_fields)s, %(balance_lvl)s, %(balance_by)s from %(t)s' % format_d)
        f_str_d = {}
        for f_num in sorted(f_str):
            f_props = f_str[f_num]
            f_name = f_props[0]
            if not f_name:
                raise SpravError(3, tab_name , f_num, u'В строке не задано имя')
            self.__sorted_keys['a_f'].append(f_name)
            sum_f = self.split_str_change_type(f_props[1], ',', 'int', tab_name, f_num)
            # Заполняем sum_f значениями имеющихся ключей вместо их id
            sum_f = tuple([f_str[f_n][0] for f_n in sum_f])
            f_str_d[f_name] = {'sum_f':sum_f}
            try:
                f_str_d[f_name]['codes'] = l_codes[f_num]
            except KeyError:
                f_str_d[f_name]['codes'] = ()
        #Add balance properties
        self._add_balance_props(f_str.values(),0, 2, 3, f_str_d, tab_name)
        return f_str_d

    @staticmethod
    def _add_balance_props(selected, key_ind, b_lvl_ind, b_by_ind, props_dict, tab_name):
        """

        :param selected: Data received from sprav database(type: list)
        :param key_ind: index of future row|field key in selected items(same as props_dict keys)
        :param b_lvl_ind: index of 'balance level' in selected items
        :param b_by_ind: index of 'balance by' in selected items
        :param props_dict: ! modifying dict. Method adds balance_lvl and balance_by keys
        :param tab_name: the name of queried table
        :raise SpravError: raises special balance errors from SpravError instance
        """
        for val in selected:
            if val[b_lvl_ind]:
                key = val[key_ind]
                balance_lvl =val[b_lvl_ind]
                balance_by = val[b_by_ind]
                if not balance_by:
                    raise SpravError(5, tab_name, key)
                if balance_by not in props_dict and balance_by != u'*':
                    raise SpravError(4, tab_name, key, balance_by)
                props_dict[key]['balance_lvl'] = balance_lvl
                props_dict[key]['balance_by'] = balance_by

    def _get_expa_r_str(self, valid_aliases):
        """
        !!! key 'total' hold additional information with distinct group fields
        """

        tab_name = DbStructures.s_a_r_str
        tab_str = DbStructures.str_db_cfg[tab_name]
        format_d = {
            't': tab_name,
            'row_id':  tab_str['row_id']['name'],
            'codes':   tab_str['codes']['name'],
            'row_name':  tab_str['row_name']['name'],
            'group_field':tab_str['group_field']['name'],
            'balance_lvl': tab_str['balance_lvl']['name'],
            'balance_by': tab_str['balance_by']['name'],
        }
        query = u'select %(row_id)s, %(row_name)s, %(codes)s, %(group_field)s, %(balance_lvl)s, %(balance_by)s from %(t)s' % format_d
        params = self._s_conn.get_tab_dict(query)
        r_props = {}
        for r_key in sorted(params):
            r_name = params[r_key][0]
            if not r_name:
                raise SpravError(3, tab_name, r_key, u'В строке не задано имя')
            self.__sorted_keys['a_r'].append(r_name) # Создание порядка следования строк для финальной выгрузки

            if r_name == 'total':
                r_props[r_name] = {}
            else:
                alias = params[r_key][2]
                if alias not in valid_aliases:
                    self.raise_strct_err(tab_name, r_key)
                cods = self.split_str_change_type(params[r_key][1], ',', valid_aliases[alias]['f_type'], tab_name, r_key)
                if cods:
                    r_props[r_name] = {'codes': cods, 'sort_alias': alias}
                else:
                    self.raise_strct_err(tab_name, r_key)
        self._add_balance_props(params.values(), 0,3,4,r_props, tab_name)
        return r_props

    def get_expb_f_str(self, l_codes, valid_aliases):
        tab_name = DbStructures.s_b_f_str
        tab_str = DbStructures.str_db_cfg[tab_name]
        format_d = {
            't': tab_name,
            'f_num':  tab_str['f_num']['name'],
            'f_name':tab_str['f_name']['name'],
            'alias_codes':  tab_str['alias_codes']['name'],
            'sum_fields':tab_str['sum_fields']['name'],
            'balance_lvl': tab_str['balance_lvl']['name'],
            'balance_by': tab_str['balance_by']['name']
        }
        f_structure = self._s_conn.get_tab_dict(u'select  %(f_num)s, %(f_name)s, %(alias_codes)s, %(sum_fields)s, %(balance_lvl)s, %(balance_by)s from %(t)s' % format_d)
        # r_codes = self._s_conn.get_tab_dict(u'select RowName, Code, SortIndex from ExpA_r_Structure')
        f_order = []
        f_props = {}
        for f_num in sorted(f_structure):
            f_name, als_cds, sum_flds = f_structure[f_num][:3]
            f_order.append(f_name)
            sum_f = self.split_str_change_type(sum_flds, ',', 'int', tab_name, f_num) if sum_flds else ()
            sum_f = tuple([f_structure[f_n][0] for f_n in sum_f])
            f_props[f_name] = {'sum_f': sum_f}
            s_cases = self.split_line(als_cds, ';')
            if s_cases:
                aliases_codes = {}
                for srt in s_cases:
                    a_c = self.split_line(srt, '=')
                    if len(a_c) != 2:
                        self.raise_strct_err(tab_name, f_num)
                    als, cds = a_c
                    tmp_cods = []
                    if als == u'lc':
                        cds = self.split_line(cds, ',')
                        for c in cds:
                            if '*' in c:
                                c = c.replace('*', '')
                                c = self.to_int(c, tab_name, f_num)
                                if c in l_codes:
                                    tmp_cods.extend(l_codes[c])
                            else:
                                c = self.to_int(c, tab_name, f_num)
                                tmp_cods.append(c)
                    elif als in valid_aliases:
                        tmp_cods = self.split_str_change_type(cds, ',', valid_aliases[als]['f_type'], tab_name, f_num)
                    else:
                        self.raise_strct_err(tab_name, f_num)
                    aliases_codes[als] = tuple(tmp_cods)
                f_props[f_name]['alias_codes'] = aliases_codes
        #Строим список ключей упорядоченных в соответствии с порядковыми номерами
        self.__sorted_keys['b_f'] = tuple(f_order)
        self._add_balance_props(f_structure.values(), 0, 3,4, f_props, tab_name)
        return f_props



    def get_l_codes(self):
        tab = DbStructures.s_lc
        tab_str = DbStructures.str_db_cfg[tab]
        format_d = {
            't': tab,
            'lc': tab_str['lc']['name'],
            'f_num':tab_str['f_num']['name']
        }
        lc_d = {}
        l_codes = self.select_sprav(u'select %(f_num)s, %(lc)s from %(t)s' % format_d)
        for (key, kod) in l_codes:
            try:
                lc_d[key].append(kod)
            except KeyError:
                lc_d[key] = [kod,]
        for k,v in lc_d.items():
            lc_d[k] = tuple(v)
        return lc_d


    def get_expb_r_str(self, valid_aliases):
        tab_name = DbStructures.s_b_r_str
        tab_str = DbStructures.str_db_cfg[tab_name]
        format_d = {
            't': tab_name,
            'row_id':   tab_str['row_id']['name'],
            'row_key':  tab_str['row_key']['name'],
            'f22_value':tab_str['f22_value']['name'],
            'sort_by':  tab_str['sort_by']['name'],
            'sort_codes':tab_str['sort_codes']['name'],
            'sum_conditions':tab_str['sum_conditions']['name'],
            'balance_lvl': tab_str['balance_lvl']['name'],
            'balance_by': tab_str['balance_by']['name']
        }
        query = u'select %(row_id)s, %(row_key)s, %(f22_value)s, %(sort_by)s, %(sort_codes)s, %(sum_conditions)s, %(balance_lvl)s, %(balance_by)s from %(t)s' % format_d
        r_selected = self._s_conn.get_tab_dict(query)
        b_f_names = self.__sorted_keys['b_f']
        r_props = {}
        for r_id in sorted(r_selected):
            r_key = r_selected[r_id][0]
            self.__sorted_keys['b_r'].append(r_key)
            r_props[r_key] = {}
        for row in r_selected.values():
            r_key = row[0]
            r_props[r_key] = {'r_name': row[1]}       #work with val_f22
            s_by, s_cds, sum_cnds = row[2:5]
            if s_by in valid_aliases:
                s_cds = self.split_str_change_type(s_cds, ",", valid_aliases[s_by]['f_type'], tab_name, r_key)
                if s_cds:
                    r_props[r_key]['s_by'] = s_by # артибут, по которму производится сортировка
                    r_props[r_key]['s_codes'] = s_cds
                else:
                    self.raise_strct_err(tab_name, r_key)
            elif not s_by:
                r_props[r_key]['s_by'] = None
            else:
                self.raise_strct_err(tab_name, r_key)

            if sum_cnds:
                conditions = self.split_line(sum_cnds, u';')
                r_props[r_key]['conds'] = {}
                for cond in conditions:
                    cond_op = cond[0]
                    cond = cond[1:]
                    if not cond:
                        self.raise_strct_err(tab_name, r_key)
                    if cond_op in u'+-':
                        add_rows = self.split_line(cond, u',')
                        if not self.is_include(r_props.keys(), add_rows):  #check is include, add included
                            self.raise_strct_err(tab_name, r_key)
                        key_name = 'add' if cond_op == u'+' else u'sub'
                        r_props[r_key]['conds'][key_name] = add_rows
                    elif cond_op == u'&':
                        eq_di = {}
                        eq = self.split_line(cond, u'=')
                        if len(eq) == 2:
                            eq = list(eq)
                            # get operation type
                            if eq[0][-1] == u'+':

                                eq[0] = eq[0][:-1]
                                eq_di['op'] = u'+'
                            elif eq[0][-1] == u'-':
                                eq[0] = eq[0][:-1]
                                eq_di['op'] = u'-'
                            else:
                                eq_di['op'] = u'='
                            # parse parameters and check their validation
                            if eq[0] in b_f_names:
                                eq_di['upd_f'] = eq[0]
                                eq_right = self.split_line(eq[1],u':')
                                if len(eq_right) == 2:
                                    if eq_right[0] in r_props and eq_right[1] in b_f_names:
                                        eq_di['take_f'] = eq_right[1]
                                        eq_di['take_r'] = eq_right[0]
                                    else: continue
                                elif len(eq_right) == 1:
                                    if eq_right[0] in b_f_names:
                                        eq_di['take_f'] = eq_right[0]
                                        eq_di['take_r'] = r_key
                                    else:
                                        self.raise_strct_err(tab_name, r_key)
                                else:
                                    self.raise_strct_err(tab_name, r_key)
                                #add eq_di key to r_params[key] in case that all clear
                                try:
                                    r_props[r_key]['conds']['eq_f'].append(eq_di)
                                except KeyError:
                                    r_props[r_key]['conds']['eq_f'] = [eq_di,]
                            else:
                                self.raise_strct_err(tab_name, r_key)
                        else:
                            self.raise_strct_err(tab_name, r_key)
        self._add_balance_props(r_selected.values(), 0, 5, 6 ,r_props, tab_name)
        return  r_props

    @staticmethod
    def split_str_change_type(string, splitter, result_type, tab, row):
        type_func = {
            'int':  lambda x: int(x),
            'str':  lambda x: unicode(x),
            'float':lambda x: float(x)
            }
        try:
            if string:
                res = string.split(splitter)
                res = map(type_func[result_type], res)  #changing result type
                return tuple(res)
            else:
                return ()
        except:
            raise SpravError(2, tab, row)

    @staticmethod
    def split_line(line, symbol):
        """
        :param line:
        :param symbol: splitter
        :return: without spaces, without elements which returns False
        """
        if type(line) in (str, unicode):
            split_l = line.replace(u' ',u'').split(symbol)
            for l in split_l:
                if not l:
                    split_l.remove(l)
            return tuple(split_l)
        else:
            return ()

    @staticmethod
    def raise_strct_err(table_name, r_id):
        raise SpravError(2, table_name, r_id)

    def to_int(self, str_line, table_name, r_id):
        try:
            return int(str_line)
        except:
            self.raise_strct_err(table_name, r_id)

    @staticmethod
    def is_include(main_li, inc_li):
        li = main_li[:]
        li.extend(inc_li)
        if len(set(li)) == len(main_li):
            return True
        else: return False

    def get_np_type(self):
        tab_name = DbStructures.s_soato
        tab_str = DbStructures.spr_db_cfg[tab_name]
        format_d = {
            't': tab_name,
            'zn_1':     tab_str['zn_1']['name'],
            'zn_2':     tab_str['zn_2']['name'],
            'zn_57min': tab_str['zn_57min']['name'],
            'zn_57max': tab_str['zn_57max']['name'],
            'zn_810min':tab_str['zn_810min']['name'],
            'zn_810max':tab_str['zn_810max']['name'],
            'type_np':  tab_str['type_np']['name']
        }
        query = u'select %(zn_1)s, %(zn_2)s, %(zn_57min)s, %(zn_57max)s, %(zn_810min)s, %(zn_810max)s, %(type_np)s from %(t)s' % format_d
        return self._s_conn.exec_sel_query(query)

    def remake_bgd1(self):
        """
        BGD1 have fields: F22,UTYPE, NPTYPE_min, NPTYPE_max, State, SLNAD, NEWUSNAME, DOPUSNAME
        :return: list with BGD1 rows
        """
        tab_name = DbStructures.s_b2e_1
        tab_str = DbStructures.spr_db_cfg[tab_name]
        format_d = {
            't':        tab_name,
            'f22':      tab_str['f22']['name'],
            'u_type':   tab_str['u_type']['name'],
            'np_type':  tab_str['np_type']['name'],
            'state':    tab_str['state']['name'],
            'sl_nad':   tab_str['sl_nad']['name'],
            'new_us_name':  tab_str['new_us_name']['name'],
            'dop_us_name':  tab_str['dop_us_name']['name']
        }
        selectbgd1 = u'select %(f22)s, %(u_type)s, %(np_type)s, %(state)s, %(sl_nad)s, %(new_us_name)s, %(dop_us_name)s from %(t)s' % format_d
        newbgd = []
        if self._s_conn:
            for row in self.select_sprav(selectbgd1):
                utypelist = self.u_to_int(row[1].split(','))
                nptypelist = self.u_to_int(row[2].split(','))
                stateli = self.u_to_int(row[3].split(','))
                nptypeliremaked = self.remake_list(nptypelist)
                for state in stateli:
                    for utype in utypelist:
                        for npt in nptypeliremaked:
                            newbgd.append((row[0], utype, state, int(row[4]), npt[0], npt[1],  row[5],row[6]))
        return newbgd

    def remake_bgd2(self):
        tab_name = DbStructures.s_b2e_2
        tab_str = DbStructures.spr_db_cfg[tab_name]
        format_d = {
            't':        tab_name,
            'f22':      tab_str['f22']['name'],
            'new_f22':  tab_str['new_f22']['name'],
            'u_type':   tab_str['u_type']['name'],
            'np_type':  tab_str['np_type']['name'],
            'lc_min':   tab_str['lc_min']['name'],
            'lc_max':   tab_str['lc_max']['name'],
            'new_lc':   tab_str['new_lc']['name'],
            'state':    tab_str['state']['name'],
            'sl_nad':       tab_str['sl_nad']['name'],
            'new_us_name':  tab_str['new_us_name']['name'],
            'dop_us_name':  tab_str['dop_us_name']['name']
        }
        selectbgd2 = u'select %(f22)s, %(new_f22)s, %(u_type)s, %(np_type)s, %(lc_min)s, %(lc_max)s, %(new_lc)s, %(state)s, %(sl_nad)s, %(new_us_name)s, %(dop_us_name)s from %(t)s' % format_d
        bgd2 = []
        if self._s_conn:
            for row in self.select_sprav(selectbgd2):
                utypelist = self.u_to_int(row[2].split(u','))
                nptypelist = self.u_to_int(row[3].split(u','))
                stateli = self.u_to_int(row[7].split(u','))
                nptypeliremaked = self.remake_list(nptypelist)
                nlc = row[6] if row[6] else None
                for state in stateli:
                    for utype in utypelist:
                        for npt in nptypeliremaked:
                            bgd2.append((row[0], utype, state, int(row[8]), row[1],  npt[0], npt[1], row[4], row[5], nlc, row[9], row[10]))
                            # bgd_row: F22, UTYPE, State, SLNAD, newF22,NPTYPE_min, NPTYPE_max, lc_min, lc_max, newlc, NEWUSNAME, DOPUSNAME
            bgd2 = (self.remake_bgd1(),bgd2)
        return bgd2


    def get_f22_names(self):
        tab_name = DbStructures.s_f22
        tab_str = DbStructures.spr_db_cfg[tab_name]
        format_d = {
            't': tab_name,
            'f22_code': tab_str['f22_code']['name'],
            'f22_name': tab_str['f22_name']['name']
        }
        f22_names = self.select_sprav(u'Select %(f22_code)s, %(f22_name)s from %(t)s' % format_d)
        f22_n_dict = {}
        for row in f22_names:
            f22_n_dict[row[0]] = row[1]
        return f22_n_dict

    @staticmethod
    def bgd_to_dicts(bgd_li):
        """
        :param bgd_li:
        :return: bgd like a tree (dict of dict structure) Keys: f22->utype->state->slnad-> list of others parameters
        """
        bgd_dict = dict()
        for row in bgd_li:
            if row[0] not in bgd_dict:
                bgd_dict[row[0]] = dict()
            if row[1] not in bgd_dict[row[0]]:
                bgd_dict[row[0]][row[1]] = dict()
            if row[2] not in bgd_dict[row[0]][row[1]]:
                bgd_dict[row[0]][row[1]][row[2]] = dict()
            if row[3] not in bgd_dict[row[0]][row[1]][row[2]]:
                bgd_dict[row[0]][row[1]][row[2]][row[3]] = []
            bgd_dict[row[0]][row[1]][row[2]][row[3]].append(row[4:])
        return bgd_dict

    @staticmethod
    def u_to_int(li):
        newli = []
        for i in range(len(li)):
            newli.append(int(li[i]))
        return newli

    @staticmethod
    def remake_list(li):
        """
            Rturns list of tuples with intervals of numbers
        :param li: <example> [1,2,3,4,8,9]
        :return: <example> [(1,4),(8,9)]
        """
        minli = []
        maxli = []
        lilen = len(li)
        inext = 0
        for i in range(len(li)):
            if i == 0:
                minli.append(li[0])
            elif i < inext:
                continue
            try:
                icheck = li[i+1]
            except:
                maxli.append(li[lilen-1])
                break
            w = 1
            while i+w < lilen:
                if li[i+w] - li[i+w-1] == 1:
                    w+=1
                else:
                    inext = i+w
                    maxli.append(li[i+w-1])
                    minli.append(li[i+w])
                    break
        return zip(minli,maxli)

