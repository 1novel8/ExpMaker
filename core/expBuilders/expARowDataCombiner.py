from .buildUtils import ExpBuilder


class RowDataCombiner(object):
    def __init__(self, data_li, full_inf, main_inf, soato_inf, soato_code, nusname, group_as_sad=False):
        self.soato_inf = soato_inf
        self.soato_code = soato_code
        self.nusname = nusname
        self.__init_data = data_li
        self.expl_data = {}
        self.obj_name = main_inf
        self.full_obj_name = full_inf
        self.group_as_sad = group_as_sad
        self.errors = {}

    def add_data(self, sprav_holder):
        """
        :param sprav_holder: sprav_holder instance
        Makes json-style simple explication a in case that it's not counted yet
        """
        if self.expl_data:
            # Data already added
            pass
        else:
            expl_data = dict.fromkeys(sprav_holder.str_orders['a_r'])
            for r_key in expl_data:
                if r_key == 'total':
                    filtered_rows = self.__init_data
                else:
                    r_codes = sprav_holder.expa_r_str[r_key]['codes']
                    s_alias = sprav_holder.expa_r_str[r_key]['sort_alias']
                    filtered_rows = [row for row in self.__init_data if row[s_alias] in r_codes]
                try:
                    expl_data[r_key] = RowDataCombiner.sum_by_lc(filtered_rows, sprav_holder.expa_f_str)
                except (IndexError, TypeError, AttributeError) as e:
                    self.errors[r_key] = e.message
            self.expl_data = expl_data
            self.__init_data = None

    def round_expl_data(self, round_setts):
        rounded_e_data = {}
        if self.expl_data:
            round_setts.accuracy = round_setts.a_s_accuracy
            for row in self.expl_data:
                rounded_e_data[row] = ExpBuilder.round_and_modify(self.expl_data[row], round_setts.__dict__)
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

    @staticmethod
    def prepare_out_matrix(s_dict, sprav_holder, for_xls=True):
        """
        Caution! The first row contains field Names in order to export!
        :return : list, matrix to export
        """
        f_at_order = sprav_holder.str_orders['a_f']
        matr = []
        if not for_xls:
            matr.append(f_at_order)
        for row in sprav_holder.str_orders['a_r']:
            digits = list(map(lambda x: s_dict[row][x]['val'], f_at_order))
            matr.append(digits)
        return matr

    @staticmethod
    def sum_by_lc(rows, f_str):
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
                    if f_key in f_values:
                        continue
                    sum_f_li = f_str[f_key]['sum_f']
                    f_sum = RowDataCombiner.try_get_sum(sum_f_li, f_values)
                    if f_sum == -1:
                        continue
                    else:
                        f_values[f_key] = f_sum
                if f_len == len(f_values):
                    raise Exception('Возникла взаимоблокирующая ситуация. '
                                    'Справочник структуры полей содержит некорректные данные в ')

            return f_values
        return dict.fromkeys(f_str, 0)

    @staticmethod
    def try_get_sum(key_li, sum_di):
        """
        If sum_di has all keys from key_li, function returns this sum else returns False
        """
        r_sum = 0
        for f_key in key_li:
            try:
                r_sum += sum_di[f_key]
            except KeyError:
                return -1
        return r_sum
