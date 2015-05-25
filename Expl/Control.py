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
        self.workfile = filepath
        self.__dbfile = u'%s\\tempDbase.mdb' % workDir
        shutil.copyfile(self.workfile, self.__dbfile)
        self.__db = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' % self.__dbfile
        self.__isconnected = 0
        self.__needtabs = [u'crostab_razv',u'SOATO',u'Users']

    def contrTables(self):
        self.__connect
        if self.__isconnected == 1:
            for row in self.__dbc.tables(tableType=u'TABLE'):
                self.tableNames.append(row[2])
            #print(self.tableNames)
            self.newlist = zip(self.__needtabs, map(lambda x: x in self.tableNames, self.__needtabs))
            self.__disconnect
            return self.newlist
        else:
            self.errConnect()

    def contrFieldTypes(self, tabname):
        """
            Takes 2 parameters : self and [Table Name] for current control

        TODO:
        Remake return as Dictionary
        """
        self.__connect
        if self.__isconnected == 1:
            for row in self.__dbc.columns(table= tabname):
                self.fieldTypes.append((row[3],row[5]))
            self.__disconnect
            return self.fieldTypes
        else:
            self.errConnect()

    def contrField(self, bgdTable, bgdCodeField,  table, field, isnull = 0):
        """
        Makes dictionary with OBJECTID rows with errors
        :param bgdTable: Name of S_'TableName' in BGDtoEKP in unicode format
        :param bgdCodeField: Name of Field consists codes and located in S_'TableName', unicode format
        :param table: control table name, unicode
        :param field: control field name, unicode
        :return: dictionary with keys notin,isnull, [field] and values - OBJECTID with errors
        """
        self.__connect
        if self.__isconnected == 1:
            codesstr = self.makeliByBGD(bgdCodeField, bgdTable)
            self.__dbc.execute(u'select OBJECTID from %s where %s not in %s and %s is not Null' % (table, field, codesstr, field))
            notinCode = [row[0] for row in self.__dbc.fetchall()]
            if isnull == 0:
                self.__dbc.execute(u'select OBJECTID from %s where %s is Null' % (table, field))
                rowsIsNull = [row[0] for row in self.__dbc.fetchall()]
                self.__disconnect
                return dict(notin = notinCode, isnull = rowsIsNull, fieldname = field)
            else: return notinCode
        else: self.errConnect()

    def contrSoato(self):
        self.__connect
        if self.__isconnected == 1:
            self.__dbc.execute(u'SELECT a.OBJECTID FROM crostab_razv a LEFT JOIN SOATO b ON a.SOATO = b.KOD WHERE b.KOD Is Null')
            notinSoatoCode = [row[0] for row in self.__dbc.fetchall()]
            self.__dbc.execute(u'select OBJECTID from crostab_razv where SOATO is Null')
            soatoIsNull = [row[0] for row in self.__dbc.fetchall()]
            self.__disconnect
            return dict(isnull = list(set(soatoIsNull)-set(notinSoatoCode)), notin = notinSoatoCode)
        else: self.errConnect()

    def contrUser_1(self):
        self.__connect
        if self.__isconnected == 1:
            self.__dbc.execute(u'SELECT a.OBJECTID FROM crostab_razv a LEFT JOIN Users b ON a.UserN_1 = b.UserN WHERE b.UserN Is Null and UserN_Sad is NULL')
            notinUserN1 = [row[0] for row in self.__dbc.fetchall()]
            self.__dbc.execute(u'select OBJECTID from crostab_razv where UserN_1 is Null')
            usern1IsNull = [row[0] for row in self.__dbc.fetchall()]
            self.__disconnect
            return dict(isnull = list(set(usern1IsNull)-set(notinUserN1)), notin = notinUserN1)
        else: self.errConnect()

    def contrPart_1(self):
        self.__connect
        if self.__isconnected == 1:
            self.__dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE not Part_1 between 0.0001 and 100')
            part1err = [row[0] for row in self.__dbc.fetchall()]
            self.__dbc.execute(u'select OBJECTID from crostab_razv where Part_1 is Null')
            part1IsNull = [row[0] for row in self.__dbc.fetchall()]
            self.__disconnect
            return dict(isnull = list(set(part1IsNull)-set(part1err)), notin = part1err)
        else: self.errConnect()

    def contrPart(self):
        self.__connect
        if self.__isconnected == 1:
            partsum = u'Part_1'
            for i in range(self.__n):
                if i>1: partsum += u'+Part_%s' % unicode(i)
            self.__dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE round(%s,3) <> 100' % partsum)
            parterr = [row[0] for row in self.__dbc.fetchall()]
            self.__disconnect
            return parterr
        else: self.errConnect()

    def contrUserN_Sad(self):
        self.__connect
        if self.__isconnected == 1:
            self.__dbc.execute(u'SELECT a.OBJECTID FROM crostab_razv a LEFT JOIN Users b ON a.UserN_Sad = b.UserN WHERE b.UserN Is Null and UserN_Sad is not NULL')
            notinUserN1 = [row[0] for row in self.__dbc.fetchall()]
            self.__disconnect
            return notinUserN1
        else: self.errConnect()

    def contrSoatoTable(self):
        self.__connect
        if self.__isconnected == 1:
            self.__dbc.execute(u'SELECT OBJECTID FROM SOATO WHERE KOD Is Null or Name is Null')
            IsNull = [row[0] for row in self.__dbc.fetchall()]
            self.__disconnect
            return IsNull
        else: self.errConnect()

    def contrUsF22Part(self):
        self.__connect
        if self.__isconnected == 1:
            n=1
            UserErr = {}
            F22Err = {}
            PartErr = {}
            while True:
                N = unicode(n)
                self.__dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE UserN_%(nn)s is NOT Null and (F22_%(nn)s is Null or Part_%(nn)s = 0)' % {u'nn': N})
                errinUserN = [row[0] for row in self.__dbc.fetchall()]
                self.__dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE F22_%(nn)s is NOT Null and (UserN_%(nn)s is Null or Part_%(nn)s = 0)' % {u'nn': N})
                errinF22 = [row[0] for row in self.__dbc.fetchall()]
                self.__dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE Part_%(nn)s <> 0 and (UserN_%(nn)s is Null or F22_%(nn)s is Null)' % {u'nn': N})
                errinPartN = [row[0] for row in self.__dbc.fetchall()]
                if errinUserN != []: UserErr[n] = errinUserN
                if errinF22 != []: F22Err[n] = errinF22
                if errinPartN != []: PartErr[n] = errinPartN
                try:
                    n+=1
                    self.__dbc.execute(u'SELECT F22_%s FROM crostab_razv;' % unicode(n))
                except pyodbc.Error :
                    self.__disconnect
                    return dict(UserN_ = UserErr, F22_ = F22Err, Part_ = PartErr)
        else: self.errConnect()

    def contrUserN(self):
        self.__connect
        if self.__isconnected == 1:
            n=2
            notinUserN = {}
            while True:
                N = unicode(n)
                self.__dbc.execute(u'''SELECT a.OBJECTID FROM crostab_razv a LEFT JOIN Users b ON a.UserN_%s = b.UserN
                                        WHERE b.UserN Is Null and a.UserN_%s is not Null and UserN_Sad is Null''' % (N,N))
                notin = [row[0] for row in self.__dbc.fetchall()]
                if notin != []: notinUserN[n] = notin
                try:
                    n+=1
                    self.__dbc.execute(u'SELECT UserN_%s FROM crostab_razv;' % unicode(n))
                except pyodbc.Error :
                    self.__disconnect
                    return notinUserN
        else: self.errConnect()

    def contrPartN(self):
        self.__connect
        if self.__isconnected == 1:
            n=2
            errorPartN = {}
            while True:
                N = unicode(n)
                self.__dbc.execute(u'SELECT OBJECTID FROM crostab_razv WHERE not Part_%s between 0 and 99.9999 or Part_%s is Null' % (N, N))
                errors = [row[0] for row in self.__dbc.fetchall()]
                if errors != []: errorPartN[n] = errors
                try:
                    n+=1
                    self.__dbc.execute(u'SELECT Part_%s FROM crostab_razv;' % unicode(n))
                except pyodbc.Error :
                    self.__disconnect
                    self.__n = n
                    return errorPartN
        else: self.errConnect()

    def contrF22N(self):
        self.__connect
        if self.__isconnected == 1:
            n=2
            notinf22n = {}
            while True:
                N = unicode(n)
                notin = self.contrField(u'S_Forma22', u'F22Code', u'crostab_razv', u'F22_%s' % N, 1)
                if notin != []: notinf22n[n] = notin
                try:
                    n+=1
                    self.__dbc.execute(u'SELECT F22_%s FROM crostab_razv;' % unicode(n))
                except pyodbc.Error :
                    self.__disconnect
                    return notinf22n
        else: self.errConnect()


    def contrUsers(self):
        return self.contrField(u'S_Usertype', u'UsertypeCode', u'Users', u'UserType')

    def contrSlNad(self):
        return self.contrField(u'S_SlNad', u'SLNADCode', u'crostab_razv', u'SLNAD')

    def contrState(self):
        return self.contrField(u'S_State', u'StateCode', u'crostab_razv', u'State_1')

    def contrF22_1(self):
        return self.contrField(u'S_Forma22', u'F22Code', u'crostab_razv', u'F22_1')

    def contrLCode(self):
        return self.contrField(u'LandCodes', u'LandCode', u'crostab_razv', u'LANDCODE')

    def contrMelioCode(self):
        return self.contrField(u'S_MelioCode', u'MelioCode', u'crostab_razv', u'MELIOCODE')

    @staticmethod
    def errConnect():
        print u'Произошла ошибка соединения с базой данных'

    def makeliByBGD(self, codesfield, tablename):
        codesList = self.__selectbgd(u'select %s from %s' % (codesfield, tablename))
        codes = tuple(codesList)
        return unicode(codes)

    def runFieldControl(self):
        descript1 = u'Найдены несоответствия с проверочной таблицей'
        descript2 = lambda tabl: u'Найдены несоответствия с таблицей %s' % tabl
        descnonull = u'Не должно быть значений Null'
        descript3 = lambda num: u'''Должно выполняться одно из условий:\
 F22_%(nn)d не Null, UserN_%(nn)d не Null, Part_%(nn)d не равно 0,\
 либо F22_%(nn)d Null, UserN_%(nn)d Null, Part_%(nn)d равно 0''' % {u'nn' : num}
        soatotable = self.contrSoatoTable()
        fieldUserNSad = self.contrUserN_Sad()
        ctr = u'crostab_razv'
        returnlist = [(u'SOATO', u'KOD, Name', soatotable, descnonull),
                      (ctr, u'UserN_Sad', fieldUserNSad, descript2(u'Users'))]
        fieldcontrols = (self.contrUser_1(), self.contrSoato(), self.contrPart_1(), self.contrUsers(), self.contrSlNad(), self.contrState(), self.contrF22_1(), self.contrLCode(), self.contrMelioCode())
        for i in fieldcontrols:
            table = ctr
            if i == fieldcontrols[3]:table = u'Users'
            if i[u'isnull'] != []:
                returnlist.append((table, i[u'fieldname'], i[u'isnull'], descnonull))
            if i[u'notin'] != []:
                if i == fieldcontrols[0]:
                    returnlist.append((table, u'Users', i[u'notin'], descript2(u'Users')))
                elif i == fieldcontrols[1]:
                    returnlist.append((table, u'SOATO', i[u'notin'], descript2(u'SOATO')))
                elif i == fieldcontrols[2]:
                    returnlist.append((table, u'Part_1', i[u'notin'], u'Значение поля Part_1 должно быть больше 0 и не превышать 100'))
                else:
                    returnlist.append((table, i[u'fieldname'], i[u'notin'], descript1))
        fieldcontrols = (self.contrUserN(), self.contrF22N(), self.contrPartN())
        for i in fieldcontrols:
            if i != {}:
                if i == fieldcontrols[0]:
                    fieldname = lambda num: u'UserN_%s' % num
                    description = descript2(u'Users')
                elif i == fieldcontrols[1]:
                    fieldname = lambda num: u'F22_%s' % num
                    description = descript1
                else:
                    fieldname = lambda num: u'Part_%s' % num
                    description = u'Значение поля должно быть больше либо равно 0 и меньше 100'
                for key in i.keys():
                    returnlist.append((ctr, fieldname(key), i[key], description))
        fieldsUsPartF22 = self.contrUsF22Part()
        if fieldsUsPartF22 != {}:
            for key in fieldsUsPartF22.keys():
                if fieldsUsPartF22[key] != {}:
                    for n in fieldsUsPartF22[key].keys():
                        returnlist.append((ctr, u'%s%d' % (key,n), fieldsUsPartF22[key][n], descript3(n)))
        returnlist.append((ctr, u'Part_1..Part_N', self.contrPart(), u'Сумма полей Part_* должна быть равна 100'))
        return filter(lambda x: x[2] != [], returnlist)

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
    def tryToConnect(self):
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
    def dropTempDBF(self):
        os.remove(self.__dbfile)


if __name__ == u'__main__':
    import time
    db_source = u'D:\Work\ForTest.mdb'
    dc = DataControl(db_source)
    print dc.contrTables()
    print dc.contrFieldTypes(u'crostab_razv')
    print time.ctime(), u'Run begins'
    Errlist =  dc.runFieldControl()
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
