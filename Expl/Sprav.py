#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyodbc
import os.path

class DBConn(object):
    def __init__(self, db_pass, do_conn = True):
        self.db_pass = db_pass
        self.db_access = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' % db_pass
        self.__conn = None
        self.__dbc = None
        self.reconnect = False
        if do_conn:
            self.make_connection()
    def get_dbc(self):
        return self.__dbc

    def make_connection(self):
        if not self.__dbc:
            try:
                self.__conn = pyodbc.connect(self.db_access, autocommit = True, unicode_results = True)
                self.__dbc = self.__conn.cursor()
            except pyodbc.Error:
                self.__dbc = False

    def close_conn(self):
        if self.__dbc:
            try:
                self.__dbc.close()
                self.__conn.close()
                self.__conn = None
                self.__dbc = None
            except: pass

    def get_tables(self):
        if self.__dbc:
            try:
                return self.__dbc.tables(tableType=u'TABLE')
            except: pass
        return []

    def get_columns(self, table_name):
        if self.__dbc:
            try:
                return self.__dbc.columns(table= table_name)
            except:
                return []

    def get_f_names(self, table_name):
        f_names = []
        for f_info in self.get_columns(table_name):
            f_names.append(f_info[3])
        return f_names

    def get_f_names_types(self, table_name):
        f_name_type = {}
        for f_info in self.get_columns(table_name):
            f_name_type[f_info[3]] = f_info[5]
        return f_name_type

    def insert_row(self, tab_name, fields, vals):
        if self.__dbc:
            ins_query = u'insert into %s(' % tab_name
            f_count = len(fields)-1
            ins_query+=u'?,'*f_count+u'?) values (' + u'?,'*f_count +u'?);'
            args = tuple(fields+vals)

            try:
                self.__dbc.execute(ins_query, args)
                return True
            except pyodbc.ProgrammingError:
                pass
            except pyodbc.Error:
                print  pyodbc.Error
                pass
        return False

    def exec_query(self, query, reconnect = False):
        if self.__dbc:
            try:
                self.__dbc.execute(query)
                return True
            except pyodbc.ProgrammingError:
                return False
            except pyodbc.Error:
                if reconnect:
                    self.close_conn()
                    self.make_connection()
                    return self.exec_query(query)
                else:
                    return False
    def run_db(self):
        os.system(u'start %s' % self.db_pass)
    @property
    def has_dbc(self):
        return True if self.__dbc else False

    def exec_sel_query(self, query):
        if self.__dbc:
            try:
                sel_res = [row for row in self.__dbc.execute(query).fetchall()]
                return sel_res
            except pyodbc.ProgrammingError: pass
            except pyodbc.Error: pass
        return False

    def get_tab_dict(self, query):
        """Вернет словарь на основе данных полученных в результате выполнения запроса.
            :key - первый параметр запроса
            :value - список оставшихся параметров"""
        rc_dict ={}
        rc_rows = self.exec_sel_query(query)
        if isinstance(rc_rows, list):
            for row in rc_rows:
                rc_dict[row[0]] = list(row[1:])
            return rc_dict
        else: return {}

    def get_tab_list(self, query):
        result = self.exec_sel_query(query)
        if isinstance(result, list):
            return result
        else: return []

    def __del__(self):
        self.close_conn()

def u_to_int(li):
    newli = []
    for i in range(len(li)):
        newli.append(int(li[i]))
    return newli


def remake_list(li):
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

class SpravError(Exception):
    def __init__(self, e_type, *args):
        self.text = u'Unexpected error!'
        if e_type == 1:
            if len(args) == 2:
                row, table  = args
                self.text = u'Не корректные данные справочника! Проверьте строку %s в таблице %s' % (table, row)
            else: self.text+=u'wrong args.'
        elif e_type==0:
            self.text = u'Не удалось соединиться с базой данных справочников'
        elif e_type == 2:
            self.text = u'не удалось выполнить запрос %s. Проверьте корректность базы данных' % unicode(args)
        super(SpravError, self).__init__(self.text)

def catch_sprav_err(decor_method):
    def wrapper(*args, **kwargs):
        try:
            return decor_method(*args, **kwargs)
        except SpravError:
            raise
        except:
            if len(args) == 1:
                raise SpravError(2, args)
            else:
                raise SpravError(3)
    return wrapper

class SpravHolder(object):
    def __init__(self):
        self.s_conn = None
        self.expa_f_str = None
        self.expa_r_str = None
        self.expb_f_str = None
        self.expb_r_str = None
        self.soato_npt = None
        self.bgd2ekp =   None
        self.f22_notes = None
        self.bgd2ekp_1 = None
        self.bgd2ekp_2 = None
        self.user_types = None
        self.slnad_codes =None
        self.state_codes =None
        self.melio_codes =None
        self.land_codes =None

    def set_parameters(self, sprav_dict):
        try:
            self.expa_f_str = sprav_dict[u'expa_f_str']
            self.expa_r_str = sprav_dict[u'expa_r_str']
            self.expb_f_str = sprav_dict[u'expb_f_str']
            self.expb_r_str = sprav_dict[u'expb_r_str']
            self.soato_npt = sprav_dict[u'soato_npt']
            self.f22_notes = sprav_dict[u'f22_notes']
            self.bgd2ekp_1 = self.bgd_to_dicts(sprav_dict[u'bgd2ekp'][0])
            self.bgd2ekp_2 = self.bgd_to_dicts(sprav_dict[u'bgd2ekp'][2])
            self.user_types = sprav_dict[u'user_types']
            self.slnad_codes = sprav_dict[u'slnad_codes']
            self.state_codes = sprav_dict[u'state_codes']
            self.melio_codes = sprav_dict[u'melio_codes']
            self.land_codes = sprav_dict[u'land_codes']
            return True
        except KeyError:
            return False

    def get_data_from_db(self, spr_path):
        self.s_conn = DBConn(spr_path, False)
        data_dict = {}
        self.s_conn.make_connection()
        if self.s_conn.has_dbc:
            try:
                data_dict[u'land_codes'] = self.get_l_codes()
                data_dict[u'expa_f_str'] = self.get_expa_f_str(data_dict[u'land_codes'])
                data_dict[u'expa_r_str'] = self.get_expa_r_str()
                data_dict[u'expb_f_str'] = self.get_expb_f_str(data_dict[u'land_codes'])
                data_dict[u'expb_r_str'] = self.get_expb_r_str(data_dict[u'expb_f_str'].keys())
                data_dict[u'soato_npt'] = self.get_np_type()
                data_dict[u'bgd2ekp'] = self.remake_bgd2()
                data_dict[u'f22_notes'] = self.get_f22_notes()
                data_dict[u'user_types'] = self.select_to_str(u'select UsertypeCode from S_Usertype')
                data_dict[u'slnad_codes'] = self.select_to_str(u'select SLNADCode from S_Slnad')
                data_dict[u'state_codes'] = self.select_to_str(u'select StateCode from S_State')
                data_dict[u'melio_codes'] = self.select_to_str(u'select MelioCode from S_MelioCode')
            except SpravError:
                raise
            except Exception:
                raise SpravError(3)
        else:
            raise SpravError(0)
        self.s_conn.close_conn()
        return data_dict

    @catch_sprav_err
    def select_sprav(self, query):
        res = self.s_conn.get_tab_list(query)
        return res

    @catch_sprav_err
    def select_to_str(self, query):
        codes_list = self.s_conn.exec_sel_query(query)
        codes_list = map(lambda x : u'\'%s\'' % x[0] if isinstance(x[0], unicode) else str(x[0]), codes_list)
        codes_list = ', '.join(codes_list)
        return codes_list
    def get_expa_f_str(self,l_codes):
        f_structure = self.s_conn.get_tab_dict(u'select f_num, f_name, sum_fields from ExpA_f_Structure')
        for key in f_structure:
            f_props = f_structure[key]
            sum_f = self.eval_to_list(f_props[1]) if f_props[1] else []
            f_structure[key] = {u'f_name':f_props[0], u'sum_f':sum_f}
            try:
                f_structure[key][u'codes'] = l_codes[key]
            except KeyError:
                f_structure[key][u'codes'] = []
        return f_structure

    def get_expb_f_str(self, l_codes):
        f_structure = self.s_conn.get_tab_dict(u'select f_name, f_num, sort_key, sum_fields from ExpB_f_Structure')
        r_codes = self.s_conn.get_tab_dict(u'select RowName, Code, SortIndex from ExpA_r_Structure')
        for key in f_structure:
            f_props = f_structure[key]
            sum_f = self.eval_to_list(f_props[2]) if f_props[2] else []
            f_structure[key] = {u'f_num':f_props[0], u'sum_f':sum_f}
            srt_cases = self.split_line(f_props[1], u';')
            if not srt_cases:
                continue
            sort_codes = []
            indexes = []
            for srt in srt_cases:
                if u'(' in srt:
                    s_by = srt[:srt.index('(')]
                    substr = srt[srt.index('(')+1:-1]
                    if s_by == u'lc':
                        srt_ind = 1
                    elif s_by in r_codes:
                        srt_ind = r_codes[srt][1]
                    else:
                        raise SpravError(1, u'ExpB_f_Structure', key)
                    params = self.split_line(substr, u',')
                    temp_li = []
                    for i in params:
                        if u'*' in i and srt_ind == 1:
                            i = i.replace(u'*',u'')
                            try:
                                i = int(i)
                            except ValueError:
                                raise SpravError(1, u'ExpB_f_Structure', key)
                            if i in l_codes:
                                temp_li.extend(l_codes[i])
                        else:
                            try:
                                temp_li.append(int(i))
                            except ValueError:
                                raise SpravError(1, u'ExpB_f_Structure', key)
                    sort_codes.append(temp_li)
                    indexes.append(srt_ind)
                elif srt == u'lc':
                    if l_codes.has_key(f_props[0]):
                        sort_codes.append(l_codes[f_props[0]])
                        indexes.append(1)
                elif srt in r_codes:
                    codes = self.eval_to_list(r_codes[srt][0])
                    if codes:
                        sort_codes.append(codes)
                        indexes.append(r_codes[srt][1])
                else:
                    raise SpravError(1, u'ExpB_f_Structure', key)
            if sort_codes:
                f_structure[key][u'codes'] = sort_codes
                f_structure[key][u'sort_i'] = indexes
        return f_structure

    @staticmethod
    def eval_to_list(string):
        try:
            return list(eval(string))
        except (SyntaxError, NameError, TypeError)  :return []

    @staticmethod
    def split_line(line, symbol):
        """
        :param line:
        :param symbol: splitter
        :return: without spaces, without elements which returns False
        """
        if type(line) in (str, unicode):
            split_l = line.replace(u' ',u'').split(symbol)
            for l in split_l:
                if not l:split_l.remove(l)
            return split_l
        else:
            return []

    def get_l_codes(self):
        lc_d = {}
        l_codes = self.select_sprav(u'select Field_num, LandCode from LandCodes')
        for (key, kod) in l_codes:
            try: lc_d[key].append(kod)
            except KeyError: lc_d[key] = [kod,]
        return lc_d

    def get_expa_r_str(self):
        query = u'select RowID, RowName, Code, SortIndex from ExpA_r_Structure'
        params = self.s_conn.get_tab_dict(query)
        for key in params:
            if params[key][1]:
                cods = self.eval_to_list(params[key][1])
                if not cods:
                    raise SpravError(1, u'ExpA_r_Structure', key)
            else: cods = []
            params[key][1] = cods
        return  params


    def get_expb_r_str(self, f_names):
        query = u'select row_key, val_f22, sort_by, ConditionSum from ExpB_r_Structure'
        r_params = self.s_conn.get_tab_dict(query)
        def r_err(r_k):
            raise SpravError(1, u'ExpB_r_Structure', r_k)
        for key in r_params:
            start_params = r_params[key]
            r_params[key] = {u'row_name':start_params[0]}       #work with val_f22
            if start_params[1]:                                    #work with sort_by
                sort_param = self.split_line(start_params[1], u'=')
                if len(sort_param) == 2: # проверка, правильно ли введена инфа в поле sort_by
                    r_params[key][u's_by'] = sort_param[0] # артибут, по которму производится сортировка
                    if sort_param[0] == u'f22':
                        r_params[key][u's_p'] = sort_param[1]# значение атрибута
                    else:
                        s_p = self.eval_to_list(sort_param[1])
                        r_params[key][u's_p'] = s_p if s_p else []
            else:r_params[key][u's_by'] = []
            if start_params[2]:
                r_params[key][u'conds'] = {}
                conditions = self.split_line(start_params[2], u';')
                for cond in conditions:
                    cond_op = cond[0]
                    cond = cond[1:]
                    if cond:
                        if cond_op in u'+-':
                            add_rows = self.split_line(cond, u',')
                            if not self.is_include(r_params.keys(), add_rows):  #check is include, add included
                                r_err(key)
                            key_name = u'add' if cond_op == u'+' else u'sub'
                            r_params[key][u'conds'][key_name] = add_rows
                        elif cond_op == u'&':
                            eq_di = {}
                            eq = self.split_line(cond, u'=')
                            if len(eq) == 2:
                                # get operation type
                                if eq[0][-1] == u'+':
                                    eq[0] = eq[0][:-1]
                                    eq_di[u'op'] = u'+'
                                elif eq[0][-1] == u'-':
                                    eq[0] = eq[0][:-1]
                                    eq_di[u'op'] = u'-'
                                else:
                                    eq_di[u'op'] = u'='
                                # parse parameters and check their validation
                                if eq[0] in f_names:
                                    eq_di[u'upd_f'] = eq[0]
                                    eq_right = self.split_line(eq[1],u':')
                                    if len(eq_right) == 2:
                                        if eq_right[0] in r_params and eq_right[1] in f_names:
                                            eq_di[u'take_f'] = eq_right[1]
                                            eq_di[u'take_r'] = eq_right[0]
                                        else: continue
                                    elif len(eq_right) == 1:
                                        if eq_right[0] in f_names:
                                            eq_di[u'take_f'] = eq_right[0]
                                            eq_di[u'take_r'] = key
                                        else: r_err(key)
                                    else: r_err(key)
                                    #add eq_di key to r_params[key] in case that all clear
                                    try:
                                        r_params[key][u'conds'][u'eq_f'].append(eq_di)
                                    except KeyError:
                                        r_params[key][u'conds'][u'eq_f'] = [eq_di,]
                                else: r_err(key)
                            else: r_err(key)
                    else: r_err(key)
        return  r_params

    @staticmethod
    def is_include(main_li, inc_li):
        li = main_li[:]
        li.extend(inc_li)
        if len(set(li)) == len(main_li):
            return True
        else: return False

    def get_np_type(self):
        query = u'select znak1, znak2, znak57min, znak57max, znak810min,znak810max,TypeNP from SOATO'
        return self.s_conn.exec_sel_query(query)

    def remake_bgd1(self):
        """
        BGD1 have fields: F22,UTYPE, NPTYPE_min, NPTYPE_max, State, SLNAD, NEWUSNAME, DOPUSNAME
        :return: list with BGD1 rows
        """
        selectbgd1 = u'select F22,UTYPE,NPTYPE,STATE,SLNAD,NEWUSNAME,DOPUSNAME from BGDtoEkp1'
        newbgd = []
        if self.s_conn:
            for row in self.select_sprav(selectbgd1):
                utypelist = u_to_int(row[1].split(','))
                nptypelist = u_to_int(row[2].split(','))
                stateli = u_to_int(row[3].split(','))
                nptypeliremaked = remake_list(nptypelist)
                for state in stateli:
                    for utype in utypelist:
                        for npt in nptypeliremaked:
                            newbgd.append((row[0], utype, state, int(row[4]), npt[0], npt[1],  row[5],row[6]))
        return newbgd

    def remake_bgd2(self, upd_lc_st = True):
        selectbgd2 = u'select F22,NEWF22,UTYPE,NPTYPE,LCODE_MIN,LCODE_MAX,NewLCODE,STATE,NewSTATE,SLNAD, NEWUSNAME,DOPUSNAME from BGDtoEkp2'
        bgd2 = []
        if self.s_conn:
            for row in self.select_sprav(selectbgd2):
                utypelist = u_to_int(row[2].split(u','))
                nptypelist = u_to_int(row[3].split(u','))
                stateli = u_to_int(row[7].split(u','))
                nptypeliremaked = remake_list(nptypelist)
                if upd_lc_st:
                    nlc, nst = row[6],row[8]
                else:
                    nlc, nst = None, None
                for state in stateli:
                    for utype in utypelist:
                        for npt in nptypeliremaked:
                            bgd2.append((row[0], utype, state, int(row[9]), row[1],  npt[0], npt[1], row[4], row[5], nlc,
                                         nst,  row[10], row[11]))
            bgd2 = (self.remake_bgd1(),upd_lc_st,bgd2)
        return bgd2
    # bgd_row: F22, UTYPE, State, SLNAD, newF22,NPTYPE_min, NPTYPE_max, lc_min, lc_max, newlc,  newstate,  NEWUSNAME, DOPUSNAME

    def get_f22_notes(self):
        f22_notes = self.select_sprav(u'Select F22Code, Notes from S_Forma22')
        f22_n_dict = {}
        for row in f22_notes:
            f22_n_dict[row[0]] = row[1]
        return f22_n_dict

    @staticmethod
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

class SpravControl(object):
    def __init__(self, db_path, fullcontr = True):
        self.db_path = db_path
        self.tabs_fields = dict()
        self.tabs_fields[u'LandCodes'] = [(u'OBJECTID', u'COUNTER'), (u'LandCode', u'SMALLINT'), (u'field_Num', u'SMALLINT'), (u'ValueF22', u'VARCHAR')]
        self.tabs_fields[u'ExpA_r_Structure'] = [(u'RowID', u'INTEGER'), (u'Code', u'VARCHAR'), (u'RowName', u'VARCHAR'), (u'SortIndex', u'SMALLINT')]
        self.tabs_fields[u'ExpA_f_Structure'] = [(u'f_num', u'INTEGER'), (u'f_name', u'VARCHAR'), (u'sum_fields', u'VARCHAR')]
        self.tabs_fields[u'ExpB_f_Structure'] = [(u'f_num', u'INTEGER'), (u'f_name', u'VARCHAR'), (u'sort_key', u'VARCHAR'), (u'sum_fields', u'VARCHAR')]
        self.tabs_fields[u'ExpB_r_Structure'] = [(u'row_key', u'VARCHAR'), (u'val_f22', u'VARCHAR'), (u'sort_by', u'VARCHAR'), (u'ConditionSum', u'VARCHAR')]
        if fullcontr:
            self.tabs_fields[u'BGDToEkp1'] = [(u'F22', u'VARCHAR'), (u'UTYPE', u'VARCHAR'), (u'NPTYPE', u'VARCHAR'), (u'STATE', u'VARCHAR'), (u'SLNAD', u'VARCHAR'), (u'NEWUSNAME', u'SMALLINT'), (u'DOPUSNAME', u'VARCHAR')]
            self.tabs_fields[u'BGDToEkp2'] = [(u'F22', u'VARCHAR'), (u'NEWF22', u'VARCHAR'), (u'UTYPE', u'VARCHAR'), (u'NPTYPE', u'VARCHAR'), (u'LCODE_MIN', u'SMALLINT'), (u'LCODE_MAX', u'SMALLINT'), (u'NewLCODE', u'SMALLINT'), (u'STATE', u'VARCHAR'), (u'NewSTATE', u'VARCHAR'), (u'SLNAD', u'VARCHAR'), (u'NEWUSNAME', u'SMALLINT'), (u'DOPUSNAME', u'VARCHAR')]
            self.tabs_fields[u'SOATO'] = [(u'OBJECTID', u'COUNTER'), (u'znak1', u'VARCHAR'), (u'znak2', u'SMALLINT'), (u'znak57min', u'SMALLINT'), (u'znak57max', u'SMALLINT'), (u'znak810max', u'SMALLINT'), (u'znak810min', u'SMALLINT'), (u'TypeNP', u'SMALLINT'), (u'NPTypeNotes', u'VARCHAR'), (u'SovType', u'VARCHAR')]
            self.tabs_fields[u'S_State'] = [(u'OBJECTID', u'COUNTER'), (u'StateCode', u'SMALLINT')]
            self.tabs_fields[u'S_Forma22'] = [(u'OBJECTID', u'COUNTER'), (u'F22Code', u'VARCHAR'), (u'Notes', u'VARCHAR')]
            self.tabs_fields[u'S_MelioCode'] = [(u'OBJECTID', u'COUNTER'), (u'MelioCode', u'SMALLINT'), (u'Notes', u'VARCHAR'), (u'NumberStrEkp', u'VARCHAR'), (u'ValueFormEkp', u'VARCHAR'), (u'NumberGrF22_1', u'VARCHAR'), (u'ValueFormF22_1', u'VARCHAR')]
            self.tabs_fields[u'S_SlNad'] = [(u'OBJECTID', u'COUNTER'), (u'SLNADCode', u'BYTE')]
            self.tabs_fields[u'S_Usertype'] = [(u'OBJECTID', u'COUNTER'), (u'UsertypeCode', u'BYTE')]
        self.s_conn = DBConn(self.db_path)
        if self.s_conn.has_dbc:
            self.losttables = self.contr_tables()
            self.badfields = dict.fromkeys(self.tabs_fields.keys())
            for key in self.tabs_fields:
                self.badfields[key] = self.contr_field_types(key, self.tabs_fields[key])
                if not self.badfields[key]:
                    del self.badfields[key]
        else:
            raise SpravError(0)

    def __del__(self):
        del self.s_conn

    def contr_tables(self):
        self.sprav_tables = [row[2] for row in self.s_conn.get_tables()]
        returnlist = []
        for tab in self.tabs_fields:
            if tab not in self.sprav_tables:
                returnlist.append(tab)
        return returnlist

    def contr_field_types(self, tabname, tabstructure):
        fields_types = [(row[3], row[5]) for row in self.s_conn.get_columns(tabname)]
        returnlist = []
        for field in tabstructure:
            if field not in fields_types:
                returnlist.append(field)
        return returnlist

    
    
