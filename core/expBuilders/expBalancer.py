import math
import traceback


class ExpBalancer:
    b_counter = 0
    accuracy = None
    current_exp = None
    field_settings = None

    @staticmethod
    def check_zero(value, is_positive):
        if is_positive:
            return value > 0
        else:
            return value < 0

    @staticmethod
    def _assert_equal(parent_cell, child_cells):
        """
        :param parent_cell: test parent cell
        :param child_cells: test child cells
        @:return boolean
        """
        is_equal = True

        if not parent_cell['fixed']:
            is_equal = False
        for ch_cell in child_cells:
            if not ch_cell['fixed']:
                is_equal = False
                break
        if not is_equal:
            return is_equal

        child_sum = 0
        parent_val = parent_cell['val'] + parent_cell['bonus']
        for cell in child_cells:
            child_sum += cell['val'] + cell['bonus']
        if parent_val != child_sum:
            is_equal = False
        return is_equal

    @staticmethod
    def get_inds_with_false_key(cells, key):
        inds_false_key = []
        for ind in range(len(cells)):
            if cells[ind][key]:
                inds_false_key.append(ind)

        return inds_false_key

    @staticmethod
    def get_inds_with_false_key_plus_minus(cells, is_positive):
        inds_false_key = []
        if is_positive:
            key = 'plus'
        else:
            key = 'minus'

        for ind in range(len(cells)):
            if cells[ind][key]:
                inds_false_key.append(ind)

        return inds_false_key

    def _get_bonus_cell_ind(self, cells, is_positive, possible_indexes=None):
        if len(cells) == 1:
            raise Exception("Wrong input data format")
        if isinstance(possible_indexes, (list, tuple)):
            # self calling
            possible_bonus_items = possible_indexes
            self.b_counter += 1
            if self.b_counter > 10:
                raise Exception('Balancing caused recursive loop')
                # protection from recursive calling
        else:
            # calling first time
            self.b_counter = 0
            possible_bonus_items = list(range(len(cells)))
            fixed_items = self.get_inds_with_false_key(cells, 'fixed')
            plus_minus_items = self.get_inds_with_false_key_plus_minus(cells, is_positive)

            for i in range(len(cells)):
                if i in fixed_items:
                    possible_bonus_items.remove(i)
                    continue
                if i in plus_minus_items:
                    possible_bonus_items.remove(i)
                    continue
                if not is_positive and cells[i]['val'] < 1:
                    possible_bonus_items.remove(i)
                    continue

        if len(possible_bonus_items) < 1:
            # Counts only by max value
            return self._run_bonus_competition(cells, range(len(cells)), is_positive, 'tail')

        winner_i = self._run_bonus_competition(cells, possible_bonus_items, is_positive)
        winner_cell = cells[winner_i]
        # min_bonus = 10**-int(self.accuracy) #10 ** self.accuracy
        if winner_cell['fixed']:
            print('something went wrong. Winner cell already fixed')
        # small values < 0 could be and should be in tail!
        # zero_val_winned = winner_cell['val'] > 1 * min_bonus

        '''if zero_val_winned:
            if is_positive:
                return winner_i
            else:
                possible_bonus_items.remove(winner_i)
                return self._get_bonus_cell_ind(cells, is_positive, possible_bonus_items)
        else:'''
        return winner_i

    @staticmethod
    def is_current_wins(last_winner, current, is_positive):
        return last_winner > current if is_positive else last_winner < current

    def _run_bonus_competition(self, cells, cell_ind_array, is_positive, competition_by='tail'):
        """
        :param cells:
        :param cell_ind_array:
        :param is_positive: What value is searching for
        :param competition_by:
        :return: index of winner cell
        """
        winner_tail_i = cell_ind_array[0]

        for i in cell_ind_array[1:]:
            if is_positive:
                if cells[winner_tail_i][competition_by] > 0 or cells[winner_tail_i]['minus'] is True:
                    if cells[i][competition_by] > 0 or cells[i]['minus'] is True:
                        if cells[winner_tail_i][competition_by] < cells[i][competition_by]:
                            winner_tail_i = i
                        else:
                            if cells[winner_tail_i][competition_by] == cells[i][competition_by]:
                                if cells[winner_tail_i]['val'] < cells[i]['val']:
                                    winner_tail_i = i
                else:
                    winner_tail_i = i
            else:
                if cells[winner_tail_i][competition_by] < 0 or cells[winner_tail_i]['plus'] is True:
                    if cells[i][competition_by] < 0 or cells[i]['plus'] is True:
                        if abs(cells[winner_tail_i][competition_by]) < abs(cells[i][competition_by]):
                            if cells[i]['val'] != 0:
                                winner_tail_i = i
                        else:
                            if abs(cells[winner_tail_i][competition_by]) == abs(cells[i][competition_by]):
                                if cells[winner_tail_i]['val'] < cells[i]['val']:
                                    if cells[i]['val'] != 0:
                                        winner_tail_i = i
                else:
                    if cells[i]['val'] != 0:
                        winner_tail_i = i
        return winner_tail_i

    @staticmethod
    def _run_bonus_competition_max_value(cells):
        cell_ind_array = range(len(cells))
        winner_tail_i = cell_ind_array[0]
        for i in cell_ind_array[1:]:
            if cells[winner_tail_i]['val'] < cells[i]['val']:
                winner_tail_i = i
        return winner_tail_i

    # находим ячейку, куда записать бонус(невязку)
    def _split_bonus_each_row(self, p_cell, cells, base_r, fld_cells):
        bonus = p_cell['bonus']
        bonus_count = math.fabs(bonus * 10 ** self.accuracy)
        count_cells = len(cells)
        if bonus_count:
            print(bonus_count, bonus)
        if bonus_count == 0:
            return
        bonus /= bonus_count
        bonus = round(bonus, int(self.accuracy))
        if count_cells < bonus_count:
            bonus_count = count_cells
        for bonusInd in range(int(bonus_count)):
            if len(cells) == 1:
                bonus_cell_key = 0
            else:
                bonus_cell_key = self._get_bonus_cell_ind(cells, bonus > 0, self.accuracy)
            try:
                cells[bonus_cell_key]['bonus'] += bonus
                p_cell['bonus'] -= bonus
                # запись бонуса в итоговую строку данного столбца
                self.current_exp[base_r][fld_cells[bonus_cell_key]]['bonus'] -= bonus
                if bonus > 0:
                    self.current_exp[base_r][fld_cells[bonus_cell_key]]['plus'] = True
                    cells[bonus_cell_key]['plus'] = True
                else:
                    self.current_exp[base_r][fld_cells[bonus_cell_key]]['minus'] = True
                    cells[bonus_cell_key]['minus'] = True

            except KeyError:
                print('Something went wrong while Balancing')
                cells[bonus_cell_key]['bonus'] = bonus
                raise Exception('Something went wrong while Balancing split bonus each row')

    def _split_bonus_each_field(self, p_cell, cells, base_f, base_r, r_cells, alt_fields=None):
        if alt_fields is None:
            alt_fields = []
        bonus = p_cell['bonus']
        bonus_count = math.fabs(bonus * 10 ** self.accuracy)
        count_cells = len(cells)
        if bonus_count:
            print(bonus_count, bonus)
        bonus /= bonus_count
        if count_cells < bonus_count:
            bonus_count = count_cells
        for bonusInd in range(int(bonus_count)):
            if len(cells) == 1:
                bonus_cell_key = 0
            else:
                bonus_cell_key = self._get_bonus_cell_ind(cells, bonus > 0, self.accuracy)
            try:
                cells[bonus_cell_key]['bonus'] += bonus
                p_cell['bonus'] -= bonus
                #  запить бонуса в итоговую строку данного столбца
                self.current_exp[r_cells[bonus_cell_key]][base_f]['bonus'] -= bonus
                if bonus > 0:
                    self.current_exp[r_cells[bonus_cell_key]][base_f]['plus'] = True
                    cells[bonus_cell_key]['plus'] = True
                else:
                    self.current_exp[r_cells[bonus_cell_key]][base_f]['minus'] = True
                    cells[bonus_cell_key]['minus'] = True
                #  запись бонуса в эту же строку  столбца с противоположным остатком
                if len(alt_fields) > 0:
                    alt_bonus = self.current_exp[base_r][alt_fields[bonus_cell_key]]['bonus']
                    if alt_bonus == 0:
                        if bonus < 0:
                            alt_bonus = 1
                        else:
                            alt_bonus = -1
                    alt_bonus_count = math.fabs(alt_bonus * 10 ** self.accuracy)
                    alt_bonus /= alt_bonus_count
                    self.current_exp[r_cells[bonus_cell_key]][alt_fields[bonus_cell_key]]['bonus'] += alt_bonus
                    self.current_exp[base_r][alt_fields[bonus_cell_key]]['bonus'] -= alt_bonus
                    self.current_exp[r_cells[bonus_cell_key]][base_f]['bonus'] -= alt_bonus
                    if bonus > 0:
                        self.current_exp[r_cells[bonus_cell_key]][alt_fields[bonus_cell_key]]['plus'] = True
                    else:
                        self.current_exp[r_cells[bonus_cell_key]][alt_fields[bonus_cell_key]]['minus'] = True

            except KeyError:
                print('Something went wrong while Balancing')
                cells[bonus_cell_key]['bonus'] = bonus
                # raise Exception('Something went wrong while Balancing')

    def _split_bonus(self, bonus, cells):
        bonus_count = math.fabs(bonus * 10 ** self.accuracy)
        if bonus_count:
            print(bonus_count, bonus)
        bonus /= bonus_count
        bonus = round(bonus, int(self.accuracy))
        for bonusInd in range(int(bonus_count)):
            if len(cells) == 1:
                bonus_cell_key = 0
            else:
                bonus_cell_key = self._get_bonus_cell_ind(cells, bonus > 0, self.accuracy)
            try:
                cells[bonus_cell_key]['bonus'] += bonus
                cells[bonus_cell_key]['bonus'] = round(cells[bonus_cell_key]['bonus'], self.accuracy)
                if bonus > 0:
                    cells[bonus_cell_key]['plus'] = True
                else:
                    cells[bonus_cell_key]['minus'] = True

            except KeyError:
                print('Something went wrong while Balancing')
                cells[bonus_cell_key]['bonus'] = round(bonus, self.accuracy)
                # TODO: Uncomment here after debugging
                # raise Exception('Something went wrong while Balancing')

    def _make_equal_bonus_fix(self, parent_cell, child_cells, level):
        # сравниваем итоговое значение с суммой входящих ячеек и находим бонус, который записываем в ячейку и фиксируем
        # значения, они уже уравнены
        """
        Caution. This method changes the input objects
        it doesnt change the keys of input parameters,
        just adds bonuses which guarantees that val sums with bonuses are equal
        :param parent_cell: parent cell
        :param child_cells: array of cells
        :return:
        """
        accuracy = int(self.accuracy)
        child_sum = 0
        parent_val = round(parent_cell['val'] + parent_cell['bonus'], accuracy)
        for cell in child_cells:
            child_sum += cell['val'] + cell['bonus']

        child_sum = round(child_sum, accuracy)
        if parent_cell['fixed']:
            if level == 1 or level == 2:
                total_bonus = round(parent_val - child_sum, accuracy)
                if total_bonus != 0:
                    self._split_bonus(total_bonus, child_cells)
                for cll in child_cells:
                    cll['fixed'] = True
            elif level == 3:
                total_bonus = round(parent_val - child_sum, accuracy)
                if total_bonus < 0:
                    self._split_bonus(total_bonus, child_cells)
                for cll in child_cells:
                    cll['fixed'] = True
            else:
                for cll in child_cells:
                    if parent_val < cll['val']:
                        total_bonus = round(parent_val - cll['val'], accuracy)
                        cll['bonus'] = cll['bonus'] + total_bonus
                    cll['fixed'] = True
        else:
            parent_cell['bonus'] = round(child_sum - parent_cell['val'], accuracy)
            parent_cell['fixed'] = True

    def _make_equal_bonus_fix_bonus(self, parent_cell, child_cells, level, bonus_fields_plus, bonus_fields_minus):
        # сравниваем итоговое значение с суммой входящих ячеек и находим бонус, который записываем в ячейку и фиксируем
        # значения, они уже уравнены
        """
        Caution. This method changes the input objects
        it doesnt change the keys of input parameters,
        just adds bonuses which guarantees that val sums with bonuses are equal
        :param parent_cell: parent cell
        :param child_cells: array of cells
        :return:
        """
        accuracy = int(self.accuracy)
        child_sum = 0
        parent_val = round(parent_cell['val'] + parent_cell['bonus'], accuracy)
        for cell in child_cells:
            child_sum += cell['val'] + cell['bonus']
        child_sum = round(child_sum, accuracy)

        if parent_cell['fixed']:
            if level == 1 or level == 2:
                total_bonus = round(parent_val - child_sum, accuracy)

                if total_bonus != 0:
                    self._split_bonus(total_bonus, child_cells)
                for cll in child_cells:
                    cll['fixed'] = True
            elif level == 3:
                total_bonus = round(parent_val - child_sum, accuracy)
                if total_bonus < 0:
                    self._split_bonus(total_bonus, child_cells)
                for cll in child_cells:
                    cll['fixed'] = True
            else:
                for cll in child_cells:
                    if parent_val < cll['val']:
                        total_bonus = round(parent_val - cll['val'], accuracy)
                        cll['bonus'] = cll['bonus'] + total_bonus
                    cll['fixed'] = True
        else:
            parent_cell['bonus'] = round(child_sum - parent_cell['val'], accuracy)
            parent_cell['fixed'] = True

    def _make_equal_bonus_not_fix(self, parent_cell, child_cells, level):

        """
        Caution. This method changes the input objects
        it doesnt change the keys of input parameters,
        just adds bonuses which guarantees that val sums with bonuses are equal
        :param parent_cell: parent cell
        :param child_cells: array of cells
        :return:
        """
        accuracy = int(self.accuracy)
        child_sum = 0
        parent_val = parent_cell['val'] + parent_cell['bonus']
        for cell in child_cells:
            child_sum += cell['val'] + cell['bonus']

        if parent_cell['fixed']:
            if level == 1 or level == 2:
                total_bonus = round(parent_val - child_sum, accuracy)
                if total_bonus != 0:
                    self._split_bonus(total_bonus, child_cells)
            elif level == 3:
                total_bonus = round(parent_val - child_sum, accuracy)
                if total_bonus < 0:
                    self._split_bonus(total_bonus, child_cells)
            else:
                for cll in child_cells:
                    if parent_val < cll['val']:
                        total_bonus = round(parent_val - cll['val'], accuracy)
                        cll['bonus'] = cll['bonus'] + total_bonus
        else:
            parent_cell['bonus'] = round(child_sum - parent_cell['val'], accuracy)
            parent_cell['fixed'] = True

    def _make_equal_bonus_not_fix_25(self, parent_cell, child_cells, level):

        """
        Caution. This method changes the input objects
        it doesnt change the keys of input parameters,
        just adds bonuses which guarantees that val sums with bonuses are equal
        :param parent_cell: parent cell
        :param child_cells: array of cells
        :return:
        """
        accuracy = int(self.accuracy)

        child_sum = 0
        parent_val = parent_cell['val'] + parent_cell['bonus']
        for cell in child_cells:
            child_sum += cell['val'] + cell['bonus']

        if level == 1 or level == 2:
            total_bonus = round(parent_val - child_sum, accuracy)
            parent_cell['bonus'] += total_bonus
            parent_cell['bonus'] = round(parent_cell['bonus'], accuracy)
        elif level == 3:
            total_bonus = round(parent_val - child_sum, accuracy)
            if total_bonus < 0:
                parent_cell['bonus'] += total_bonus
                parent_cell['bonus'] = round(parent_cell['bonus'], accuracy)
        else:
            for cll in child_cells:
                if parent_val < cll['val']:
                    total_bonus = round(parent_val - cll['val'], accuracy)
                    parent_cell['bonus'] += total_bonus
                    parent_cell['bonus'] = round(parent_cell['bonus'], accuracy)

    def _make_equal_bonus_not_fix_Total(self, parent_cell, child_cells, level):

        """
        Caution. This method changes the input objects
        it doesnt change the keys of input parameters,
        just adds bonuses which guarantees that val sums with bonuses are equal
        :param parent_cell: parent cell
        :param child_cells: array of cells
        :return:
        """
        accuracy = int(self.accuracy)

        child_sum = 0
        parent_val = parent_cell['val'] + parent_cell['bonus']
        for cell in child_cells:
            child_sum += cell['val'] + cell['bonus']

        if level == 1 or level == 2:
            total_bonus = round(parent_val - child_sum, accuracy)
            parent_cell['bonus'] -= total_bonus
        elif level == 3:
            total_bonus = round(parent_val - child_sum, accuracy)
            if total_bonus < 0:
                parent_cell['bonus'] -= total_bonus
        else:
            for cll in child_cells:
                if parent_val < cll['val']:
                    total_bonus = round(parent_val - cll['val'], accuracy)
                    parent_cell['bonus'] -= total_bonus

    def _search_tail_in_a_field(self, f_key, depend_rs, is_positive):
        winner_tail_cells = []
        if is_positive:
            for r_key in depend_rs:
                if not self.current_exp[r_key][f_key]['fixed']:
                    if (self.current_exp[r_key][f_key]['val'] + self.current_exp[r_key][f_key][
                        'bonus']) >= 1 * 10 ** -self.accuracy:
                        if self.current_exp[r_key][f_key]['tail'] < 0:
                            if not self.current_exp[r_key][f_key]['minus']:
                                winner_tail_cells.append(self.current_exp[r_key][f_key])
        else:
            for r_key in depend_rs:
                if not self.current_exp[r_key][f_key]['fixed']:
                    if self.current_exp[r_key][f_key]['tail'] > 0:
                        if not self.current_exp[r_key][f_key]['plus']:
                            winner_tail_cells.append(self.current_exp[r_key][f_key])

        if len(winner_tail_cells) >= 1:
            return True
        else:
            return False

    def _search_tail_in_a_field_max_value(self, f_key, depend_rs, is_positive):
        winner_tail_cells = []
        for r_key in depend_rs:
            if not self.current_exp[r_key][f_key]['fixed']:
                if not is_positive:
                    if (self.current_exp[r_key][f_key]['val'] + self.current_exp[r_key][f_key][
                        'bonus']) >= 1 * 10 ** -self.accuracy:
                        winner_tail_cells.append(self.current_exp[r_key][f_key])
                else:
                    winner_tail_cells.append(self.current_exp[r_key][f_key])

        if len(winner_tail_cells) >= 1:
            return True
        else:
            return False

    def _search_tail_in_a_row(self, r_key, fields_fs, is_positive):
        winner_tail_cells = []
        winner_fld = []
        if is_positive:
            for f_key in fields_fs:
                if not self.current_exp[r_key][f_key]['fixed']:
                    if (self.current_exp[r_key][f_key]['val'] +
                        self.current_exp[r_key][f_key]['bonus']) >= 1 * 10 ** -self.accuracy:
                        if self.current_exp[r_key][f_key]['tail'] < 0:
                            if not self.current_exp[r_key][f_key]['minus']:
                                winner_tail_cells.append(self.current_exp[r_key][f_key])
                                winner_fld.append(f_key)
        else:
            for f_key in fields_fs:
                if not self.current_exp[r_key][f_key]['fixed']:
                    if self.current_exp[r_key][f_key]['tail'] > 0:
                        if not self.current_exp[r_key][f_key]['plus']:
                            winner_tail_cells.append(self.current_exp[r_key][f_key])
                            winner_fld.append(f_key)

        if len(winner_tail_cells) == 1:
            winner_fld_id = winner_fld[0]
        elif len(winner_tail_cells) > 1:
            winner_id = self._run_bonus_competition(winner_tail_cells, range(len(winner_tail_cells)), is_positive,
                                                    'tail')
            winner_fld_id = winner_fld[winner_id]
        else:
            winner_fld_id = None

        return winner_fld_id

    # поиск одного значения в графе при невязке в тотал строке
    def _search_one_cell_in_a_field(self, base_r, base_f, depend_rs, bonus_field):
        not_empty_cells = []
        row_list = []
        p_cell = self.current_exp[base_r][bonus_field]
        for row_key in depend_rs:
            # if self.check_zero(p_cell['bonus'], p_cell['bonus'] > 0):
            if not self.current_exp[row_key][bonus_field]['fixed']:
                # if self.check_zero(self.current_exp[row_key][bonus_field]['tail'], p_cell['bonus'] > 0):
                not_empty_cells.append(self.current_exp[row_key][bonus_field])
                row_list.append(row_key)
        return not_empty_cells, row_list

    def _search_one_cell_in_a_row(self, base_r, base_f, depend_fs, r_key):
        not_empty_cells = []
        fld_list = []
        p_cell = self.current_exp[r_key][base_f]
        for f_key in depend_fs:
            # if self.check_zero(p_cell['bonus'], p_cell['bonus'] > 0):
            if not self.current_exp[r_key][f_key]['fixed']:
                # if self.check_zero(self.current_exp[r_key][f_key]['tail'], p_cell['bonus'] > 0):
                not_empty_cells.append(self.current_exp[r_key][f_key])
                fld_list.append(f_key)
        return not_empty_cells, fld_list

    @staticmethod
    def modify_settings(settings):
        mod_settings = {1: {}, -1: {}, 'lvls': [1, ]}
        for f in settings:
            if 'balance_lvl' not in settings[f]:
                continue
            lvl_key = settings[f]['balance_lvl']
            b_by_key = settings[f]['balance_by']
            if lvl_key not in mod_settings:
                mod_settings[lvl_key] = {}
            if b_by_key not in mod_settings[lvl_key]:
                mod_settings[lvl_key][b_by_key] = []
            mod_settings[lvl_key][b_by_key].append(f)
        check_lvl = 2
        while True:
            if check_lvl in mod_settings:
                mod_settings['lvls'].append(check_lvl)
                check_lvl += 1
            else:
                break
        mod_settings['lvls'].append(-1)
        return mod_settings

    @staticmethod
    def prepare_matrix(matr, accuracy):
        for row in matr:
            for field in matr[row]:
                try:
                    matr[row][field]['bonus'] = 0
                    matr[row][field]['plus'] = False
                    matr[row][field]['minus'] = False
                    if matr[row][field]['val'] == 0 and matr[row][field]['tail'] == 0:
                        matr[row][field]['fixed'] = True
                    else:
                        matr[row][field]['fixed'] = False
                    matr[row][field]['tail'] = round(matr[row][field]['tail'], (accuracy + 2))
                except KeyError:
                    raise Exception('Get wrong cell data during balancing!')
                except Exception:
                    print('Ошибка:\n', traceback.format_exc())

    @staticmethod
    def merge_bonuses_to_values(nested_exp_doc):
        for row in nested_exp_doc:
            for field in nested_exp_doc[row]:
                nested_exp_doc[row][field]['val'] += nested_exp_doc[row][field]['bonus']
                nested_exp_doc[row][field]['bonus'] = 0

    def _fix_little_tails(self, depend_rs, depend_fs, accuracy, is_positive, little_tail=0.3):
        for r_key in depend_rs:
            for f_key in depend_fs:
                if 0 < abs(round(self.current_exp[r_key][f_key]['tail'], accuracy + 1)) < little_tail * 10 ** -accuracy:
                    self.current_exp[r_key][f_key]['fixed'] = is_positive
                    if not is_positive:
                        if 0 < abs(round(self.current_exp[r_key][f_key]['tail'], accuracy + 1)) < 0.1 * 10 ** -accuracy:
                            self.current_exp[r_key][f_key]['fixed'] = True

    # поиск ячейки в графе для бонуса
    def _bonus_cell_in_a_field(self, p_cell, f_key, base_f, depend_rs, fields, ch_cells, r_cells, alt_fields=None):
        if alt_fields is None:
            alt_fields = []
        for r_key in depend_rs:
            if not self.current_exp[r_key][f_key]['fixed']:
                if self.check_zero(p_cell['bonus'], p_cell['bonus'] > 0):
                    if self.check_zero(self.current_exp[r_key][f_key]['tail'], p_cell['bonus'] > 0):
                        if self.current_exp[r_key][base_f]['bonus'] == 0:
                            search_tail_fld = self._search_tail_in_a_row(r_key, fields,
                                                                         p_cell['bonus'] > 0)
                            if search_tail_fld is not None:
                                ch_cells.append(self.current_exp[r_key][f_key])
                                r_cells.append(r_key)
                                alt_fields.append(search_tail_fld)
                        else:
                            ch_cells.append(self.current_exp[r_key][f_key])
                            r_cells.append(r_key)
        return ch_cells, r_cells, alt_fields

    # поиск ячейки в строке, в которую записать невязку, если ограничение на малые остатки не дало результат.
    # Ищем по максимальному значению
    def _bonus_cell_in_a_filed_max_value(self, p_cell, f_key, depend_rs, depend_fs, ch_cells, r_cells):
        for r_key in depend_fs:
            if not self.current_exp[r_key][f_key]['fixed']:
                # проверяем, есть ли в данном столбце ячейки с противоположным
                # остатком(чтобы было с чем потом увязать)
                # search_tail_fld = self._search_tail_in_a_field(f_key, depend_rs, p_cell['bonus'] > 0)
                # if search_tail_fld:
                ch_cells.append(self.current_exp[r_key][f_key])
                r_cells.append(f_key)
        return ch_cells, r_cells

    # уравнивание по графам с невязками
    def _balancing_by_each_field(self, base_r, base_f, depend_rs, depend_fs, balance_level):
        for f_key in depend_fs:
            p_cell = self.current_exp[base_r][f_key]
            # если невязка по графе
            if round(p_cell['bonus'], self.accuracy) != 0:
                ch_cells = []
                r_cells = []
                alt_fields = []
                bonus_fs_plus = []
                bonus_fs_minus = []
                for fld_key in depend_fs:
                    if self.current_exp[base_r][fld_key]['bonus'] < 0:
                        bonus_fs_minus.append(fld_key)
                    if self.current_exp[base_r][fld_key]['bonus'] > 0:
                        bonus_fs_plus.append(fld_key)
                if p_cell['bonus'] > 0:
                    bonus_fields = bonus_fs_minus
                else:
                    bonus_fields = bonus_fs_plus
                try:
                    # смотрим ячейки с противоположным остатком, если есть , то добавляем эту строку для выборки по
                    # графе
                    ch_cells, r_cells, alt_fields = self._bonus_cell_in_a_field(p_cell, f_key, base_f, depend_rs,
                                                                                bonus_fields, ch_cells, r_cells,
                                                                                alt_fields)
                    # если есть ячейки с противоположным остатком
                    if len(ch_cells) != 0:
                        # выбираем ячейку в графе, для записи невязки
                        self._split_bonus_each_field(p_cell, ch_cells, base_f, base_r, r_cells, alt_fields)
                    else:
                        self._fix_little_tails(depend_rs, depend_fs, self.accuracy, False)
                        ch_cells, r_cells, alt_fields = self._bonus_cell_in_a_field(p_cell, f_key, base_f, depend_rs,
                                                                                    bonus_fields, ch_cells, r_cells,
                                                                                    alt_fields)
                        if len(ch_cells) != 0:
                            self._split_bonus_each_field(p_cell, ch_cells, base_f, base_r, r_cells, alt_fields)
                        self._fix_little_tails(depend_rs, depend_fs, self.accuracy, True)
                    if p_cell['bonus'] != 0:
                        ch_cells, r_cells, alt_fields = self._bonus_cell_in_a_field(p_cell, f_key, base_f, depend_rs,
                                                                                    depend_fs, ch_cells, r_cells)
                        if len(ch_cells) != 0:
                            self._split_bonus_each_field(p_cell, ch_cells, base_f, base_r, r_cells, alt_fields)
                        else:
                            self._fix_little_tails(depend_rs, depend_fs, self.accuracy, False)
                            ch_cells, r_cells, alt_fields = self._bonus_cell_in_a_field(p_cell, f_key, base_f,
                                                                                        depend_rs,
                                                                                        depend_fs, ch_cells, r_cells)
                            if len(ch_cells) != 0:
                                self._split_bonus_each_field(p_cell, ch_cells, base_f, base_r, r_cells, alt_fields)
                                self._fix_little_tails(depend_rs, depend_fs, self.accuracy, True)
                            else:

                                # если итак нет, то берем максимальное значение
                                self._fix_little_tails(depend_rs, depend_fs, self.accuracy, False)
                                ch_cells, r_cells = self._bonus_cell_in_a_field_max_value(p_cell, f_key, depend_rs,
                                                                                          depend_fs, ch_cells, r_cells,
                                                                                          base_f)
                                if len(ch_cells) != 0:
                                    winner_i = self._run_bonus_competition_max_value(ch_cells)
                                    self.current_exp[r_cells[winner_i]][f_key]['bonus'] += p_cell['bonus']
                                    if p_cell['bonus'] > 0:
                                        self.current_exp[r_cells[winner_i]][f_key]['plus'] = True
                                    else:
                                        self.current_exp[r_cells[winner_i]][f_key]['minus'] = True
                                else:
                                    print('Error. Error. Error. There is no bonus in a filed!')
                                    return 1

                                self._fix_little_tails(depend_rs, depend_fs, self.accuracy, True)

                except Exception:
                    print('Ошибка:\n', traceback.format_exc())

    # поиск ячейки в строке, в которую записать невязку
    def _bonus_cell_in_a_row(self, p_cell, r_key, depend_rs, depend_fs, ch_cells, fld_cells):
        for f_key in depend_fs:
            if not self.current_exp[r_key][f_key]['fixed']:
                if self.check_zero(p_cell['bonus'], p_cell['bonus'] > 0):
                    if self.check_zero(self.current_exp[r_key][f_key]['tail'], p_cell['bonus'] > 0):
                        # проверяем, есть ли в данном столбце ячейки с противоположным
                        # остатком(чтобы было с чем потом увязать)
                        search_tail_fld = self._search_tail_in_a_field(f_key, depend_rs,
                                                                       p_cell['bonus'] > 0)
                        if search_tail_fld:
                            ch_cells.append(self.current_exp[r_key][f_key])
                            fld_cells.append(f_key)
        return ch_cells, fld_cells

    # поиск ячейки в строке, в которую записать невязку, если ограничение на малые остатки не дало результат.
    # Ищем по максимальному значению
    def _bonus_cell_in_a_row_max_value(self, p_cell, r_key, depend_rs, depend_fs, ch_cells, fld_cells, base_r):
        for f_key in depend_fs:
            if not self.current_exp[r_key][f_key]['fixed']:
                # проверяем, есть ли в данном столбце ячейки с противоположным
                # остатком(чтобы было с чем потом увязать)
                search_tail_fld = self._search_tail_in_a_field_max_value(f_key, depend_rs, p_cell['bonus'] > 0)
                if search_tail_fld:
                    ch_cells.append(self.current_exp[r_key][f_key])
                    fld_cells.append(f_key)
                else:
                    if self.current_exp[base_r][f_key]['bonus'] != 0:
                        ch_cells.append(self.current_exp[r_key][f_key])
                        fld_cells.append(f_key)
        return ch_cells, fld_cells

    # поиск ячейки в графе, в которую записать невязку, если ограничение на малые остатки не дало результат.
    # Ищем по максимальному значению

    def _bonus_cell_in_a_field_max_value(self, p_cell, f_key, depend_rs, depend_fs, ch_cells, r_cells, base_f):
        for r_key in depend_rs:
            if not self.current_exp[r_key][f_key]['fixed']:
                # проверяем, есть ли в данном столбце ячейки с противоположным
                # остатком(чтобы было с чем потом увязать)
                search_tail_fld = self._search_tail_in_a_row(r_key, depend_fs, p_cell['bonus'] > 0)
                if search_tail_fld:
                    ch_cells.append(self.current_exp[r_key][f_key])
                    r_cells.append(r_key)
                else:
                    if self.current_exp[r_key][base_f]['bonus'] != 0:
                        ch_cells.append(self.current_exp[r_key][f_key])
                        r_cells.append(f_key)
        return ch_cells, r_cells

    # уравнивание по каждой строке. Сумма ячеек строки должна соответствовать значению ячейки из итоговой графы
    def _balancing_by_each_row(self, base_r, base_f, depend_rs, depend_fs):
        for r_key in depend_rs:
            p_cell = self.current_exp[r_key][base_f]
            if round(p_cell['bonus'], self.accuracy) != 0:
                ch_cells = []
                fld_cells = []
                bonus_fs_plus = []
                bonus_fs_minus = []
                # определяем, в каких графах есть бонусы(невязки)
                for f_key in depend_fs:
                    if self.current_exp[base_r][f_key]['bonus'] < 0:
                        bonus_fs_minus.append(f_key)
                    if self.current_exp[base_r][f_key]['bonus'] > 0:
                        bonus_fs_plus.append(f_key)
                if p_cell['bonus'] > 0:
                    bonus_fields = bonus_fs_plus
                else:
                    bonus_fields = bonus_fs_minus
                try:
                    # сначала уравниваем в строке, используя графы с бонусами(невязками),
                    # если таковых нет, то берем в расчет все графы
                    for f_key in bonus_fields:
                        if not self.current_exp[r_key][f_key]['fixed']:
                            if self.check_zero(p_cell['bonus'], p_cell['bonus'] > 0):
                                if self.check_zero(self.current_exp[r_key][f_key]['tail'], p_cell['bonus'] > 0):
                                    ch_cells.append(self.current_exp[r_key][f_key])
                                    fld_cells.append(f_key)
                    # проверяем, есть ли ячейки с нужным остатком в графах с бонусами(невязками)
                    # если есть, находим максимальный остаток и максимальное число при равенстве остатков и
                    # записываем в эту ячейку бонус. Записываем в тотал графу и тотал строку бонусы
                    # идем дальше по строкам
                    if len(ch_cells) != 0:
                        self._split_bonus_each_row(p_cell, ch_cells, base_r, fld_cells)
                    else:
                        # снимаем ограничение на малые остатки и берем их в расчет
                        self._fix_little_tails(depend_rs, depend_fs, self.accuracy, False)
                        for f_key in bonus_fields:
                            if not self.current_exp[r_key][f_key]['fixed']:
                                if self.check_zero(p_cell['bonus'], p_cell['bonus'] > 0):
                                    if self.check_zero(self.current_exp[r_key][f_key]['tail'], p_cell['bonus'] > 0):
                                        ch_cells.append(self.current_exp[r_key][f_key])
                                        fld_cells.append(f_key)
                        if len(ch_cells) != 0:
                            self._split_bonus_each_row(p_cell, ch_cells, base_r, fld_cells)
                        self._fix_little_tails(depend_rs, depend_fs, self.accuracy, True)
                    # проверяем, если еще остались бонусы в строке, то идем по всем графам
                    if p_cell['bonus'] != 0:
                        ch_cells = []
                        fld_cells = []
                        ch_cells, fld_cells = self._bonus_cell_in_a_row(p_cell, r_key, depend_rs, depend_fs,
                                                                        ch_cells, fld_cells)
                        if len(ch_cells) != 0:
                            self._split_bonus_each_row(p_cell, ch_cells, base_r, fld_cells)
                        else:
                            # снимаем ограничение на малые остатки и берем их в расчет
                            self._fix_little_tails(depend_rs, depend_fs, self.accuracy, False)
                            ch_cells, fld_cells = self._bonus_cell_in_a_row(p_cell, r_key, depend_rs, depend_fs,
                                                                            ch_cells, fld_cells)

                            if len(ch_cells) != 0:
                                self._split_bonus_each_row(p_cell, ch_cells, base_r, fld_cells)
                                self._fix_little_tails(depend_rs, depend_fs, self.accuracy, True)
                            else:
                                ch_cells, fld_cells = self._bonus_cell_in_a_row_max_value(p_cell, r_key, depend_rs,
                                                                                          depend_fs, ch_cells,
                                                                                          fld_cells, base_r)
                                if len(ch_cells) != 0:
                                    winner_i = self._run_bonus_competition_max_value(ch_cells)
                                    self.current_exp[r_key][fld_cells[winner_i]]['bonus'] += p_cell['bonus']
                                    if p_cell['bonus'] > 0:
                                        self.current_exp[r_key][fld_cells[winner_i]]['plus'] = True
                                    else:
                                        self.current_exp[r_key][fld_cells[winner_i]]['minus'] = True
                                else:
                                    print('Уравнивание не удалось')
                                    return 1
                                self._fix_little_tails(depend_rs, depend_fs, self.accuracy, True)
                except Exception:
                    print('Ошибка:\n', traceback.format_exc())
                    print('Fail on balancing each row')

    def _run_matrix_clockwise_balancing(self, base_r, depend_rs, base_f, depend_fs, field_level, row_level):
        """
                    includes 3 steps :
                        1) right --> depend rows balancing;
                        2) down collecting;
                        3) <-- asserting and improving;
                    :param base_r: row to start
                    :param depend_rs: balancing rows where all base fields are fixed
                    :param base_f: field to start
                    :param depend_fs: balancing fields
                    """
        # 1...balancing_matrix_stage_1 balancing by depend fields from base field in every row
        for row_key in depend_rs:
            p_cell = self.current_exp[row_key][base_f]
            ch_cells = []
            for f_key in depend_fs:
                try:
                    ch_cells.append(self.current_exp[row_key][f_key])
                except KeyError:
                    print('Fail on first clockwise balancing phase')
            self._make_equal_bonus_fix(p_cell, ch_cells, field_level)

        # 2...balancing_matrix_stage_2 collecting fixed fields from previous step to total row
        for f_key in depend_fs:
            p_cell = self.current_exp[base_r][f_key]
            ch_cells = []
            for row_key in depend_rs:
                try:
                    ch_cells.append(self.current_exp[row_key][f_key])
                except KeyError:
                    print('Fail on second clockwise balancing phase')
            self._make_equal_bonus_fix(p_cell, ch_cells, row_level)

    def _run_matrix_finish_balancing(self, base_r, depend_rs, base_f, depend_fs, field_level, row_level):
        # 1...balancing_matrix_stage_1 balancing by depend fields from base field in every row
        for row_key in depend_rs:
            p_cell = self.current_exp[row_key][base_f]
            ch_cells = []
            for f_key in depend_fs:
                try:
                    ch_cells.append(self.current_exp[row_key][f_key])
                except KeyError:
                    print('Fail on first clockwise balancing phase')
            child_sum = 0
            # guarantee_keys(parent_cell)
            parent_val = p_cell['val'] + p_cell['bonus']
            for cell in ch_cells:
                # guarantee_keys(cell)
                child_sum += cell['val'] + cell['bonus']
            p_cell['bonus'] = child_sum - parent_val
            p_cell['fixed'] = True
            self.current_exp[row_key]['total']['bonus'] += p_cell['bonus']
            self.current_exp[row_key]['total']['fixed'] = True

    def _run_matrix_balancing_1_stage(self, base_r, depend_rs, base_f, depend_fs, balance_level):
        """
        includes 5 steps :
            1) down --> balancing;
            2) right --> balancing;
            3) each row --> balancing;
            4) each field down --> collecting
            5) each field --> improving

        :param base_r: row to start
        :param depend_rs: balancing rows
        :param base_f: field to start
        :param depend_fs: balancing fields
        """
        # 1... уравниваем итоговую строку с общими площадями, фиксируем значения в итоговой строке
        try:
            p_cell = self.current_exp[base_r][base_f]
            ch_cells = []
            for f_key in depend_fs:
                try:
                    ch_cells.append(self.current_exp[base_r][f_key])
                except:
                    print('Fail on first anticlockwise balancing phase')
            self._make_equal_bonus_fix(p_cell, ch_cells, balance_level)
            self.merge_bonuses_to_values(self.current_exp)
        except:
            print('1 Fail on Total row balance')

        # 1.2... уравниваем итоговую графу с общими площадями
        try:
            p_cell = self.current_exp[base_r][base_f]
            ch_cells = []
            for r_key in depend_rs:
                try:
                    ch_cells.append(self.current_exp[r_key][base_f])
                except:
                    print('Fail on fourth anticlockwise balancing phase')
            self._make_equal_bonus_fix(p_cell, ch_cells, balance_level)
            self.merge_bonuses_to_values(self.current_exp)
        except:
            print('1.2 Fail on Total field balance')

        # 2... поиск бонусов(невязок) в графе и запись бонуса в итоговую(25) строку по каждой графе
        for f_key in depend_fs:
            try:
                p_cell = self.current_exp[base_r][f_key]
                ch_cells = []
                for r_key in depend_rs:
                    try:
                        ch_cells.append(self.current_exp[r_key][f_key])
                    except:
                        print('Fail on second clockwise balancing phase')
                self._make_equal_bonus_not_fix_25(p_cell, ch_cells, balance_level)
            except:
                print('2. Fail on searching Bonuses on each field')

        # 2.2... Проверка, есть ли значения в графах с бонусом(невязкой), если значение только одно,
        # то добавляем туда бонус(невязку) и записываем в итоговую строку и итоговую графу эту невязку
        for f_key in depend_fs:
            try:
                p_cell = self.current_exp[base_r][f_key]
                if p_cell['bonus'] != 0:
                    not_empty_cells, row_list = self._search_one_cell_in_a_field(base_r, base_f, depend_rs, f_key)

                    if len(not_empty_cells) == abs(p_cell['bonus']):
                        for i in range(len(not_empty_cells)):
                            bonus = p_cell['bonus'] / len(not_empty_cells)
                            self.current_exp[row_list[i]][f_key]['bonus'] += bonus
                            if p_cell['bonus'] > 0:
                                self.current_exp[row_list[i]][f_key]['minus'] = True
                            else:
                                self.current_exp[row_list[i]][f_key]['plus'] = True

                            p_cell['bonus'] -= bonus
                            # self.current_exp[row_list[i]][base_f]['bonus'] -= bonus
            except:
                print('2.2 Fail on searching one bonus in a field')

        # 3... поиск бонусов по каждой строке и запись в итоговую графу
        for r_key in depend_rs:
            p_cell = self.current_exp[r_key][base_f]
            ch_cells = []
            try:
                for f_key in depend_fs:
                    try:
                        ch_cells.append(self.current_exp[r_key][f_key])
                    except:
                        print('Fail on third anticlockwise balancing phase')
                self._make_equal_bonus_not_fix_25(p_cell, ch_cells, balance_level)
            except:
                print('3. Fail on searching bonus in a row')

            # 3.2... Проверка, есть ли значения в строках с бонусом(невязкой), если значение только одно,
            # то добавляем туда бонус(невязку) и записываем в итоговую строку в итоговую строку эту невязку
            for r_key in depend_rs:
                try:
                    p_cell = self.current_exp[r_key][base_f]
                    if p_cell['bonus'] != 0:
                        not_empty_cells, fld_list = self._search_one_cell_in_a_row(base_r, base_f, depend_fs,
                                                                                   r_key)

                        if len(not_empty_cells) == abs(p_cell['bonus']):
                            for i in range(len(not_empty_cells)):
                                bonus = p_cell['bonus'] / len(not_empty_cells)
                                self.current_exp[r_key][fld_list[i]]['bonus'] += bonus
                                if p_cell['bonus'] > 0:
                                    self.current_exp[r_key][fld_list[i]]['minus'] = True
                                else:
                                    self.current_exp[r_key][fld_list[i]]['plus'] = True

                                p_cell['bonus'] -= bonus
                                self.current_exp[base_r][fld_list[i]]['bonus'] -= bonus
                except:
                    print('3.2 Fail on searching one bonus in a row')

        # 4.1... если в итоговой строке значение 0, то весь столбец фиксируем и значения = 0

        for f_key in depend_fs:
            if self.current_exp[base_r][f_key]['val'] == 0 and self.current_exp[base_r][f_key]['fixed'] is True:
                for r_key in depend_rs:
                    self.current_exp[r_key][f_key]['val'] = 0
                    self.current_exp[r_key][f_key]['tail'] = 0
                    self.current_exp[r_key][f_key]['fixed'] = True

        # 5... собираем невязки по строкам и графам
        bonus_list = []
        for f_key in depend_fs:
            if self.current_exp[base_r][f_key]['bonus'] != 0:
                bonus_list.append(f_key)
        for r_key in depend_rs:
            if self.current_exp[r_key][base_f]['bonus'] != 0:
                bonus_list.append(r_key)

        # 4... фиксируем значения с малым или большим остатком (>0.3 и >0.8)
        self._fix_little_tails(depend_rs, depend_fs, self.accuracy, True, 0.3)

        # 6... уравнивание по строкам и графам
        # пока бонусов(невязки) не будет ни в итоговой строке, ни в итоговой графе

        check_balance = True

        while len(bonus_list) != 0:
            # 8.1... уравнивание по каждой строке, сумма ячеек по строке должна соответствовать
            # итоговой ячейке в итоговой графе
            try:
                balance_row = 0
                balance_row = self._balancing_by_each_row(base_r, base_f, depend_rs, depend_fs)
                '''if balance_row is None:
                    if balance_row == 1:
                        check_balance = False
                        break'''

            except:
                print('Fail on balancing by each row')

            # 8.2... уравнивание по графе с невязкой, сумма ячеек по графе должна соответствовать
            # итоговой ячейке в итоговой строке
            for r_key in depend_rs:
                self.current_exp[r_key][base_f]['bonus'] = round(self.current_exp[r_key][base_f]['bonus'],
                                                                 self.accuracy)
                for f_key in depend_fs:
                    self.current_exp[r_key][f_key]['bonus'] = round(self.current_exp[r_key][f_key]['bonus'],
                                                                    self.accuracy)

            try:
                balance_field = 0
                balance_field = self._balancing_by_each_field(base_r, base_f, depend_rs, depend_fs, balance_level)
                '''if balance_field is None:
                    if balance_field == 1:
                        check_balance = False
                        break'''
            except Exception:
                print('Ошибка:\n', traceback.format_exc())
                print('Fail on balancing by each field')
            '''for r_key in depend_rs:
                self.current_exp[r_key][base_f]['bonus'] = round(self.current_exp[r_key][base_f]['bonus'], self.accuracy)
                for f_key in depend_fs:
                    self.current_exp[r_key][f_key]['bonus'] = round(self.current_exp[r_key][f_key]['bonus'],
                                                                    self.accuracy)'''
            # 8.3... проверяем наличие невязок по строкам и графам
            bonus_list = []
            for f_key in depend_fs:
                if round(self.current_exp[base_r][f_key]['bonus'], self.accuracy) != 0:
                    bonus_list.append(f_key)
            for r_key in depend_rs:
                if round(self.current_exp[r_key][base_f]['bonus'], self.accuracy) != 0:
                    bonus_list.append(r_key)

        '''if not check_balance:
            self.show_modal('Уравнивание не удалось, необходимо уравнаять вручную', modal_type='warning')'''
        # 7... объединяем невязки(бонусы) со значениями
        self.merge_bonuses_to_values(self.current_exp)

        # 8... фиксируем значения увязанных данных
        for r_key in depend_rs:
            for f_key in depend_fs:
                self.current_exp[r_key][f_key]['fixed'] = True

    def _run_matrix_balancing_2_stage(self, base_r, depend_rs, base_f, depend_fs, balance_level, field_level):
        """
        includes 5 steps :
            1) down --> balancing;
            2) right --> balancing;
            3) each row --> balancing;
            4) each field down --> collecting
            5) each field --> improving

        :param base_r: row to start
        :param depend_rs: balancing rows
        :param base_f: field to start
        :param depend_fs: balancing fields
        """

        # 1... поиск бонусов(невязок) в Total (25) строке и запись бонуса в Total(25) строку по каждой графе
        for f_key in depend_fs:
            try:
                p_cell = self.current_exp[base_r][f_key]
                ch_cells = []
                for r_key in depend_rs:
                    try:
                        ch_cells.append(self.current_exp[r_key][f_key])
                    except:
                        print('Fail on second clockwise balancing phase')
                self._make_equal_bonus_not_fix(p_cell, ch_cells, balance_level)
            except:
                print('2. Fail on searching Bonuses on each field')

        # 2... поиск бонусов по каждой строке и запись в Total графу
        for r_key in depend_rs:
            p_cell = self.current_exp[r_key][base_f]
            ch_cells = []
            try:
                for f_key in depend_fs:
                    try:
                        ch_cells.append(self.current_exp[r_key][f_key])
                    except:
                        print('Fail on third anticlockwise balancing phase')
                self._make_equal_bonus_not_fix_Total(p_cell, ch_cells, field_level)  # not_fix_total

            except:
                print('3. Fail on searching bonus in a row')

        # 3... объединяем невязки(бонусы) со значениями
        self.merge_bonuses_to_values(self.current_exp)

        # 4.. фиксируем значения увязанных данных
        for r_key in depend_rs:
            self.current_exp[r_key][base_f]['fixed'] = True
            for f_key in depend_fs:
                self.current_exp[r_key][f_key]['fixed'] = True

    # увязка матрицы по графам. Если итоговая графа не увязана (fixed), то метод увязки для 1 уровня,
    # если увязана, то другой метод
    def _run_matrix_balancing_by_base_row(self, base_row, depend_rows, row_stage):
        for field_stage in self.field_settings['lvls']:
            for lvl_f_key in self.field_settings[field_stage]:
                base_fields_fixed = True  # need clockwise balancing
                for row in depend_rows:
                    if not self.current_exp[row][lvl_f_key]['fixed']:
                        base_fields_fixed = False
                        break

                if base_fields_fixed:
                    self._run_matrix_clockwise_balancing(
                        base_row,
                        depend_rows,
                        lvl_f_key,
                        self.field_settings[field_stage][lvl_f_key],
                        field_stage, row_stage
                    )
                    if row_stage == 2:
                        if field_stage == 2:
                            self._run_matrix_finish_balancing(
                                base_row,
                                depend_rows,
                                lvl_f_key,
                                self.field_settings[field_stage][lvl_f_key],
                                field_stage, row_stage
                            )
                else:
                    if row_stage == 1:

                        self._run_matrix_balancing_1_stage(
                            base_row,
                            depend_rows,
                            lvl_f_key,
                            self.field_settings[field_stage][lvl_f_key],
                            row_stage
                        )
                    else:
                        self._run_matrix_balancing_2_stage(
                            base_row,
                            depend_rows,
                            lvl_f_key,
                            self.field_settings[field_stage][lvl_f_key],
                            row_stage, field_stage
                        )

    def run_b_balancer(self, main_exp, _f_settings, _r_settings, accuracy):
        self.current_exp = main_exp
        self.accuracy = int(accuracy)
        self.field_settings = self.modify_settings(_f_settings)
        row_settings = self.modify_settings(_r_settings)
        self.prepare_matrix(main_exp, int(self.accuracy))
        try:
            self.current_exp['25']['total']['bonus'] = \
                self.current_exp['by_SHAPE']['total']['val'] - self.current_exp['25']['total']['val']
            self.current_exp['25']['total']['fixed'] = True
        except KeyError:
            print('Balancing Failed. No sense to balance without by_SHAPE or 25 row key')
            return self.current_exp
        # TODO: Add by_SHAPE row to * array

        for row_stage in row_settings['lvls']:
            for lvl_r_key in row_settings[row_stage]:
                if lvl_r_key == '*':
                    print('Not matrix balancing')
                    # TODO: run balancing by fields only for one row of rows in _r_settings['*'] array
                else:
                    if row_settings['lvls'].index(row_stage) == 0:  # first stage
                        try:
                            # setting base cells for first step fixed
                            first_f_lvl_key = self.field_settings['lvls'][0]
                            # should be equal to 1
                            for main_f_key in self.field_settings[first_f_lvl_key]:
                                self.current_exp[lvl_r_key][main_f_key]['fixed'] = True
                        except KeyError:
                            raise Exception('Failed on setting main cells to fixed')
                    try:
                        self._run_matrix_balancing_by_base_row(lvl_r_key, row_settings[row_stage][lvl_r_key], row_stage)
                    except Exception as e:
                        print('Ошибка:\n', traceback.format_exc())
        self.merge_bonuses_to_values(self.current_exp)

    def run_as_balancer(self, main_exp, _f_settings, _r_settings):
        print('Not yet implemented', main_exp)
        # self.field_settings = modify_settings(_f_settings)
        # row_settings = modify_settings(_r_settings)

    def run_asv_balancer(self, main_exp, _f_settings, _r_settings):
        print('Not yet implemented')
        # self.field_settings = modify_settings(_f_settings)
        # row_settings = modify_settings(_r_settings)}
