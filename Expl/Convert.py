#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyodbc
from Sprav import DBConn

ct = u'crostab_razv'
def add_column(connection, tabname, colname, coltype=u'int Null'):
    connection.exec_query(u'ALTER TABLE %s DROP "%s";' % (tabname, colname))
    sql = u'ALTER TABLE %s ADD %s %s ;'%(tabname, colname, coltype)
    connection.exec_query(sql, True)

def make_nptype(kod, npt_sprav):
    for row in npt_sprav:
        if int(kod[0]) == 5:
            return row[6]
        elif int(kod[1]) == row[1]:
                if row[2] <= int(kod[4:7]) <= row[3] or row[3] is None:
                    if row[4] <= int(kod[7:10]) <= row[5] or row[4] is None:
                        return row[6]

def upd_soato_tnp(table, f_kod, zn1, zn2, zn57min, zn57max, zn810min, zn810max, typenp):
    sqlupdnp = u'update %s set NPType = %s where mid(%s, 1, 1) in (%s)'%(table, typenp, f_kod, zn1)
    if zn2 is not  None:
        sqlupdnp += u' and mid(%s, 2, 1) = %s' % (f_kod, zn2)
    if zn57min is not None and zn57max is not None:
        sqlupdnp += u' and (mid(%s, 5, 3) between %s and %s)' % (f_kod, zn57min, zn57max)
    if zn810min is not None or zn810max is not None:
        sqlupdnp += u' and (mid(%s, 8, 3) between %s and %s)' % (f_kod, zn810min, zn810max)
    return sqlupdnp


def add_utype_partn(connection):
    n = 1
    while True:
        un = unicode(n)
        #---------------------------UserType_n----------------------------------------------
        add_column(connection, ct, u'UserType_%s' % un)
        sql1 = u'''UPDATE Users INNER JOIN %(t)s ON Users.UserN = %(t)s.usern_%(nn)s
                    SET %(t)s.Usertype_%(nn)s = [Users].[UserType];''' % {u't': ct, u'nn': un}
        # sql2 = u'''UPDATE Users INNER JOIN %(t)s ON Users.UserN = %(t)s.UserN_Sad
        #             SET %(t)s.Usertype_%(nn)s = [Users].[UserType],
        #                 %(t)s.UserN_%(nn)s = %(t)s.[UserN_Sad]
        #             WHERE %(t)s.UserN_%(nn)s is not null
        #                     and %(t)s.UserN_Sad is not null
        #                     and SLNAD = 2 ;''' % {u't': ct, u'nn': un}
        connection.exec_query(sql1)
        #---------------------------PART_n----------------------------------------------
        add_column(connection, ct, u"Area_%s" % un, u'DOUBLE NULL')
        sqlarea = u'''UPDATE %(t)s
                    SET Area_%(nn)s = (Part_%(nn)s/100)*[Shape_Area]
                    WHERE Part_%(nn)s <> 0''' % {u't': ct, u'nn': un}
        connection.exec_query(sqlarea)
        n += 1
        if not connection.exec_sel_query(u'SELECT UserN_%s FROM %s;' % (unicode(n), ct)):
            break
    return n-1

def convert_soato(connection):
    add_column(connection, u'SOATO', u'NameSov', u'varchar(80) NULL')
    add_column(connection, u'SOATO', u'NameNasp', u'varchar(80) NULL')
    updnamenasp1 = u'''update SOATO set NameNasp = NAME +' '+PREF where PREF in ('р-н','с/с');'''
    updnamenasp2 = u'''update SOATO set NameNasp = PREF +' '+ NAME where  NameNasp is Null;'''
    connection.exec_query(updnamenasp1)
    connection.exec_query(updnamenasp2)


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

class CtrRow(object):
    def __init__(self, r_args, n_dop_args, nm, sprav):
        """
        :param r_args: OBJECTID, SOATO, SlNad, State_1, LANDCODE, MELIOCODE, ServType08, F22_*, UserN_*,Usertype_*, Area_*, *dop_params
        :param n_dop_args: len of dop params array in the end of r_args
        :param nm: max number of parts in crostab table
        :param sprav: SpravHolder instance
        """
        self.has_err = False                # отанется False - контроль пройден,
        # 1 - ошибки при доле 100%,
        # 2 - ошибки при долях, не нашлось соответствий с bgd1, bgd2;
        # 3 - сброс всех параметров,ошибка new_state при долях
        # 4 - не сформирован soato

        self.object_id = r_args[0]
        self.soato = r_args[1]
        self.np_type = make_nptype(self.soato, sprav.soato_npt)
        if self.np_type is None:
            self.has_err = 4
            return
        self.spr_bgd_1 = sprav.bgd2ekp_1
        self.spr_bgd_2   = sprav.bgd2ekp_2
        self.slnad = r_args[2]
        self.state = r_args[3]
        self.lc = r_args[4]
        self.mc = r_args[5]
        self.st08 = r_args[6]
        self.f22 = r_args[7:nm+7]
        self.n = 0
        while self.f22[self.n]:
            self.n+=1
        self.f22 = list(self.f22[:self.n])
        self.usern = list(r_args[nm+7:nm+7+self.n])
        self.utype = list(r_args[2*nm+7:2*nm+7+self.n])
        self.area = list(r_args[3*nm+7:3*nm+7+self.n])
        if n_dop_args:self.dop_args = r_args[-n_dop_args:]
        else:
            self.dop_args = []
        self.new_state = None
        self.new_lc = None
        self.old_changed_state = None
        self.old_changed_lc = None
        self.dopname = [None]*self.n
        self.nusname = [None]*self.n
        self.bgd_control()

    def has_code(self, n, param, codes):
        if param == u'f22':
            if self.f22[n] == codes: return True
        else:
            if param == u'melio':
                if self.mc in codes: return True
            if param == u'srvtype':
                if self.st08 in codes: return True
            if param == u'nptype':
                if self.np_type in codes: return True
            if param == u'slnad':
                if self.slnad in codes: return True
            if param == u'state':
                if self.state in codes: return True
            if u'dop_f' in param:
                param = param[5:]
                try:
                    param = int(param)
                    if self.dop_args[param] in codes: return True
                except (ValueError, IndexError): return False
            else: return False

    def bgd_control(self):
        if self.n == 1:
            if self.bgd1_control(0):
                pass
            elif self.bgd2_control(0):
                if self.new_state is not None:
                    self.change_state()
                if self.new_lc is not None:
                    self.change_lc()
            else:
                self.has_err = 1
        else:
            bgd1_failed = []
            for n in range(self.n):
                if not self.bgd1_control(n):
                    bgd1_failed.append(n)
            if bgd1_failed:
                for n in bgd1_failed:
                    if self.bgd2_control(n):
                        if self.new_lc is not None:
                            self.change_lc()
                        if self.new_state is not None:
                            self.has_err = 3
                            break
                    else:
                        self.has_err = 2
                        break

    def change_lc(self):
        self.old_changed_lc = self.lc
        self.lc = self.new_lc

    def change_state(self):
        self.old_changed_state = self.state
        self.state = self.new_state

    def bgd1_control(self, nn):
        try:
            bgd_li = self.spr_bgd_1[self.f22[nn]][self.utype[nn]][self.state][self.slnad]
            for b_row in bgd_li:  # bgd_row: f22 > UTYPE > State > SLNAD > NPTYPE_min, NPTYPE_max,  NEWUSNAME, DOPUSNAME,
                if b_row[0] <= self.np_type <= b_row[1]:
                    self.nusname[nn] = b_row[2]
                    self.dopname[nn] = b_row[3]
                    return True
        except KeyError:
            pass
        return False

    def bgd2_control(self, nn):
        try:
            bgd_li = self.spr_bgd_2[self.f22[nn]][self.utype[nn]][self.state][self.slnad]
            for b_row in bgd_li: # bgd_row: newF22(0), NPTYPE_min (1), NPTYPE_max (2), lc_min(3), lc_max(4), newlc(5),  newstate(6),  NEWUSNAME(7), DOPUSNAME(8)
                if b_row[1] <= self.np_type <= b_row[2] \
                        and b_row[3] <= self.lc <= b_row[4]:
                    self.f22[nn]  = b_row[0]
                    self.nusname[nn] = b_row[7]
                    self.dopname[nn] = b_row[8]

                    self.new_lc, self.new_state = b_row[5], b_row[6]
                    return True
        except KeyError:
            pass
        return False

def for_query(field, count):
    fields = u''
    for i in range(1,count+1):
        fields += u'%s%s, ' % field, i
    return fields[:-2]

def convert(sprav_holder, temp_db_path):
    ctr_conn = DBConn(temp_db_path)
    convert_soato(ctr_conn)
    n_max = add_utype_partn(ctr_conn)

    def make_fields_str(f_name, col = n_max):
        s = u''
        for n in range(col):
            s+=u'%s%d,' % (f_name, n+1)
        return s[:-1]

    cr_tab_fields = ctr_conn.get_f_names(ct)
    select_ctr_all = u'select OBJECTID, SOATO, SlNad, State_1, LANDCODE, MELIOCODE, ServType08, %s, %s, %s, %s' % \
                     (make_fields_str(u'F22_'),make_fields_str(u'UserN_'),make_fields_str(u'Usertype_'),make_fields_str(u'Area_'))
    dop_fields = []
    for field in sorted(cr_tab_fields):
        if 'Dop' in field:
            dop_fields.append(field)
    dop_f_count = len(dop_fields)
    if dop_f_count:
        dop_fields = u','.join(dop_fields)
        select_ctr_all+=u','+dop_fields
    select_ctr_all += u' from %s' % ct
    rows_ok, rows_failed, = [],[]
    select_result = ctr_conn.exec_sel_query(select_ctr_all)

    whats_err = {}
    if select_result:
        for row in select_result:
            new_row = CtrRow(row, dop_f_count,  n_max, sprav_holder )       #row[0], row[1], row[2], row[3],row[4], row[5:n_max+5], row[n_max+5:]
            if new_row.has_err:
                rows_failed.append(new_row)
            else:
                rows_ok.append(new_row)
        del ctr_conn

        err_dict = dict()

        for err_row in rows_failed:
            try:
                whats_err[err_row.has_err].append(err_row.object_id)
            except KeyError:
                whats_err[err_row.has_err] = [err_row.object_id, ]

        print whats_err
        users_d, soato_d = data_users_soato(temp_db_path)
        save_info = [rows_ok, users_d, soato_d]
        if whats_err:
            return whats_err
        else:
            return save_info
        # return save_info
    else:
        raise Exception('Ошибка при загрузке данных из crostab. Connection failed')


def data_users_soato(db_f):
    """
    returns UsersDict and SoatoDict with keys usern and soato
    and values in unicode
    """
    ct_conn = DBConn(db_f)
    if ct_conn.has_dbc:
        sel_result = ct_conn.exec_sel_query(u'select UserN, UsName from Users')
        users_dict = dict(sel_result)
        sel_result = ct_conn.exec_sel_query(u'select KOD, NameNasp from SOATO')
        soato_dict = dict(sel_result)
        return users_dict, soato_dict
    else:
        #TODO: Remake exception
        print u'Error with connecting to crtab database'

def make_soato_group(s_kods):
    soato_group = {}
    ate_soato = []
    for s in s_kods:
        ate_key = s_kods[:-3]
        if not s_kods[-3:] == '000':
            try:
                soato_group[ate_key].append(s_kods)
            except KeyError:
                soato_group[ate_key] = [s_kods]
        else:
            ate_soato.append(ate_key)
        for soato in ate_soato:
            if soato not in soato_group.keys():
                soato_group[soato] = []
    return soato_group

if __name__ == u'__main__':
    npt_sprav = [(u'1,2,3,4,6,7', 2, 801, 900, 900, 999, 2),
                 (u'5', None, None, None, None, None, 1),
                 (u'1,2,3,4,6,7', 4, 0, 550, None, None, 1),
                 (u'1,2,3,4,6,7', 4, 551, 750, None, None, 2),
                 (u'1,2,3,4,6,7', 4, 751, 999, None, None, 3),
                 (u'1,2,3,4,6,7', 2, 0, 0, None, None, 0),
                 (u'1,2,3,4,6,7', 2, 1, 550, None, None, 1),
                 (u'1,2,3,4,6,7', 2, 551, 700, None, None, 2),
                 (u'1,2,3,4,6,7', 2, 701, 900, 1, 999, 3),
                 (u'1,2,3,4,6,7', 2, 701, 800, 0, 0, 0),
                 (u'1,2,3,4,6,7', 2, 801, 900, 0, 0, 0)]
    res = make_nptype(u'3223904003', npt_sprav)
    print res