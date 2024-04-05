import shutil
from typing import Dict, List, Type

from core.db.connector import DbConnector
from core.db.structures.abstractions import AbstractDBStructure
from core.errors.dberror import DbError
from core.system_logger import log_error


class DbController:
    def __init__(self, db_path: str, db_schema: Type[AbstractDBStructure], temp_db_path: str = None):
        self.db_path = db_path
        self.db_schema = db_schema
        if temp_db_path:
            try:
                shutil.copyfile(db_path, temp_db_path)
            except shutil.Error:
                raise DbError("shutil_err", db_path)
            self.db_path = temp_db_path
        self.conn = DbConnector(self.db_path)

    def __del__(self) -> None:
        del self.conn

    @property
    def is_connected(self) -> bool:
        return self.conn.has_dbc

    def get_not_found_tables(self) -> List[str]:
        """Возвращает список не найденных таблиц"""
        not_found_tables = []
        tab_names = self.conn.get_all_table_names()
        for tab in self.db_schema.all_tables:
            if tab not in tab_names:
                not_found_tables.append(tab)
        return not_found_tables

    def get_empty_tables(self) -> List:
        """
        Получить список пустых таблиц
        """
        """
        :return: Tables from __need_tabs that has no any data
        """
        empty_tables = []
        for tab in self.db_schema.all_tables:
            if not self.conn.exec_sel_query("select * from %s" % tab):
                empty_tables.append(tab)
        return empty_tables

    def validate_field_types(self) -> Dict:
        """
        Достаем поля и их типы из реальной таблицы и сравниваем с структурой в db.structures.ctr
        возвращаем dict {table_name: [bad_fields], ...]}
        """
        """
        the method compares default db field schema with connected db
        :return: nested dictionary like "tab_name" : "field_name" : [field, (field, type), field, ....]
        """
        fails = {}
        for table in self.db_schema.all_tables:
            try:
                loaded_table_schema = self.conn.read_table_scheme(table)  # получить все поля и их типы
                bad_fields = []
                table_scheme = self.db_schema.get_table_scheme(table)
                for field in table_scheme:
                    field_name = table_scheme[field]["name"]
                    field_types = table_scheme[field]["type"]
                    if field_name not in loaded_table_schema:
                        bad_fields.append(field_name)
                    elif loaded_table_schema[field_name] not in field_types:
                        bad_fields.append((field_name, field_types))
                if bad_fields:
                    fails[table] = tuple(bad_fields)
            except Exception as err:
                log_error(err)
        return fails

    def read_all_tables_scheme(self) -> Dict[str, Dict[str, str]]:
        """
        returns {
            table1: {
                "field_name" : "field_type",
                "field2_name" : "field_type"
            }, ...
        """
        all_fields = {}
        for table in self.db_schema.all_tables:
            all_fields[table] = self.conn.read_table_scheme(table)
        return all_fields
