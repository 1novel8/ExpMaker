#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

li1 = [[2941766.8860134804, 886.79595366918, 779.58821893535, 86.2505280796191, 2930138.63968789, 3081.57325414444, 6794.03837076164],
       [10810889.550832964, 3214.20173861995, 614.91408782033, 1057262.79739716, 6457.27703173003, 9743072.58100759, 267.7795700432],
       [12411732.474104717, 481.893555435379, 55.7787204987318, 3808656.57925138, 357.88229970823, 8596380.72654963, 5799.61372806483],
       [10016049.824814899, 9864667.05248715, 20395.7937766741, 46689.6240508603, 30549.0740155624, 42835.8364938752, 10912.4439907763],
       [2637101.695419007, 2095776.29412423, 299.22340413854, 191.119897769249, 1994.50579923185, 195457.241098326, 343383.311095311],
       [3896913.373186771, 327.351092218808, 1973614.82451198, 1901289.8151775, 18263.8089345062, 1388.99232770628, 2028.58114285974],
       [1921909.556347085, 327.351092218808, 0, 1901289.8151775, 18263.8089345062, 0, 2028.58114285974],
       [44636363.360641, 11965680.94, 1995760.12272, 8715466.00148, 3006024.9967, 18582216.9507, 371214.349041]]
li = [1196560.94, 1995760.122720047, 779.58821893535,0, 86.2505280796191, 0, 0, 2930.63968789]
def balance_list(d, need_sum, after_round_li, round_to = 4, iters = 15):
    low_discr = 10**-(round_to-1)
    discr = d
    iters_left = iters
    do = after_round_li[:]
    while math.fabs(discr) > low_discr:
        after_round_li = map(lambda x: round(x+x*discr/need_sum, round_to) if x>1 else x, after_round_li)
        discr = need_sum - sum(after_round_li)
        iters_left -= 1
        if not iters_left:break
    add_discr_to_max(after_round_li, round(discr, round_to))
    print do
    print after_round_li
    return after_round_li

def add_discr_to_max(li, discr):
    li[li.index(max(li))] += discr
    return li


if __name__ == '__main__':

    n_sum = sum(li)
    print n_sum
    print sum(balance_list(5, n_sum+5, li))


# def recountExp(edbdir):
#     expdbf = u'%s\Explication.mdb' % edbdir
#     disp = countDisp(expdbf)
#     i = 0
#     while  math.fabs(disp) > 0.0002:
#         addColumn(expdbf, u'EXPLICATIONALL', u'f_disp', u'double Null')
#         adddisp = disp/sum_crtab
#         sumupd = u'update EXPLICATIONALL set f_1 = round((f_1 + f_1*%s),4), f_disp = f_1*%s where f_RowNumber = 1 ' % (adddisp, adddisp)
#         runQuery(expdbf, sumupd)
#         disp = countDisp(expdbf)
#         i+=1
#         if i == 10:
#             '''
#             TODO:
#             Need to make window for asking in GUI
#             '''
#             print u'Произведено 10 итераций распределения невязки. Продолжить?'
