from .buildUtils import ExpBuilder


class ExpF22Maker:
    def __init__(self, ctr_rows, sprav_holder):
        self.r_structure = sprav_holder.expf22_r_str
        self.f_structure = sprav_holder.expf22_f_str
        self.filtered_rows = self.filter_by_r_str(ctr_rows, list(sprav_holder.attr_config.keys()))

    def filter_by_r_str(self, ct_rows, aliases):
        """
            return fbrow_dict: f22(key_of_row_in_formB) -> [(area, LANDCODE, MELIOCODE, ServType08, State_1),...]
        """
        fbrow_dict = {'by_SHAPE': []}
        for key in self.r_structure:
            fbrow_dict[key] = []
        print(f'fbrow_dict = {fbrow_dict}')
        keys_not_used = ('ctr_structure', 'id', 'usern_sad', 'part', 'usern')
        need_keys = [k for k in aliases if k not in keys_not_used]
        r_str = self.r_structure.items()
        print(f'need_keys = {need_keys}')
        print(f'r_str = {r_str}')

        for row in ct_rows:
            for n in range(row.n):
                need_params = row.simplify_to_d(n, need_keys)
                print(f'need_params = {need_params}')
                fbrow_dict['by_SHAPE'].append(need_params)
                for key, fb_row in r_str:
                    try:
                        if row.check_filter_match(n, fb_row['sort_filter']):
                            fbrow_dict[key].append(need_params)
                    except KeyError:
                        fb_row['sort_filter'] = {}

        self.r_structure['by_SHAPE'] = {'r_name': 'Всего:', 'sort_filter': {}}
        return fbrow_dict

    def make_fbr_params(self, rows):
        f_str = self.f_structure
        r_params_d = dict.fromkeys(f_str.keys(), 0)
        if rows:
            ready_fields = []
            for f_key, f_val in f_str.items():
                if 'alias_codes' in f_val:
                    s = 0
                    for row in rows:
                        passed = True
                        for als, cds in f_val['alias_codes'].items():
                            if row[als] not in cds:
                                passed = False
                                break
                        if passed:
                            s += row['area']
                    r_params_d[f_key] = s
                if not f_val['sum_f']:
                    ready_fields.append(f_key)
            while len(f_str) > len(ready_fields):
                ready_f_count = len(ready_fields)
                for f, value in f_str.items():
                    if f in ready_fields:
                        continue
                    add_fields = value['sum_f']
                    check_li = ready_fields[:]
                    check_li.extend(add_fields)
                    if len(ready_fields) == len(set(check_li)):
                        # проверка входят ли все элементы value['sum_f'] в число уже сформированных полей
                        for a_f in add_fields:
                            r_params_d[f] += r_params_d[a_f]
                        ready_fields.append(f)
                if len(ready_fields) == ready_f_count:
                    break
        return r_params_d

    def create_exp_dict(self, round_setts):
        exp_dict = self.filtered_rows
        count_ready = 0
        ready_key = 'ready'
        for key in exp_dict:
            exp_dict[key] = self.make_fbr_params(exp_dict[key])
            if 'conds' in self.r_structure[key]:
                exp_dict[key][ready_key] = False
            else:
                count_ready += 1
                exp_dict[key][ready_key] = True

        while count_ready < len(exp_dict):
            cr_old = count_ready
            for key in exp_dict:
                r_spr = self.r_structure[key]
                if not exp_dict[key][ready_key]:
                    new_row = exp_dict[key].copy()
                    row_ready = True
                    for cond_k, cond_v in r_spr['conds'].items():
                        if cond_k in ('add', 'sub'):
                            is_add = True if cond_k == 'add' else False
                            if self.all_ready(exp_dict, cond_v):
                                add_rows = map(lambda x: exp_dict[x], cond_v)
                                new_row = ExpBuilder.sum_dict_values(new_row, add_rows, add_ok=is_add)
                            else:
                                row_ready = False
                                break
                        elif cond_k == 'eq_f':
                            for eq_i in cond_v:
                                take_r = eq_i['take_r']
                                if exp_dict[take_r][ready_key]:
                                    take_f = eq_i['take_f']
                                    upd_f = eq_i['upd_f']
                                    op = eq_i['op']
                                    if op == '=':
                                        new_row[upd_f] = exp_dict[take_r][take_f]
                                    elif op == '-':
                                        new_row[upd_f] -= exp_dict[take_r][take_f]
                                    elif op == '+':
                                        new_row[upd_f] += exp_dict[take_r][take_f]
                                else:
                                    row_ready = False
                                    break
                    if row_ready:
                        exp_dict[key] = new_row
                        exp_dict[key][ready_key] = True
                        count_ready += 1
            if cr_old == count_ready:
                break
        for key in exp_dict:
            exp_dict[key].pop(ready_key)
        round_setts.accuracy = round_setts.b_accuracy
        self.__round_fb(exp_dict, round_setts)
        return exp_dict

    @staticmethod
    def prepare_matrix(b_dict, sprav_holder):
        """
        Caution! The first row contains field Names in order to export!
        :return : tuple, matrix to export
        """
        f_orders = sprav_holder.str_orders['b_f']
        r_orders = sprav_holder.str_orders['b_r']
        r_orders = r_orders[:41]  # отсекаем строки с 25 по 41, они заполняются в экселе автоматически
        matr = []
        print(f_orders)
        print(r_orders)

        def push_to_matr(remain):
            row = []
            row.extend(remain)
            matr.append(row)

        print(matr)
        push_to_matr(f_orders)  # ('F22', 'description', f_orders)
        for r_key in r_orders:
            # print(r_key)
            digits = map(lambda x: b_dict[r_key][x]['val'], f_orders)
            push_to_matr(digits)  # (r_key, sprav_holder.expf22_r_str[r_key]['r_name'], digits)

        # digits = map(lambda x: b_dict['by_SHAPE'][x]['val'], f_orders)
        # push_to_matr( digits)#push_to_matr('Total', 'By_Shape', digits)
        print('****')
        print(matr)
        return matr

    @staticmethod
    def prepare_matrix_total(b_dict, sprav_holder):
        """
        Caution! The first row contains field Names in order to export!
        :return : tuple, matrix to export
        """
        f_orders = sprav_holder.str_orders['b_f']
        r_orders = sprav_holder.str_orders['b_r']
        matr_total = []
        print(f_orders)

        def push_to_matr_total(remain):
            row = []
            row.extend(remain)
            matr_total.append(row)

        digits = map(lambda x: b_dict['by_SHAPE'][x]['val'], f_orders)
        push_to_matr_total(digits)  # push_to_matr('Total', 'By_Shape', digits)
        print(matr_total)
        return matr_total

    @staticmethod
    def all_ready(e_dict, keys, ready_key='ready'):
        for key in keys:
            try:
                if not e_dict[key][ready_key] == True:
                    return False
            except KeyError:
                return False
        return True

    @staticmethod
    def __round_fb(fb_dict, round_setts):
        round_setts = round_setts.copy() if isinstance(round_setts, dict) else round_setts.__dict__
        round_setts['show_small'] = False
        for key1, data_d in fb_dict.items():
            fb_dict[key1] = ExpBuilder.round_and_modify(data_d, round_setts)
