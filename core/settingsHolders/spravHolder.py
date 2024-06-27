import json
import time
from typing import Any, Dict, List, Tuple, Union

from constants import coreFiles
from constants import spravErrTypes as errTypes
from core.db.structures.sprav import SpravStructure
from core.errors import SpravError
from core.extractors.initializer import SpravController


def catch_ex_as_sprav_err(decor_method):
    def wrapper(*args, **kwargs):
        try:
            return decor_method(*args, **kwargs)
        except SpravError:
            raise
        except Exception as err:
            raise SpravError(errTypes.unexpected, err)

    return wrapper


class SpravHolder:
    def __init__(self):
        self._s_conn = None
        self.expa_f_str = None
        self.expa_r_str = None
        self.expf22_f_str = None
        self.expf22_r_str = None
        self.soato_npt = None
        self.bgd2ekp = None
        self.f22_notes = None
        self.bgd2ekp_1 = None
        self.bgd2ekp_2 = None
        self.user_types = None
        self.slnad_codes = None
        self.state_codes = None
        self.melio_codes = None
        self.category_codes = None

        self.select_conditions = None
        self.land_codes = None
        self.max_n = None
        self.crtab_columns = None
        self.str_orders = None
        self.__sorted_keys = None
        self.current_sprav_data = None
        self.reset_sorted_keys()

    def reset_sorted_keys(self):
        self.__sorted_keys = {
            'a_f': [],
            'a_r': [],
            'sv_f': [],
            'b_f': [],
            'b_r': []
        }

    def check_spr_db(self, db_path: str) -> None:
        s_controller = SpravController(db_path)
        if not s_controller.is_connected:
            raise SpravError(errTypes.no_db_conn, db_path)
        not_found_tables = s_controller.get_not_found_tables()
        if not_found_tables:
            raise SpravError(errTypes.empty_spr_tabs, not_found_tables)
        wrong_typed_fields = s_controller.validate_field_types()
        if wrong_typed_fields:
            raise SpravError(errTypes.empty_spr_fields, wrong_typed_fields.items())
        else:
            self._s_conn = s_controller.conn

    def close_db_connection(self):
        if self._s_conn and self._s_conn.has_dbc:
            self._s_conn.close_conn()

    def set_parameters(self, sprav_dict):
        self.__sorted_keys = None
        try:
            self.attr_config = sprav_dict['attr_depnd']
            self.expa_f_str = sprav_dict['expa_f_str']
            self.expa_r_str = sprav_dict['expa_r_str']
            self.expf22_f_str = sprav_dict['expf22_f_str']
            self.expf22_r_str = sprav_dict['expf22_r_str']
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
            self.category_codes = sprav_dict['category_codes']
            self.select_conditions = sprav_dict['select_conditions']
            return True
        except KeyError:
            return False

    def set_changes(self, change_data: Dict, sprav_path: str):
        # тут написан какой-то бред
        if self.set_parameters(change_data):
            self.current_sprav_data = change_data
            self.current_sprav_data['path_info'] = sprav_path
        else:
            if self.current_sprav_data:
                self.set_parameters(change_data)
                raise SpravError(errTypes.changes_rejected, True)
            else:
                raise SpravError(errTypes.changes_rejected, True)

    def get_info(self):
        data = self.current_sprav_data
        if not data:
            return ""
        return """Создан:\n\t%s\nЗагружен из:\n\t%s\n""" % (data["create_time"], data["path_info"])

    @catch_ex_as_sprav_err
    def get_data_from_db(self, close_conn=True):
        data_dict = {}
        self._s_conn.make_connection()
        if not self._s_conn.has_dbc:
            raise SpravError(errTypes.connection_failed)
        self.reset_sorted_keys()
        data_dict['land_codes'] = self.get_land_codes()
        attr_config = self.make_attr_dependencies()
        data_dict['expa_f_str'] = self.get_expa_f_str(data_dict['land_codes'])
        data_dict['expa_r_str'] = self.get_expa_r_str(attr_config)
        data_dict['expf22_f_str'] = self.get_expf22_f_str(data_dict['land_codes'], attr_config)
        data_dict['expf22_r_str'] = self.get_expf22_r_str(attr_config)
        data_dict['attr_depnd'] = self.remake_attr_conf(attr_config)
        data_dict['str_orders'] = self.make_orders()
        data_dict['soato_npt'] = self.get_np_type()
        data_dict['bgd2ekp'] = self.remake_bgd2()
        data_dict['f22_notes'] = self.get_f22_names()

        table_name = SpravStructure.ustype
        table_scheme = SpravStructure.get_table_scheme(table_name)
        query = f"SELECT {table_scheme['user_type']['name']} FROM {table_name}"
        data_dict['user_types'] = self.select_to_str(query)

        table_name = SpravStructure.slnad
        table_scheme = SpravStructure.get_table_scheme(table_name)
        query = f"SELECT {table_scheme['sl_nad_code']['name']} FROM {table_name}"
        data_dict['slnad_codes'] = self.select_to_str(query)

        table_name = SpravStructure.state
        table_scheme = SpravStructure.get_table_scheme(table_name)
        query = f"SELECT {table_scheme['state_code']['name']} FROM {table_name}"
        data_dict['state_codes'] = self.select_to_str(query)

        table_name = SpravStructure.mc
        table_scheme = SpravStructure.get_table_scheme(table_name)
        query = f"SELECT {table_scheme['mc']['name']} FROM {table_name}"
        data_dict['melio_codes'] = self.select_to_str(query)

        table_name = SpravStructure.category
        table_scheme = SpravStructure.get_table_scheme(table_name)
        query = f"SELECT {table_scheme['category']['name']} FROM {table_name}"
        data_dict['category_codes'] = self.select_to_str(query)

        data_dict['select_conditions'] = self.get_select_conditions()
        data_dict['create_time'] = time.strftime(u"%H:%M__%d.%m.%Y")

        if close_conn:
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
        codes_list = map(lambda x: '\'%s\'' % x[0] if isinstance(x[0], str) else str(x[0]), codes_list)
        codes_list = ', '.join(codes_list)
        return codes_list

    @catch_ex_as_sprav_err
    def select_to_str_path(self, query):
        codes_list = self._s_conn.exec_sel_query(query)
        codes_list = map(lambda x: '%s' % x[0] if isinstance(x[0], str) else str(x[0]), codes_list)
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
        check_aliases = ['lc', 'mc', 'area', 'usertype', 'usern_sad', 'id', 'f22', 'state', 'part', 'slnad', 'usern',
                         'nptype']
        # check_aliases are resolved key-names, they got info about Field_Names (their indexes)
        table_scheme = SpravStructure.get_table_scheme(SpravStructure.r_alias)

        query = (f"SELECT {table_scheme['alias']['name']}, "
                 f"       {table_scheme['match_f']['name']}, "
                 f"       {table_scheme['f_type']['name']} "
                 f"FROM {SpravStructure.r_alias}")
        try:
            attr_aliasing = self._s_conn.get_tab_dict(query)
            if not attr_aliasing:
                raise Exception()
        except Exception:
            raise SpravError(1, query)
        ctr_attr_structure = []
        for alias, field in attr_aliasing.items():
            field_ctr = str(field[0])
            field_type = str(field[1])
            if alias == 'usertype':
                field_ctr = 'UserType_*'
                field_type = 'int'
            if ' ' in field_ctr:  # Небольшая подстраховка  :)
                raise SpravError(3, SpravStructure.r_alias, field_ctr, 'Названия полей не должны содержать пробелов!')
            ctr_attr_structure.append(field_ctr)
            attr_aliasing[alias] = {
                'f_type': field_type,
                'f_index': ctr_attr_structure.index(field_ctr)
            }
        attr_aliasing['ctr_structure'] = tuple(ctr_attr_structure)
        all_aliases = list(attr_aliasing.keys())
        all_aliases.extend(check_aliases)
        if len(attr_aliasing) == len(set(all_aliases)):
            return attr_aliasing
        else:
            failed_aliases = []
            for alias in check_aliases:
                if alias not in attr_aliasing:
                    failed_aliases.append(alias)
            raise SpravError(
                0,
                'В таблице %s не заданы используемые в программе соответствия %s' % (
                    SpravStructure.r_alias, str(failed_aliases))
            )

    def make_orders(self):
        order = self.__sorted_keys
        sv_order = []
        sv_order.extend(order['a_f'])
        for r_key in order['a_r']:
            if r_key != 'total':
                if r_key in sv_order:
                    raise SpravError(0,
                                     'Названия строк и полей (за исключением "total") не должны совпадать: %s' % r_key)
                sv_order.append(r_key)
        order['sv_f'] = sv_order
        return order

    def get_expa_f_str(self, land_codes):
        table_name = SpravStructure.a_f_str
        table_scheme = SpravStructure.get_table_scheme(table_name)
        query = (f"SELECT {table_scheme['f_num']['name']}, "
                 f"       {table_scheme['f_name']['name']}, "
                 f"       {table_scheme['sum_fields']['name']}, "
                 f"       {table_scheme['balance_lvl']['name']}, "
                 f"       {table_scheme['balance_by']['name']} "
                 f"FROM {table_name}")
        f_str = self._s_conn.get_tab_dict(query)

        f_str_d = {}
        for f_num in sorted(f_str):
            f_props = f_str[f_num]
            f_name = f_props[0]
            if not f_name:
                raise SpravError(3, table_name, f_num, 'В строке не задано имя')
            self.__sorted_keys['a_f'].append(f_name)
            sum_ids = self.split_str_change_type(f_props[1], ',', 'int', table_name, f_num)
            # Заполняем sum_f значениями имеющихся ключей вместо их id
            sum_names = tuple([f_str[f_n][0] for f_n in sum_ids])
            f_str_d[f_name] = {'sum_f': sum_names}
            try:
                f_str_d[f_name]['codes'] = land_codes[f_num]
            except KeyError:
                f_str_d[f_name]['codes'] = ()
        self._add_balance_props(f_str.values(), 0, 2, 3, f_str_d, table_name)
        return f_str_d

    @staticmethod
    def _add_balance_props(
            f_str_lists: List[List],
            key_ind: int,
            b_lvl_ind: int,
            b_by_ind: int,
            props_dict: Dict,
            tab_name: str,
    ) -> None:
        """
        :param f_str_lists: Data received from sprav database(type: list)
        :param key_ind: index of future row|field key in selected items(same as props_dict keys)
        :param b_lvl_ind: index of 'balance level' in selected items
        :param b_by_ind: index of 'balance by' in selected items
        :param props_dict: ! modifying dict. Method adds balance_lvl and balance_by keys
        :param tab_name: the name of queried table
        :raise SpravError: raises special balance errors from SpravError instance
        """
        for f_name_single in f_str_lists:
            if f_name_single[b_lvl_ind] is not None:
                key = f_name_single[key_ind]
                balance_lvl = f_name_single[b_lvl_ind]
                balance_by = f_name_single[b_by_ind]
                if balance_by is None:
                    raise SpravError(5, tab_name, key)
                if balance_by not in props_dict and balance_by != '*':
                    raise SpravError(4, tab_name, key, balance_by)
                props_dict[key]['balance_lvl'] = balance_lvl
                props_dict[key]['balance_by'] = balance_by

    def get_expa_r_str(
            self,
            valid_aliases: Dict[
                str,
                Union[
                    Dict[str, Union[str, int]],
                    Tuple[str, ...]
                ]
            ]
    ) -> Dict:
        """
        !!! key 'total' hold additional information with distinct group fields
        """

        table_name = SpravStructure.a_r_str
        table_scheme = SpravStructure.get_table_scheme(table_name)
        query = (f"SELECT {table_scheme['row_id']['name']}, "
                 f"       {table_scheme['row_name']['name']}, "
                 f"       {table_scheme['codes']['name']}, "
                 f"       {table_scheme['group_field']['name']}, "
                 f"       {table_scheme['balance_lvl']['name']}, "
                 f"       {table_scheme['balance_by']['name']} "
                 f"FROM {table_name}")

        params = self._s_conn.get_tab_dict(query)
        rows_props = {}
        for row_id in sorted(params):
            row_name = params[row_id][0]
            if not row_name:
                raise SpravError(3, table_name, row_id, 'В строке не задано имя')
            self.__sorted_keys['a_r'].append(row_name)  # Создание порядка следования строк для финальной выгрузки

            if row_name == 'total':
                rows_props[row_name] = {}
            else:
                row_group_field = params[row_id][2]
                if row_group_field not in valid_aliases:
                    raise SpravError(2, table_name, row_id)
                codes = self.split_str_change_type(
                    string=params[row_id][1],
                    splitter=',',
                    result_type=valid_aliases[row_group_field]['f_type'],
                    table=table_name,
                    row_id=row_id,
                )
                if codes:
                    rows_props[row_name] = {
                        'codes': codes,
                        'sort_alias': row_group_field,
                    }
                else:
                    self.raise_strct_err(table_name, row_id)
                    raise SpravError(2, table_name, row_id)
        self._add_balance_props(params.values(), 0, 3, 4, rows_props, table_name)
        return rows_props

    def get_expf22_f_str(self, l_codes, valid_aliases):
        table_name = SpravStructure.f22_f_str
        table_scheme = SpravStructure.get_table_scheme(table_name)
        query = (f"SELECT {table_scheme['f_num']['name']}, "
                 f"       {table_scheme['f_name']['name']}, "
                 f"       {table_scheme['alias_codes']['name']}, "
                 f"       {table_scheme['sum_fields']['name']}, "
                 f"       {table_scheme['balance_lvl']['name']}, "
                 f"       {table_scheme['balance_by']['name']} "
                 f"FROM {table_name}")
        f_structure = self._s_conn.get_tab_dict(query)

        f_order = []
        f_props = {}
        for f_num in sorted(f_structure):
            f_name, als_cds, sum_flds = f_structure[f_num][:3]
            f_order.append(f_name)
            sum_f = self.split_str_change_type(sum_flds, ',', 'int', table_name, f_num) if sum_flds else ()
            sum_f = tuple([f_structure[f_n][0] for f_n in sum_f])
            f_props[f_name] = {'sum_f': sum_f}
            s_cases = self.split_line(als_cds, ';')
            if s_cases:
                aliases_codes = {}
                for srt in s_cases:
                    a_c = self.split_line(srt, '=')
                    if len(a_c) != 2:
                        self.raise_strct_err(table_name, f_num)
                    als, cds = a_c
                    tmp_cods = []
                    if als == 'lc':
                        cds = self.split_line(cds, ',')
                        for c in cds:
                            if '*' in c:
                                c = c.replace('*', '')
                                c = self.to_int(c, table_name, f_num)
                                if c in l_codes:
                                    tmp_cods.extend(l_codes[c])
                            else:
                                c = self.to_int(c, table_name, f_num)
                                tmp_cods.append(c)
                    elif als in valid_aliases:
                        tmp_cods = self.split_str_change_type(cds, ',', valid_aliases[als]['f_type'], table_name, f_num)
                    else:
                        self.raise_strct_err(table_name, f_num)
                    aliases_codes[als] = tuple(tmp_cods)
                f_props[f_name]['alias_codes'] = aliases_codes
        # Строим список ключей упорядоченных в соответствии с порядковыми номерами
        self.__sorted_keys['b_f'] = tuple(f_order)
        self._add_balance_props(f_structure.values(), 0, 3, 4, f_props, table_name)
        return f_props

    def get_land_codes(self):
        table = SpravStructure.lc
        table_scheme = SpravStructure.get_table_scheme(table)
        land_codes_mapped = {}
        land_codes = self.select_sprav(f"SELECT {table_scheme['f_num']['name']}, "
                                       f"       {table_scheme['lc']['name']} "
                                       f"FROM {table}")
        for (key, kod) in land_codes:
            try:
                land_codes_mapped[key].append(kod)
            except KeyError:
                land_codes_mapped[key] = [kod, ]
        for k, v in land_codes_mapped.items():
            land_codes_mapped[k] = tuple(v)
        return land_codes_mapped

    def get_expf22_r_str(self, valid_aliases):
        tab_name = SpravStructure.f22_r_str
        tab_str = SpravStructure.get_table_scheme(tab_name)
        format_d = {
            't': tab_name,
            'row_id': tab_str['row_id']['name'],
            'row_key': tab_str['row_key']['name'],
            'f22_value': tab_str['f22_value']['name'],
            'sort_filter': tab_str['sort_filter']['name'],
            'sum_conditions': tab_str['sum_conditions']['name'],
            'balance_lvl': tab_str['balance_lvl']['name'],
            'balance_by': tab_str['balance_by']['name']
        }
        query = 'select %(row_id)s, %(row_key)s, %(f22_value)s, %(sort_filter)s, %(sum_conditions)s, %(balance_lvl)s, %(balance_by)s from %(t)s' % format_d
        r_selected = self._s_conn.get_tab_dict(query)
        b_f_names = self.__sorted_keys['b_f']
        r_props = {}
        for r_id in sorted(r_selected):
            r_key = r_selected[r_id][0]
            self.__sorted_keys['b_r'].append(r_key)
            r_props[r_key] = {}
        for row in r_selected.values():
            r_key = row[0]
            r_props[r_key] = {'r_name': row[1]}  # work with val_f22
            try:
                r_props[r_key]['sort_filter'] = SpravHolder.parse_filter_data(row[2], valid_aliases)
            except Exception as err:
                self.raise_strct_err(tab_name, r_key)
            sum_cnds = row[3]

            if sum_cnds:
                conditions = self.split_line(sum_cnds, ';')
                r_props[r_key]['conds'] = {}
                for cond in conditions:
                    cond_op = cond[0]
                    cond = cond[1:]
                    if not cond:
                        self.raise_strct_err(tab_name, r_key)
                    if cond_op in '+-':
                        add_rows = self.split_line(cond, ',')
                        if not self.is_include(r_props.keys(), add_rows):  # check is include, add included
                            self.raise_strct_err(tab_name, r_key)
                        key_name = 'add' if cond_op == '+' else 'sub'
                        r_props[r_key]['conds'][key_name] = add_rows
                    elif cond_op == '&':
                        eq_di = {}
                        eq = self.split_line(cond, '=')
                        if len(eq) == 2:
                            eq = list(eq)
                            # get operation type
                            if eq[0][-1] == '+':

                                eq[0] = eq[0][:-1]
                                eq_di['op'] = '+'
                            elif eq[0][-1] == '-':
                                eq[0] = eq[0][:-1]
                                eq_di['op'] = '-'
                            else:
                                eq_di['op'] = '='
                            # parse parameters and check their validation
                            if eq[0] in b_f_names:
                                eq_di['upd_f'] = eq[0]
                                eq_right = self.split_line(eq[1], ':')
                                if len(eq_right) == 2:
                                    if eq_right[0] in r_props and eq_right[1] in b_f_names:
                                        eq_di['take_f'] = eq_right[1]
                                        eq_di['take_r'] = eq_right[0]
                                    else:
                                        continue
                                elif len(eq_right) == 1:
                                    if eq_right[0] in b_f_names:
                                        eq_di['take_f'] = eq_right[0]
                                        eq_di['take_r'] = r_key
                                    else:
                                        self.raise_strct_err(tab_name, r_key)
                                else:
                                    self.raise_strct_err(tab_name, r_key)
                                # add eq_di key to r_params[key] in case that all clear
                                try:
                                    r_props[r_key]['conds']['eq_f'].append(eq_di)
                                except KeyError:
                                    r_props[r_key]['conds']['eq_f'] = [eq_di, ]
                            else:
                                self.raise_strct_err(tab_name, r_key)
                        else:
                            self.raise_strct_err(tab_name, r_key)
        self._add_balance_props(r_selected.values(), 0, 4, 5, r_props, tab_name)
        return r_props

    @staticmethod
    def parse_filter_data(data, fields_validation):
        parsed_data = {}
        if data:
            parsed_data = json.loads(data)
            for k, v in parsed_data.items():
                if k not in fields_validation:
                    raise Exception('Failed to parse filter data. Key name is not valid')
        return parsed_data

    @staticmethod
    def split_str_change_type(
            string: str,
            splitter: str,
            result_type: str,
            table: str,
            row_id: int,
    ) -> Tuple[Union[int, str, float], ...]:
        type_func = {
            'int': lambda x: int(x),
            'str': lambda x: str(x),
            'float': lambda x: float(x),
        }
        try:
            if string:
                res = string.split(splitter)
                res = map(type_func[result_type], res)  # changing result type
                return tuple(res)
            else:
                return ()
        except Exception:
            raise SpravError(2, table, row_id)

    @staticmethod
    def split_line(line, symbol):
        """
        :param line:
        :param symbol: splitter
        :return: without spaces, without elements which returns False
        """
        if isinstance(line, str):
            split_l = line.replace(' ', '').split(symbol)
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
        li = list(main_li)
        li.extend(inc_li)
        return len(set(li)) == len(main_li)

    def get_np_type(self) -> List:
        table_name = SpravStructure.soato
        tab_str = SpravStructure.get_table_scheme(table_name)
        query = (f"SELECT {tab_str['zn_1']['name']}, "
                 f"       {tab_str['zn_2']['name']}, "
                 f"       {tab_str['zn_57min']['name']}, "
                 f"       {tab_str['zn_57max']['name']}, "
                 f"       {tab_str['zn_810min']['name']}, "
                 f"       {tab_str['zn_810max']['name']}, "
                 f"       {tab_str['type_np']['name']} "
                 f"FROM {table_name}")
        return self._s_conn.exec_sel_query(query)

    def get_select_conditions(self):
        tab_name = SpravStructure.select_conditions
        tab_str = SpravStructure.get_table_scheme(tab_name)
        id = tab_str['id']['name']
        title = tab_str['title']['name']
        wc = tab_str['where_case']['name']
        return self._s_conn.get_common_selection(tab_name, [id, title, wc])

    def remake_bgd1(self):
        """
        BGD1 have fields: F22,UTYPE, NPTYPE_min, NPTYPE_max, State, SLNAD, NEWUSNAME, DOPUSNAME
        :return: list with BGD1 rows
        """
        tab_name = SpravStructure.b2e_1
        tab_str = SpravStructure.get_table_scheme(tab_name)
        format_d = {
            't': tab_name,
            'f22': tab_str['f22']['name'],
            'u_type': tab_str['u_type']['name'],
            'np_type': tab_str['np_type']['name'],
            'state': tab_str['state']['name'],
            'sl_nad': tab_str['sl_nad']['name'],
            'new_us_name': tab_str['new_us_name']['name'],
            'dop_us_name': tab_str['dop_us_name']['name']
        }
        selectbgd1 = 'select %(f22)s, %(u_type)s, %(np_type)s, %(state)s, %(sl_nad)s, %(new_us_name)s, %(dop_us_name)s from %(t)s' % format_d
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
                            newbgd.append((row[0], utype, state, int(row[4]), npt[0], npt[1], row[5], row[6]))
        return newbgd

    def remake_bgd2(self):
        table_name = SpravStructure.b2e_2
        table_scheme = SpravStructure.get_table_scheme(table_name)
        query = (f"SELECT {table_scheme['f22']['name']}, "
                 f"       {table_scheme['new_f22']['name']}, "
                 f"       {table_scheme['u_type']['name']}, "
                 f"       {table_scheme['np_type']['name']}, "
                 f"       {table_scheme['lc_min']['name']}, "
                 f"       {table_scheme['lc_max']['name']}, "
                 f"       {table_scheme['new_lc']['name']}, "
                 f"       {table_scheme['state']['name']}, "
                 f"       {table_scheme['sl_nad']['name']}, "
                 f"       {table_scheme['new_us_name']['name']}, "
                 f"       {table_scheme['dop_us_name']['name']} "
                 f"FROM {table_name}")
        bgd2 = []
        if self._s_conn:
            for row in self.select_sprav(query):
                utype_list = self.u_to_int(row[2].split(','))
                nptype_list = self.u_to_int(row[3].split(','))
                state_list = self.u_to_int(row[7].split(','))
                nptype_list_remaked = self.remake_list(nptype_list)
                nlc = row[6] if row[6] else None
                for state in state_list:
                    for utype in utype_list:
                        for npt in nptype_list_remaked:
                            bgd2.append((row[0], utype, state, int(row[8]), row[1], npt[0], npt[1], row[4], row[5], nlc,
                                         row[9], row[10]))
                            # bgd_row: F22, UTYPE, State, SLNAD, newF22,NPTYPE_min, NPTYPE_max, lc_min, lc_max, newlc, NEWUSNAME, DOPUSNAME
            bgd2 = (self.remake_bgd1(), bgd2)
        return bgd2

    def get_f22_names(self):
        tab_name = SpravStructure.f22
        tab_str = SpravStructure.get_table_scheme(tab_name)
        format_d = {
            't': tab_name,
            'f22_code': tab_str['f22_code']['name'],
            'f22_name': tab_str['f22_name']['name']
        }
        f22_names = self.select_sprav('Select %(f22_code)s, %(f22_name)s from %(t)s' % format_d)
        f22_n_dict = {}
        for row in f22_names:
            f22_n_dict[row[0]] = row[1]
        return f22_n_dict

    @staticmethod
    def bgd_to_dicts(bgd_li) -> dict:
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
    def u_to_int(list_: List) -> List[int]:
        new_list = []
        for i in range(len(list_)):
            new_list.append(int(list_[i]))
        return new_list

    @staticmethod
    def remake_list(li: List[int]) -> List[Tuple[int, int]]:
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
                icheck = li[i + 1]
            except:
                maxli.append(li[lilen - 1])
                break
            w = 1
            while i + w < lilen:
                if li[i + w] - li[i + w - 1] == 1:
                    w += 1
                else:
                    inext = i + w
                    maxli.append(li[i + w - 1])
                    minli.append(li[i + w])
                    break
        return list(zip(minli, maxli))
