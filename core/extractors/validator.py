from typing import Dict

from core.db.structures.ctr import CtrStructure
from core.db.structures.sprav import SpravStructure
from core.settingsHolders.spravHolder import SpravHolder

from .initializer import CtrControl


class DataControl(CtrControl):
    def __init__(self, sprav_holder: SpravHolder, file_path: str, temp_db_path: str) -> None:
        self.errors_protocol = []
        self.sprav_holder = sprav_holder
        super().__init__(file_path, temp_db_path)
        self.all_tabs_columns: Dict[str, Dict[str, str]] = self.read_all_tables_scheme()
        self.f22_string: str = self.get_f22_string()
        self.max_n: int = self.get_n_max()
        sprav_holder.max_n = self.max_n
        self.update_str_to_null()
        self.drop_empty_f_pref()

    def drop_empty_f_pref(self):
        self.conn.exec_query(
            'delete from %s where %s is Null'
            % (CtrStructure.soato_table, CtrStructure.get_table_scheme(CtrStructure.soato_table)['pref']['name'])
        )

    def get_crostab_fields(self):
        return self.conn.read_table_scheme(CtrStructure.crs_table).keys()

    def update_str_to_null(self) -> None:
        for table in self.db_schema.all_tables:
            for field in self.db_schema.get_table_scheme(table).values():
                if isinstance(field['type'], list) and 'VARCHAR' in field['type']:
                    # TODO:
                    # You can add a check query here like "select OBJECTID from %s where  %s = ''" to make it better
                    self.conn.exec_query(
                        u"update %s set %s = Null where %s = ''" % (table, field['name'], field['name']))

    def select_errors(self, query: str):
        return self.conn.select_single_f(query)

    def get_f22_string(self) -> str:
        f22_str = []
        for key in self.sprav_holder.f22_notes:
            f22_str.append('\'%s\'' % key)
        f22_str = ','.join(f22_str)
        return f22_str

    def add_to_protocol(self, table: str, field: str, err_ids: str, err_code: int, dynamic_param=None):
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
                'err_msg': err_code,
                'dyn_param': dynamic_param,
            }
            self.errors_protocol.append(err_doc)

    def check_group_fields(self):
        crostab_fields = self.get_crostab_fields()
        check_fields = []
        for field in self.sprav_holder.attr_config['ctr_structure']:
            if '*' in field:
                multi_fields = map(lambda x: field.replace('*', str(x)), range(1, self.max_n + 1))
                check_fields.extend(multi_fields)
            else:
                check_fields.append(field)
        return list(filter(lambda x: x in crostab_fields, check_fields))

    def run_field_control(self):
        """
        Весь контроль входной базы данных
        """
        self.errors_protocol = []
        self.check_group_fields()
        self.check_valid_soato_table()
        self.check_usern__usern_sad_relation()
        self.check_user_1()
        self.check_soato_crostab_relation()
        self.check_part_1()
        self.check_users()
        self.check_sl_nad()
        self.check_state()
        self.check_f22_1()
        self.check_land_code()
        self.check_melio_code()
        self.check_user_n()
        self.check_f22_n()
        self.check_part_n()
        self.check_part_sum()
        self.check_us_f22_part()
        return self.errors_protocol

    def check_us_f22_part(self):
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        f22_part = cros_table_scheme['f22']['part_name']
        user_n_part = cros_table_scheme['user_n']['part_name']
        part_n_part = cros_table_scheme['part_n']['part_name']
        for ind in range(2, self.max_n + 1):
            protocol_tip = (f"{f22_part}{ind}, "
                            f"{user_n_part}{ind}, "
                            f"{part_n_part}{ind}")
            query = (f"SELECT {cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} "
                     f"WHERE {user_n_part}{ind} is NOT Null "
                     f"     and ({f22_part}{ind} is Null or {part_n_part}{ind} = 0)")
            search_err = self.select_errors(query)
            self.add_to_protocol(cros_table, protocol_tip, search_err, 6, ind)

            query = (f"SELECT {cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} "
                     f"WHERE {f22_part}{ind} is not Null "
                     f"     and ({user_n_part}{ind} is Null or {part_n_part}{ind} = 0)")
            search_err = self.select_errors(query)
            self.add_to_protocol(cros_table, protocol_tip, search_err, 6, ind)

            query = (f"SELECT {cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} "
                     f"WHERE {part_n_part}{ind} <> 0 "
                     f"     and ({user_n_part}{ind} is Null or {f22_part}{ind} is Null)")
            search_err = self.select_errors(query)
            self.add_to_protocol(cros_table, protocol_tip, search_err, 6, ind)

    def check_part_sum(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        part_sum = cros_table_scheme['part_n']['name']
        for n in range(2, self.max_n + 1):
            part_sum += '+' + cros_table_scheme['part_n']['part_name'] + str(n)

        query = (f"SELECT {cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} "
                 f"WHERE round({part_sum},3) <> 100")
        search_err = self.select_errors(query)
        self.add_to_protocol(cros_table, f"{cros_table_scheme['part_n']['name']} ... {part_sum}self.max_n", search_err,
                             8)

    def check_part_n(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        for ind in range(2, self.max_n + 1):
            query = (f"SELECT {cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} "
                     f"WHERE not {cros_table_scheme['part_n']['part_name']}{ind} between 0 and 99.9999 "
                     f"      or {cros_table_scheme['part_n']['part_name']}{ind} is Null")
            search_err = self.select_errors(query)
            self.add_to_protocol(CtrStructure.crs_table, 'Part_%d' % ind, search_err, 7)

            query = (f"SELECT {cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} "
                     f"WHERE {cros_table_scheme['part_n']['part_name']}{ind} is Null")
            search_err = self.select_errors(query)
            self.add_to_protocol(cros_table, 'Part_%d' % ind, search_err, 3)

    def check_f22_n(self):
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)
        for ind in range(2, self.max_n + 1):
            field_name = cros_table_scheme['f22']['part_name'] + str(ind)
            self.check_field_choices(
                table=cros_table,
                field=field_name,
                choices=self.f22_string,
                sprav_table_name=SpravStructure.f22,
                id_field=cros_table_scheme['id']['name'],
                is_null_allowed=True,
            )

    def get_n_max(self):
        def part_fields(n):
            return [
                CtrStructure.get_table_scheme(CtrStructure.crs_table)['part_n']['part_name'] + n,
                CtrStructure.get_table_scheme(CtrStructure.crs_table)['user_n']['part_name'] + n,
                CtrStructure.get_table_scheme(CtrStructure.crs_table)['f22']['part_name'] + n
            ]

        def raise_err(msg):
            raise Exception('Проверьте наличие полей %s' % str(msg))

        max_n = 1
        crtab_fields = list(self.get_crostab_fields())
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

    def check_user_n(self):
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)
        users_table = CtrStructure.users_table
        users_table_scheme = CtrStructure.get_table_scheme(users_table)

        for n in range(2, self.max_n + 1):
            query = (f"SELECT c.{cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} c "
                     f"LEFT JOIN {users_table} u "
                     f"         ON c.{cros_table_scheme['user_n']['name']} = u.{users_table_scheme['user_n']['name']} "
                     f"WHERE u.{users_table_scheme['user_n']['name']} Is Null "
                     f"      and c.{cros_table_scheme['user_n']['name']} is not Null "
                     f"      and c.{cros_table_scheme['user_n_sad']['name']} is Null")
            search_err = self.select_errors(query)
            self.add_to_protocol(cros_table, cros_table_scheme['user_n']['name'], search_err, 2, users_table)

    def check_melio_code(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        self.check_field_choices(
            table=cros_table,
            field=cros_table_scheme['mc']['name'],
            choices=self.sprav_holder.melio_codes,
            sprav_table_name=SpravStructure.mc,
            id_field=cros_table_scheme['id']['name'],
            is_null_allowed=False,
        )

    def check_land_code(self) -> None:
        land_codes = []
        sprav_land_codes = self.sprav_holder.land_codes
        for key in sprav_land_codes:
            land_codes.extend(sprav_land_codes[key])
        land_codes = set(land_codes)
        land_codes = ','.join(map(lambda x: str(x), land_codes))

        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)
        self.check_field_choices(
            table=cros_table,
            field=cros_table_scheme['lc']['name'],
            choices=land_codes,
            sprav_table_name=SpravStructure.lc,
            id_field=cros_table_scheme['id']['name'],
            is_null_allowed=False,
        )

    def check_f22_1(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        self.check_field_choices(
            table=cros_table,
            field=cros_table_scheme['f22']['name'],
            choices=self.f22_string,
            sprav_table_name=SpravStructure.f22,
            id_field=cros_table_scheme['id']['name'],
            is_null_allowed=False,
        )

    def check_state(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        self.check_field_choices(
            table=cros_table,
            field=cros_table_scheme['state']['name'],
            choices=self.sprav_holder.state_codes,
            sprav_table_name=SpravStructure.state,
            id_field=cros_table_scheme['id']['name'],
            is_null_allowed=False,
        )

    def check_sl_nad(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        self.check_field_choices(
            table=cros_table,
            field=cros_table_scheme['sl_nad']['name'],
            choices=self.sprav_holder.slnad_codes,
            sprav_table_name=SpravStructure.slnad,
            id_field=cros_table_scheme['id']['name'],
            is_null_allowed=False,
        )

    def check_users(self) -> None:
        users_table = CtrStructure.users_table
        users_table_scheme = CtrStructure.get_table_scheme(users_table)

        self.check_field_choices(
            table=users_table,
            field=users_table_scheme['user_type']['name'],
            choices=self.sprav_holder.user_types,
            sprav_table_name=SpravStructure.ustype,
            id_field=users_table_scheme['id']['name'],
            is_null_allowed=False,
        )
        self.check_is_unique(
            table_name=users_table,
            unique_field=users_table_scheme['user_n']['name'],
            id_field=users_table_scheme['id']['name'],
        )

    def check_is_unique(self, table_name: str, unique_field: str, id_field) -> None:
        unique_rows = self.select_errors(f"SELECT {unique_field} FROM {table_name}")
        duplicate_codes = list(filter(lambda x: unique_rows.count(x) > 1, unique_rows))
        if duplicate_codes:
            query = (f"SELECT {id_field} "
                     f"FROM {table_name} "
                     f"WHERE {unique_field} in {str(tuple(set(duplicate_codes)))}")
            search_err = self.select_errors(query)
            self.add_to_protocol(table_name, unique_field, search_err, 9)

    def check_field_choices(
            self,
            table: str,
            field: str,
            choices: str,
            sprav_table_name: str,
            id_field: str,
            is_null_allowed: bool = False,
    ) -> None:
        query = (f"SELECT {id_field} "
                 f"FROM {table} "
                 f"WHERE {field} not in ({choices}) "
                 f"       and {field} is not Null")
        search_err = self.select_errors(query)
        self.add_to_protocol(table, field, search_err, 1, sprav_table_name)
        if not is_null_allowed:
            query = (f"SELECT {id_field} "
                     f"FROM {table} "
                     f"WHERE {field} is Null")
            search_err = self.select_errors(query)
            self.add_to_protocol(table, field, search_err, 3)

    def check_part_1(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        query = (f"SELECT {cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} "
                 f"WHERE not {cros_table_scheme['part_n']['name']} between 0.0001 and 100")
        search_err = self.select_errors(query)
        self.add_to_protocol(CtrStructure.crs_table, cros_table_scheme['part_n']['name'], search_err, 5)

        query = (f"SELECT {cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} "
                 f"WHERE {cros_table_scheme['part_n']['name']} is Null")
        search_err = self.select_errors(query)
        self.add_to_protocol(CtrStructure.crs_table, 'Part_1', search_err, 3)

    def check_soato_crostab_relation(self):
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)
        soato_table = CtrStructure.soato_table
        soato_table_scheme = CtrStructure.get_table_scheme(soato_table)

        query = (f"SELECT c.{cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} c "
                 f"LEFT JOIN {soato_table} s "
                 f"         ON c.{cros_table_scheme['soato']['name']} = s.{soato_table_scheme['code']['name']} "
                 f"WHERE s.{soato_table_scheme['code']['name']} Is Null")
        search_err = self.select_errors(query)
        self.add_to_protocol(cros_table, cros_table_scheme['soato']['name'], search_err, 2, soato_table)

        query = (f"SELECT {cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} "
                 f"WHERE {cros_table_scheme['soato']['name']} Is Null")
        search_err = self.select_errors(query)
        self.add_to_protocol(cros_table, cros_table_scheme['soato']['name'], search_err, 3)

    def check_user_1(self):
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)
        users_table = CtrStructure.users_table
        users_table_scheme = CtrStructure.get_table_scheme(users_table)

        query = (f"SELECT c.{cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} c "
                 f"LEFT JOIN {users_table} u"
                 f"          ON c.{cros_table_scheme['user_n']['name']} = u.{users_table_scheme['user_n']['name']} "
                 f"WHERE u.{users_table_scheme['user_n']['name']} IS NULL "
                 f"       and c.{cros_table_scheme['user_n_sad']['name']} IS NULL")
        search_err = self.select_errors(query)
        self.add_to_protocol(CtrStructure.crs_table, cros_table_scheme['user_n']['name'], search_err, 2,
                             CtrStructure.users_table)

        query = (f"SELECT {cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} "
                 f"WHERE {cros_table_scheme['user_n']['name']} IS NULL")
        search_err = self.select_errors(query)
        self.add_to_protocol(CtrStructure.crs_table, cros_table_scheme['user_n']['name'], search_err, 3)

    def check_usern__usern_sad_relation(self):
        """НЕЛОГИЧНЫЙ ЗАПРОС"""
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)
        users_table = CtrStructure.users_table
        users_table_scheme = CtrStructure.get_table_scheme(users_table)

        query = (f"SELECT c.{cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} c "
                 f"LEFT JOIN {users_table} u"
                 f"          ON c.{cros_table_scheme['user_n_sad']['name']} = u.{users_table_scheme['user_n']['name']} "
                 f"WHERE u.{users_table_scheme['user_n']['name']} IS NULL "
                 f"       and c.{cros_table_scheme['user_n_sad']['name']} IS NOT NULL")

        search_err = self.select_errors(query)
        self.add_to_protocol(cros_table, cros_table_scheme['user_n_sad']['name'], search_err, 2,
                             CtrStructure.users_table)

    def check_valid_soato_table(self) -> None:
        """
        Проверяем есть ли в таблице SOATO записи с Name == Null or KOD == Null
        """
        table_name = CtrStructure.soato_table
        table_scheme = CtrStructure.get_table_scheme(table_name)

        query = (f"SELECT {table_scheme['id']['name']} "
                 f"FROM {table_name} "
                 f"WHERE {table_scheme['code']['name']} IS NULL "
                 f"       or {table_scheme['name']['name']} Is NULL")
        search_err = self.select_errors(query)
        self.add_to_protocol(table_name, 'KOD, Name', search_err, 3)
        self.check_is_unique(
            table_name,
            table_scheme['code']['name'],
            table_scheme['id']['name'],
        )
