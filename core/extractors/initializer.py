from typing import Union

from core.db.controller import DbController
from core.db.structures.ctr import CtrStructure
from core.db.structures.sprav import SpravStructure


class CtrController(DbController):
    def __init__(self, db_path: str, tmp_db_path: str):
        super().__init__(db_path, CtrStructure, tmp_db_path)

    def is_empty_f_pref(self) -> Union[str, bool]:
        """
        Поле Pref (д., р-н. и тд)
        проверяет если есть незаполненные поля (None)
        """
        soato_table_scheme = CtrStructure.get_table_scheme(self.db_schema.soato_table)
        all_soato = self.conn.select_single_f(
            'select %s from %s where %s is Null' % (
                soato_table_scheme['code']['name'],
                self.db_schema.soato_table,
                soato_table_scheme['pref']['name'],
            )
        )

        failed_obj = []
        for i in all_soato:
            if i[4] != "9":  # если не СЭЗ
                failed_obj.append(i)

        if failed_obj:
            failed_obj = str(tuple(failed_obj))
            return failed_obj
        else:
            return False

    def is_wrong_f_pref(self) -> Union[str, bool]:
        """
        проверяем чтобы все значения soato были правильными
        """
        soato_table_scheme = CtrStructure.get_table_scheme(self.db_schema.soato_table)
        all_soato = self.conn.select_single_f(
            'select %s from %s ' % (
                soato_table_scheme['code']['name'],
                self.db_schema.soato_table),
        )
        failed_obj = []
        for i in all_soato:
            if (i[:7] + "000") not in all_soato:
                if i[4] == "8":  # если не СЭЗ
                    failed_obj.append(i)
                if i[4] == "7":
                    failed_obj.append(i)

        if failed_obj:
            failed_obj = str(tuple(failed_obj))
            return failed_obj
        else:
            return False

    def is_wrong_f_pref_sez(self) -> Union[str, bool]:
        """проверяем на правильность SOATO"""
        table_scheme = CtrStructure.get_table_scheme(self.db_schema.soato_table)
        query = (f"SELECT {table_scheme['code']['name']} "
                 f"FROM {CtrStructure.soato_table} "
                 f"WHERE {table_scheme['pref']['name']} is not Null")
        soato_codes = self.conn.select_single_f(query)

        failed_obj = []
        for code in soato_codes:
            if code[4] == "9":  # если СЭЗ
                failed_obj.append(code)

        if failed_obj:
            failed_obj = str(tuple(failed_obj))
            return failed_obj
        else:
            return False


class SpravController(DbController):
    def __init__(self, db_path: str):
        super().__init__(db_path, SpravStructure)
