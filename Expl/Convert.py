#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyodbc
from Control import work_dir

ct = u'crostab_razv'
def add_column(connection, tabname, colname, coltype=u'int Null'):
    try:
        connection.execute(u'ALTER TABLE %s DROP COLUMN "%s";' % (tabname, colname))
    except pyodbc.Error:
        pass
    connection.execute(u'ALTER TABLE %s ADD column %s %s ;'%(tabname, colname, coltype))


def load_npt_sprav():
    sprav = u'%s\\Spravochnik.mdb' % work_dir
    sprav_db = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' % sprav
    selectrows = u'select znak1,znak2,znak57min,znak57max,znak810min,znak810max,TypeNP from SOATO'
    nptcon = pyodbc.connect(sprav_db, autocommit=True, unicode_results=True)
    npt_dbc = nptcon.cursor()
    global npt_sprav
    npt_sprav = [row for row in npt_dbc.execute(selectrows)]


def make_nptype(kod):
    np_s = npt_sprav
    for row in np_s:
        if int(kod[0]) == 5:
            return row[6]
        elif int(kod[1]) == row[1]:
                if row[2] <= int(kod[4:7]) <= row[3] or row[3] is None:
                    if row[4] <= int(kod[7:10]) <= row[5] or row[4] is None:
                        return row[6]

def  upd_soato_tnp(table, f_kod, zn1, zn2, zn57min, zn57max, zn810min, zn810max, typenp):
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
        sql2 = u'''UPDATE Users INNER JOIN %(t)s ON Users.UserN = %(t)s.UserN_Sad
                    SET %(t)s.Usertype_%(nn)s = [Users].[UserType],
                        %(t)s.UserN_%(nn)s = %(t)s.[UserN_Sad]
                    WHERE %(t)s.UserN_%(nn)s is not null
                            and %(t)s.UserN_Sad is not null
                            and SLNAD = 2 ;''' % {u't': ct, u'nn': un}
        connection.execute(sql1)
        # try:
        #     connection.execute(sql2)
        # except pyodbc.Error:
        #     print u'Возможно, нету поля UserN_Sad?'
        #---------------------------PART_n----------------------------------------------
        add_column(connection, ct, u"Area_%s" % un, u'DOUBLE NULL')
        sqlarea = u'''UPDATE %(t)s
                    SET Area_%(nn)s = (Part_%(nn)s/100)*[Shape_Area]
                    WHERE Part_%(nn)s <> 0''' % {u't': ct, u'nn': un}
        connection.execute(sqlarea)
        n += 1
        try:
            connection.execute(u'SELECT UserN_%s FROM %s;' % (unicode(n), ct))
        except pyodbc.Error:
            break
    return n-1

def convert_soato(connection):
    add_column(connection, u'SOATO', u'NameSov', u'varchar(80) NULL')
    add_column(connection, u'SOATO', u'NameNasp', u'varchar(80) NULL')
    # add_column(connection, u'SOATO', u'NameSNp', u'varchar(150) NULL')
    # sqlsoato = u'''select mid(KOD,1,7), [NAME], PREF from SOATO where mid(KOD,8,3) = '000';'''
    # updnamesov = u'''update SOATO set NameSov = ?+' '+?+' ' where mid(KOD,1,7) = ? ;'''
    updnamenasp1 = u'''update SOATO set NameNasp = NAME +' '+PREF where PREF in ('р-н','с/с');'''
    updnamenasp2 = u'''update SOATO set NameNasp = PREF +' '+ NAME where  NameNasp is Null;'''
    # updnamesnp = u'''update SOATO set NameSNp = IIF(isNull(NameSov), NameNasp, NameSov + NameNasp)'''
    # connection.execute(sqlsoato)
    # sov_kods = [row for row in connection.fetchall()]
    # for i in sov_kods:
    #     connection.execute(updnamesov, (i[1], i[2], i[0]))
    connection.execute(updnamenasp1)
    connection.execute(updnamenasp2)
    # add_column(connection, u'SOATO', u'NPType')
    # for row in npt_sprav:
    #     sqltnp = upd_soato_tnp(u'SOATO', u'KOD', *row)
    #     connection.execute(sqltnp)
    # connection.execute(updnamesnp)

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
    def __init__(self, r_args, nm):  #r_args: OBJECTID, SOATO, SlNad, State_1, LANDCODE, MELIOCODE, ServType08, F22_*, UserN_*,Usertype_*, Area_*,
        self.has_err = False                # False - контроль пройден,
                                            # 1 - ошибки при доле 100%,
                                            # 2 - ошибки при долях, не нашлось соответствий с bgd1, bgd2;
                                            # 3 - сброс всех параметров,ошибка new_state при долях
        self.object_id = r_args[0]
        self.soato = r_args[1]
        self.np_type = make_nptype(self.soato)
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
        self.new_state = False
        self.new_lc = False
        self.state_changed = False
        self.lc_changed = False
        self.dopname = [None]*self.n
        self.nusname = [None]*self.n


    def bgd_control(self):
        if self.n == 1:
            if self.bgd1_control(0):
                pass
            elif self.bgd2_control(0):
                if self.new_state:
                    self.change_state()
                if self.new_lc:
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
                        if self.new_lc:
                            self.change_lc()
                        if self.new_state:
                            self.reset_bgd_args()
                            break
                    else:
                        self.has_err = 2

    def change_lc(self):
        self.lc_changed = self.lc
        self.lc = self.new_lc
    def change_state(self):
        self.state_changed = self.state
        self.state = self.new_state
    def reset_bgd_args(self):
        self.dopname = [None]*self.n
        self.nusname = [None]*self.n
        self.has_err = 3

    def bgd1_control(self, nn):
        try:
            bgd_li = bgd_1[self.f22[nn]][self.utype[nn]][self.state][self.slnad]
            for b_row in bgd_li:  # bgd_row: f22 > UTYPE > State > SLNAD > NPTYPE_min, NPTYPE_max,  NEWUSNAME, DOPUSNAME,
                if b_row[0] <= self.np_type <= b_row[1]:
                    self.nusname[nn] = b_row[2]
                    self.dopname[nn] = b_row[3]
                    # self.after_control = 1
                    return True
        except KeyError:
            pass
        return False

    def bgd2_control(self, nn):
        try:
            bgd_li = bgd_2[self.f22[nn]][self.utype[nn]][self.state][self.slnad]
            for b_row in bgd_li: # bgd_row: newF22(0), NPTYPE_min (1), NPTYPE_max (2), lc_min(3), lc_max(4), newlc(5),  newstate(6),  NEWUSNAME(7), DOPUSNAME(8)
                if b_row[1] <= self.np_type <= b_row[2] \
                        and b_row[3] <= self.lc <= b_row[4]:
                    self.f22[nn]  = b_row[0]
                    self.nusname[nn] = b_row[7]
                    self.dopname[nn] = b_row[8]
                    self.new_lc, self.new_state = b_row[5],b_row[6]
                    return True
        except KeyError:
            pass
        return False

def for_query(field, count):
    fields = u''
    for i in range(1,count+1):
        fields += u'%s%s, ' % field, i
    return fields[:-2]

def convert(soursedbf, bgd2e_li):
    global bgd_1, bgd_2
    bgd_1 = bgd_to_dicts(bgd2e_li[0])
    bgd_2 = bgd_to_dicts(bgd2e_li[2])
    db_file = soursedbf
    load_npt_sprav()
    dbc_ctr,conn_ctr = connect_crtab(db_file)
    n_max = add_utype_partn(dbc_ctr)
    convert_soato(dbc_ctr)

    def many_fields_str(f_name, col = n_max):
        s = u''
        for n in range(col):
            s+=u'%s%d,' % (f_name, n+1)
        return s[:-1]
    select_ctr_all = u'''select OBJECTID, SOATO, SlNad, State_1, LANDCODE, MELIOCODE, ServType08,
    %s, %s, %s, %s from %s''' % (many_fields_str(u'F22_'),many_fields_str(u'UserN_'),many_fields_str(u'Usertype_'),many_fields_str(u'Area_'),ct)
    rows_ok = []
    rows_failed = []
    save_rows = []
    for row in dbc_ctr.execute(select_ctr_all):
        new_row = CtrRow(row, n_max)       #row[0], row[1], row[2], row[3],row[4], row[5:n_max+5], row[n_max+5:]
        new_row.bgd_control()
        if new_row.has_err:
            rows_failed.append(new_row)
        else:
            rows_ok.append(new_row)
            save_rows.append(row)
    disconnect_crtab(dbc_ctr,conn_ctr)

    err_dict = dict()
    whats_err = {1 : [], 2 : [], 3 : []}
    for err in rows_failed:
        for n in range(err.n):
            if not err.nusname[n]:
                try:
                    err_dict[n+1].append(err.object_id)
                except KeyError:
                    err_dict[n+1] = [err.object_id,]
        whats_err[err.has_err].append(err.object_id)
    print whats_err
    users_d, soato_d = data_users_soato(db_file)
    save_info = [rows_ok, users_d, soato_d]
    return {}, save_info  #err_dict

def connect_crtab(db_f):
    try:
        work_db = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' % db_f
        conn = pyodbc.connect(work_db, autocommit=True, unicode_results=True)
        dbc = conn.cursor()
        return dbc, conn
    except:
        return False, False

def disconnect_crtab(dbc, conn):
    try:
        dbc.close()
        conn.close()
    except: pass

def data_users_soato(db_f):
    """
    returns UsersDict and SoatoDict with keys usern and soato
    and values in unicode
    """
    ct_dbc,conn_ct = connect_crtab(db_f)
    if ct_dbc:
        ct_dbc.execute(u'select UserN, UsName from Users')
        sel_result = [row for row in ct_dbc.fetchall()]
        users_dict = dict(sel_result)
        ct_dbc.execute(u'select KOD, NameNasp from SOATO')
        sel_result = [row for row in ct_dbc.fetchall()]
        soato_dict = dict(sel_result)
        disconnect_crtab(ct_dbc,conn_ct)
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

if __name__ == '__main__':
    dbf_file = u'%s\\tempDbase.mdb' % work_dir
    load_npt_sprav()
    print npt_sprav




