from typing import List

from core.db.structures.ctr import CtrStructure
from core.db.structures.sprav import SpravStructure
from core.extractors.initializer import CtrController
from core.settingsHolders.spravHolder import SpravHolder


class DataControl(CtrController):
    """ Отвечает за контроль входной базы данных """

    def __init__(self, sprav_holder: SpravHolder, db_path: str, temp_db_path: str) -> None:
        self.errors_protocol = []
        self.sprav_holder = sprav_holder
        super().__init__(db_path, temp_db_path)
        # self.all_tabs_columns: Dict[str, Dict[str, str]] = self.read_all_tables_scheme()
        self.f22_choices: str = self.get_f22_string()
        self.max_n: int = self.get_n_max()
        sprav_holder.max_n = self.max_n

        self._update_empty_string_to_null()
        self._delete_empty_pref_rows()

    def run_control(self) -> List:
        """
        Весь контроль входной базы данных
        """
        self.errors_protocol = []

        self.check_group_fields()  # ничего не делает
        self.check_valid_soato_table()  # SOATO table not null and unique check
        self.check_usern__usern_sad_relation()  # проверка users + crostab по userN_Sad
        self.check_user_1()  # crostab_razv.UserN_1 not NULL Users.UserN not NULL
        self.check_soato_crostab_relation()  # SOATO.code != None & crostab_razv.soato != None
        self.check_part_1()  # crostab_razv.Part_1 ≠ Null 0.0001≤ crostab_razv.Part_1 ≤ 10
        self.check_users()  # users.userN - unique users.UserType in spav choices
        self.check_sl_nad()  # crostab_razv.SLNAD - должен находиться в списке возможных в справочнике
        self.check_state()  # crostab_razv.STATE - должен находиться в списке возможных в справочнике
        self.check_f22_1()  # crostab_razv.Forma22_1 - должен находиться в списке возможных в справочнике
        self.check_land_code()  # crostab_razv.LANDCODE -  должен находиться в списке возможных в справочнике
        self.check_melio_code()  # crostab_razv.MELIOCODE -  должен находиться в списке возможных в справочнике
        self.check_user_n()  # crostab_razv.UserN_<N> not NULL or Users.UserN_Sad not NULL
        self.check_f22_n()  # crostab_razv.Forma22_<N> - должен находиться в списке возможных в справочнике
        self.check_part_n()  # crostab_razv.Part_<N> ≠ Null; 0 ≤ crostab_razv.Part_<N> ≤ 100
        self.check_part_sum()  # crostab_razv.Part_<N> сумма должна быть 100
        self.check_us_f22_part()  # crostab_razv.Forma22_<N> crostab_razv.Part_<N> crostab_razv.UserN_<N> если одно
        # из этих значений присутствует, то остальные должны быть правильными
        return self.errors_protocol

    def _delete_empty_pref_rows(self) -> None:
        soato_table = CtrStructure.soato_table
        soato_table_scheme = CtrStructure.get_table_scheme(soato_table)
        query = (f"DELETE FROM {soato_table} "
                 f"WHERE {soato_table_scheme['pref']['name']} is Null")
        self.conn.exec_query(query)

    def _update_empty_string_to_null(self) -> None:
        for table in self.db_schema.all_tables:
            for field in self.db_schema.get_table_scheme(table).values():
                if isinstance(field['type'], list) and 'VARCHAR' in field['type']:
                    query = (f"UPDATE {table} "
                             f"SET {field['name']} = NULL "
                             f"WHERE {field['name']} = ''")
                    self.conn.exec_query(query)

    def get_crostab_fields(self):
        return self.conn.read_table_scheme(CtrStructure.crs_table).keys()

    def select_errors(self, query: str):
        return self.conn.select_single_f(query)

    def get_f22_string(self) -> str:
        f22_str = []
        for key in self.sprav_holder.f22_notes:
            f22_str.append('\'%s\'' % key)
        f22_str = ','.join(f22_str)
        return f22_str

    def add_error_to_protocol(
            self,
            table: str,
            field: str,
            err_ids: str,
            err_code: int,
            dynamic_param=None,
    ) -> None:
        if err_ids:
            err_doc = {
                'table': table,
                'field': field,
                'err_ids': err_ids,
                'err_msg': err_code,
                'dyn_param': dynamic_param,
            }
            self.errors_protocol.append(err_doc)

    def check_group_fields(self) -> List:
        """ DO NOTHING """
        crostab_fields = self.get_crostab_fields()
        check_fields = []
        for field in self.sprav_holder.attr_config['ctr_structure']:
            if '*' in field:
                multi_fields = map(lambda x: field.replace('*', str(x)), range(1, self.max_n + 1))
                check_fields.extend(multi_fields)
            else:
                check_fields.append(field)
        return list(filter(lambda x: x in crostab_fields, check_fields))

    def check_us_f22_part(self) -> None:
        """
        crostab_razv.Forma22_<N>
        crostab_razv.Part_<N>
        crostab_razv.UserN_<N>
        если одно из этих значений присутствует, то остальные должны быть правильными
        """
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
            self.add_error_to_protocol(cros_table, protocol_tip, search_err, 6, ind)

            query = (f"SELECT {cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} "
                     f"WHERE {f22_part}{ind} is not Null "
                     f"     and ({user_n_part}{ind} is Null or {part_n_part}{ind} = 0)")
            search_err = self.select_errors(query)
            self.add_error_to_protocol(cros_table, protocol_tip, search_err, 6, ind)

            query = (f"SELECT {cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} "
                     f"WHERE {part_n_part}{ind} <> 0 "
                     f"     and ({user_n_part}{ind} is Null or {f22_part}{ind} is Null)")
            search_err = self.select_errors(query)
            self.add_error_to_protocol(cros_table, protocol_tip, search_err, 6, ind)

    def check_part_sum(self) -> None:
        """
        crostab_razv.Part_<N> сумма должна быть 100
        """

        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        part_sum = cros_table_scheme['part_n']['name']
        for n in range(2, self.max_n + 1):
            part_sum += '+' + cros_table_scheme['part_n']['part_name'] + str(n)

        query = (f"SELECT {cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} "
                 f"WHERE round({part_sum},3) <> 100")
        search_err = self.select_errors(query)
        self.add_error_to_protocol(cros_table, f"{cros_table_scheme['part_n']['name']} ... {part_sum}self.max_n",
                                   search_err,
                                   8)

    def check_part_n(self) -> None:
        """
        crostab_razv.Part_1 ≠ Null
        0≤ crostab_razv.Part_1 ≤ 10
        """

        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        for ind in range(2, self.max_n + 1):
            query = (f"SELECT {cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} "
                     f"WHERE not {cros_table_scheme['part_n']['part_name']}{ind} between 0 and 99.9999 "
                     f"      or {cros_table_scheme['part_n']['part_name']}{ind} is Null")
            search_err = self.select_errors(query)
            self.add_error_to_protocol(CtrStructure.crs_table, 'Part_%d' % ind, search_err, 7)

            query = (f"SELECT {cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} "
                     f"WHERE {cros_table_scheme['part_n']['part_name']}{ind} is Null")
            search_err = self.select_errors(query)
            self.add_error_to_protocol(cros_table, 'Part_%d' % ind, search_err, 3)

    def check_f22_n(self) -> None:
        """
        crostab_razv.Forma22_<N> - должен находиться в списке возможных в справочнике
        """

        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)
        for ind in range(2, self.max_n + 1):
            field_name = cros_table_scheme['f22']['part_name'] + str(ind)
            self.check_field_choices(
                table=cros_table,
                field=field_name,
                choices=self.f22_choices,
                sprav_table_name=SpravStructure.f22,
                id_field=cros_table_scheme['id']['name'],
                is_null_allowed=True,
            )

    def get_n_max(self) -> int:
        def part_fields(n) -> List[str]:
            cros_table = CtrStructure.crs_table
            cros_table_scheme = CtrStructure.get_table_scheme(table_name=cros_table)
            return [
                cros_table_scheme['part_n']['part_name'] + n,
                cros_table_scheme['user_n']['part_name'] + n,
                cros_table_scheme['f22']['part_name'] + n
            ]

        max_n = 1
        crtab_fields = list(self.get_crostab_fields())
        col_fields = len(crtab_fields)
        while True:
            f_set = set(crtab_fields + part_fields(str(max_n)))
            if col_fields == len(f_set):
                max_n += 1
            elif max_n == 1:
                raise Exception(f"Проверьте наличие полей {part_fields(1)}")
            elif len(f_set) - col_fields == 3:
                break
            else:
                raise Exception(f"Проверьте наличие полей {', '.join(part_fields(max_n))}")
        return max_n - 1

    def check_user_n(self) -> None:
        """
        crostab_razv.UserN_<N> not NULL or Users.UserN_Sad not NULL
        """
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)
        users_table = CtrStructure.users_table
        users_table_scheme = CtrStructure.get_table_scheme(users_table)

        for n in range(2, self.max_n + 1):
            query = (f"SELECT c.{cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} c "
                     f"LEFT JOIN {users_table} u "
                     f"         ON c.{cros_table_scheme['user_n']['part_name']}{n} = u.{users_table_scheme['user_n']['name']} "
                     f"WHERE u.{users_table_scheme['user_n']['name']} Is Null "
                     f"      and c.{cros_table_scheme['user_n']['part_name']}{n} is not Null "
                     f"      and c.{cros_table_scheme['user_n_sad']['name']} is Null")
            search_err = self.select_errors(query)
            self.add_error_to_protocol(cros_table, cros_table_scheme['user_n']['name'], search_err, 2, users_table)

    def check_melio_code(self) -> None:
        """
        crostab_razv.MELIOCODE -  должен находиться в списке возможных в справочнике
        """
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
        """
        crostab_razv.LANDCODE -  должен находиться в списке возможных в справочнике
        """

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
        """
        crostab_razv.Forma22_1 - должен находиться в списке возможных в справочнике
        """

        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        self.check_field_choices(
            table=cros_table,
            field=cros_table_scheme['f22']['name'],
            choices=self.f22_choices,
            sprav_table_name=SpravStructure.f22,
            id_field=cros_table_scheme['id']['name'],
            is_null_allowed=False,
        )

    def check_state(self) -> None:
        """
        STATE - должен находиться в списке возможных в справочнике
        """
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
        """
        crostab_razv.SLNAD - должен находиться в списке возможных в справочнике
        """
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
        """
        UserN - уникальное
        UserType -  должен находиться в списке возможных в справочнике
        """
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

    def check_is_unique(
            self,
            table_name: str,
            unique_field: str,
            id_field: str,
    ) -> None:
        unique_rows = self.select_errors(f"SELECT {unique_field} FROM {table_name}")
        duplicate_codes = list(filter(lambda x: unique_rows.count(x) > 1, unique_rows))
        if duplicate_codes:
            query = (f"SELECT {id_field} "
                     f"FROM {table_name} "
                     f"WHERE {unique_field} in {str(tuple(set(duplicate_codes)))}")
            search_err = self.select_errors(query)
            self.add_error_to_protocol(table_name, unique_field, search_err, 9)

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
        self.add_error_to_protocol(table, field, search_err, 1, sprav_table_name)
        if not is_null_allowed:
            query = (f"SELECT {id_field} "
                     f"FROM {table} "
                     f"WHERE {field} is Null")
            search_err = self.select_errors(query)
            self.add_error_to_protocol(table, field, search_err, 3)

    def check_part_1(self) -> None:
        """
        crostab_razv.Part_1 ≠ Null
        0.0001≤ crostab_razv.Part_1 ≤ 100
        """

        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        query = (f"SELECT {cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} "
                 f"WHERE not {cros_table_scheme['part_n']['name']} between 0.0001 and 100")
        search_err = self.select_errors(query)
        self.add_error_to_protocol(CtrStructure.crs_table, cros_table_scheme['part_n']['name'], search_err, 5)

        query = (f"SELECT {cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} "
                 f"WHERE {cros_table_scheme['part_n']['name']} is Null")
        search_err = self.select_errors(query)
        self.add_error_to_protocol(CtrStructure.crs_table, 'Part_1', search_err, 3)

    def check_soato_crostab_relation(self) -> None:
        """
        SOATO.KOD ≠ Null
        crostab_razv.soato ≠ Null
        """

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
        self.add_error_to_protocol(cros_table, cros_table_scheme['soato']['name'], search_err, 2, soato_table)

        query = (f"SELECT {cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} "
                 f"WHERE {cros_table_scheme['soato']['name']} Is Null")
        search_err = self.select_errors(query)
        self.add_error_to_protocol(cros_table, cros_table_scheme['soato']['name'], search_err, 3)

    def check_user_1(self) -> None:
        """
        UserN_1 not NULL
        UserN not NULL
        """
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
        self.add_error_to_protocol(CtrStructure.crs_table, cros_table_scheme['user_n']['name'], search_err, 2,
                                   CtrStructure.users_table)

        query = (f"SELECT {cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} "
                 f"WHERE {cros_table_scheme['user_n']['name']} IS NULL")
        search_err = self.select_errors(query)
        self.add_error_to_protocol(CtrStructure.crs_table, cros_table_scheme['user_n']['name'], search_err, 3)

    def check_usern__usern_sad_relation(self) -> None:
        """ проверяем что все Users которые есть в UserN_Sad существуют """
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
        self.add_error_to_protocol(cros_table, cros_table_scheme['user_n_sad']['name'], search_err, 2,
                                   users_table)

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
        self.add_error_to_protocol(table_name, 'KOD, Name', search_err, 3)
        self.check_is_unique(
            table_name,
            table_scheme['code']['name'],
            table_scheme['id']['name'],
        )
