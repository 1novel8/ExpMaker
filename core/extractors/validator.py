from core.db import ctrStructure, sprStructure

from .initializer import CtrControl

crs_tab = ctrStructure.crs_tab
soato_tab = ctrStructure.soato_tab
users_tab = ctrStructure.users_tab
crs_tab_str = ctrStructure.get_tab_str(crs_tab)
soato_tab_str = ctrStructure.get_tab_str(soato_tab)
users_tab_str = ctrStructure.get_tab_str(users_tab)


class DataControl(CtrControl):
    def __init__(self, sprav_holder, file_path, temp_db_path):
        self.errors_protocol = []
        self.sprav_holder = sprav_holder
        super(DataControl, self).__init__(file_path, temp_db_path)
        self.all_tabs_columns = self.get_all_fields()
        self.f22_string = self.get_f22_string()
        self.max_n = self.get_n_max()
        sprav_holder.max_n = self.max_n
        self.update_str_to_null()
        self.drop_empty_f_pref()

    def drop_empty_f_pref(self):
        self.conn.exec_query('delete from %s where %s is Null' % (soato_tab, soato_tab_str['pref']['name']))

    def get_crtab_fields(self):
        return self.conn.get_f_names_types(crs_tab).keys()

    def update_str_to_null(self):
        for tab in self.db_schema.tabs_enum:
            for field in self.db_schema.get_tab_str(tab).values():
                if isinstance(field['type'], list) and 'VARCHAR' in field['type']:
                    # TODO:
                    # You can add a check query here like "select OBJECTID from %s where  %s = ''" to make it better
                    self.conn.exec_query(u"update %s set %s = Null where %s = ''" % (tab, field['name'], field['name']))

    def select_errors(self, query):
        return self.conn.select_single_f(query)

    def get_f22_string(self):
        f22_str = []
        for key in self.sprav_holder.f22_notes:
            f22_str.append('\'%s\'' % key)
        f22_str = ','.join(f22_str)
        return f22_str

    def add_to_protocol(self, table, field, err_ids, err_desc, dynamic_param=None):
        """
        Makes data systematization for errors protocol, adds to protocol when err_ids returns True
        :param table: table with errors                 type: str
        :param field: field where errors found          type: str
        :param err_ids: OBJECTIDs where errors found,   type: str or some array type
        :param err_desc: code of the error (you can find the description of error by this code), type: int
        :param dynamic_param: if description, founded by err_desc code, need some dop parameters, you should transfer it by this parameter
        """
        if err_ids:
            err_doc = {
                'table': table,
                'field': field,
                'err_ids': err_ids,
                'err_msg': err_desc,
                'dyn_param': dynamic_param
            }
            self.errors_protocol.append(err_doc)

    def check_group_fields(self):
        tab_flds = self.get_crtab_fields()
        check_flds = []
        for field in self.sprav_holder.attr_config['ctr_structure']:
            if '*' in field:
                multi_flds = map(lambda x: field.replace('*', str(x)), range(1, self.max_n + 1))
                check_flds.extend(multi_flds)
            else:
                check_flds.append(field)
        return list(filter(lambda x: x in tab_flds, check_flds))
        # TODO:
        # raise error if returns true(show lost fields)

    def run_field_control(self):
        self.errors_protocol = []
        self.check_group_fields()
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
        def format_d(x):
            return {
                'cr_tab': crs_tab,
                'o_id': crs_tab_str['id']['name'],
                'f22_n': crs_tab_str['f22']['part_name'] + str(x),
                'part_n': crs_tab_str['part_n']['part_name'] + str(x),
                'user_n': crs_tab_str['user_n']['part_name'] + str(x),
            }

        for n in range(2, self.max_n + 1):
            protocol_tip = '%(f22_n)s, %(user_n)s или %(part_n)s' % format_d(n)
            search_err = self.select_errors(
                'SELECT %(o_id)s FROM %(cr_tab)s WHERE %(user_n)s is NOT Null and (%(f22_n)s is Null or %(part_n)s = 0)' % format_d(
                    n))
            self.add_to_protocol(crs_tab, protocol_tip, search_err, 6, n)
            search_err = self.select_errors(
                'SELECT %(o_id)s FROM %(cr_tab)s WHERE %(f22_n)s is NOT Null and (%(user_n)s is Null or %(part_n)s = 0)' % format_d(
                    n))
            self.add_to_protocol(crs_tab, protocol_tip, search_err, 6, n)
            search_err = self.select_errors(
                'SELECT %(o_id)s FROM %(cr_tab)s WHERE %(part_n)s <> 0 and (%(user_n)s is Null or %(f22_n)s is Null)' % format_d(
                    n))
            self.add_to_protocol(crs_tab, protocol_tip, search_err, 6, n)

    def contr_part_sum(self):
        format_d = {
            'cr_tab': crs_tab,
            'o_id': crs_tab_str['id']['name'],
            'part1': crs_tab_str['part_n']['name'],
            'part': crs_tab_str['part_n']['part_name'],
            'max_n': self.max_n
        }
        part_sum = format_d['part1']
        for n in range(2, self.max_n + 1):
            part_sum += '+' + format_d['part'] + str(n)
        format_d['part_sum'] = part_sum
        search_err = self.select_errors(
            'SELECT %(o_id)s FROM %(cr_tab)s WHERE round(%(part_sum)s,3) <> 100' % format_d)
        self.add_to_protocol(crs_tab, '%(part1)s..%(part)s%(max_n)s' % format_d, search_err, 8)

    def contr_part_n(self):

        def format_d(x):
            return {
                'cr_tab': crs_tab,
                'o_id': crs_tab_str['id']['name'],
                'part_n': crs_tab_str['part_n']['part_name'] + str(x),
            }

        for n in range(2, self.max_n + 1):
            search_err = self.select_errors(
                'SELECT %(o_id)s FROM %(cr_tab)s WHERE not %(part_n)s between 0 and 99.9999 or %(part_n)s is Null' % format_d(
                    n))
            self.add_to_protocol(crs_tab, 'Part_%d' % n, search_err, 7)
            search_err = self.select_errors(
                'SELECT %(o_id)s FROM %(cr_tab)s WHERE %(part_n)s is Null' % format_d(n))
            self.add_to_protocol(crs_tab, 'Part_%d' % n, search_err, 3)

    def contr_f22_n(self):
        for n in range(2, self.max_n + 1):
            f_name = crs_tab_str['f22']['part_name'] + str(n)
            self.contr_field(crs_tab, f_name, self.f22_string, sprStructure.f22, crs_tab_str['id']['name'], True)

    def get_n_max(self):
        def part_fields(n):
            return [
                crs_tab_str['part_n']['part_name'] + n,
                crs_tab_str['user_n']['part_name'] + n,
                crs_tab_str['f22']['part_name'] + n
            ]

        def raise_err(msg):
            raise Exception('Проверьте наличие полей %s' % str(msg))

        max_n = 1
        crtab_fields = list(self.get_crtab_fields())
        col_fields = len(crtab_fields)
        while True:
            f_set = set(crtab_fields + part_fields(str(max_n)))
            if col_fields == len(f_set):
                max_n += 1
            elif max_n == 1:
                raise_err(part_fields(1))
            elif len(f_set) - col_fields == 3:
                break
            else:
                raise_err(', '.join(part_fields(max_n)))
        return max_n - 1

    def contr_user_n(self):
        def format_d(x):
            return {
                'cr_tab': crs_tab,
                'o_id': crs_tab_str['id']['name'],
                'us_tab': users_tab,
                'c_us_n': crs_tab_str['user_n']['part_name'] + str(x),
                'u_us_n': users_tab_str['user_n']['name'],
                'us_sad': crs_tab_str['user_n_sad']['name']
            }

        for n in range(2, self.max_n + 1):
            query = 'SELECT c.%(o_id)s FROM %(cr_tab)s c LEFT JOIN %(us_tab)s u ON c.%(c_us_n)s = u.%(u_us_n)s ' \
                    'WHERE u.%(u_us_n)s Is Null and c.%(c_us_n)s is not Null and %(us_sad)s is Null' % format_d(n)
            search_err = self.select_errors(query)
            self.add_to_protocol(crs_tab, format_d(n)['c_us_n'], search_err, 2, users_tab)

    def contr_melio_code(self):
        self.contr_field(
            crs_tab,
            crs_tab_str['mc']['name'],
            self.sprav_holder.melio_codes,
            sprStructure.mc,
            crs_tab_str['id']['name'])

    def contr_lc(self):
        lc = []
        lc_sprav = self.sprav_holder.land_codes
        for key in lc_sprav:
            lc.extend(lc_sprav[key])
        lc = set(lc)
        lc = ','.join(map(lambda x: str(x), lc))
        self.contr_field(crs_tab, crs_tab_str['lc']['name'], lc, sprStructure.lc, crs_tab_str['id']['name'])

    def contr_f22_1(self):
        self.contr_field(
            crs_tab,
            crs_tab_str['f22']['name'],
            self.f22_string,
            sprStructure.f22,
            crs_tab_str['id']['name'])

    def contr_state(self):
        self.contr_field(
            crs_tab,
            crs_tab_str['state']['name'],
            self.sprav_holder.state_codes,
            sprStructure.state,
            crs_tab_str['id']['name'])

    def contr_slnad(self):
        self.contr_field(
            crs_tab,
            crs_tab_str['sl_nad']['name'],
            self.sprav_holder.slnad_codes,
            sprStructure.slnad,
            crs_tab_str['id']['name'])

    def contr_users(self):
        self.contr_field(
            users_tab,
            users_tab_str['user_type']['name'],
            self.sprav_holder.user_types,
            sprStructure.ustype,
            users_tab_str['id']['name'])
        self.contr_is_unique(
            users_tab,
            users_tab_str['user_n']['name'],
            users_tab_str['id']['name'])

    def contr_is_unique(self, table, field, search_id):
        all_usern = self.select_errors('SELECT %s FROM %s' % (field, table))
        wrong_kodes = list(filter(lambda x: all_usern.count(x) > 1, all_usern))
        if wrong_kodes:
            query = 'SELECT %s FROM %s WHERE %s in %s' % (search_id, table, field, str(tuple(set(wrong_kodes))))
            search_err = self.select_errors(query)
            self.add_to_protocol(table, field, search_err, 9)

    def contr_field(self, table, field, check_codes, spr_table, search_id, null_granted=False, ):
        """
        Makes dictionary with OBJECTID rows with errors
        :type null_granted: bool
        :param spr_table: Name of S_'TableName' in Sprav, type str
        :param check_codes: type str
        :param table: control table name, str
        :param search_id:
        :param field: control field name, str
        """
        format_d = {'t': table, 'f': field, 'id': search_id, 'c': check_codes}
        query = 'SELECT %(id)s FROM %(t)s where %(f)s not in (%(c)s) and %(f)s is not Null' % format_d
        search_err = self.select_errors(query)
        self.add_to_protocol(table, field, search_err, 1, spr_table)
        if not null_granted:
            search_err = self.select_errors('SELECT %(id)s FROM %(t)s where %(f)s is Null' % format_d)
            self.add_to_protocol(table, field, search_err, 3)

    def contr_part_1(self):
        format_d = {
            'cr_tab': crs_tab,
            'o_id': crs_tab_str['id']['name'],
            'part1': crs_tab_str['part_n']['name']
        }
        search_err = self.select_errors(
            'SELECT %(o_id)s FROM %(cr_tab)s WHERE not %(part1)s between 0.0001 and 100' % format_d)
        self.add_to_protocol(crs_tab, format_d['part1'], search_err, 5)
        search_err = self.select_errors(
            'select %(o_id)s from %(cr_tab)s WHERE %(part1)s is Null' % format_d)
        self.add_to_protocol(crs_tab, 'Part_1', search_err, 3)

    def contr_soato_crtab(self):
        format_d = {
            'cr_tab': crs_tab,
            'o_id': crs_tab_str['id']['name'],
            's_tab': soato_tab,
            'c_kod': crs_tab_str['soato']['name'],
            's_kod': soato_tab_str['code']['name']
        }
        search_err = self.select_errors(
            'SELECT c.%(o_id)s FROM %(cr_tab)s c LEFT JOIN %(s_tab)s s ON c.%(c_kod)s = s.%(s_kod)s WHERE s.%(s_kod)s Is Null' % format_d)
        self.add_to_protocol(crs_tab, format_d['c_kod'], search_err, 2, soato_tab)
        search_err = self.select_errors(
            'SELECT %(o_id)s FROM %(cr_tab)s WHERE %(c_kod)s is Null' % format_d)
        self.add_to_protocol(crs_tab, format_d['c_kod'], search_err, 3)

    def contr_user_1(self):
        format_d = {
            'cr_tab': crs_tab,
            'o_id': crs_tab_str['id']['name'],
            'u_tab': users_tab,
            'c_us_1': crs_tab_str['user_n']['name'],
            'c_sad': crs_tab_str['user_n_sad']['name'],
            'u_us': users_tab_str['user_n']['name'],
        }
        search_err = self.select_errors(
            'SELECT c.%(o_id)s FROM %(cr_tab)s c left join %(u_tab)s u ON c.%(c_us_1)s = u.%(u_us)s'
            ' WHERE u.%(u_us)s is Null and c.%(c_sad)s is NULL' % format_d)
        self.add_to_protocol(crs_tab, format_d['c_us_1'], search_err, 2, users_tab)
        search_err = self.select_errors(
            'SELECT %(o_id)s FROM %(cr_tab)s WHERE %(c_us_1)s is Null' % format_d)
        self.add_to_protocol(crs_tab, format_d['c_us_1'], search_err, 3)

    def contr_usern_sad(self):
        format_d = {
            'cr_tab': crs_tab,
            'o_id': crs_tab_str['id']['name'],
            'u_tab': users_tab,
            'c_sad': crs_tab_str['user_n_sad']['name'],
            'u_us': users_tab_str['user_n']['name'],
        }
        search_err = self.select_errors(
            'SELECT c.%(o_id)s FROM %(cr_tab)s c left join %(u_tab)s u on c.%(c_sad)s = u.%(u_us)s '
            'WHERE u.%(u_us)s Is Null and %(c_sad)s is not Null' % format_d)
        self.add_to_protocol(crs_tab, format_d['c_sad'], search_err, 2, users_tab)

    def contr_kods_soato(self):
        format_d = {
            's_tab': soato_tab,
            'id': soato_tab_str['id']['name'],
            'kod': soato_tab_str['code']['name'],
            'name': soato_tab_str['name']['name'],
        }
        query = 'SELECT %(id)s FROM %(s_tab)s WHERE %(kod)s Is Null or %(name)s is Null' % format_d
        search_err = self.select_errors(query)
        self.add_to_protocol(soato_tab, 'KOD, Name', search_err, 3)
        self.contr_is_unique(soato_tab, format_d['kod'], format_d['id'])
