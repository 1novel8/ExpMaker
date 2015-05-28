#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pyodbc
import shutil

workDir = unicode(os.path.dirname(os.path.abspath(__file__)))


class DataControl(object):
    def __init__(self, filepath):
        self.tableNames = []
        self.fieldTypes = []
        self.work_file = filepath
        self.__db_file = u'%s\\tempDbase.mdb' % workDir
        shutil.copyfile(self.workfile, self.__db_file)
        self.__db = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' % self.__db_file
        self.__isconnected = 0
        self.__need_tabs = [u'crostab_razv',u'SOATO',u'Users']

    def contr_tables(self):
        self.__connect
        if self.__isconnected == 1:
            for row in self.__dbc.tables(tableType=u'TABLE'):
                self.tableNames.append(row[2])
            self.new_list = zip(self.__need_tabs, map(lambda x: x in self.tableNames, self.__need_tabs))
            self.__disconnect
            return self.new_list
        else:
            self.err_connect()

    def contr_field_types(self, tab_name):
        """
            Takes 2 parameters : self and [Table Name] for current control

        TODO:
        Remake return as Dictionary
        """
        self.__connect
        if self.__isconnected == 1:
            for row in self.__dbc.columns(table= tab_name):
                self.fieldTypes.append((row[3],row[5]))
            self.__disconnect
            return self.fieldTypes
        else:
            self.err_connect()

    def contr_field(self, bgd_table, bgd_code_field,  table, field, isnull = 0):
        """
        Makes dictionary with OBJECTID rows with errors
        :param bgd_table: Name of S_'TableName' in BGDtoEKP in unicode format
        :param bgd_code_field: Name of Field consists codes and located in S_'TableName', unicode format
        :param table: control table name, unicode
        :param field: control field name, unicode
        :return: dictionary with keys notin,isnull, [field] and values - OBJECTID with errors
        """
        self.__connect
        if self.__isconnected == 1:
            codes_str = self.make_li_by_bgd(bgd_code_field, bgd_table)
            self.__dbc.execute(u'select OBJECTID from %s where %s not in %s and %s is not Null' % (table, field, codes_str, field))
            not_in_code = [row[0] for row in self.__dbc.fetchall()]
            if isnull == 0:
                self.__dbc.execute(u'select OBJECTID from %s where %s is Null' % (table, field))
                rows_is_null = [row[0] for row in self.__dbc.fetchall()]
                self.__disconnect
                return dict(notin = not_in_code, isnull = rows_is_null, fieldname = field)
            else: return not_in_code
        else: self.err_connect()

    def contr_soato(self):
        self.__connect
        if self.__isconnected == 1:
            self.__dbc.execute(u'SELECT a.OBJECTID FROM crostab_razv a LEFT JOIN SOATO b ON a.SOATO = b.KOD WHERE b.KOD Is Null')
            not_in_soato_code = [row[0] for row in self.__dbc.fetchall()]
            self.__dbc.execute(u'select OBJECTID from crostab_razv where SOATO is Null')
            soato_is_null = [row[0] for row in self.__dbc.fetchall()]
            self.__disconnect
            return dict(isnull = list(set(soato_is_null)-set(not_in_soato_code)), notin = not_in_soato_code)
        else: self.err_connect()

    def contr_user_1(self):
        self.__connect
        if self.__isconnected == 1:
            self.__dbc.execute(u'SELECT a.OBJECTID FROM crostab_razv a LEFT JOIN Users b ON a.UserN_1 = b.UserN WHERE b.UserN Is Null and UserN_Sad is NULL')
            notin_user_n1 = [row[0] for row in self.__dbc.fetchall()]
            self.__dbc.execute(u'select OBJECTID from crostab_razv where UserN_1 is Null')
            usern1_is_null = [row[0] for row in self.__dbc.fetchall()]
            self.__disconnect
            return dict(isnull = list(set(usern1_is_null)-set(notin_user_n1)), notin = notin_user_n1)
        else: self.err_connect()

    def contr_part_1(self):
        self.__connect
        if self.__isconnected == 1:
            self.__dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE not Part_1 between 0.0001 and 100')
            part1err = [row[0] for row in self.__dbc.fetchall()]
            self.__dbc.execute(u'select OBJECTID from crostab_razv where Part_1 is Null')
            part1isnull = [row[0] for row in self.__dbc.fetchall()]
            self.__disconnect
            return dict(isnull = list(set(part1isnull)-set(part1err)), notin = part1err)
        else: self.err_connect()

    def contr_part(self):
        self.__connect
        if self.__isconnected == 1:
            part_sum = u'Part_1'
            for i in range(self.__n):
                if i>1: part_sum += u'+Part_%s' % unicode(i)
            self.__dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE round(%s,3) <> 100' % part_sum)
            parterr = [row[0] for row in self.__dbc.fetchall()]
            self.__disconnect
            return parterr
        else: self.err_connect()

    def contr_user_n_sad(self):
        self.__connect
        if self.__isconnected == 1:
            self.__dbc.execute(u'SELECT a.OBJECTID FROM crostab_razv a LEFT JOIN Users b ON a.UserN_Sad = b.UserN WHERE b.UserN Is Null and UserN_Sad is not NULL')
            not_in_user_n1 = [row[0] for row in self.__dbc.fetchall()]
            self.__disconnect
            return not_in_user_n1
        else: self.err_connect()

    def contr_soato_table(self):
        self.__connect
        if self.__isconnected == 1:
            self.__dbc.execute(u'SELECT OBJECTID FROM SOATO WHERE KOD Is Null or Name is Null')
            is_null = [row[0] for row in self.__dbc.fetchall()]
            self.__disconnect
            return is_null
        else: self.err_connect()

    def contr_us_f22part(self):
        self.__connect
        if self.__isconnected == 1:
            n=1
            user_err = {}
            f22_err = {}
            part_err = {}
            while True:
                u_n = unicode(n)
                self.__dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE UserN_%(nn)s is NOT Null and (F22_%(nn)s is Null or Part_%(nn)s = 0)' % {u'nn': u_n})
                errin_user_n = [row[0] for row in self.__dbc.fetchall()]
                self.__dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE F22_%(nn)s is NOT Null and (UserN_%(nn)s is Null or Part_%(nn)s = 0)' % {u'nn': u_n})
                errin_f22 = [row[0] for row in self.__dbc.fetchall()]
                self.__dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE Part_%(nn)s <> 0 and (UserN_%(nn)s is Null or F22_%(nn)s is Null)' % {u'nn': u_n})
                errin_part_n = [row[0] for row in self.__dbc.fetchall()]
                if errin_user_n: user_err[n] = errin_user_n
                if errin_f22: f22_err[n] = errin_f22
                if errin_part_n: part_err[n] = errin_part_n
                try:
                    n+=1
                    self.__dbc.execute(u'SELECT F22_%s FROM crostab_razv;' % unicode(n))
                except pyodbc.Error :
                    self.__disconnect
                    return dict(UserN_ = user_err, F22_ = f22_err, Part_ = part_err)
        else: self.err_connect()

    def contr_user_n(self):
        self.__connect
        if self.__isconnected == 1:
            n=2
            not_in_usern = {}
            while True:
                u_n = unicode(n)
                self.__dbc.execute(u'''SELECT a.OBJECTID FROM crostab_razv a LEFT JOIN Users b ON a.UserN_%s = b.UserN
                                        WHERE b.UserN Is Null and a.UserN_%s is not Null and UserN_Sad is Null''' % (u_n,u_n))
                notin = [row[0] for row in self.__dbc.fetchall()]
                if notin: not_in_usern[n] = notin
                try:
                    n+=1
                    self.__dbc.execute(u'SELECT UserN_%s FROM crostab_razv;' % unicode(n))
                except pyodbc.Error :
                    self.__disconnect
                    return not_in_usern
        else: self.err_connect()

    def contr_part_n(self):
        self.__connect
        if self.__isconnected == 1:
            n=2
            error_part_n = {}
            while True:
                u_n = unicode(n)
                self.__dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE not Part_%s between 0 and 99.9999 or Part_%s is Null' % (u_n, u_n))
                errors = [row[0] for row in self.__dbc.fetchall()]
                if errors: error_part_n[n] = errors
                try:
                    n+=1
                    self.__dbc.execute(u'SELECT Part_%s FROM crostab_razv;' % unicode(n))
                except pyodbc.Error :
                    self.__disconnect
                    self.__n = n
                    return error_part_n
        else: self.err_connect()

    def contr_f22_n(self):
        self.__connect
        if self.__isconnected == 1:
            n=2
            notinf22n = {}
            while True:
                u_n = unicode(n)
                notin = self.contr_field(u'S_Forma22', u'F22Code', u'crostab_razv', u'F22_%s' % u_n, 1)
                if notin: notinf22n[n] = notin
                try:
                    n+=1
                    self.__dbc.execute(u'SELECT F22_%s FROM crostab_razv;' % unicode(n))
                except pyodbc.Error :
                    self.__disconnect
                    return notinf22n
        else: self.err_connect()


    def contr_users(self):
        return self.contr_field(u'S_Usertype', u'UsertypeCode', u'Users', u'UserType')

    def contr_slnad(self):
        return self.contr_field(u'S_SlNad', u'SLNADCode', u'crostab_razv', u'SLNAD')

    def contr_state(self):
        return self.contr_field(u'S_State', u'StateCode', u'crostab_razv', u'State_1')

    def contr_f22_1(self):
        return self.contr_field(u'S_Forma22', u'F22Code', u'crostab_razv', u'F22_1')

    def contr_lc(self):
        return self.contr_field(u'LandCodes', u'LandCode', u'crostab_razv', u'LANDCODE')

    def contr_melio_code(self):
        return self.contr_field(u'S_MelioCode', u'MelioCode', u'crostab_razv', u'MELIOCODE')

    @staticmethod
    def err_connect():
        print u'Произошла ошибка соединения с базой данных'

    def make_li_by_bgd(self, codesfield, tablename):
        codes_list = self.__selectbgd(u'select %s from %s' % (codesfield, tablename))
        codes = tuple(codes_list)
        return unicode(codes)

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

    @staticmethod
    def __selectbgd(query):
        __bgd = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s\\Spravochnik.mdb;' % workDir
        conn = pyodbc.connect(__bgd, autocommit = True, unicode_results = True)
        dbc = conn.cursor()
        selresult = [str(row[0]) if type(row[0]) == unicode else row[0] for row in dbc.execute(query).fetchall()]
        dbc.close()
        conn.close()
        return selresult

    @property
    def try_to_connect(self):
        self.__connect
        if self.__isconnected == 1:
            self.__disconnect
            return 1
        else: return 0

    @property
    def __connect(self):
        """
        Connect to TempDatabase
        """
        try:
            self.__conn = pyodbc.connect(self.__db, autocommit = True, unicode_results = True)
            self.__dbc = self.__conn.cursor()
            self.__isconnected = 1
        except pyodbc.Error :
            self.__isconnected = 0

    @property
    def __disconnect(self):
        """
        Disconnect TempDatabase
        """
        if self.__isconnected == 1:
            self.__dbc.close()
            self.__conn.close()
        else:
            print u'Error. Database already disconnected'

    @property
    def drop_temp_dbf(self):
        os.remove(self.__db_file)


if __name__ == u'__main__':
    import time
    db_source = u'D:\Work\ForTest.mdb'
    dc = DataControl(db_source)
    print dc.contr_tables()
    print dc.contr_field_types(u'crostab_razv')
    print time.ctime(), u'Run begins'
    Errlist =  dc.run_field_control()
    for i in Errlist:
        print i
    print time.ctime(), u'Run ends'
    # dc.contrUsers()
    # dc.contrSoato()
    # dc.contrSlNad()
    # dc.contrState()
    # dc.contrF22_1()
    # dc.contrLCode()
    # dc.contrMelioCode()
    # dc.contrSoatoTable()
    # dc.contrUsF22Part()
    # dc.contrUser_1()
    # dc.contrUserN()
    # dc.contrF22N()
    # dc.contrUserN_Sad()
    # dc.contrPart_1()
    # dc.contrPartN()
    # dc.contrPart()
    # print time.ctime(), u'ends'


    # print u'Users: ',dc.contrUsers()
    # print u'Soato: ',dc.contrSoato()
    # print u'SlNad: ',dc.contrSlNad()
    # print u'State: ', dc.contrState()
    # print u'F22_1: ',dc.contrF22_1()
    # print u'LCode: ',dc.contrLCode()
    # print u'MelioCode: ', dc.contrMelioCode()
    # print u'Soato table: ', dc.contrSoatoTable()
    # print u'User, Part, F22: ', dc.contrUsF22Part()
    # print u'Users_1: ', dc.contrUser_1()
    # print u'UserN_n: ', dc.contrUserN()
    # print u'F22_n: ',   dc.contrF22N()
    # print u'UserN_Sad: ', dc.contrUserN_Sad()
    # print u'Part_1: ', dc.contrPart_1()
    # print u'Part_N: ', dc.contrPartN()
    # print u'Part: ', dc.contrPart()
