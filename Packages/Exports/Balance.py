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



def _make_equal_bonus_fix(parent_cell, child_cells):

    """
    Caution. This method changes the input objects
    it doesnt changes the keys of input parameters, just adds bonuses which guarantees that val sums with bonuses are equal
    :param parent_cell: parent cell
    :param child_cells: array of cells
    :return:
    """
    accuracy = 0
    def guarantee_keys(cll):
        if not isinstance(cll, dict):
            raise Exception('Get wrong cell data during balancing!')
        if not cll.has_key('bonus'):
            cll['bonus'] = 0
        if not cll.has_key('fixed'):
            cll['fixed'] = False


    def get_bonus_cell_ind(cells, is_positive):
        current_wins = lambda last_winner, current: last_winner < current if is_positive else last_winner > current

        def run_bonus_competition(cell_ind_array, competition_by ='tail'):
            winner_tail_i = cell_ind_array[0]
            for i in cell_ind_array[1:]:
                if current_wins(cells[winner_tail_i][competition_by], cells[i][competition_by]):
                    winner_tail_i = i
            return winner_tail_i


        def get_inds_without_key(key):
            inds_without_key = []
            for ind in xrange(len(cells)):
                if key in cells[ind]:
                    inds_without_key.append(ind)
            return inds_without_key

        winner_i = run_bonus_competition(range(len(cells)))
        winner_cell = cells[winner_i]
        if 'bonus' not in winner_cell and 'fixed' not in winner_cell:
            return winner_i # seems all ok
        else:
            no_bonus_items = get_inds_without_key('bonus')
            if len(no_bonus_items):
                if len(no_bonus_items) < len(cells): # still ok
                    winner_i = run_bonus_competition(no_bonus_items)
                else: #all cells has bonuses
                    winner_i = run_bonus_competition(range(len(cells)), 'val')
                if 'fixed' not in cells[winner_i]:
                    return winner_i # it is possible
                else:
                    no_fixed_items = get_inds_without_key('fixed')
                    if len(no_fixed_items) < len(cells):
                        return run_bonus_competition(no_fixed_items, 'val')

            pass  # problem in fixed statement (all fixed)
            print 'Seems something went wrong, you have tried to give bonus for fixed cell'


    def split_bonus(bonus, cells):
        try:
            bonus_count = math.fabs(bonus/accuracy)
        except ZeroDivisionError:
            bonus_count = math.fabs(bonus)
        bonus /= bonus_count
        for bonusInd in xrange(bonus_count):
            bonus_cell_key = get_bonus_cell_ind(cells, bonus > 0 )
            try:
                cells[bonus_cell_key]['bonus'] += bonus
            except KeyError:
                print('Something went wrong while Balancing')
                cells[bonus_cell_key]['bonus'] = bonus

    child_sum = 0
    guarantee_keys(parent_cell)
    parent_val = parent_cell['val'] + parent_cell['bonus']
    for cell in child_cells:
        guarantee_keys(cell)
        child_sum += cell['val'] + cell['bonus']

    if parent_cell['fixed']:
        total_bonus = round(parent_val - child_sum, accuracy)
        if total_bonus == 0:
            return
        else:
            split_bonus(total_bonus, child_cells)
    else:
        parent_cell['bonus'] = child_sum - parent_cell.val
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

def run_as_balancer(_maian_exp, _f_settings, _r_settings):
    field_settings = modify_settings(_f_settings)
    row_settings = modify_settings(_r_settings)

def run_asv_balancer(_maian_exp, _f_settings, _r_settings):
    field_settings = modify_settings(_f_settings)
    row_settings = modify_settings(_r_settings)


def run_b_balancer(_main_exp, _f_settings, _r_settings):
    field_settings = modify_settings(_f_settings)
    row_settings = modify_settings(_r_settings)
    try:
        _main_exp['25']['bonus'] = _main_exp['by_SHAPE']['total'] - _main_exp['25']['total']
        _main_exp['25']['fixed'] = True
    except KeyError:
        print 'Balancing Failed. No sense to balance without by_SHAPE or 25 row key'
        return _main_exp
    #TODO: Add by_SHAPE row to * array

    def run_matrix_balancing_by_base_row(base_row, depend_rows):
        for field_stage in _f_settings['lvls']:
            for lvl_f_key in _f_settings[field_stage]:
                # 1...balancing_matrix_stage_1 balancing fields by total
                p_cell = _main_exp[base_row][lvl_f_key]

                ch_cells = []
                for f_key in _f_settings[field_stage][lvl_f_key]:
                    try:
                        ch_cells.append(_main_exp[base_row][f_key])
                    except KeyError:
                        print 'Fail on first balancing phase'
                # ch_cells = _f_settings[field_stage][lvl_f_key].map(lambda x: _main_exp[base_row][x])
                #TODO: debug this lambda not to change _main_exp
                _make_equal_bonus_fix(p_cell, ch_cells)
                # 2...balancing_matrix_stage_2 balancing fixed fields from previous step by depend rows
                #TODO: write another steps
                # 3...balancing_matrix_stage_3 making total field of every depend row to fixed
                        # something like :
                        # if _main_exp[depend_row][total][fixed]:
                        #     anther algorythm
                        # else:
                        #     the same one
                    # two different algorythms, wether total field of depend rows is fixed
                    # (to be sure make main def to return success or fail_key if all parameters cells are fixed)
                # 4...balancing_matrix_stage_4 asserting the results; should be balanced


    for row_stage in _r_settings['lvls']:
        for lvl_r_key in _r_settings[row_stage]:
            if lvl_r_key == '*':
                print 'Not matrix balancing'
                #TODO: run balancing by fields only for one row of rows in _r_settings['*'] array
            else:
                if _r_settings['lvls'].index(row_stage) == 0: #first stage
                    try:
                        #setting base cells for first step fixed
                        first_f_lvl_key = field_settings['lvls'][0] # should be equal to 1
                        for main_f_key in field_settings[first_f_lvl_key]:
                            _main_exp[lvl_r_key][main_f_key]['fixed'] = True
                    except KeyError:
                        raise Exception('Failed on setting main cells to fixed')

                run_matrix_balancing_by_base_row(lvl_r_key, _r_settings[lvl_r_key])



if __name__ == '__main__':
    print 'Not a runnable file. Contains just balancing methods'
    # n_sum = sum(li)
    # print n_sum
    # print sum(balance_list(5, n_sum+5, li))