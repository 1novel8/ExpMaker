#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyodbc
from Control import workDir

class BGDtoERemaker(object):
    def __init__(self):
        self.dbf = '%s\\Spravochnik.mdb' % workDir
        self.__bgd = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s\\Spravochnik.mdb;' % workDir
        self.tabs_fields = dict()
        self.tabs_fields[u'BGDToEkp1'] = [(u'F22', u'VARCHAR'), (u'UTYPE', u'VARCHAR'), (u'NPTYPE', u'VARCHAR'), (u'STATE', u'VARCHAR'), (u'SLNAD', u'VARCHAR'), (u'NEWUSNAME', u'SMALLINT'), (u'DOPUSNAME', u'VARCHAR')]
        self.tabs_fields[u'BGDToEkp2'] = [(u'F22', u'VARCHAR'), (u'NEWF22', u'VARCHAR'), (u'UTYPE', u'VARCHAR'), (u'NPTYPE', u'VARCHAR'), (u'LCODE_MIN', u'SMALLINT'), (u'LCODE_MAX', u'SMALLINT'), (u'NewLCODE', u'SMALLINT'), (u'STATE', u'VARCHAR'), (u'NewSTATE', u'VARCHAR'), (u'SLNAD', u'VARCHAR'), (u'NEWUSNAME', u'SMALLINT'), (u'DOPUSNAME', u'VARCHAR')]
        self.tabs_fields[u'LandCodes'] = [(u'OBJECTID', u'COUNTER'), (u'LandCode', u'SMALLINT'), (u'Notes', u'VARCHAR'), (u'NumberGraf', u'SMALLINT'), (u'ValueForm', u'VARCHAR'), (u'ValueForma22', u'VARCHAR')]
        self.tabs_fields[u'RowCodes'] = [(u'RowID', u'COUNTER'), (u'Code', u'VARCHAR'), (u'Notes', u'VARCHAR'), (u'RowNames', u'VARCHAR'), (u'SortedBy', u'VARCHAR')]
        self.tabs_fields[u'S_F22All'] = [(u'OBJECTID', u'COUNTER'), (u'Forma22', u'VARCHAR'), (u'ValueForm22', u'VARCHAR'), (u'SignData', u'BYTE'), (u'ValueLand', u'VARCHAR'), (u'ConditionSum', u'VARCHAR')]
        self.tabs_fields[u'S_Forma22'] = [(u'OBJECTID', u'COUNTER'), (u'F22Code', u'VARCHAR'), (u'Notes', u'VARCHAR')]
        self.tabs_fields[u'S_MelioCode'] = [(u'OBJECTID', u'COUNTER'), (u'MelioCode', u'SMALLINT'), (u'Notes', u'VARCHAR'), (u'NumberStrEkp', u'VARCHAR'), (u'ValueFormEkp', u'VARCHAR'), (u'NumberGrF22_1', u'VARCHAR'), (u'ValueFormF22_1', u'VARCHAR')]
        self.tabs_fields[u'S_SlNad'] = [(u'OBJECTID', u'COUNTER'), (u'SLNADCode', u'BYTE'), (u'Notes', u'VARCHAR')]
        self.tabs_fields[u'S_State'] = [(u'OBJECTID', u'COUNTER'), (u'StateCode', u'SMALLINT'), (u'Notes', u'VARCHAR')]
        self.tabs_fields[u'S_Usertype'] = [(u'OBJECTID', u'COUNTER'), (u'UsertypeCode', u'BYTE'), (u'Notes', u'VARCHAR')]
        self.tabs_fields[u'SOATO'] = [(u'OBJECTID', u'COUNTER'), (u'znak1', u'VARCHAR'), (u'znak2', u'SMALLINT'), (u'znak57min', u'SMALLINT'), (u'znak57max', u'SMALLINT'), (u'znak810max', u'SMALLINT'), (u'znak810min', u'SMALLINT'), (u'TypeNP', u'SMALLINT'), (u'NPTypeNotes', u'VARCHAR'), (u'SovType', u'VARCHAR')]
        self.selectbgd1 = u'select F22,UTYPE,NPTYPE,STATE,SLNAD,NEWUSNAME,DOPUSNAME from BGDtoEkp1'
        self.selectbgd2 = u'select F22,NEWF22,UTYPE,NPTYPE,LCODE_MIN,LCODE_MAX,NewLCODE,STATE,NewSTATE,SLNAD, NEWUSNAME,DOPUSNAME from BGDtoEkp2'
        self.sprav_connected = self.trytoconnect()
        if self.sprav_connected:
            self.losttables = self.contrTables()
            self.badfields = dict.fromkeys(self.tabs_fields.keys())
            for key in self.tabs_fields:
                self.badfields[key] = self.contrFieldTypes(key, self.tabs_fields[key])
                if not self.badfields[key]:
                    del self.badfields[key]

    def remakeBGD1(self):

        """
        BGD1 have fields: F22,UTYPE, NPTYPE_min, NPTYPE_max, State, SLNAD, NEWUSNAME, DOPUSNAME
        :return: list with BGD1 rows
        """
        newbgd = []
        if self.sprav_connected == 1:
            for row in self.__executeSprav(self.selectbgd1):
                utypelist = self.uToInt(row[1].split(','))
                nptypelist = self.uToInt(row[2].split(','))
                stateli = self.uToInt(row[3].split(','))
                nptypeliremaked = self.remakelist(nptypelist)
                for state in stateli:
                    for utype in utypelist:
                        for npt in nptypeliremaked:
                            newbgd.append((row[0], utype, state, int(row[4]), npt[0], npt[1],  row[5],row[6]))
        return newbgd

    def remakeBGD2(self, upd_ctr = False):
        bgd2 = []
        if self.sprav_connected == 1:
            for row in self.__executeSprav(self.selectbgd2):
                utypelist = self.uToInt(row[2].split(','))
                nptypelist = self.uToInt(row[3].split(','))
                stateli = self.uToInt(row[7].split(','))
                nptypeliremaked = self.remakelist(nptypelist)
                nlc, nst = row[6],row[8] if upd_ctr else 0
                for state in stateli:
                    for utype in utypelist:
                        for npt in nptypeliremaked:
                            bgd2.append((row[0], utype, state, int(row[9]), row[1],  npt[0], npt[1], row[4], row[5], nlc,
                                         nst,  row[10], row[11]))
            bgd2 = (self.remakeBGD1(),upd_ctr,bgd2)
        return bgd2
# bgd_row: F22, UTYPE, State, SLNAD, newF22,NPTYPE_min, NPTYPE_max, lc_min, lc_max, newlc,  newstate,  NEWUSNAME, DOPUSNAME
    def __executeSprav(self, query):
        self.connectSprav()
        selresult = [row for row in self.__dbc.execute(query).fetchall()]
        self.disconnectSprav()
        return selresult

    def trytoconnect(self):
        try:
            self.connectSprav()
            self.disconnectSprav()
        except pyodbc.Error:
            return 0
        else:
            return 1

    def contrTables(self):
        self.connectSprav()
        self.sprav_tables = [row[2] for row in self.__dbc.tables(tableType=u'TABLE')]
        self.disconnectSprav()
        returnlist = []
        for tab in self.tabs_fields:
            if tab not in self.sprav_tables:
                returnlist.append(tab)
        return returnlist

    def contrFieldTypes(self, tabname, tabstructure):
        self.connectSprav()
        fields_types = [(row[3], row[5]) for row in self.__dbc.columns(table= tabname)]
        self.disconnectSprav()
        returnlist = []
        for field in tabstructure:
            if field not in fields_types:
                returnlist.append(field)
        return returnlist

    def connectSprav(self):
        self.__conn = pyodbc.connect(self.__bgd, autocommit = True, unicode_results = True)
        self.__dbc = self.__conn.cursor()

    def disconnectSprav(self):
        try:
            self.__dbc.close()
            self.__conn.close()
        except:
            pass

    @staticmethod
    def uToInt(li):
        newli = []
        for i in range(len(li)):
            newli.append(int(li[i]))
        return newli

    @staticmethod
    def remakelist(li):
        """
            Rturns list of tuples with intervals of numbers
        :param li: <example> [1,2,3,4,8,9]
        :return: <example> [(1,4),(8,9)]
        """
        minli = []
        maxli = []
        lilen = len(li)
        inext = 0
        for i in range(len(li)):
            if i == 0:
                minli.append(li[0])
            elif i < inext:
                continue
            try:
                icheck = li[i+1]
            except:
                maxli.append(li[lilen-1])
                break
            w = 1
            while i+w < lilen:
                if li[i+w] - li[i+w-1] == 1:
                    w+=1
                else:
                    inext = i+w
                    maxli.append(li[i+w-1])
                    minli.append(li[i+w])
                    break
        return zip(minli,maxli)

if __name__=='__main__':
    bgd = BGDtoERemaker()
    
    
