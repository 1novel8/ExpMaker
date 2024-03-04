from core.extractors.ctrRow import CtrRow
from core.settingsHolders.spravHolder import SpravHolder

from .buildUtils import ExpBuilder
from .expARowDataCombiner import RowDataCombiner as DataComb


class ExpAMaker:
    shape_area_sum = 0
    exp_tree = None
    sv_matrix = []
    row_counter = 1

    def __init__(
            self,
            rows_data: list[CtrRow],
            users_data: dict,
            soato_data: dict,
            sprav_holder: SpravHolder = None,
            options: dict = None,
    ) -> None:
        self.sprav_holder = sprav_holder
        self.errors_occured = {}
        self.usersInfo, self.soatoInfo = users_data, soato_data
        if options and 'shape_sum_enabled' in options:
            self.shape_area_sum = options['shape_sum']
        self.cc_soato_d = self.get_cc_soato_d()
        self.datadict = self.make_datadict(rows_data)
        self.exps_dict = self.make_comb_data()

    def get_cc_soato_d(self):
        cc_soato_d = {}
        for soato in self.soatoInfo:
            if soato[-3:] == '000':
                cc_soato_d[soato[:-3]] = self.soatoInfo[soato]
        return cc_soato_d

    def get_cc_name(self, soato):
        soato = str(soato)
        try:
            return self.cc_soato_d[soato[:-3]] + '  '
        except KeyError:
            return '! '

    def make_datadict(self, rows):
        f22_dict = {}
        keys_not_used = ('ctr_structure', 'id', 'usern_sad', 'part', 'f22', 'usern', 'slnad', 'usertype', 'nptype')
        need_keys = [k for k in self.sprav_holder.attr_config if k not in keys_not_used]
        for row in rows:
            for n in range(row.n):
                f22_key = row.get_el_by_fkey_n('f22', n)
                nusn = row.nusname[n]
                if nusn == 1:  # группировка по User_N
                    group_key = row.get_el_by_fkey_n('usern', n)
                else:  # группировка по SOATo
                    group_key = row.soato
                row_params = row.simplify_to_d(n, need_keys)
                # NEWUSNAME_%(N)d, Area_%(N)d, LANDCODE, MELIOCODE, ServType08, State_1
                try:
                    f22_dict[f22_key][group_key]['r_params'].append(row_params)
                except KeyError:
                    if f22_key not in f22_dict:
                        f22_dict[f22_key] = {}
                    soato_inf = self.get_cc_name(row.soato)
                    main_inf = self.usersInfo[group_key] if nusn == 1 else self.soatoInfo[group_key]
                    dop_inf = row.dopname[n] if row.dopname[n] else ''

                    group_as_sad = False
                    if f22_key == '07':
                        slnad = row.get_el_by_fkey('slnad')
                        usern_sad = row.get_el_by_fkey('usern_sad')
                        if slnad == 2 and not usern_sad:
                            group_as_sad = True

                    f22_dict[f22_key][group_key] = {
                        'r_params': [row_params, ],
                        'main_inf': '%s %s' % (dop_inf, main_inf),
                        'soato_inf': soato_inf,
                        'soato_code': row.soato,
                        'nusname': nusn,
                        'full_inf': self.get_full_e_name(main_inf, dop_inf, soato_inf, nusn),
                        'group_as_sad': group_as_sad
                    }
        return f22_dict

    @staticmethod
    def get_full_e_name(main_name, dop_name, ss_name, nusn_code):
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
        self.exp_tree = tree_dict

    def make_comb_data(self):
        comb_dicts = dict.fromkeys(list(self.datadict.keys()))
        for key1 in comb_dicts:
            comb_dicts[key1] = dict.fromkeys(self.datadict[key1].keys())
            for key2 in comb_dicts[key1]:
                comb_li = self.datadict[key1][key2]
                comb_dicts[key1][key2] = DataComb(
                    comb_li['r_params'],
                    comb_li['full_inf'],
                    comb_li['main_inf'],
                    comb_li['soato_inf'],
                    comb_li['soato_code'],
                    comb_li['nusname'],
                    comb_li['group_as_sad'],
                )
        return comb_dicts

    def calc_all_exps_by_ss(self, round_setts):
        sv_exp = {}
        sv_texts = {}
        if self.exps_dict:
            for key1 in self.exps_dict:
                sv_exp[key1] = {}
                sv_texts[key1] = {}
                for key2 in self.exps_dict[key1]:
                    exp_obj = self.exps_dict[key1][key2]
                    sv_row = exp_obj.make_sv_row(self.sprav_holder)
                    if exp_obj.errors:
                        self.errors_occured[1] = exp_obj.errors
                        return {}

                    if exp_obj.group_as_sad:
                        soato_total_key = exp_obj.soato_code[:-3]
                        if soato_total_key in sv_exp[key1]:
                            sv_exp[key1][soato_total_key] = ExpBuilder.sum_dict_values(
                                sv_exp[key1][soato_total_key],
                                (sv_row,)
                            )
                        else:
                            sv_exp[key1][soato_total_key] = sv_row
                            title = self.cc_soato_d[soato_total_key] + ' Сад'
                            sv_texts[key1][soato_total_key] = '%s. Всего:' % title

                    elif exp_obj.nusname == 1:
                        sv_exp[key1][key2] = sv_row
                        sv_texts[key1][key2] = self.__get_sv_row_text(key2, exp_obj.obj_name)
                        if exp_obj.errors:
                            self.errors_occured[1] = exp_obj.errors
                            return {}
                    else:
                        soato_total_key = exp_obj.soato_code[:-3]
                        if soato_total_key in sv_exp[key1]:
                            sv_exp[key1][soato_total_key] = ExpBuilder.sum_dict_values(
                                sv_exp[key1][soato_total_key],
                                (sv_row,)
                            )
                        else:
                            sv_exp[key1][soato_total_key] = sv_row
                            sv_texts[key1][soato_total_key] = '%s. Всего:' % self.cc_soato_d[soato_total_key]

            self.__add_total_rows(sv_exp)
            if self.shape_area_sum:
                sv_exp['sh_init_sum'] = self.__make_init_shape_row()

            round_setts.accuracy = round_setts.a_sv_accuracy
            self.__round_sv(sv_exp, round_setts)
            sv_exp['texts'] = sv_texts
            return sv_exp
        else:
            self.errors_occured[0] = 'No data'
            return sv_exp

    def calc_all_exps_by_np(self, round_setts):
        sv_exp = {}
        sv_texts = {}
        if self.exps_dict:
            for key1 in self.exps_dict:
                sv_exp[key1] = {}
                sv_texts[key1] = {}
                for key2 in self.exps_dict[key1]:
                    exp_obj = self.exps_dict[key1][key2]
                    sv_row = exp_obj.make_sv_row(self.sprav_holder)
                    if exp_obj.errors:
                        self.errors_occured[1] = exp_obj.errors
                        return {}

                    if exp_obj.group_as_sad:
                        soato_total_key = exp_obj.soato_code[:-3]
                        soato_code = exp_obj.soato_code
                        if soato_code in sv_exp[key1]:
                            sv_exp[key1][soato_code] = ExpBuilder.sum_dict_values(sv_exp[key1][soato_code], (sv_row,))
                        else:
                            sv_exp[key1][soato_code] = sv_row
                            sv_texts[key1][soato_code] = exp_obj.soato_inf + 'Сад.'

                        if soato_total_key in sv_exp[key1]:
                            sv_exp[key1][soato_total_key] = ExpBuilder.sum_dict_values(sv_exp[key1][soato_total_key],
                                                                                       (sv_row,))
                        else:
                            sv_exp[key1][soato_total_key] = sv_row
                            sv_texts[key1][soato_total_key] = '%s. Всего:' % self.cc_soato_d[soato_total_key]

                    elif exp_obj.nusname == 1:
                        sv_exp[key1][key2] = sv_row
                        sv_texts[key1][key2] = self.__get_sv_row_text(key2, exp_obj.obj_name)
                    else:
                        soato_total_key = exp_obj.soato_code[:-3]
                        soato_code = exp_obj.soato_code
                        if soato_code in sv_exp[key1]:
                            sv_exp[key1][soato_code] = ExpBuilder.sum_dict_values(sv_exp[key1][soato_code], (sv_row,))
                        else:
                            sv_exp[key1][soato_code] = sv_row
                            sv_texts[key1][soato_code] = self.__get_sv_row_text(key2, exp_obj.obj_name)

                        if soato_total_key in sv_exp[key1]:
                            sv_exp[key1][soato_total_key] = ExpBuilder.sum_dict_values(sv_exp[key1][soato_total_key],
                                                                                       (sv_row,))
                        else:
                            sv_exp[key1][soato_total_key] = sv_row
                            sv_texts[key1][soato_total_key] = '%s. Всего:' % self.cc_soato_d[soato_total_key]

            self.__add_total_rows(sv_exp, sv_texts)
            if self.shape_area_sum:
                sv_exp['sh_init_sum'] = self.__make_init_shape_row()

            round_setts.accuracy = round_setts.a_sv_accuracy
            self.__round_sv(sv_exp, round_setts)
            sv_exp['texts'] = sv_texts
            return sv_exp
        else:
            self.errors_occured[0] = 'No data'
            return sv_exp

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
                        # TODO: Work with exception (get message from exp_obj)
                        self.errors_occured[1] = exp_obj.errors
                        return {}
            self.__add_total_rows(sv_exp, sv_texts)
            sv_exp['sh_sum'] = self.__make_shape_row()
            if self.shape_area_sum:
                sv_exp['sh_init_sum'] = self.__make_init_shape_row()

            round_setts.accuracy = round_setts.a_sv_accuracy
            self.__round_sv(sv_exp, round_setts)
            sv_exp['texts'] = sv_texts
            return sv_exp
        else:
            self.errors_occured[0] = 'No data'
            return sv_exp

    def __push_to_sv_matrix(self, f22_desc, row_name, shapes, skip_num=False, for_xls=True):
        row = []
        if for_xls:
            if skip_num:
                row = ['', ]
            else:
                row = [self.row_counter, ]
                self.row_counter += 1
        row.extend([f22_desc, row_name])
        row.extend(shapes)
        self.sv_matrix.append(row)

    def prepare_sv_matrix(self, sv_dict, for_xls=True):
        """
        Caution! The first row contains field Names in order to export!
        :return : tuple, matrix to export
        """
        """ТУТ ВРОДЕ ГЕНЕРИРУЕТЯС МАТРИЦА"""
        f_orders = self.sprav_holder.str_orders['sv_f']
        r_order_base = sv_dict['texts']
        self.sv_matrix = []
        self.row_counter = 1
        self.__push_to_sv_matrix('F22_id', 'description', f_orders, skip_num=True, for_xls=for_xls)

        for f22_key in sorted(list(r_order_base.keys())):
            if for_xls:
                self.__push_to_sv_matrix(
                    '',
                    '',
                    ['', ] * (len(f_orders) + 2),
                    skip_num=True,
                    for_xls=for_xls,
                )
                self.__push_to_sv_matrix(
                    f22_key,
                    self.sprav_holder.f22_notes[f22_key],
                    ['', ] * len(f_orders),
                    skip_num=True,
                    for_xls=for_xls,
                )
            n = 1

            for row_key, row_name in self.get_ordered_by_keys_items(r_order_base[f22_key]):
                digits = map(lambda x: sv_dict[f22_key][row_key][x]['val'], f_orders)
                self.__push_to_sv_matrix('%s.%d' % (f22_key, n), row_name, digits, skip_num=False, for_xls=for_xls)
                n += 1
            digits = map(lambda x: sv_dict[f22_key]['total'][x]['val'], f_orders)
            self.__push_to_sv_matrix(f22_key + '*', 'Итого:', digits, skip_num=False, for_xls=for_xls)

        if 'total' in sv_dict:
            # добавление итоговой строки total
            digits = map(lambda x: sv_dict['total'][x]['val'], f_orders)
            self.__push_to_sv_matrix('**', 'Всего:', digits, skip_num=False, for_xls=for_xls)
        if 'sh_sum' in sv_dict:
            # добовление информационной строки Shape_area
            digits = map(lambda x: sv_dict['sh_sum'][x]['val'], f_orders)
            self.__push_to_sv_matrix('***', 'Shape_Area (для сравнения):', digits, skip_num=False, for_xls=for_xls)
        if 'sh_init_sum' in sv_dict:
            # добовление информационной строки Shape_area
            digits = map(lambda x: sv_dict['sh_init_sum'][x]['val'], f_orders)
            self.__push_to_sv_matrix('***', 'Фактическая сумма Shape_Area (для сравнения):', digits,
                                     skip_num=False, for_xls=for_xls)
        return self.sv_matrix

    @staticmethod
    def get_ordered_by_keys_items(target):
        return sorted(target.items(), key=lambda x: x[1])

    @staticmethod
    def __round_sv(sv_nested_di, round_setts):
        """
        use to transform sv_explication_dict. Depends of round settings.
        instead of digits it will paste dicts with value key and tail key
        !Caution! It changes the input object!
        """
        for key1 in sv_nested_di:
            if key1 in ('total', 'sh_sum', 'sh_init_sum'):
                sv_nested_di[key1] = ExpBuilder.round_and_modify(sv_nested_di[key1], round_setts.__dict__)
            else:
                for key2, data_d in sv_nested_di[key1].items():
                    sv_nested_di[key1][key2] = ExpBuilder.round_and_modify(data_d, round_setts.__dict__)

    def __get_sv_row_text(self, soato_key, obj_text):
        cc_kod = str(soato_key)[:-3]
        try:
            return '%s %s' % (self.cc_soato_d[cc_kod], obj_text)
        except KeyError:
            return obj_text

    def __make_shape_row(self):
        conv_rows = []
        for k1 in self.datadict:
            for k2 in self.datadict[k1]:
                conv_rows.extend(self.datadict[k1][k2]['r_params'])
        shape_comb = DataComb(conv_rows, 'Shape_sum:', '', '', None, 0)
        return shape_comb.make_sv_row(self.sprav_holder)

    def __make_init_shape_row(self):

        tmpl = dict.fromkeys(self.sprav_holder.str_orders['sv_f'], 0)
        tmpl['total'] = self.shape_area_sum
        return tmpl

    def __add_total_rows(self, sv_e, sv_t=None):
        """
        Caution! this method changes enter parameter sv_e
        :param sv_e: Sv explication data only
        :return: modified sv_e with total keys
        """
        tmpl = dict.fromkeys(self.sprav_holder.str_orders['sv_f'], 0)
        total_all = tmpl.copy()
        for key1 in sv_e:
            total_f22 = tmpl.copy()
            for key2 in sv_e[key1]:
                if not sv_t or 'Всего:' not in sv_t[key1][key2]:
                    total_f22 = ExpBuilder.sum_dict_values(total_f22, (sv_e[key1][key2],))
            sv_e[key1]['total'] = total_f22
            total_all = ExpBuilder.sum_dict_values(total_all, (total_f22,))
        sv_e['total'] = total_all
