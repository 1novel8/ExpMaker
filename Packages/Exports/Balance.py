#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

# li1 = [[2941766.8860134804, 886.79595366918, 779.58821893535, 86.2505280796191, 2930138.63968789, 3081.57325414444, 6794.03837076164],
#        [10810889.550832964, 3214.20173861995, 614.91408782033, 1057262.79739716, 6457.27703173003, 9743072.58100759, 267.7795700432],
#        [12411732.474104717, 481.893555435379, 55.7787204987318, 3808656.57925138, 357.88229970823, 8596380.72654963, 5799.61372806483],
#        [10016049.824814899, 9864667.05248715, 20395.7937766741, 46689.6240508603, 30549.0740155624, 42835.8364938752, 10912.4439907763],
#        [2637101.695419007, 2095776.29412423, 299.22340413854, 191.119897769249, 1994.50579923185, 195457.241098326, 343383.311095311],
#        [3896913.373186771, 327.351092218808, 1973614.82451198, 1901289.8151775, 18263.8089345062, 1388.99232770628, 2028.58114285974],
#        [1921909.556347085, 327.351092218808, 0, 1901289.8151775, 18263.8089345062, 0, 2028.58114285974],
#        [44636363.360641, 11965680.94, 1995760.12272, 8715466.00148, 3006024.9967, 18582216.9507, 371214.349041]]
# li = [1196560.94, 1995760.122720047, 779.58821893535,0, 86.2505280796191, 0, 0, 2930.63968789]
#
#
# def balance_list(d, need_sum, after_round_li, round_to = 4, iters = 15):
#     low_discr = 10**-(round_to-1)
#     discr = d
#     iters_left = iters
#     do = after_round_li[:]
#     while math.fabs(discr) > low_discr:
#         after_round_li = map(lambda x: round(x+x*discr/need_sum, round_to) if x>1 else x, after_round_li)
#         discr = need_sum - sum(after_round_li)
#         iters_left -= 1
#         if not iters_left:break
#     add_discr_to_max(after_round_li, round(discr, round_to))
#     print do
#     print after_round_li
#     return after_round_li
#
# def add_discr_to_max(li, discr):
#     li[li.index(max(li))] += discr
#     return li


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


def get_inds_with_false_key(cells, key):
    inds_false_key = []
    for ind in xrange(len(cells)):
        if not cells[ind][key]:
            inds_false_key.append(ind)
    return inds_false_key

current_wins = lambda last_winner, current, is_positive: last_winner < current if is_positive else last_winner > current

def run_bonus_competition(cells, cell_ind_array, is_positive,competition_by='tail'):
    winner_tail_i = cell_ind_array[0]
    for i in cell_ind_array[1:]:
        if current_wins(cells[winner_tail_i][competition_by], cells[i][competition_by], is_positive):
            winner_tail_i = i
    return winner_tail_i


def get_bonus_cell_ind(cells, is_positive):
    winner_i = run_bonus_competition(cells, range(len(cells)), is_positive)
    winner_cell = cells[winner_i]

    # small values < 0 could be and should be in tail!
    zero_val_winned = False
    if not winner_cell['bonus'] and not winner_cell['fixed']:
        if winner_cell['val'] > 1:
            return winner_i  # seems all ok
        else:
            zero_val_winned = True
    no_bonus_items = get_inds_with_false_key(cells, 'bonus')
    if zero_val_winned:
        no_bonus_items.remove(winner_i)
    if len(no_bonus_items):
        if len(no_bonus_items) < len(cells):  # still ok
            winner_i = run_bonus_competition(cells, no_bonus_items, is_positive)
            #     0 val cell can be a winner. It can't be. So we make winner by max value
            if cells[winner_i]['val'] <= 1:
                winner_i = run_bonus_competition(cells, range(len(cells)), True, 'val')
        else:  # all cells has bonuses
            winner_i = run_bonus_competition(cells, range(len(cells)), True, 'val')

        if not cells[winner_i]['fixed']:
            return winner_i  # it is possible
        else:
            no_fixed_items = get_inds_with_false_key(cells, 'fixed')
            if len(no_fixed_items) < len(cells):
                return run_bonus_competition(cells, no_fixed_items, True, 'val')

    # problem in fixed statement (all fixed)
    # print 'Seems something went wrong, you have tried to give bonus for fixed cell'
    raise Exception('Seems something went wrong, you have tried to give bonus for fixed cell')


def split_bonus(bonus, cells, accuracy):
    try:
        bonus_count = math.fabs(bonus / accuracy)
    except ZeroDivisionError:
        bonus_count = math.fabs(bonus)
    bonus /= bonus_count

    for bonusInd in xrange(int(bonus_count)):
        bonus_cell_key = get_bonus_cell_ind(cells, bonus > 0)
        try:
            cells[bonus_cell_key]['bonus'] += bonus
        except KeyError:
            print 'Something went wrong while Balancing'
            cells[bonus_cell_key]['bonus'] = bonus
            # TODO: Uncomment here after debugging
            # raise Exception('Something went wrong while Balancing')

def _make_equal_bonus_fix(parent_cell, child_cells):

    """
    Caution. This method changes the input objects
    it doesnt changes the keys of input parameters, just adds bonuses which guarantees that val sums with bonuses are equal
    :param parent_cell: parent cell
    :param child_cells: array of cells
    :return:
    """
    accuracy = 0
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
            split_bonus(total_bonus, child_cells, accuracy)

    #         TODO: MAKE FIXED CHILDS IF NOT FAULT
        for cll in child_cells:
            cll['fixed'] = True
    else:
        parent_cell['bonus'] = child_sum - parent_cell['val']
        parent_cell['fixed'] = True


def modify_settings(settings):
    mod_settings = {1: {}, -1: {}, 'lvls': [1, ]}
    for f in settings:
        if not settings[f].has_key('balance_lvl'): continue
        lvl_key = settings[f]['balance_lvl']
        b_by_key = settings[f]['balance_by']
        if not mod_settings.has_key(lvl_key):
            mod_settings[lvl_key] = {}
        if not mod_settings[lvl_key].has_key(b_by_key):
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


def prepare_matrix(matr):
    for row in matr:
        for field in matr[row]:
            try:
                matr[row][field]['bonus'] = 0
                matr[row][field]['fixed'] = False
            except KeyError:
                raise Exception('Get wrong cell data during balancing!')
            except Exception:
                raise Exception('Get wrong cell data during balancing!')


def run_as_balancer(_maian_exp, _f_settings, _r_settings):
    field_settings = modify_settings(_f_settings)
    row_settings = modify_settings(_r_settings)


def run_asv_balancer(_maian_exp, _f_settings, _r_settings):
    field_settings = modify_settings(_f_settings)
    row_settings = modify_settings(_r_settings)


def run_b_balancer(_main_exp, _f_settings, _r_settings):
    field_settings = modify_settings(_f_settings)
    row_settings = modify_settings(_r_settings)
    prepare_matrix(_main_exp)
    try:
        _main_exp['25']['total']['bonus'] = _main_exp['by_SHAPE']['total']['val'] - _main_exp['25']['total']['val']
        _main_exp['25']['total']['fixed'] = True
    except KeyError:
        print 'Balancing Failed. No sense to balance without by_SHAPE or 25 row key'
        return _main_exp
    #TODO: Add by_SHAPE row to * array

    def run_matrix_clockwise_balancing(base_r, depend_rs, base_f, depend_fs):
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
            p_cell = _main_exp[row_key][base_f]
            ch_cells = []
            for f_key in depend_fs:
                try:
                    ch_cells.append(_main_exp[row_key][f_key])
                except KeyError:
                    print 'Fail on first clockwise balancing phase'
            _make_equal_bonus_fix(p_cell, ch_cells)

    # 2...balancing_matrix_stage_2 collecting fixed fields from previous step to total row
        for f_key in depend_fs:
            p_cell = _main_exp[base_r][f_key]
            ch_cells = []
            for row_key in depend_rs:
                try:
                    ch_cells.append(_main_exp[row_key][f_key])
                except KeyError:
                    print 'Fail on second clockwise balancing phase'
            _make_equal_bonus_fix(p_cell, ch_cells)

    # 3...balancing_matrix_stage_3 asserting fields by total in base row
        p_cell = _main_exp[base_r][base_f]
        ch_cells = []
        for f_key in depend_fs:
            try:
                ch_cells.append(_main_exp[base_r][f_key])
            except KeyError:
                print 'Fail on third clockwise balancing phase'

        if _assert_equal(p_cell, ch_cells):
            print 'BLOCK OK'
        else:
            print 'FAILED'
            # raise Exception('Balabcing failed. Please check your input')

    def run_matrix_anticlockwise_balancing(base_r, depend_rs, base_f, depend_fs):
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
        p_cell = _main_exp[base_r][base_f]
        ch_cells = []
        for f_key in depend_fs:
            try:
                ch_cells.append(_main_exp[base_r][f_key])
            except KeyError:
                print 'Fail on first anticlockwise balancing phase'

                # ch_cells = _f_settings[field_stage][lvl_f_key].map(lambda x: _main_exp[base_row][x])
                # TODO: debug this lambda not to change _main_exp
        _make_equal_bonus_fix(p_cell, ch_cells)


    # 2...balancing_matrix_stage_2 balancing fixed fields from previous step by depend rows
        for f_key in depend_fs:
            p_cell = _main_exp[base_r][f_key]
            ch_cells = []
            for row_key in depend_rs:
                try:
                    ch_cells.append(_main_exp[row_key][f_key])
                except KeyError:
                    print 'Fail on second anticlockwise balancing phase'
            _make_equal_bonus_fix(p_cell, ch_cells)

    # 3...balancing_matrix_stage_3 making total field of every depend row to fixed
        for row_key in depend_rs:
            p_cell = _main_exp[row_key][base_f]
            ch_cells = []
            for f_key in depend_fs:
                try:
                    ch_cells.append(_main_exp[row_key][f_key])
                except KeyError:
                    print 'Fail on third anticlockwise balancing phase'
            _make_equal_bonus_fix(p_cell, ch_cells)

    # 4...balancing_matrix_stage_4 asserting the results; should be balanced
        p_cell = _main_exp[base_r][base_f]
        ch_cells = []
        for row_key in depend_rs:
            try:
                ch_cells.append(_main_exp[row_key][base_f])
            except KeyError:
                print 'Fail on fourth anticlockwise balancing phase'

        if _assert_equal(p_cell, ch_cells):
            print 'BLOCK OK'
        else:
            print 'FAILED'
            # raise Exception('Balabcing failed. Please check your input')

    def run_matrix_balancing_by_base_row(base_row, depend_rows, is_first_lvl = False):
        for field_stage in field_settings['lvls']:
            for lvl_f_key in field_settings[field_stage]:
                # if is_first_lvl:
                #     run_matrix_anticlockwise_balancing(base_row, depend_rows, lvl_f_key, field_settings[field_stage][lvl_f_key])
                #     continue
                # TODO: You can use this to upgrade performance
                base_fields_fixed = True #need clockwise balancing
                for row in depend_rows:
                    if not _main_exp[row][lvl_f_key]['fixed']:
                        base_fields_fixed = False
                        break

                if base_fields_fixed:
                    run_matrix_clockwise_balancing(
                        base_row,
                        depend_rows,
                        lvl_f_key,
                        field_settings[field_stage][lvl_f_key]
                    )
                else:
                    run_matrix_anticlockwise_balancing(
                        base_row,
                        depend_rows,
                        lvl_f_key,
                        field_settings[field_stage][lvl_f_key]
                    )

    for row_stage in row_settings['lvls']:
        for lvl_r_key in row_settings[row_stage]:
            if lvl_r_key == '*':
                print 'Not matrix balancing'
                #TODO: run balancing by fields only for one row of rows in _r_settings['*'] array
            else:
                if row_settings['lvls'].index(row_stage) == 0: #first stage
                    try:
                        #setting base cells for first step fixed
                        first_f_lvl_key = field_settings['lvls'][0] # should be equal to 1
                        for main_f_key in field_settings[first_f_lvl_key]:
                            _main_exp[lvl_r_key][main_f_key]['fixed'] = True
                    except KeyError:
                        raise Exception('Failed on setting main cells to fixed')

                run_matrix_balancing_by_base_row(lvl_r_key, row_settings[row_stage][lvl_r_key])



if __name__ == '__main__':
    print 'Not a runnable file. Contains just balancing methods'
    # n_sum = sum(li)
    # print n_sum
    # print sum(balance_list(5, n_sum+5, li))