#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyodbc
import shutil
from Sprav import DBConn

crs_tab = u'crostab_razv'
soato_tab =u'SOATO'
users_tab = u'Users'

class DbControl(object):
    def __init__(self, file_path, tempDB_path):
        self.need_tabs = [crs_tab,soato_tab,users_tab]
        self.db_file = tempDB_path
        self.tempdb_conn = DBConn(self.db_file, False)
        shutil.copyfile(file_path, tempDB_path)

    def can_connect(self):
        self.tempdb_conn.make_connection()
        if self.temp_dbc:
            self.close_conn()
            return True
        else: return False

    def __del__(self):
        self.close_conn()

    @property
    def temp_dbc(self):
        return self.tempdb_conn.get_dbc()

    def close_conn(self):
        self.tempdb_conn.close_conn()

    def is_tables_exist(self, try_mkconn = True):
        if self.temp_dbc:
            table_names = []
            for row in self.tempdb_conn.get_tables():
                table_names.append(row[2])
            tab_not_found = []
            for tab in self.need_tabs:
                if tab not in table_names:
                    tab_not_found.append(tab)
            return tab_not_found
        elif try_mkconn:
            self.tempdb_conn.make_connection()
            return self.is_tables_exist(False)
        else:
            self.err_connect()

    def is_tables_empty(self, try_mkconn = True):
        """
        :return: Tables from __need_tabs that has no any data
        """
        if self.temp_dbc:
            no_data_in = []
            for tab in self.need_tabs:
                if not self.tempdb_conn.exec_sel_query(u'select * from %s' % tab):
                    no_data_in.append(tab)
            if no_data_in:
                return no_data_in
            else: return False
        elif try_mkconn:
            self.tempdb_conn.make_connection()
            return self.is_tables_empty(False)
        else:
            self.err_connect()

    def is_empty_f_pref(self):
        failed_obj = self.tempdb_conn.exec_sel_query(u'select OBJECTID from %s where Pref is Null' % soato_tab)
        if failed_obj:
            failed_obj = [row[0] for row in failed_obj]
            failed_obj = unicode(tuple(failed_obj))
            self.tempdb_conn.exec_query(u'delete from %s where OBJECTID in %s' %(soato_tab, failed_obj))
            return failed_obj
        else:
            return False

    @staticmethod
    def err_connect():
        raise Exception(u'Не удалось соединиться')

    def contr_field_types(self, tab_name, try_mkconn = True):
        """
            Takes 2 parameters : self and [Table Name] for current control

        TODO:
        Remake return as Dictionary
        """
        field_types = []
        if self.temp_dbc:
            for row in self.temp_dbc.columns(table= tab_name):
                field_types.append((row[3],row[5]))
            return field_types
        elif try_mkconn:
            self.tempdb_conn.make_connection()
            return self.contr_field_types(False)
        else: self.err_connect()

class DataControl(DbControl):
    def __init__(self, sprav_holder, file_path, tempDB_path):
        self.sprav_holder = sprav_holder
        super(DataControl,self).__init__(file_path, tempDB_path)
        self.is_empty_f_pref()
        self.f22_string = self.get_f22_string()

    def contr_field(self, in_str,  table, field, can_be_null = False, try_mkconn = True):
        """
        Makes dictionary with OBJECTID rows with errors
        :param bgd_table: Name of S_'TableName' in BGDtoEKP in unicode format
        :param bgd_code_field: Name of Field consists codes and located in S_'TableName', unicode format
        :param table: control table name, unicode
        :param field: control field name, unicode
        :return: dictionary with keys notin,isnull, [field] and values - OBJECTID with errors
        """
        if self.temp_dbc:
            self.temp_dbc.execute(u'select OBJECTID from %s where %s not in (%s) and %s is not Null' % (table, field, in_str, field))
            not_in_code = [row[0] for row in self.temp_dbc.fetchall()]
            if not can_be_null:
                self.temp_dbc.execute(u'select OBJECTID from %s where %s is Null' % (table, field))
                rows_is_null = [row[0] for row in self.temp_dbc.fetchall()]
                return dict(notin = not_in_code, isnull = rows_is_null, fieldname = field)
            else: return not_in_code
        elif try_mkconn:
            self.tempdb_conn.make_connection()
            return self.contr_field(in_str, table, field, try_mkconn =  False)
        else: self.err_connect()

    def contr_soato(self, try_mkconn = True):
        if self.temp_dbc:
            self.temp_dbc.execute(u'SELECT a.OBJECTID FROM crostab_razv a LEFT JOIN SOATO b ON a.SOATO = b.KOD WHERE b.KOD Is Null')
            not_in_soato_code = [row[0] for row in self.temp_dbc.fetchall()]
            self.temp_dbc.execute(u'select OBJECTID from crostab_razv where SOATO is Null')
            soato_is_null = [row[0] for row in self.temp_dbc.fetchall()]
            return dict(isnull = list(set(soato_is_null)-set(not_in_soato_code)), notin = not_in_soato_code)
        elif try_mkconn:
            self.tempdb_conn.make_connection()
            return self.contr_soato(False)
        else: self.err_connect()

    def contr_user_1(self, try_mkconn = True):
        if self.temp_dbc:
            self.temp_dbc.execute(u'SELECT a.OBJECTID FROM crostab_razv a LEFT JOIN Users b ON a.UserN_1 = b.UserN WHERE b.UserN Is Null and UserN_Sad is NULL')
            notin_user_n1 = [row[0] for row in self.temp_dbc.fetchall()]
            self.temp_dbc.execute(u'select OBJECTID from crostab_razv where UserN_1 is Null')
            usern1_is_null = [row[0] for row in self.temp_dbc.fetchall()]
            return dict(isnull = list(set(usern1_is_null)-set(notin_user_n1)), notin = notin_user_n1)
        elif try_mkconn:
            self.tempdb_conn.make_connection()
            return self.contr_user_1(False)
        else: self.err_connect()

    def contr_part_1(self, try_mkconn = True):
        if self.temp_dbc:
            self.temp_dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE not Part_1 between 0.0001 and 100')
            part1err = [row[0] for row in self.temp_dbc.fetchall()]
            self.temp_dbc.execute(u'select OBJECTID from crostab_razv where Part_1 is Null')
            part1isnull = [row[0] for row in self.temp_dbc.fetchall()]
            return dict(isnull = list(set(part1isnull)-set(part1err)), notin = part1err)
        elif try_mkconn:
            self.tempdb_conn.make_connection()
            return self.contr_part_1(False)
        else: self.err_connect()

    def contr_part(self, try_mkconn = True):
        if not self.temp_dbc:
            self.tempdb_conn.make_connection()
        if self.temp_dbc:
            part_sum = u'Part_1'
            for i in range(self.__n):
                if i>1: part_sum += u'+Part_%s' % unicode(i)
            self.temp_dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE round(%s,3) <> 100' % part_sum)
            parterr = [row[0] for row in self.temp_dbc.fetchall()]
            return parterr
        elif try_mkconn:
            self.tempdb_conn.make_connection()
            return self.contr_part(False)
        else: self.err_connect()

    def contr_user_n_sad(self, try_mkconn = True):
        if self.temp_dbc:
            self.temp_dbc.execute(u'SELECT a.OBJECTID FROM crostab_razv a LEFT JOIN Users b ON a.UserN_Sad = b.UserN WHERE b.UserN Is Null and UserN_Sad is not NULL')
            not_in_user_n1 = [row[0] for row in self.temp_dbc.fetchall()]
            return not_in_user_n1
        elif try_mkconn:
            self.tempdb_conn.make_connection()
            return self.contr_user_n_sad(False)
        else: self.err_connect()

    def contr_soato_table(self, try_mkconn = True):
        if self.temp_dbc:
            self.temp_dbc.execute(u'SELECT OBJECTID FROM SOATO WHERE KOD Is Null or Name is Null')
            is_null = [row[0] for row in self.temp_dbc.fetchall()]
            return is_null
        elif try_mkconn:
            self.tempdb_conn.make_connection()
            return self.contr_soato_table(False)
        else: self.err_connect()

    def contr_us_f22part(self, try_mkconn = True):
        if self.temp_dbc:
            n=1
            user_err = {}
            f22_err = {}
            part_err = {}
            while True:
                u_n = unicode(n)
                self.temp_dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE UserN_%(nn)s is NOT Null and (F22_%(nn)s is Null or Part_%(nn)s = 0)' % {u'nn': u_n})
                errin_user_n = [row[0] for row in self.temp_dbc.fetchall()]
                self.temp_dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE F22_%(nn)s is NOT Null and (UserN_%(nn)s is Null or Part_%(nn)s = 0)' % {u'nn': u_n})
                errin_f22 = [row[0] for row in self.temp_dbc.fetchall()]
                self.temp_dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE Part_%(nn)s <> 0 and (UserN_%(nn)s is Null or F22_%(nn)s is Null)' % {u'nn': u_n})
                errin_part_n = [row[0] for row in self.temp_dbc.fetchall()]
                if errin_user_n: user_err[n] = errin_user_n
                if errin_f22: f22_err[n] = errin_f22
                if errin_part_n: part_err[n] = errin_part_n
                try:
                    n+=1
                    self.temp_dbc.execute(u'SELECT F22_%s FROM crostab_razv;' % unicode(n))
                except pyodbc.Error :
                    return dict(UserN_ = user_err, F22_ = f22_err, Part_ = part_err)
        elif try_mkconn:
            self.tempdb_conn.make_connection()
            return self.contr_us_f22part(False)
        else: self.err_connect()

    def contr_user_n(self, try_mkconn = True):
        if self.temp_dbc:
            n=2
            not_in_usern = {}
            while True:
                u_n = unicode(n)
                self.temp_dbc.execute(u'''SELECT a.OBJECTID FROM crostab_razv a LEFT JOIN Users b ON a.UserN_%s = b.UserN
                                        WHERE b.UserN Is Null and a.UserN_%s is not Null and UserN_Sad is Null''' % (u_n,u_n))
                notin = [row[0] for row in self.temp_dbc.fetchall()]
                if notin: not_in_usern[n] = notin
                try:
                    n+=1
                    self.temp_dbc.execute(u'SELECT UserN_%s FROM crostab_razv;' % unicode(n))
                except pyodbc.Error :
                    return not_in_usern
        elif try_mkconn:
            self.tempdb_conn.make_connection()
            return self.contr_user_n(False)
        else: self.err_connect()

    def contr_part_n(self, try_mkconn = True):
        if self.temp_dbc:
            n=2
            error_part_n = {}
            while True:
                u_n = unicode(n)
                self.temp_dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE not Part_%s between 0 and 99.9999 or Part_%s is Null' % (u_n, u_n))
                errors = [row[0] for row in self.temp_dbc.fetchall()]
                if errors: error_part_n[n] = errors
                try:
                    n+=1
                    self.temp_dbc.execute(u'SELECT Part_%s FROM crostab_razv;' % unicode(n))
                except pyodbc.Error :
                    self.__n = n
                    return error_part_n
        elif try_mkconn:
            self.tempdb_conn.make_connection()
            return self.contr_part_n(False)
        else: self.err_connect()

    def get_f22_string(self):
        f22_str = []
        for key in self.sprav_holder.f22_notes:
            f22_str.append('\'%s\''%key)
        f22_str = ','.join(f22_str)
        return f22_str

    def contr_f22_n(self, try_mkconn = True):
        if self.temp_dbc:
            n=2
            notinf22n = {}
            columns = self.tempdb_conn.get_f_names(crs_tab)
            f22_fields = [f_name for f_name in columns if 'F22' in f_name]
            while True:
                if u'F22_%d'%n in f22_fields:
                    notin = self.contr_field(self.f22_string, crs_tab, u'F22_%d' % n, can_be_null = True)
                    if notin: notinf22n[n] = notin
                    n+=1
                else:
                    return notinf22n
        elif try_mkconn:
            self.tempdb_conn.make_connection()
            return self.contr_f22_n(False)
        else: self.err_connect()

    def contr_f22_1(self):
        return self.contr_field(self.f22_string, u'crostab_razv', u'F22_1')

    def contr_users(self):
        return self.contr_field(self.sprav_holder.user_types, u'Users', u'UserType')

    def contr_slnad(self):
        return self.contr_field(self.sprav_holder.slnad_codes, u'crostab_razv', u'SLNAD')

    def contr_state(self):
        return self.contr_field(self.sprav_holder.state_codes, u'crostab_razv', u'State_1')

    def contr_lc(self):
        lc = []
        lc_sprav = self.sprav_holder.land_codes
        for key in lc_sprav:
            lc.extend(lc_sprav[key])
        lc = set(lc)
        lc = ','.join(map(lambda x: str(x), lc))
        return self.contr_field(lc, u'crostab_razv', u'LANDCODE')

    def contr_melio_code(self):
        return self.contr_field(self.sprav_holder.melio_codes, u'crostab_razv', u'MELIOCODE')

    def run_field_control(self):
        descript1 = u'Найдены несоответствия с проверочной таблицей'
        descript2 = lambda tabl: u'Найдены несоответствия с таблицей %s' % tabl
        descnonull = u'Не должно быть значений Null'
        descript3 = lambda num: u'''Должно выполняться одно из условий:\
 F22_%(nn)d не Null, UserN_%(nn)d не Null, Part_%(nn)d не равно 0,\
 либо F22_%(nn)d Null, UserN_%(nn)d Null, Part_%(nn)d равно 0''' % {u'nn' : num}
        soato_table = self.contr_soato_table()
        field_usern_sad = self.contr_user_n_sad()
        ctr = u'crostab_razv'
        return_list = [(u'SOATO', u'KOD, Name', soato_table, descnonull),
                      (ctr, u'UserN_Sad', field_usern_sad, descript2(u'Users'))]
        field_controls = (self.contr_user_1(), self.contr_soato(), self.contr_part_1(), self.contr_users(), self.contr_slnad(), self.contr_state(), self.contr_f22_1(), self.contr_lc(), self.contr_melio_code())
        for fc1 in field_controls:
            table = ctr
            if fc1 == field_controls[3]:table = u'Users'
            if fc1[u'isnull']:
                return_list.append((table, fc1[u'fieldname'], fc1[u'isnull'], descnonull))
            if fc1[u'notin']:
                if fc1 == field_controls[0]:
                    return_list.append((table, u'Users', fc1[u'notin'], descript2(u'Users')))
                elif fc1 == field_controls[1]:
                    return_list.append((table, u'SOATO', fc1[u'notin'], descript2(u'SOATO')))
                elif fc1 == field_controls[2]:
                    return_list.append((table, u'Part_1', fc1[u'notin'], u'Значение поля Part_1 должно быть больше 0 и не превышать 100'))
                else:
                    return_list.append((table, fc1[u'fieldname'], fc1[u'notin'], descript1))
        field_controls = (self.contr_user_n(), self.contr_f22_n(), self.contr_part_n())
        for fc2 in field_controls:
            if fc2:
                if fc2 == field_controls[0]:
                    fieldname = lambda num: u'UserN_%s' % num
                    description = descript2(u'Users')
                elif fc2 == field_controls[1]:
                    fieldname = lambda num: u'F22_%s' % num
                    description = descript1
                else:
                    fieldname = lambda num: u'Part_%s' % num
                    description = u'Значение поля должно быть больше либо равно 0 и меньше 100'
                for key in fc2.keys():
                    return_list.append((ctr, fieldname(key), fc2[key], description))
        fields_us_part_f22 = self.contr_us_f22part()
        if fields_us_part_f22 != {}:
            for key in fields_us_part_f22.keys():
                if fields_us_part_f22[key] != {}:
                    for n in fields_us_part_f22[key].keys():
                        return_list.append((ctr, u'%s%d' % (key,n), fields_us_part_f22[key][n], descript3(n)))
        return_list.append((ctr, u'Part_1..Part_N', self.contr_part(), u'Сумма полей Part_* должна быть равна 100'))
        return filter(lambda x: x[2] != [], return_list)
