#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math


class ExpBalancer:
    b_counter = 0
    accuracy = None
    current_exp = None
    field_settings = None

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
            if not cells[ind][key]:
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
            bonus_items = self.get_inds_with_false_key(cells, 'bonus')
            # if need with fixed items comment this
            fixed_items = self.get_inds_with_false_key(cells, 'fixed')
            for i in range(len(cells)):
                if i in bonus_items:
                    possible_bonus_items.remove(i)
                    continue
                if i in fixed_items:
                    possible_bonus_items.remove(i)
                    continue
                if is_positive and cells[i]['val'] < 0:
                    possible_bonus_items.remove(i)
                    continue
                if not is_positive and cells[i]['val'] > 0:
                    possible_bonus_items.remove(i)

        if len(possible_bonus_items) <= 1:
            # Counts only by max value
            return self._run_bonus_competition(cells, range(len(cells)), True, 'val')

        winner_i = self._run_bonus_competition(cells, possible_bonus_items, is_positive)
        winner_cell = cells[winner_i]
        min_bonus = 10 ** self.accuracy
        if winner_cell['fixed']:
            print('something went wrong. Winner cell already fixed')
        # small values < 0 could be and should be in tail!
        zero_val_winned = winner_cell['val'] < 2 * min_bonus

        if zero_val_winned:
            if is_positive:
                return winner_i
            else:
                possible_bonus_items.remove(winner_i)
                return self._get_bonus_cell_ind(cells, is_positive, possible_bonus_items)
        else:
            return winner_i

    @staticmethod
    def is_current_wins(last_winner, current, is_positive):
        return last_winner < current if is_positive else last_winner > current

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
            if self.is_current_wins(cells[winner_tail_i][competition_by], cells[i][competition_by], is_positive):
                winner_tail_i = i
        return winner_tail_i

    def _split_bonus(self, bonus, cells):
        bonus_count = math.fabs(bonus * 10**self.accuracy)
        if bonus_count:
            print(bonus_count, bonus)
        bonus /= bonus_count

        for bonusInd in range(int(bonus_count)):
            bonus_cell_key = self._get_bonus_cell_ind(cells, bonus > 0, self.accuracy)
            try:
                cells[bonus_cell_key]['bonus'] += bonus
            except KeyError:
                print('Something went wrong while Balancing')
                cells[bonus_cell_key]['bonus'] = bonus
                # TODO: Uncomment here after debugging
                # raise Exception('Something went wrong while Balancing')

    def _make_equal_bonus_fix(self, parent_cell, child_cells):

        """
        Caution. This method changes the input objects
        it doesnt change the keys of input parameters,
        just adds bonuses which guarantees that val sums with bonuses are equal
        :param parent_cell: parent cell
        :param child_cells: array of cells
        :return:
        """
        accuracy = int(self.accuracy)
        # def guarantee_keys(cll):
        #     # TODO: it can be deprecated after adding bonus and fixed keys to all cells by function prepare_matrix
        #     if not isinstance(cll, dict):
        #         raise Exception('Get wrong cell data during balancing!')
        #     if not cll.has_key('bonus'):
        #         cll['bonus'] = 0
        #     if not cll.has_key('fixed'):
        #         cll['fixed'] = False

        child_sum = 0
        # guarantee_keys(parent_cell)
        parent_val = parent_cell['val'] + parent_cell['bonus']
        for cell in child_cells:
            # guarantee_keys(cell)
            child_sum += cell['val'] + cell['bonus']

        if parent_cell['fixed']:
            total_bonus = round(parent_val - child_sum, accuracy)
            if total_bonus != 0:
                self._split_bonus(total_bonus, child_cells)
        #         TODO: MAKE FIXED CHILDS IF NOT FAULT
            for cll in child_cells:
                cll['fixed'] = True
        else:
            parent_cell['bonus'] = child_sum - parent_cell['val']
            parent_cell['fixed'] = True

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
    def prepare_matrix(matr):
        for row in matr:
            for field in matr[row]:
                try:
                    matr[row][field]['bonus'] = 0
                    if matr[row][field]['val'] == 0 and matr[row][field]['tail'] == 0:
                        matr[row][field]['fixed'] = True
                    else:
                        matr[row][field]['fixed'] = False
                except KeyError:
                    raise Exception('Get wrong cell data during balancing!')
                except Exception:
                    raise Exception('Get wrong cell data during balancing!')

    @staticmethod
    def merge_bonuses_to_values(nested_exp_doc):
        for row in nested_exp_doc:
            for field in nested_exp_doc[row]:
                nested_exp_doc[row][field]['val'] += nested_exp_doc[row][field]['bonus']

    def _run_matrix_clockwise_balancing(self, base_r, depend_rs, base_f, depend_fs):
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
            self._make_equal_bonus_fix(p_cell, ch_cells)

        # 2...balancing_matrix_stage_2 collecting fixed fields from previous step to total row
        for f_key in depend_fs:
            p_cell = self.current_exp[base_r][f_key]
            ch_cells = []
            for row_key in depend_rs:
                try:
                    ch_cells.append(self.current_exp[row_key][f_key])
                except KeyError:
                    print('Fail on second clockwise balancing phase')
            self._make_equal_bonus_fix(p_cell, ch_cells)

        # 3...balancing_matrix_stage_3 asserting fields by total in base row
        p_cell = self.current_exp[base_r][base_f]
        ch_cells = []
        for f_key in depend_fs:
            try:
                ch_cells.append(self.current_exp[base_r][f_key])
            except KeyError:
                print('Fail on third clockwise balancing phase')

        if self._assert_equal(p_cell, ch_cells):
            print('BLOCK OK')
        else:
            print('FAILED')
            # raise Exception('Balabcing failed. Please check your input')

    def _run_matrix_anticlockwise_balancing(self, base_r, depend_rs, base_f, depend_fs):
        """
        includes 4 steps :
            1) right --> balancing;
            2) up balancing;
            3) left <-- collecting;
            4) down - improving
        :param base_r: row to start
        :param depend_rs: balancing rows
        :param base_f: field to start
        :param depend_fs: balancing fields
        """

        # 1...balancing_matrix_stage_1 balancing fields by total
        p_cell = self.current_exp[base_r][base_f]
        ch_cells = []
        for f_key in depend_fs:
            try:
                ch_cells.append(self.current_exp[base_r][f_key])
            except KeyError:
                print('Fail on first anticlockwise balancing phase')

                # ch_cells = _f_settings[field_stage][lvl_f_key].map(lambda x: self.current_exp[base_row][x])
                # TODO: debug this lambda not to change self.current_exp
        self._make_equal_bonus_fix(p_cell, ch_cells)

        # 2...balancing_matrix_stage_2 balancing fixed fields from previous step by depend rows
        for f_key in depend_fs:
            p_cell = self.current_exp[base_r][f_key]
            ch_cells = []
            for row_key in depend_rs:
                try:
                    ch_cells.append(self.current_exp[row_key][f_key])
                except KeyError:
                    print('Fail on second anticlockwise balancing phase')
            self._make_equal_bonus_fix(p_cell, ch_cells)

        # 3...balancing_matrix_stage_3 making total field of every depend row to fixed
        for row_key in depend_rs:
            p_cell = self.current_exp[row_key][base_f]
            ch_cells = []
            for f_key in depend_fs:
                try:
                    ch_cells.append(self.current_exp[row_key][f_key])
                except KeyError:
                    print('Fail on third anticlockwise balancing phase')
            self._make_equal_bonus_fix(p_cell, ch_cells)

        # 4...balancing_matrix_stage_4 asserting the results; should be balanced
        p_cell = self.current_exp[base_r][base_f]
        ch_cells = []
        for row_key in depend_rs:
            try:
                ch_cells.append(self.current_exp[row_key][base_f])
            except KeyError:
                print('Fail on fourth anticlockwise balancing phase')

        if self._assert_equal(p_cell, ch_cells):
            print('BLOCK OK')
        else:
            print('FAILED')
            # raise Exception('Balabcing failed. Please check your input')

    def _run_matrix_balancing_by_base_row(self, base_row, depend_rows, is_first_lvl=False):
        for field_stage in self.field_settings['lvls']:
            for lvl_f_key in self.field_settings[field_stage]:
                # if is_first_lvl:
                #     run_matrix_anticlockwise_balancing(
                #         base_row, depend_rows, lvl_f_key, self.field_settings[field_stage][lvl_f_key])
                #     continue
                # TODO: You can use this to upgrade performance
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
                        self.field_settings[field_stage][lvl_f_key]
                    )
                else:
                    self._run_matrix_anticlockwise_balancing(
                        base_row,
                        depend_rows,
                        lvl_f_key,
                        self.field_settings[field_stage][lvl_f_key]
                    )

    def run_b_balancer(self, main_exp, _f_settings, _r_settings, accuracy):
        self.current_exp = main_exp
        self.accuracy = int(accuracy)
        self.field_settings = self.modify_settings(_f_settings)
        row_settings = self.modify_settings(_r_settings)
        self.prepare_matrix(main_exp)
        try:
            self.current_exp['25']['total']['bonus'] =\
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
                    if row_settings['lvls'].index(row_stage) == 0: # first stage
                        try:
                            # setting base cells for first step fixed
                            first_f_lvl_key = self.field_settings['lvls'][0]
                            # should be equal to 1
                            for main_f_key in self.field_settings[first_f_lvl_key]:
                                self.current_exp[lvl_r_key][main_f_key]['fixed'] = True
                        except KeyError:
                            raise Exception('Failed on setting main cells to fixed')
                    self._run_matrix_balancing_by_base_row(lvl_r_key, row_settings[row_stage][lvl_r_key])
        self.merge_bonuses_to_values(self.current_exp)

    def run_as_balancer(self, main_exp, _f_settings, _r_settings):
        print('Not yet implemented', main_exp)
        # self.field_settings = modify_settings(_f_settings)
        # row_settings = modify_settings(_r_settings)

    def run_asv_balancer(self, main_exp, _f_settings, _r_settings):
        print('Not yet implemented')
        # self.field_settings = modify_settings(_f_settings)
        # row_settings = modify_settings(_r_settings)
