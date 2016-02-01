#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyodbc
import shutil
from Sprav import DBConn

crs_tab = u'crostab_razv'
soato_tab =u'SOATO'
users_tab = u'Users'
db_structure = {
    crs_tab: {u'OBJECTID': u'COUNTER', u'Shape_Area': u'DOUBLE', u'SOATO': u'VARCHAR',
    u'Part_1': u'DOUBLE', u'UserN_1': u'INTEGER',u'Forma22_1': u'VARCHAR',
    u'ServType08': u'SMALLINT', u'SLNAD': u'SMALLINT',u'State_1': u'SMALLINT',
    u'LANDCODE': u'SMALLINT', u'MELIOCODE': u'SMALLINT', u'UserN_Sad': u'INTEGER'
    },
    soato_tab: {u'NAME': u'VARCHAR',
                u'OBJECTID': u'COUNTER',
                u'PREF': u'VARCHAR',
                u'KOD': u'VARCHAR'
    },
    users_tab: {u'OBJECTID': u'COUNTER',
                u'UserType': u'SMALLINT',
                u'UsName': u'VARCHAR',
                u'UserN': u'INTEGER'
    }
}
def try_make_conn(func_with_connect):
    """
    Decorator for functions with connection to database
    decorator is decorated to take parameter self
    """
    try_mk_conn = {1:True}
    def wrapper(self, *args, **kwargs):
        if self.temp_dbc:
            try_mk_conn[1] = True
            return func_with_connect(self, *args, **kwargs)

        elif try_mk_conn[1]:
            try_mk_conn[1] = False
            self.tempdb_conn.make_connection()
            return wrapper(self, *args, **kwargs)
        else:
            raise Exception(u'Не удалось соединиться с базой данных')
    return wrapper

class DbControl(object):
    def __init__(self, file_path, tempDB_path):
        self.need_tabs = [crs_tab,soato_tab,users_tab]
        self.db_file = tempDB_path
        shutil.copyfile(file_path, tempDB_path)
        self.tempdb_conn = DBConn(self.db_file, False)
        self.all_tabs_columns = self.get_all_fields()

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

    @try_make_conn
    def is_tables_exist(self):
        table_names = []
        for row in self.tempdb_conn.get_tables():
            table_names.append(row[2])
        tab_not_found = []
        for tab in self.need_tabs:
            if tab not in table_names:
                tab_not_found.append(tab)
        return tab_not_found

    def is_tables_empty(self):
        """
        :return: Tables from __need_tabs that has no any data
        """
        no_data_in = []
        for tab in self.need_tabs:
            if not self.tempdb_conn.exec_sel_query(u'select * from %s' % tab):
                no_data_in.append(tab)
        if no_data_in:
            return no_data_in
        else: return False


    def is_empty_f_pref(self):
        failed_obj = self.tempdb_conn.exec_sel_query(u'select OBJECTID from %s where Pref is Null' % soato_tab)
        if failed_obj:
            failed_obj = [row[0] for row in failed_obj]
            failed_obj = unicode(tuple(failed_obj))
            self.tempdb_conn.exec_query(u'delete from %s where OBJECTID in %s' %(soato_tab, failed_obj))
            return failed_obj
        else:
            return False

    @try_make_conn
    def get_all_fields(self):
        all_fields = {}
        for tab in self.need_tabs:
            all_fields[tab] = self.tempdb_conn.get_f_names_types(tab)
        return all_fields

    @try_make_conn
    def contr_field_types(self):
        result = {}
        for tab in self.need_tabs:
            fields_types = self.tempdb_conn.get_f_names_types(tab)
            failed = []
            for (f, f_type) in db_structure[tab].items():
                if f not in fields_types:
                    failed.append(u'%s'%f)
                elif fields_types[f] != f_type:
                    failed.append(u'%s: %s -> %s'%(f, fields_types[f], f_type))
            if failed:
                result[tab] = failed
        return result

class DataControl(DbControl):
    def __init__(self, sprav_holder, file_path, tempDB_path):
        self.errors_protocol = []
        self.sprav_holder = sprav_holder
        super(DataControl,self).__init__(file_path, tempDB_path)
        self.is_empty_f_pref()
        self.f22_string = self.get_f22_string()
        self.max_n = self.get_n_max()
        sprav_holder.crtab_columns = self.all_tabs_columns[crs_tab]
        sprav_holder.max_n = self.max_n
        self.update_str_to_null()

    def update_str_to_null(self):
        for tab in self.need_tabs:
            for key, val in self.all_tabs_columns[tab].items():
                if val == u'VARCHAR':
                    #TODO: You can add a check query here like "select OBJECTID from %s where  %s = ''" for higher performance
                    self.tempdb_conn.exec_query(u"update %s set %s = Null where %s=''" % (tab, key, key))
    @try_make_conn
    def select_errors(self, query):
        return self.tempdb_conn.select_single_f(query)

    def get_f22_string(self):
        f22_str = []
        for key in self.sprav_holder.f22_notes:
            f22_str.append('\'%s\''%key)
        f22_str = ','.join(f22_str)
        return f22_str

    def add_to_protocol(self, table, field, err_ids, err_desc, dynamic_param = None):
        """
        systematize data for errors protocol, adds to protocol when err_ids returns True
        :param table: table with errors                 type: unicode
        :param field: field where errors found          type: unicode
        :param err_ids: OBJECTIDs where errors found,   type: unicode or some array type
        :param err_desc: code of the error (you can find the description of error by this code), type: int
        :param dynamic_param: if description, founded by err_desc code, need some dop parameters, you should transfer it by this parameter
        """
        if err_ids:
            err_doc = {
                'table': table,
                'field': field,
                'err_ids': err_ids,
                'err_msg': err_desc,
                'dyn_param':dynamic_param
            }
            self.errors_protocol.append(err_doc)

    def run_field_control(self):
        self.errors_protocol = []
        self.contr_kods_soato()
        self.contr_usern_sad()
        self.contr_user_1()
        self.contr_soato_crtab()
        self.contr_part_1()
        self.contr_users()
        self.contr_slnad()
        self.contr_state()
        self.contr_f22_1()
        self.contr_lc()
        self.contr_melio_code()
        self.contr_user_n()
        self.contr_f22_n()
        self.contr_part_n()
        self.contr_part_sum()
        self.contr_us_f22_part()
        return self.errors_protocol

    def contr_us_f22_part(self):
        for n in range(2, self.max_n+1):
            search_err = self.select_errors(u'SELECT OBJECTID FROM crostab_razv WHERE UserN_%(n)d is NOT Null and (Forma22_%(n)d is Null or Part_%(n)d = 0)' % {u'n': n})
            self.add_to_protocol(crs_tab, u'Forma22_%(n)d, UserN_%(n)d или Part_%(n)d' % {u'n': n}, search_err, 6, n)
            search_err = self.select_errors(u'SELECT OBJECTID FROM crostab_razv WHERE Forma22_%(n)d is NOT Null and (UserN_%(n)d is Null or Part_%(n)d = 0)' % {u'n': n})
            self.add_to_protocol(crs_tab, u'Forma22_%(n)d, UserN_%(n)d или Part_%(n)d' % {u'n': n}, search_err, 6, n)
            search_err = self.select_errors(u'SELECT OBJECTID FROM crostab_razv WHERE Part_%(n)d <> 0 and (UserN_%(n)d is Null or Forma22_%(n)d is Null)' % {u'n': n})
            self.add_to_protocol(crs_tab, u'Forma22_%(n)d, UserN_%(n)d или Part_%(n)d' % {u'n': n}, search_err, 6, n)

    def contr_part_sum(self):
        part_sum = u'Part_1'
        for n in range(2, self.max_n+1):
            part_sum += u'+Part_%s' % unicode(n)
        search_err = self.select_errors(u'SELECT OBJECTID FROM crostab_razv WHERE round(%s,3) <> 100' % part_sum)
        self.add_to_protocol(crs_tab, u'Part_1..Part_%d' % self.max_n, search_err, 8)
    def contr_part_n(self):
        for n in range(2, self.max_n+1):
            search_err = self.select_errors(u'SELECT OBJECTID FROM crostab_razv WHERE not Part_%d between 0 and 99.9999 or Part_%d is Null' % (n, n))
            self.add_to_protocol(crs_tab, u'Part_%d'%n, search_err, 7)
            search_err = self.select_errors(u'SELECT OBJECTID FROM crostab_razv WHERE Part_%d is Null' % n)
            self.add_to_protocol(crs_tab, u'Part_%d'%n, search_err, 3)

    def contr_f22_n(self):
        for n in range(2, self.max_n+1):
            self.contr_field(crs_tab, u'Forma22_%d' % n, self.f22_string, u'S_Forma22', True)

    def get_n_max(self):
        part_fields = lambda n: [u'Part_%d'%n, u'UserN_%d'%n, u'Forma22_%d'%n]
        def raise_err(msg):
            raise Exception(u'Проверьте наличие полей %s' % unicode(msg))
        max_n = 1
        crtab_fields = self.all_tabs_columns[crs_tab].keys()
        col_fields = len(crtab_fields)
        while True:
            f_set = set(crtab_fields + part_fields(max_n))
            if col_fields == len(f_set):
                max_n+=1
            elif max_n ==1:
                raise_err(part_fields(1))
            elif len(f_set)-col_fields == 3:
                break
            else:
                raise_err(u', '.join(part_fields(max_n)))
        return max_n-1

    def contr_user_n(self):
        for n in range(2, self.max_n+1):
            search_err = self.select_errors(u'''SELECT a.OBJECTID FROM crostab_razv a LEFT JOIN Users b ON a.UserN_%d = b.UserN
                                    WHERE b.UserN Is Null and a.UserN_%d is not Null and UserN_Sad is Null''' % (n,n))
            self.add_to_protocol(crs_tab, u'UserN_%d'%n, search_err, 2, users_tab)

    def contr_melio_code(self):
        self.contr_field(crs_tab, u'MELIOCODE',self.sprav_holder.melio_codes, u'S_MelioCode')

    def contr_lc(self):
        lc = []
        lc_sprav = self.sprav_holder.land_codes
        for key in lc_sprav:
            lc.extend(lc_sprav[key])
        lc = set(lc)
        lc = ','.join(map(lambda x: str(x), lc))
        self.contr_field(crs_tab, u'LANDCODE', lc, u'S_LandCode')

    def contr_f22_1(self):
        self.contr_field(crs_tab, u'Forma22_1', self.f22_string, u'S_Forma22')

    def contr_state(self):
        self.contr_field(crs_tab, u'State_1', self.sprav_holder.state_codes, u'S_State')

    def contr_slnad(self):
        self.contr_field(crs_tab, u'SLNAD', self.sprav_holder.slnad_codes, u'SlNadel')

    def contr_users(self):
        self.contr_field(users_tab, u'UserType', self.sprav_holder.user_types, u'S_Usertype')
        self.contr_is_unique(users_tab, u'UserN')

    def contr_is_unique(self, table, field):
        all_usern = self.select_errors(u'select %s from %s' % (field, table))
        wrong_kodes = filter(lambda x: all_usern.count(x)>1, all_usern)
        if wrong_kodes:
            query = u'select OBJECTID from %s where %s in %s' % (table, field, unicode(tuple(set(wrong_kodes))))
            search_err = self.select_errors(query)
            self.add_to_protocol(table, field, search_err, 9)

    def contr_field(self, table, field, in_spr_data, spr_table, null_granted = False):
        """
        Makes dictionary with OBJECTID rows with errors
        :param spr_table: Name of S_'TableName' in Sprav, type unicode
        :param in_spr_data: type unicode
        :param table: control table name, unicode
        :param field: control field name, unicode
        """
        search_err = self.select_errors(u'select OBJECTID from %s where %s not in (%s) and %s is not Null' % (table, field, in_spr_data, field))
        self.add_to_protocol(table, field, search_err, 1, spr_table)
        if not null_granted:
            search_err = self.select_errors(u'select OBJECTID from %s where %s is Null' % (table, field))
            self.add_to_protocol(table, field, search_err, 3)

    def contr_part_1(self):
        search_err = self.select_errors(u'SELECT OBJECTID FROM crostab_razv WHERE not Part_1 between 0.0001 and 100')
        self.add_to_protocol(crs_tab, u'Part_1', search_err, 5)
        search_err = self.select_errors(u'select OBJECTID from crostab_razv where Part_1 is Null')
        self.add_to_protocol(crs_tab, u'Part_1', search_err, 3)

    def contr_soato_crtab(self):
        search_err = self.select_errors(u'SELECT a.OBJECTID FROM crostab_razv a LEFT JOIN SOATO b ON a.SOATO = b.KOD WHERE b.KOD Is Null')
        self.add_to_protocol(crs_tab, u'SOATO', search_err, 2, soato_tab)
        search_err = self.select_errors(u'select OBJECTID from crostab_razv where SOATO is Null')
        self.add_to_protocol(crs_tab, u'SOATO', search_err, 3)

    def contr_user_1(self):
        search_err = self.select_errors(u'select a.OBJECTID from crostab_razv a left join Users b ON a.UserN_1 = b.UserN where b.UserN is Null and a.UserN_Sad is NULL')
        self.add_to_protocol(crs_tab, u'UserN_1', search_err, 2, users_tab)
        search_err = self.select_errors(u'select OBJECTID from crostab_razv where UserN_1 is Null')
        self.add_to_protocol(crs_tab, u'UserN_1', search_err, 3)

    def contr_usern_sad(self):
        search_err = self.select_errors(u'select a.OBJECTID from crostab_razv a left join Users b on a.UserN_Sad = b.UserN '
                                        u'where b.UserN Is Null and UserN_Sad is not Null')
        self.add_to_protocol(soato_tab, u'KOD, Name', search_err, 2, u'Users')

    def contr_kods_soato(self):
        search_err = self.select_errors(u'select OBJECTID from SOATO where KOD Is Null or Name is Null')
        self.add_to_protocol(soato_tab, u'KOD, Name', search_err, 3)
        self.contr_is_unique(soato_tab, u'KOD')

