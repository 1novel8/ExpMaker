#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DbTools import DBConn
import DbStructures
def add_column(connection, tabname, colname, coltype=u'int Null'):
    try:
        connection.exec_query(u'ALTER TABLE %s DROP "%s";' % (tabname, colname))
    except:
        pass
    connection.exec_query(u'ALTER TABLE %s ADD %s %s;' % (tabname, colname, coltype))

def add_nasp_name_to_soato(connection):
    tab_name = DbStructures.soato_tab
    format_d = {
        'nasp': u'NameNasp',
        'tab':  tab_name,
        'pref': DbStructures.db_structure[tab_name]['pref']['name'],
        'name': DbStructures.db_structure[tab_name]['name']['name'],
    }
    add_column(connection, tab_name, format_d['nasp'], u'varchar(80) NULL')
    updnamenasp1 = u"update %(tab)s set %(nasp)s = %(name)s +' '+%(pref)s where %(pref)s in ('р-н','с/с');" %format_d
    updnamenasp2 = u"update %(tab)s set %(nasp)s = %(pref)s +' '+ %(name)s where  %(nasp)s is Null" % format_d
    connection.exec_query(updnamenasp1)
    connection.exec_query(updnamenasp2)

def add_utype_to_crtab(connection, max_n = None):
    us_tab = DbStructures.users_tab
    cr_tab = DbStructures.crs_tab
    format_d = {
        'us_t': us_tab,
        'cr_t': cr_tab,
        'u_utype': DbStructures.db_structure[us_tab]['user_type']['name'],
        'u_usern': DbStructures.db_structure[us_tab]['user_n']['name']
    }
    for n in range(1,max_n+1):
        #---------------------------UserType_n----------------------------------------------
        format_d['c_utype'] =  u'UserType_' + unicode(n)
        format_d['c_usern'] = DbStructures.db_structure[cr_tab]['user_n']['part_name'] + unicode(n)
        add_column(connection, cr_tab, format_d['c_utype'])
        query = u'UPDATE %(us_t)s u INNER JOIN %(cr_t)s c ON u.%(u_usern)s = c.%(c_usern)s SET c.%(c_utype)s = u.%(u_utype)s;' % format_d
        connection.exec_query(query)
        # sql2 = u'''UPDATE Users INNER JOIN %(t)s ON Users.UserN = %(t)s.UserN_Sad
        #             SET %(t)s.Usertype_%(nn)d = [Users].[UserType],
        #                 %(t)s.UserN_%(nn)d = %(t)s.[UserN_Sad]
        #             WHERE %(t)s.UserN_%(nn)d is not null
        #                     and %(t)s.UserN_Sad is not null
        #                     and SLNAD = 2 ;''' % {u't': ct, u'nn': n}
        # connection.exec_query(sql2)
        #---------------------------PART_n----------------------------------------------
        # add_column(connection, ct, u"Area_%s" % n, u'DOUBLE NULL')
        # sqlarea = u'''UPDATE %(t)s
        #             SET Area_%(nn)s = (Part_%(nn)s/100)*[Shape_Area]
        #             WHERE Part_%(nn)s <> 0''' % {u't': ct, u'nn': n}
        # connection.exec_query(sqlarea)
# def upd_soato_tnp(table, f_kod, zn1, zn2, zn57min, zn57max, zn810min, zn810max, typenp):
#     sqlupdnp = u'update %s set NPType = %s where mid(%s, 1, 1) in (%s)'%(table, typenp, f_kod, zn1)
#     if zn2 is not  None:
#         sqlupdnp += u' and mid(%s, 2, 1) = %s' % (f_kod, zn2)
#     if zn57min is not None and zn57max is not None:
#         sqlupdnp += u' and (mid(%s, 5, 3) between %s and %s)' % (f_kod, zn57min, zn57max)
#     if zn810min is not None or zn810max is not None:
#         sqlupdnp += u' and (mid(%s, 8, 3) between %s and %s)' % (f_kod, zn810min, zn810max)
#     return sqlupdnp
def make_nptype(kod, npt_sprav):
    for row in npt_sprav:
        if int(kod[0]) == 5:
            return row[6]
        elif int(kod[1]) == row[1]:
                if row[2] <= int(kod[4:7]) <= row[3] or row[3] is None:
                    if row[4] <= int(kod[7:10]) <= row[5] or row[4] is None:
                        return row[6]

def catch_wrong_fkey(f_to_decor):
    def wrapper(self, *args, **kwargs):
        try:
            return f_to_decor(self, *args, **kwargs)
        except KeyError:
            raise Exception(u'Прервана попытка получить элемент по несуществующему ключу %s' % args[0])
    return wrapper

class CtrRow(object):
    def __init__(self, spr_holder, r_args, n):
        """
        land_code is always on index 0, slnad on index 1

        :param r_args: OBJECTID, SOATO, SlNad, State_1, LANDCODE, MELIOCODE, ServType08, Forma22_*, UserN_*,Usertype_*, Area_*, *dop_params
        :param n_dop_args: len of dop params array in the end of r_args
        :param nm: max number of parts in crostab table
        :param sprav: SpravHolder instance
        """
        self.row_ready = False
        self.has_err = False                # отанется False - контроль пройден,
        self.err_in_part = None
        self.structure = spr_holder.attr_config
        self.n = n
        self.__r_args = r_args
        self.soato = self.get_el_by_fkey('nptype')
        self.object_id = self.get_el_by_fkey('id')
        np_type = make_nptype(self.soato, spr_holder.soato_npt)
        if np_type is None:
            self.has_err = 4
            self.err_in_part = 1
            return
        self.__r_args[self.structure['nptype']] = np_type
        self.new_lc = None
        self.dopname = [None]*self.n
        self.nusname = [None]*self.n
        self.bgd_control(spr_holder)
        if not self.has_err:
            self.remake_area()
            self.remake_usern()
            self.block_r_args()


    def simplify_to_d(self, n, need_keys):
        """
        unused keys are drops ,
        :rtype : object with keys from structure
        """
        return_di = dict.fromkeys(need_keys)
        for key in need_keys:
            elem = self.__r_args[self.structure[key]]
            if isinstance(elem, (list, tuple)):
                return_di[key] = elem[n]
            else:
                return_di[key] = elem
        return return_di

    @catch_wrong_fkey
    def get_el_by_fkey(self, f_key):
        """
        Use to get row elemets from structure keys.
        :param f_key: structure key of multiple
        :return: element by structure key from self.__r_args
        """
        return self.__r_args[self.structure[f_key]]

    @catch_wrong_fkey
    def get_el_by_fkey_n(self, f_key, n):
        """
        Use to get row elemets from structure keys.
        Usage for multiple objects only! if n parameter out of range - exception will raise
        :param f_key: structure key of multiple
        :param n: element index
        :return: n-th element by structure key from self.__r_args
        """
        return self.__r_args[self.structure[f_key]][n]

    @catch_wrong_fkey
    def set_el_by_fkey(self, f_key, val):
        if not self.row_ready:
            self.__r_args[self.structure[f_key]] = val

    @catch_wrong_fkey
    def set_el_by_fkey_n(self, f_key, n,  val):
        if not self.row_ready:
            self.__r_args[self.structure[f_key]][n] = val

    def remake_area(self):
        if self.n>1:
            areas = []
            shape_area = self.get_el_by_fkey(u'area')
            for part in self.get_el_by_fkey(u'part'):
                areas.append(shape_area*part/100)
            self.set_el_by_fkey(u'area', areas)
        else:
            self.set_el_by_fkey(u'area', self.get_el_by_fkey(u'area'))

    def remake_usern(self):
        user_sad = self.get_el_by_fkey('usern_sad')
        if user_sad:
            self.__r_args[self.structure['usern']] = [user_sad for x in xrange(self.n)]

    def block_r_args(self, fix = True):
        def change_type(item):
            return tuple(item) if fix else list(item)
        r_args = self.__r_args
        for i in range(len(r_args)):
            if isinstance(r_args[i], (tuple, list)):
                r_args[i]= change_type(r_args[i])
        self.__r_args = change_type(r_args)
        self.row_ready = fix

    def has_code(self, n, param, codes):
        # if n <= self.n:
        val = self.get_el_by_fkey(param)
        if isinstance(val, (list, tuple)):
            val = val[n]
        return val in codes



    def check_filter_match(self, n, sort_filter):
        """
        Checks if row matches the filter
        :param n: N of the checking part
        :param sort_filter: an object containing filter params
        :return: Boolean
        """
        if not isinstance(sort_filter, dict) or not len(sort_filter.keys()):
            return False
        # match_result = True
        for k, v in sort_filter.items():
            if not isinstance(v, (list, tuple)):
                v = [v]
            if not self.has_code(n, k, v):
                return False
        return True

    def bgd_control(self, s_h):
        if self.n == 1:
            if self.bgd1_control(s_h, 0):
                pass
            elif self.bgd2_control(s_h, 0):
                if self.new_lc:
                    self.set_el_by_fkey('lc', self.new_lc)
            else:
                self.has_err = 1
                self.err_in_part = 1
        else:
            for n in range(self.n):
                if self.bgd1_control(s_h, n):
                    continue
                elif self.bgd2_control(s_h, n):
                    if self.new_lc:
                        self.set_el_by_fkey('lc', self.new_lc)
                else:
                    self.has_err = 2
                    self.err_in_part = n+1
                    break

    def bgd1_control(self, spr, n):
        try:
            bgd_li = spr.bgd2ekp_1[self.get_el_by_fkey('f22')[n]][self.get_el_by_fkey('usertype')[n]][self.get_el_by_fkey('state')][self.get_el_by_fkey('slnad')]
            for b_row in bgd_li:  # bgd_row: f22 > UTYPE > State > SLNAD > NPTYPE_min, NPTYPE_max,  NEWUSNAME, DOPUSNAME,
                if b_row[0] <= self.get_el_by_fkey('nptype') <= b_row[1]:
                    self.nusname[n] = b_row[2]
                    self.dopname[n] = b_row[3]

                    return True
        except KeyError:
            pass
        return False

    def bgd2_control(self, spr, n):
        f22 = self.get_el_by_fkey('f22')[n]
        utype = self.get_el_by_fkey('usertype')[n]
        state = self.get_el_by_fkey('state')
        slnad = self.get_el_by_fkey('slnad')
        try:
            bgd_li = spr.bgd2ekp_2[f22][utype][state][slnad]
                                            # newF22,NPTYPE_min, NPTYPE_max, lc_min, lc_max, newlc, NEWUSNAME, DOPUSNAME
            for b_row in bgd_li: # bgd_row: newF22(0), NPTYPE_min (1), NPTYPE_max (2), lc_min(3), lc_max(4), newlc(5), NEWUSNAME(6), DOPUSNAME(7)
                if b_row[1] <= self.get_el_by_fkey('nptype') <= b_row[2] \
                        and b_row[3] <= self.get_el_by_fkey('lc')  <= b_row[4]:
                    self.set_el_by_fkey_n('f22', n, b_row[0])
                    self.nusname[n] = b_row[6]
                    self.dopname[n] = b_row[7]
                    self.new_lc = b_row[5]
                    return True
        except KeyError:
            pass
        return False

def _make_crtab_query(fields, n_max, conditions = None):
    query = u'SELECT '
    for f in fields:
        if '*' in f:
            for n in range(1, n_max+1):
                query += f.replace('*', unicode(n)) + u', '
        else:
            query += f + u', '
    query = query[:-2] + u' FROM %s' % DbStructures.crs_tab
    cond_li = []
    if conditions:
        for key in conditions.keys():
            if conditions[key]:
                cond_li.append(unicode(conditions[key]))
    if len(cond_li):
        query += ' WHERE ' + ' AND '.join(cond_li)
    print query
    return query

def collapse_row(row, structure, n_max):
    return_row = []
    row = list(row)
    n_survived = 0
    for f in structure:
        if '*' in f:
            f_elements = row[:n_max]
            row = row[n_max:]
            if not n_survived:
                for i in f_elements:
                    if i:
                        n_survived+=1
                    else:
                        break
            return_row.append(f_elements[:n_survived])
        else:
            return_row.append(row.pop(0))
    return return_row, n_survived

def convert(sprav_holder, temp_db_path, select_conditions):
    n_max = sprav_holder.max_n
    ctr_conn = DBConn(temp_db_path)
    add_nasp_name_to_soato(ctr_conn)
    add_utype_to_crtab(ctr_conn, n_max)
    users_d, soato_d = data_users_soato(ctr_conn)
    query_structure = sprav_holder.attr_config['ctr_structure']
    select_ctr_all = _make_crtab_query(query_structure, n_max, select_conditions)
    sel_result = ctr_conn.exec_sel_query(select_ctr_all)
    shape_area_sum = get_shape_area_sum(ctr_conn)
    del ctr_conn

    rows_ok = []
    whats_err = {1:{}, 2:{}, 3:{}, 4:{}}
    got_errors = False
    if sel_result:
        for row in sel_result:
            modified_r = collapse_row(row, query_structure, n_max)
            new_row = CtrRow(sprav_holder, *modified_r)
            if new_row.has_err:
                err_part = u'Part_%d'%new_row.err_in_part
                try:
                    whats_err[new_row.has_err][err_part].append(new_row.object_id)
                except KeyError:
                    whats_err[new_row.has_err][err_part] = [new_row.object_id, ]
                    got_errors = True
            else:
                rows_ok.append(new_row)

        if got_errors:
            return whats_err
        else:
            additional_params = {
                'shape_sum': shape_area_sum,
                'shape_sum_enabled': True
            }
            save_info = [rows_ok, users_d, soato_d, additional_params]
            return save_info
    else:
        raise Exception('Ошибка при загрузке данных из crostab. Connection failed')

def get_shape_area_sum(ct_conn):
    format_d = {
        'cr_tab': DbStructures.crs_tab,
        'sh_area': DbStructures.db_structure[DbStructures.crs_tab]['shape_area']['name']
    }
    sel_result = ct_conn.exec_sel_query(u'select sum(%(sh_area)s) from %(cr_tab)s' % format_d)
    return sel_result[0][0]

def data_users_soato(ct_conn):
    """
    returns UsersDict and SoatoDict with keys usern and soato
    and values in unicode
    """
    users_tab = DbStructures.users_tab
    soato_tab = DbStructures.soato_tab
    format_d = {
        'users':    users_tab,
        'soato':    soato_tab,
        'user_n':   DbStructures.db_structure[users_tab]['user_n']['name'],
        'us_name':  DbStructures.db_structure[users_tab]['us_name']['name'],
        'code':   DbStructures.db_structure[soato_tab]['code']['name'],
        'name_nas_p': 'NameNasp'
    }
    sel_result = ct_conn.exec_sel_query(u'select %(user_n)s, %(us_name)s from %(users)s' % format_d)
    users_dict = dict(sel_result)
    sel_result = ct_conn.exec_sel_query(u'select %(code)s, %(name_nas_p)s from %(soato)s' % format_d)
    soato_dict = dict(sel_result)
    return users_dict, soato_dict


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