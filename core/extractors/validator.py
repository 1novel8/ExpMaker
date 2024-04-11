from typing import List

from core.db.structures.ctr import CtrStructure
from core.db.structures.sprav import SpravStructure
from core.extractors.initializer import CtrController
from core.settingsHolders.spravHolder import SpravHolder


class CtrDBValidator:
    """Отвечает за контроль входной базы данных"""
    def __init__(self, sprav_holder: SpravHolder, db_path: str, temp_db_path: str):
        self.sprav_holder = sprav_holder
        self.db_manager = CtrController(db_path=db_path, tmp_db_path=temp_db_path)

        self.f22_choices: str = self.get_f22_choices(sprav_holder=sprav_holder)
        self.f22_count: int = self.get_f22_count()
        sprav_holder.max_n = self.f22_count

        self.__update_empty_string_to_null()
        self.__delete_empty_pref_rows()

        self.errors = ErrorContainer()

    def validate(self) -> List:
        self.errors = ErrorContainer()
        self.validate_soato_table()
        self.validate_cros_table()
        self.validate_users_table()
        return self.errors

    def validate_cros_table(self) -> None:
        self.validate_cros_table__user_n_sad__in_users()
        self.validate_cros_table__user_n_sad_with_slnad_2_only()
        self.validate_cros_table__user_1__in_users()
        self.validate_cros_table__user_1__is_not_null()
        self.validate_cros_table__soato__in_soato_table()
        self.validate_cros_table__soato__is_not_null()
        self.validate_cros_table__part_1__more_00001_less_100()
        self.validate_cros_table__part_1__is_not_null()
        self.validate_cros_table__sl_nad__is_sprav()
        self.validate_cros_table__state__is_sprav()
        self.validate_cros_table__forma22_1__in_sprav()
        self.validate_cros_table__land_code__in_sprav()
        self.validate_cros_table__melio_code__in_sprav()
        self.validate_cros_table__user_n()
        self.validate_cros_table__forma22_n__in_sprav()
        self.validate_cros_table__part_n__is_not_null_and_between_0_100()
        self.validate_cros_table__part_n__sum_should_be_100()
        self.validate_cros_table__user_n_f22_part_n__if_one_exist_other_not_null()

    def validate_soato_table(self) -> None:
        self.validate_soato__name_code__is_not_null()
        self.validate_soato__code__is_unique()

    def validate_users_table(self) -> None:
        self.validate_users__user_type__in_sprav()
        self.validate_users__user_n__is_unique()

    def __delete_empty_pref_rows(self) -> None:
        soato_table = CtrStructure.soato_table
        soato_table_scheme = CtrStructure.get_table_scheme(soato_table)

        query = (f"DELETE FROM {soato_table} "
                 f"WHERE {soato_table_scheme['pref']['name']} is Null")
        self.db_manager.conn.exec_query(query=query)

    def __update_empty_string_to_null(self) -> None:
        for table in CtrStructure.all_tables:
            for field in CtrStructure.get_table_scheme(table).values():
                if isinstance(field['type'], list) and 'VARCHAR' in field['type']:
                    query = (f"UPDATE {table} "
                             f"SET {field['name']} = NULL "
                             f"WHERE {field['name']} = ''")
                    self.db_manager.conn.exec_query(query)

    @staticmethod
    def get_f22_choices(sprav_holder: SpravHolder) -> str:
        f22_str = []
        for key in sprav_holder.f22_notes:
            f22_str.append('\'%s\'' % key)
        f22_str = ','.join(f22_str)
        return f22_str

    def get_f22_count(self) -> int:
        def part_fields(n) -> List[str]:
            cros_table = CtrStructure.crs_table
            cros_table_scheme = CtrStructure.get_table_scheme(table_name=cros_table)
            return [
                cros_table_scheme['part_n']['part_name'] + n,
                cros_table_scheme['user_n']['part_name'] + n,
                cros_table_scheme['f22']['part_name'] + n
            ]

        count = 1
        cros_table_fields = list(self.get_crostab_fields())
        fields_count = len(cros_table_fields)
        while True:
            fields_set = set(cros_table_fields + part_fields(str(count)))
            if fields_count == len(fields_set):
                count += 1
            elif count == 1:
                raise Exception(f"Проверьте наличие полей {part_fields(1)}")
            elif len(fields_set) - fields_count == 3:
                break
            else:
                raise Exception(f"Проверьте наличие полей {', '.join(part_fields(count))}")
        return count - 1

    def validate_cros_table__user_n_sad_with_slnad_2_only(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        sl_nad = cros_table_scheme['sl_nad']['name']
        user_n_sad = cros_table_scheme['user_n_sad']['name']

        query = (f"SELECT {cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} "
                 f"WHERE ({sl_nad} = 2 and {user_n_sad} IS NULL) "
                 f"     or ({sl_nad} <> 2 and {user_n_sad} IS NOT NULL)")
        print(1)
        search_err = self.select__first_field_only(query)
        print(search_err)
        self.errors.add(cros_table, 'UserN_Sad or SLNAD', search_err, 10)
        print(2)

    def validate_cros_table__user_n_f22_part_n__if_one_exist_other_not_null(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        f22_part = cros_table_scheme['f22']['part_name']
        user_n_part = cros_table_scheme['user_n']['part_name']
        part_n_part = cros_table_scheme['part_n']['part_name']
        for ind in range(2, self.f22_count + 1):
            protocol_tip = (f"{f22_part}{ind}, "
                            f"{user_n_part}{ind}, "
                            f"{part_n_part}{ind}")
            query = (f"SELECT {cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} "
                     f"WHERE {user_n_part}{ind} is NOT Null "
                     f"     and ({f22_part}{ind} is Null or {part_n_part}{ind} = 0)")
            search_err = self.select__first_field_only(query)
            self.errors.add(cros_table, protocol_tip, search_err, 6, ind)

            query = (f"SELECT {cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} "
                     f"WHERE {f22_part}{ind} is not Null "
                     f"     and ({user_n_part}{ind} is Null or {part_n_part}{ind} = 0)")
            search_err = self.select__first_field_only(query)
            self.errors.add(cros_table, protocol_tip, search_err, 6, ind)

            query = (f"SELECT {cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} "
                     f"WHERE {part_n_part}{ind} <> 0 "
                     f"     and ({user_n_part}{ind} is Null or {f22_part}{ind} is Null)")
            search_err = self.select__first_field_only(query)
            self.errors.add(cros_table, protocol_tip, search_err, 6, ind)

    def validate_cros_table__part_n__is_not_null_and_between_0_100(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        for ind in range(2, self.f22_count + 1):
            query = (f"SELECT {cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} "
                     f"WHERE not {cros_table_scheme['part_n']['part_name']}{ind} between 0 and 99.9999 "
                     f"      or {cros_table_scheme['part_n']['part_name']}{ind} is Null")
            search_err = self.select__first_field_only(query)
            self.errors.add(CtrStructure.crs_table, 'Part_%d' % ind, search_err, 7)

            query = (f"SELECT {cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} "
                     f"WHERE {cros_table_scheme['part_n']['part_name']}{ind} is Null")
            search_err = self.select__first_field_only(query)
            self.errors.add(cros_table, 'Part_%d' % ind, search_err, 3)

    def validate_cros_table__part_n__sum_should_be_100(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        part_sum = cros_table_scheme['part_n']['name']
        for n in range(2, self.f22_count + 1):
            part_sum += '+' + cros_table_scheme['part_n']['part_name'] + str(n)

        query = (f"SELECT {cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} "
                 f"WHERE round({part_sum},3) <> 100")
        search_err = self.select__first_field_only(query)
        self.errors.add(
            cros_table, f"{cros_table_scheme['part_n']['name']} ... {part_sum}self.max_n", search_err, 8
        )

    def validate_cros_table__forma22_1__in_sprav(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        self._is_field_values_in_choices(
            table=cros_table,
            field=cros_table_scheme['f22']['name'],
            choices=self.f22_choices,
            sprav_table_name=SpravStructure.f22,
            id_field=cros_table_scheme['id']['name'],
            is_null_allowed=False,
        )

    def validate_cros_table__forma22_n__in_sprav(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)
        for ind in range(2, self.f22_count + 1):
            field_name = cros_table_scheme['f22']['part_name'] + str(ind)
            self._is_field_values_in_choices(
                table=cros_table,
                field=field_name,
                choices=self.f22_choices,
                sprav_table_name=SpravStructure.f22,
                id_field=cros_table_scheme['id']['name'],
                is_null_allowed=True,
            )

    def validate_cros_table__land_code__in_sprav(self) -> None:
        land_codes = []
        sprav_land_codes = self.sprav_holder.land_codes
        for key in sprav_land_codes:
            land_codes.extend(sprav_land_codes[key])
        land_codes = set(land_codes)
        land_codes = ','.join(map(lambda x: str(x), land_codes))

        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)
        self._is_field_values_in_choices(
            table=cros_table,
            field=cros_table_scheme['lc']['name'],
            choices=land_codes,
            sprav_table_name=SpravStructure.lc,
            id_field=cros_table_scheme['id']['name'],
            is_null_allowed=False,
        )

    def validate_cros_table__user_n(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)
        users_table = CtrStructure.users_table
        users_table_scheme = CtrStructure.get_table_scheme(users_table)

        for n in range(2, self.f22_count + 1):
            query = (f"SELECT c.{cros_table_scheme['id']['name']} "
                     f"FROM {cros_table} c "
                     f"LEFT JOIN {users_table} u "
                     f"         ON c.{cros_table_scheme['user_n']['part_name']}{n} = u.{users_table_scheme['user_n']['name']} "
                     f"WHERE u.{users_table_scheme['user_n']['name']} Is Null "
                     f"      and c.{cros_table_scheme['user_n']['part_name']}{n} is not Null "
                     f"      and c.{cros_table_scheme['user_n_sad']['name']} is Null")
            search_err = self.select__first_field_only(query)
            self.errors.add(cros_table, cros_table_scheme['user_n']['name'], search_err, 2, users_table)

    def validate_cros_table__sl_nad__is_sprav(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        self._is_field_values_in_choices(
            table=cros_table,
            field=cros_table_scheme['sl_nad']['name'],
            choices=self.sprav_holder.slnad_codes,
            sprav_table_name=SpravStructure.slnad,
            id_field=cros_table_scheme['id']['name'],
            is_null_allowed=False,
        )

    def validate_cros_table__state__is_sprav(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        self._is_field_values_in_choices(
            table=cros_table,
            field=cros_table_scheme['state']['name'],
            choices=self.sprav_holder.state_codes,
            sprav_table_name=SpravStructure.state,
            id_field=cros_table_scheme['id']['name'],
            is_null_allowed=False,
        )

    def validate_cros_table__melio_code__in_sprav(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        self._is_field_values_in_choices(
            table=cros_table,
            field=cros_table_scheme['mc']['name'],
            choices=self.sprav_holder.melio_codes,
            sprav_table_name=SpravStructure.mc,
            id_field=cros_table_scheme['id']['name'],
            is_null_allowed=False,
        )

    def validate_users__user_type__in_sprav(self) -> None:
        users_table = CtrStructure.users_table
        users_table_scheme = CtrStructure.get_table_scheme(users_table)

        self._is_field_values_in_choices(
            table=users_table,
            field=users_table_scheme['user_type']['name'],
            choices=self.sprav_holder.user_types,
            sprav_table_name=SpravStructure.ustype,
            id_field=users_table_scheme['id']['name'],
            is_null_allowed=False,
        )

    def validate_users__user_n__is_unique(self) -> None:
        users_table = CtrStructure.users_table
        users_table_scheme = CtrStructure.get_table_scheme(users_table)

        self._is_unique_field_values(
            table=users_table,
            unique_field=users_table_scheme['user_n']['name'],
            id_field=users_table_scheme['id']['name'],
        )

    def validate_soato__name_code__is_not_null(self) -> None:
        soato_table = CtrStructure.soato_table
        soato_scheme = CtrStructure.get_table_scheme(soato_table)
        code_field = soato_scheme['code']['name']
        name_field = soato_scheme['name']['name']
        id_field = soato_scheme['id']['name']

        query = (f"SELECT {id_field} "
                 f"FROM {soato_table} "
                 f"WHERE {code_field} IS NULL "
                 f"       or {name_field} Is NULL")
        search_err = self.select__first_field_only(query)
        self.errors.add(soato_table, 'KOD, Name', search_err, 3)
        self._is_unique_field_values(soato_table, code_field, id_field)

    def validate_soato__code__is_unique(self) -> None:
        soato_table = CtrStructure.soato_table
        soato_scheme = CtrStructure.get_table_scheme(soato_table)
        code_field = soato_scheme['code']['name']
        id_field = soato_scheme['id']['name']

        self._is_unique_field_values(soato_table, code_field, id_field)

    def validate_cros_table__user_n_sad__in_users(self) -> None:
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

        search_err = self.select__first_field_only(query)
        self.errors.add(cros_table, cros_table_scheme['user_n_sad']['name'], search_err, 2, users_table)

    def validate_cros_table__user_1__in_users(self) -> None:
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
        search_err = self.select__first_field_only(query)
        self.errors.add(cros_table, cros_table_scheme['user_n']['name'], search_err, 2, users_table)

    def validate_cros_table__user_1__is_not_null(self):
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        query = (f"SELECT {cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} "
                 f"WHERE {cros_table_scheme['user_n']['name']} IS NULL")
        search_err = self.select__first_field_only(query)
        self.errors.add(cros_table, cros_table_scheme['user_n']['name'], search_err, 3)

    def validate_cros_table__soato__in_soato_table(self):
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)
        soato_table = CtrStructure.soato_table
        soato_table_scheme = CtrStructure.get_table_scheme(soato_table)

        query = (f"SELECT c.{cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} c "
                 f"LEFT JOIN {soato_table} s "
                 f"         ON c.{cros_table_scheme['soato']['name']} = s.{soato_table_scheme['code']['name']} "
                 f"WHERE s.{soato_table_scheme['code']['name']} Is Null")
        search_err = self.select__first_field_only(query)
        self.errors.add(cros_table, cros_table_scheme['soato']['name'], search_err, 2, soato_table)

    def validate_cros_table__soato__is_not_null(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        query = (f"SELECT {cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} "
                 f"WHERE {cros_table_scheme['soato']['name']} Is Null")
        search_err = self.select__first_field_only(query)
        self.errors.add(cros_table, cros_table_scheme['soato']['name'], search_err, 3)

    def validate_cros_table__part_1__is_not_null(self) -> None:
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        query = (f"SELECT {cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} "
                 f"WHERE {cros_table_scheme['part_n']['name']} is Null")
        search_err = self.select__first_field_only(query)
        self.errors.add(CtrStructure.crs_table, 'Part_1', search_err, 3)

    def validate_cros_table__part_1__more_00001_less_100(self):
        cros_table = CtrStructure.crs_table
        cros_table_scheme = CtrStructure.get_table_scheme(cros_table)

        query = (f"SELECT {cros_table_scheme['id']['name']} "
                 f"FROM {cros_table} "
                 f"WHERE not {cros_table_scheme['part_n']['name']} between 0.0001 and 100")
        search_err = self.select__first_field_only(query)
        self.errors.add(CtrStructure.crs_table, cros_table_scheme['part_n']['name'], search_err, 5)

    def get_crostab_fields(self):
        return self.db_manager.conn.read_table_scheme(CtrStructure.crs_table).keys()

    def _is_field_values_in_choices(
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
        search_err = self.select__first_field_only(query)
        self.errors.add(table, field, search_err, 1, sprav_table_name)

        if not is_null_allowed:
            query = (f"SELECT {id_field} "
                     f"FROM {table} "
                     f"WHERE {field} is Null")
            search_err = self.select__first_field_only(query)
            self.errors.add(table, field, search_err, 3)

    def _is_unique_field_values(
            self,
            table: str,
            unique_field: str,
            id_field: str,
    ) -> None:
        unique_rows = self.select__first_field_only(f"SELECT {unique_field} FROM {table}")
        duplicates = list(filter(lambda x: unique_rows.count(x) > 1, unique_rows))
        if duplicates:
            query = (f"SELECT {id_field} "
                     f"FROM {table} "
                     f"WHERE {unique_field} in {str(tuple(set(duplicates)))}")
            search_err = self.select__first_field_only(query)
            self.errors.add(table, unique_field, search_err, 9)

    def select__first_field_only(self, query: str):
        return self.db_manager.conn.select_single_f(query)


class ErrorContainer(list):
    def __init__(self):
        super().__init__()

    def add(self, table: str, field: str, err_ids: str, err_code: int, dynamic_param=None) -> None:
        if err_ids:
            error_description = {
                'table': table,
                'field': field,
                'err_ids': err_ids,
                'err_msg': err_code,
                'dyn_param': dynamic_param,
            }
            self.append(error_description)
