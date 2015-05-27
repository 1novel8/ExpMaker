#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyodbc
import time
from Control import workDir

def select_sprav(query):
    __bgd = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s\\Spravochnik.mdb;' % workDir
    conn = pyodbc.connect(__bgd, autocommit = True, unicode_results = True)
    dbc = conn.cursor()
    selresult = [row for row in dbc.execute(query).fetchall()]
    dbc.close()
    conn.close()
    return selresult

class ExpFormaB(object):
    def __init__(self, expdb, ctr_rows= False, crtabdb = u"%s\\tempDbase.mdb" % workDir):
        self.__codsdict = {}
        self.ctr_rows = ctr_rows        #dict: F22 > (UserN_%(N)d, SOATO, NEWUSNAME_%(N)d, Area_%(N)d,LANDCODE, MELIOCODE, ServType08, State_1, nptype, DOPNAME_%(N)d)
        self.__expfile = expdb
        self.__ctrfile = crtabdb
        self.__expdb = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' % self.__expfile
        self.__crtabdb = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' % self.__ctrfile
        self.__expconnected = 0
        self.__crtabconnected = 0
        self.__expname = u'ExpB_%s' % time.strftime(u"%d\%m\%Y_%H:%M")
        self.sql_exp_create = u''' create table %s(
                                    ID AUTOINCREMENT    ,
                                    Description text(250) Not Null,
                                    UserCount int Null  ,
                                    f_F22 text(3) Not Null,
                                    f_1  text(20) NULL    ,
                                    f_2  text(20) NULL    ,
                                    f_3  text(20) NULL    ,
                                    f_4  text(20) NULL    ,
                                    f_5  text(20) NULL    ,
                                    f_6  text(20) NULL    ,
                                    f_7  text(20) NULL    ,
                                    f_row09 text(20) NULL ,
                                    f_row10 text(20) NULL ,
                                    f_8  text(20) NULL    ,
                                    f_9  text(20) NULL    ,
                                    f_10 text(20) NULL    ,
                                    f_11 text(20) NULL    ,
                                    f_12 text(20) NULL    ,
                                    f_13 text(20) NULL    ,
                                    f_14 text(20) NULL    ,
                                    f_15 text(20) NULL    ,
                                    f_16 text(20) NULL    ,
                                    f_melio1 text(20) NULL ,
                                    f_melio2 text(20) NULL ,
                                    f_servtype text(20) NULL ,
                                    f_state02 text(20) NULL ,
                                    f_state03 text(20) NULL ,
                                    f_state04 text(20) NULL ,
                                    f_state05 text(20) NULL ,
                                    f_state06 text(20) NULL ,
                                    f_state07 text(20) NULL ,
                                    f_state08 text(20) NULL ,
                                    PRIMARY KEY(ID));''' % self.__expname
        self.insfields = u'''(Description, UserCount, f_F22, f_1, f_2, f_3, f_4, f_5, f_6,
                                f_7, f_row09, f_row10, f_8, f_9, f_10, f_11, f_12, f_13,
                                f_14, f_15, f_16, f_melio1, f_melio2, f_servtype, f_state02,
                                f_state03, f_state04, f_state05, f_state06, f_state07, f_state08)'''
        self.createExpTable()

    def makeRowCodes(self):
        """
        Makes dictionary with Names of Rows in FormB as keys
        and LandCodes, RowCodes as values
        """
        lcrows = self.select_sprav(u'select LandCode, NumberGraf from LandCodes')
        rcrows = self.select_sprav(u'select Code, RowNames from RowCodes')
        for row in lcrows:
            if u'f_%s' % row[1] in self.__codsdict.keys():
                self.__codsdict[u'f_%s' % row[1]].append(row[0])
            else:
                self.__codsdict[u'f_%s' % row[1]] = [row[0]]
        for row in rcrows:
            rowli = row[0][1:-1].split(u',')
            rowli = map(lambda x: int(x), rowli)
            self.__codsdict[row[1]] = rowli
        self.__codsdict[u'f_7'] = self.__codsdict[u'f_3'] + self.__codsdict[u'f_4'] + self.__codsdict[u'f_5'] + self.__codsdict[u'f_6']
        return self.__codsdict

    @staticmethod
    def diff_dict_values(*args):
        resultdict = {}
        resultdict.update(args[0])
        def summa(key):
            if idict.get(key) is not None:
                resultdict[key] -= idict[key]
        for idict in args[1:]:
            for i in idict.keys():
                if i not in resultdict.keys():
                    resultdict[i] = 0
                    print u'!'
            map(summa, resultdict.keys())
        return resultdict

    @staticmethod
    def sum_dict_values(*args):
        resultdict = {}
        resultdict.update(args[0])
        def summa(key):
            if idict.get(key) is not None:
                resultdict[key] += idict[key]
        for idict in args[1:]:
            for i in idict.keys():
                if i not in resultdict.keys():
                    resultdict[i] = 0
                    print u'!'
            map(summa, resultdict.keys())
        return resultdict

    def sort_by_fbrow(self):
        self.formb_rows = select_sprav(u'Select Forma22, ValueForm22, SignData from S_F22All')
        fbrow_dict = {}
        for fb_row in self.formb_rows:
            fbrow_dict[fb_row[0]] = [fb_row[1], ]
        # for row in self.ctr_rows:   #(row.usern[n], row.soato, row.nusname[n], row.area[n], row.lc, row.mc, row.st08, row.state, row.slnad, row.np_type, row.dopname[n])
        #     try:
        #         fbrow_dict[row]

    def create_exp_dict(self):
        self.__codes = self.makeRowCodes()
        wherecases = { u'29' : u'MELIOCODE in %s' % unicode(tuple(self.__codes[u'f_melio1'])),
                       u'30' : u'MELIOCODE in %s' % unicode(tuple(self.__codes[u'f_melio2'])),
                       u'31' : u'ServType08 = 1',
                       u'33' : u'NPType = 1', u'34' : u'NPType = 2', u'35' : u'NPType = 3',
                       u'36' : u'SLNAD = 2'}
        expDict = {}        #{}
        self.__valueF22 = {}
        for fbrow in self.formb_rows:
            self.__valueF22[fbrow[0]] = fbrow[1]
            if fbrow[2] is not None:
                expDict[fbrow[0]] = self.makeInsParameters(fbrow[0])
            elif fbrow[0] in wherecases.keys(): # Справочно...
                expDict[fbrow[0]] = self.makeInsParameters(wherecases[fbrow[0]],u'Spr')
        expDict[u'04'] = self.sum_dict_values(*map(lambda x: expDict[x], [u'05',u'06',u'07',u'08',u'09', u'10', u'11']))
        expDict[u'01'] = self.sum_dict_values(expDict[u'01'],expDict[u'02'])
        expDict[u'15'] = self.sum_dict_values(expDict[u'15'],expDict[u'16'])
        expDict[u'40'] = expDict[u'18'].copy()
        expDict[u'18'] = self.sum_dict_values(expDict[u'18'],expDict[u'19'])
        expDict[u'43'] = expDict[u'22'].copy()
        expDict[u'22'] = self.sum_dict_values(expDict[u'22'],expDict[u'23'],expDict[u'24'])
        expDict[u'25'] = self.sum_dict_values(*map(lambda x: expDict[x], [u'01',u'03',u'04',u'12',u'13',u'14',u'15',u'17',u'18',u'20',u'21',u'22']))
        expDict[u'28'] = self.sum_dict_values(expDict[u'25'],expDict[u'27'])
        expDict[u'28'] = self.diff_dict_values(expDict[u'28'],expDict[u'26'])
        expDict[u'32'] = self.sum_dict_values(expDict[u'33'],expDict[u'34'],expDict[u'35'],expDict[u'36'])
        expDict[u'37'] = self.sum_dict_values(expDict[u'01'],expDict[u'03'])
        expDict[u'39'] = self.sum_dict_values(*map(lambda x: expDict[x], [u'12',u'13',u'14',u'15',u'17']))
        expDict[u'42'] = expDict[u'21'].copy()
        expDict[u'42'][u'f_10'] = expDict[u'25'][u'f_10']
        expDict[u'42'][u'f_1'] += expDict[u'25'][u'f_10'] - expDict[u'21'][u'f_10']
        expDict[u'38'] = self.sum_dict_values(expDict[u'04'],expDict[u'23'])
        expDict[u'41'] = expDict[u'20'].copy()
        return expDict

    def makeInsParameters(self, ctr_data):
        """
        Makes parameters for insert into FormaB
        :param ctr_data: [(area, LANDCODE, MELIOCODE, ServType08, State_1),...]
        Example of dict rowCodes:{u'f_10': [400, 41, 42, 43], u'f_11': [440, 441, 442, 444, 445, 446, 447, 448, 449, 450, 701, 702, 703, 704, 705, 443],
        u'f_servtype': [1], u'f_16': [370, 48, 49, 500, 51, 57, 58, 59, 60, 61, 62, 63, 64, 65, 665, 666, 668, 669], u'f_state03': [8, 2000],
        u'f_15': [23, 24, 53, 54, 55, 56, 661, 662, 663, 664, 667], u'f_12': [451, 452, 453, 454, 455, 456, 457, 460],
        u'f_13': [67, 458, 459, 461, 462, 463, 464, 465, 467, 468, 470, 472, 473, 469, 466, 466, 469], u'f_state07': [1000, 9000],
        u'f_state06': [8000], u'f_state08': [9000], u'f_4': [113, 123], u'f_5': [6, 7, 8, 9], u'f_6': [111, 112, 114, 121, 122, 124, 131, 132, 134],
        u'f_7': [3, 4, 471, 113, 123, 6, 7, 8, 9, 111, 112, 114, 121, 122, 124, 131, 132, 134], u'f_3': [3, 4, 471],
        u'f_8': [3210, 3220, 324, 325, 326, 327, 328, 329], u'f_9': [34, 35, 36], u'f_melio2': [4, 5, 50, 60],
        u'f_melio1': [1, 2, 30, 40], u'f_state02': [5, 8, 2000, 3000, 4000, 8000], u'f_state05': [4000], u'f_state04': [3000]}
        :return: Dictionary with formB field names as keys and summs for incoming F22 parameter as values
        """
        dependOfCodes = [(u'f_3',1),(u'f_4',1),(u'f_5',1),(u'f_6',1),(u'f_8',1),(u'f_9',1),(u'f_10',1),(u'f_11',1),(u'f_12',1),(u'f_13',1),(u'f_15',1),(u'f_16',1),
                         (u'f_melio1',2), (u'f_melio2',2),(u'f_servtype',3),
                         (u'f_state02',4),(u'f_state03',4),(u'f_state04',4),(u'f_state05',4),(u'f_state06',4),(u'f_state07',4), (u'f_state08',4)]
        params = dict(f_1=0, f_2=0, f_3=0, f_4=0, f_5=0, f_6=0,f_7=0,
                      f_row09=0, f_row10=0, f_8=0, f_9=0, f_10=0, f_11=0, f_12=0, f_13=0,
                      f_14=0, f_15=0, f_16=0, f_melio1=0, f_melio2=0, f_servtype=0, f_state02=0,
                      f_state03=0, f_state04=0, f_state05=0, f_state06=0, f_state07=0, f_state08=0)
        # ctr_data =[]        [(area, LANDCODE, MELIOCODE, ServType08, State_1),...]
        # if tempBy == u'F22':
        #     ctr_data = self.selectF22Cash(sortby)
        # else:
        #     ctr_data = self.selectoCtrCash(sortby)
        if ctr_data == []:
            return params
        else:
            params[u'f_1'] = sum([row[0] for row in ctr_data])
            for i in dependOfCodes:
                if i[1] == 2:
                    sortedtemp = [row for row in ctr_data if row[2] in self.__codes[i[0]]]
                    params[i[0]] = sum([row[0] for row in sortedtemp])
                    sortedtemp = [row[0] for row in sortedtemp if row[1] in self.__codes[u'f_7']]
                    if i[0] == u'f_melio1':
                        params[u'f_row09'] = sum(sortedtemp)
                    if i[0] == u'f_melio2':
                        params[u'f_row10'] = sum(sortedtemp)
                if i[1] == 1:
                    params[i[0]] = sum([row[0] for row in ctr_data if row[1] in self.__codes[i[0]]])
                if i[1] == 4:
                    params[i[0]] = sum([row[0] for row in ctr_data if row[4] in self.__codes[i[0]]])
                if i[1] == 3:
                    params[i[0]] = sum([row[0] for row in ctr_data if row[3] in self.__codes[i[0]]])
            params[u'f_2'] += params[u'f_3'] + params[u'f_4']
            params[u'f_7'] += params[u'f_2'] + params[u'f_5'] + params[u'f_6']
            params[u'f_14'] += params[u'f_15'] + params[u'f_16']
            return params

    def selectF22Cash(self, F22):
        self.connectCrtab
        tempCT = self.selectoCtrCash(u"NewF22_1 = '%s'" % F22, u'Area_1')
        n = 2
        while True:
            N = unicode(n)
            tempCT.extend(self.selectoCtrCash(u"NewF22_%s = '%s'" % (N, F22), u'Area_%s' % N))
            try:
                n+=1
                self.__ctdbc.execute(u'SELECT NewF22_%s FROM crostab_razv;' % unicode(n))
            except pyodbc.Error:
                self.disconnectCrtab
                break
        return tempCT

    def selectoCtrCash(self, wherecase, area = u'Shape_Area'):
        self.connectCrtab
        if self.__crtabconnected == 1:
            self.__ctdbc.execute(u"select %s, LANDCODE, MELIOCODE, ServType08, State_1  from crostab_razv where %s" % (area, wherecase))
            selresult = [row for row in self.__ctdbc.fetchall()]
            return selresult
        else: print u'Error, Crtab_razv is not connected'

    def runExpB(self):
        self.expdict = self.create_exp_dict()
        for key in sorted(self.expdict.keys()):
            self.addrowExpB(self.__valueF22[key], 1, key, **self.expdict[key])

    def addrowExpB(self, Description, UserCount, f_F22, f_1=0, f_2=0, f_3=0, f_4=0, f_5=0, f_6=0,
                   f_7=0, f_row09=0, f_row10=0, f_8=0, f_9=0, f_10=0, f_11=0, f_12=0, f_13=0,
                   f_14=0, f_15=0, f_16=0, f_melio1=0, f_melio2=0, f_servtype=0, f_state02=0,
                   f_state03=0, f_state04=0, f_state05=0, f_state06=0, f_state07=0, f_state08=0):
        self.connectExp
        if self.__expconnected ==1:
            insargs = (f_1, f_2, f_3, f_4, f_5, f_6,
                       f_7, f_row09, f_row10, f_8, f_9, f_10, f_11, f_12, f_13,
                       f_14, f_15, f_16, f_melio1, f_melio2, f_servtype, f_state02,
                       f_state03, f_state04, f_state05, f_state06, f_state07, f_state08)

            insargs = map(lambda x: '%.0f'%(x/10000) if x != 0 else '0', insargs)
            sqlins = u'insert into %s %s values ( ?, ?, ?, %s);' % (self.__expname, self.insfields, unicode(insargs)[1:-1])
            self.__edbc.execute(sqlins, (Description, UserCount, f_F22))
            self.disconnectExp

    def createExpTable(self):
        self.connectExp
        if self.__expconnected == 1:
            self.__tryToDrop()
            self.__edbc.execute(self.sql_exp_create)
            self.disconnectExp
        else: print u'can\'t connect to Explication database'

    def __tryToDrop(self):
        if self.__expconnected == 1:
            try:
                self.__edbc.execute(u"Drop table %s;" % self.__expname)
            except pyodbc.Error:
                pass

    @staticmethod


    @property
    def connectExp(self):
        try:
            self.__econn = pyodbc.connect(self.__expdb, autocommit = True, unicode_results = True)
            self.__edbc = self.__econn.cursor()
            self.__expconnected = 1
        except pyodbc.Error :
            self.__expconnected = 0

    @property
    def disconnectExp(self):
        if self.__expconnected == 1:
            self.__edbc.close()
            self.__econn.close()
            self.__expconnected = 0


    
if __name__ == u'__main__':
    print u'Этот скрипт производит расчет экспликации по форме Б'
    ExpB = ExpFormaB(u'd:\workspace\explication.mdb')
    print time.ctime()
    ExpB.runExpB()
    print time.ctime()










