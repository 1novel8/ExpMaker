#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyodbc
import time
from Control import workDir
template_db = u'%s\\template.mdb' % workDir
access_dbf = u"%s\\tempDbase.mdb" % workDir
dependOfCodes = dict(f_3=1, f_4=1, f_5=1, f_6=1, f_8 =1, f_9=1, f_10=1, f_11 =1, f_12=1, f_13 =1,f_15=1, f_16 =1,
                     f_melio1=2, f_melio2=2, f_servtype=3,
                     f_state02=4, f_state03=4, f_state04 =4, f_state05=4, f_state06=4, f_state07=4, f_state08 =4)

def sum_by_lc(rowsli):
    if len(rowsli):
        sumdict = dict.fromkeys(lcdict,0)
        for key in sumdict.keys():
            for row in rowsli:
                if row[1] in lcdict[key]:
                    sumdict[key] += row[0]
        sumdict[u'f_2'] = sumdict[u'f_3']+sumdict[u'f_4']
        sumdict[u'f_7'] = sumdict[u'f_2']+sumdict[u'f_5']+sumdict[u'f_6']
        sumdict[u'f_14'] = sumdict[u'f_15']+sumdict[u'f_16']
        sumdict[u'f_1'] = sum(sumdict[u'f_%d' % i] for i in (7,8,9,10,11,12,13,14))
        a = map(lambda x : sumdict[u'f_%d' % x], range(1,len(sumdict.keys())+1))
        return a
    else:
        return [0 for i in range(16)]

def make_expa_params(rowslist):
    fAparams = {}
    fAparams[u'f_01'] = sum_by_lc(rowslist)
    for key in rcdict.keys():
        filtRowslist = [row[:2] for row in rowslist if row[dependOfCodes[key]] in rcdict[key]]
        fAparams[key] = sum_by_lc(filtRowslist)
    return fAparams

def select_sprav(query):
    __bgd = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s\\Spravochnik.mdb;' % workDir
    conn = pyodbc.connect(__bgd, autocommit = True, unicode_results = True)
    dbc = conn.cursor()
    selresult = [row for row in dbc.execute(query).fetchall()]
    dbc.close()
    conn.close()
    return selresult

def make_row_codes():
    """
    Makes dictionary with Names of Rows in FormB as keys
    and LandCodes, RowCodes as values
    """
    codsdict ={}
    global rcdict
    rcdict = {}
    lcrows = select_sprav(u'select LandCode, NumberGraf from LandCodes')
    rcrows = select_sprav(u'select Code, RowNames from RowCodes')
    for row in lcrows:
        if u'f_%s' % row[1] in codsdict.keys():
            codsdict[u'f_%s' % row[1]].append(row[0])
        else:
            codsdict[u'f_%s' % row[1]] = [row[0]]
    global lcdict
    lcdict = codsdict.copy()
    for row in rcrows:
        rowli = row[0][1:-1].split(u',')
        rowli = map(lambda x: int(x), rowli)
        rcdict[row[1]] = rowli
    codsdict.update(rcdict)
    codsdict[u'f_7'] = codsdict[u'f_3'] + codsdict[u'f_4'] + codsdict[u'f_5'] + codsdict[u'f_6']
    return codsdict
NumRowsLi = [u'f_01', u'f_state02', u'f_state03', u'f_state04', u'f_state05', u'f_state06', u'f_state07', u'f_state08', u'f_melio1', u'f_melio2', u'f_servtype' ]

class DataComb(object):
    def __init__(self, f22, user_soato, nusname, datali, inform = u''):
        self.f22 = f22
        self.us_soato = user_soato
        self.nusname = nusname
        self.data = datali[1:]
        self.expArows = []
        info_is_null = lambda x: x if x else ''
        self.info = info_is_null(datali[0])+u' '+inform

    def add_data(self):
        self.expAdict = make_expa_params(self.data)
        for i in NumRowsLi:
            self.expArows.append(self.expAdict[i])


class ExpFA(object):
    def __init__(self, expdb, ctr_rows, crtabdb = u"%s\\tempDbase.mdb" % workDir):
        self.__expfile = expdb
        self.__ctrfile = crtabdb
        self.__expAccess = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' % self.__expfile
        self.__crtAccess = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' % self.__ctrfile
        self.__expconnected = 0
        self.__crtabconnected = 0
        self.datadict = self.makeDictofDict(ctr_rows)     #Main Dict :keys F22>>Dict with keys UserN/SOATo >> list of tuples with data from ctr for ExpA
        self.usersInfo, self.soatoInfo = self.dataUsersSOATO()
        self.remakeCodes()
        self.expsdict = self.makeCombData()     #Exp Dict :keys F22>>Dict with keys UserN/SOATo >> combdata instanse
        self.a=self.make_exp_tree()

    @staticmethod
    def make_f22_dict(rows_ok):
        f22_dict = dict()
        for row in rows_ok:
            for n in range(row.n):
                row_params = (row.usern[n], row.soato, row.nusname[n], row.area[n], row.lc, row.mc, row.st08, row.state, row.dopname[n])
                            # NewF22_%(N)d, UserN_%(N)d, SOATO, NEWUSNAME_%(N)d, Area_%(N)d,LANDCODE, MELIOCODE, ServType08, State_1, NPType, DOPNAME_%(N)d,
                try:
                    f22_dict[row.f22[n]].append(row_params)
                except KeyError:
                    f22_dict[row.f22[n]] = [row_params,]
        return f22_dict

    def makeDictofDict(self, rows):
        """
        :param rows : rows instances (f22, UserN_n, SOATO, NEWUSNAME_n, Area_n,LANDCODE, MELIOCODE, ServType08, State, DOPNAME_n)
        :return: dict with dicts, keys: f22 >> usern | soato >> rows(newusname_n, dopname_n, (Area_n,LANDCODE, MELIOCODE, ServType08, State))
        """
        f22_rows = self.make_f22_dict(rows)
        ctDict = dict()
        for f22 in f22_rows.keys():
            ctDict[f22] = dict()
            for row in f22_rows[f22]:
                rowind = 0 if row[2] == 1 else 1    #NEWUSNAME_%(N)d =1 >> Sort By UserN
                                                    #NEWUSNAME_%(N)d =2|3 >> Sort By SOATO
                try:
                    ctDict[f22][row[rowind]].append(row[3:-1])
                except KeyError:
                    ctDict[f22][row[rowind]] = [row[2], row[-1], row[3:-1]]
        return ctDict

    def make_exp_tree(self):
        """ Returns dictionary:
            keys: F22, values: combdata instanses
        """
        treedict = dict.fromkeys(self.expsdict)
        for key1 in self.expsdict:
            treedict[key1] = []
            for key2 in self.expsdict[key1]:
                treedict[key1].append(self.expsdict[key1][key2])
        return treedict

    def makeCombData(self):
        combdicts = dict.fromkeys(self.datadict.keys())
        for key1 in combdicts:
            combdicts[key1] = dict.fromkeys(self.datadict[key1].keys())
            for key2 in combdicts[key1]:
                combli = self.datadict[key1][key2]
                if combli[0] == 1:
                    combdicts[key1][key2] = DataComb(key1, key2, combli[0], combli[1:], self.usersInfo[key2])
                else: combdicts[key1][key2] = DataComb(key1, key2, combli[0], combli[1:], self.soatoInfo[key2])
        return combdicts

    # def makeSingleExp(self, f22, groupparam, nusn, rowslist):       #Takes parmeters from self.datadict
    #     inf = self.usersInfo[groupparam] if nusn == 1 else self.soatoInfo[groupparam]
    #     expA = DataComb(f22, groupparam, nusn, rowslist, inf)
    #     expA.addData()
    #     return expA

    def calcAllExps(self):
        for key1 in self.expsdict:
            for key2 in self.expsdict[key1]:
                self.expsdict[key1][key2].add_data()

    def transferToIns(self):
        self.__expname = u'ExpA_%s' % time.strftime(u"%d\%m\%Y_%H:%M")
        self.createClearEdb()
        finaldict = self.expsdict
        self.calcAllExps()
        self.__connectExp()
        fdk = finaldict.keys()
        fdk.sort()
        for f22key in fdk:
            itogorow = [0 for i in range(16)]
            for ussokey in finaldict[f22key].keys():
                li = finaldict[f22key][ussokey].expArows
                data = finaldict[f22key][ussokey].info
                for i in range(1, len(li)+1):
                    if i == 1:
                        self.addrowExpA(f22key, data, i, li[i-1])
                        itogorow = map(lambda x: sum(x), zip(itogorow, li[i-1]))
                    else:
                        self.addrowExpA(f22key, ussokey, i, li[i-1])
            self.addrowExpA(f22key, u'Итого', 0, itogorow)
        self.__disconnectExp()

    def addrowExpA(self, ff22, fUsN, fRN, params):
        if self.__expconnected ==1:
            insargs = map(lambda x: round(x/10000,4), params)
            sqlins = u'''insert into %s (f_F22, f_UsN, f_RowNumber, f_1, f_2, f_3, f_4, f_5, f_6, f_7, f_8, f_9, f_10,
                        f_11, f_12, f_13, f_14, f_15, f_16) values ( ?, ?, ?, %s);''' % (self.__expname, unicode(insargs)[1:-1])
            try:
                self.__edbc.execute(sqlins, (ff22, fUsN, fRN))
            except pyodbc.DataError: pass

    def createClearEdb(self):
        createfa = u''' create table %s(
        ID AUTOINCREMENT    ,
        f_F22 text(3)       ,
        f_UsN text(100)     ,
        f_RowNumber integer NULL,
        f_1  DOUBLE NULL    ,
        f_2  DOUBLE NULL    ,
        f_3  DOUBLE NULL    ,
        f_4  DOUBLE NULL    ,
        f_5  DOUBLE NULL    ,
        f_6  DOUBLE NULL    ,
        f_7  DOUBLE NULL    ,
        f_8  DOUBLE NULL    ,
        f_9  DOUBLE NULL    ,
        f_10 DOUBLE NULL    ,
        f_11 DOUBLE NULL    ,
        f_12 DOUBLE NULL    ,
        f_13 DOUBLE NULL    ,
        f_14 DOUBLE NULL    ,
        f_15 DOUBLE NULL    ,
        f_16 DOUBLE NULL    ,
        PRIMARY KEY(ID));''' % self.__expname
        self.__connectExp()
        if self.__expconnected == 1:
            self.tryToDrop()
            self.__edbc.execute(createfa)
            self.__disconnectExp()

    def tryToDrop(self):
        if self.__expconnected == 1:
            try:
                self.__edbc.execute(u"Drop table %s;" % self.__expname)
                return True
            except pyodbc.Error:
                return False

    def dataUsersSOATO(self):
        """
        returns UsersDict and SoatoDict with keys usern and soato
        and values in unicode
        """
        self.__connectCrtab()
        if self.__crtabconnected == 1:
            self.__ctdbc.execute(u'select KOD, NameSNp from SOATO')
            selresult = [row for row in self.__ctdbc.fetchall()]
            soatoDict = dict(selresult)
            self.__ctdbc.execute(u'select UserN, UsName from Users')
            selresult = [row for row in self.__ctdbc.fetchall()]
            usersDict = dict(selresult)
            self.__disconnectCrtab()
            return usersDict, soatoDict
        else:
            #TODO: Remake exception
            print u'Error, Crtab_razv is not connected'

    def __connectExp(self):
        try:
            self.__econn = pyodbc.connect(self.__expAccess, autocommit = True, unicode_results = True)
            self.__edbc = self.__econn.cursor()
            self.__expconnected = 1
        except:
            self.__expconnected = 0

    def __disconnectExp(self):
        if self.__expconnected == 1:
            self.__edbc.close()
            self.__econn.close()
            self.__expconnected = 0

    def __connectCrtab(self):
        try:
            self.__ctconn = pyodbc.connect(self.__crtAccess, autocommit = True, unicode_results = True)
            self.__ctdbc = self.__ctconn.cursor()
            self.__crtabconnected = 1
        except:
            print u'Error, Crtab_razv is not connected!!!'
            self.__crtabconnected = 0

    def __disconnectCrtab(self):
        if self.__crtabconnected == 1:
            self.__ctdbc.close()
            self.__ctconn.close()
            self.__crtabconnected = 0

    @staticmethod
    def remakeCodes():
        make_row_codes()

if __name__ == '__main__':
    print time.ctime()
    test = ExpFA(u'd:\\workspace\\explication.mdb',access_dbf)
    test.transferToIns()
    print time.ctime()

