import os.path
import shutil
from typing import Any, Dict, List, Optional

import pyodbc
from pyodbc import Cursor

from core.db.decorators import catch_db_exception, try_make_conn
from core.errors.dberror import DbError
from core.system_logger import log_error


class DbConnector:
    def __init__(self, db_path: str, do_conn: bool = True):
        self.db_f_path = db_path
        self.db_access = "DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;" % db_path
        # "DRIVER={Microsoft Access Driver (*.mdb)};DBQ=%s;" % db_path
        self.__conn = None
        self.__dbc: Optional[Cursor] = None
        self.reconnect = False
        self.conn_attempt_available = False
        if do_conn:
            self.make_connection()

    @property
    def get_dbc(self) -> Optional[Cursor]:
        return self.__dbc

    @property
    def has_dbc(self) -> bool:
        return True if self.__dbc else False

    def make_connection(self) -> None:
        if not self.__dbc:
            try:
                self.__conn = pyodbc.connect(self.db_access, autocommit=True, unicode_results=True)
                self.__dbc = self.__conn.cursor()
            except pyodbc.Error:
                self.__dbc = None

    def close_conn(self) -> None:
        try:
            self.__dbc.close()
            self.__conn.close()
        except Exception as err:
            log_error(err, 'Failed to close database: ')

    def run_db(self) -> None:
        os.system("start %s" % self.db_f_path)

    @try_make_conn
    def get_all_table_names(self) -> List[str]:
        return [row[2] for row in self.__dbc.tables(tableType="TABLE")]

    @try_make_conn
    def __get_columns(self, table_name: str) -> Cursor:
        return self.__dbc.columns(table=table_name)

    def read_table_scheme(self, table_name: str) -> Dict[str, str]:
        fields_name_type = {}
        try:
            for field_info in list(self.__get_columns(table_name)):
                fields_name_type[field_info[3]] = field_info[5]
            return fields_name_type
        except TypeError:
            err = Exception("Ошибка соединения с базой данных")
            log_error(err)
            raise err

    def get_common_selection(self, table_name, fields: List[str], where_case: str = ""):
        query = "select "
        query += ", ".join(fields)
        query += " from %s %s" % (table_name, where_case)
        rc_rows = self.exec_sel_query(query)
        result = []
        for row in rc_rows:
            row_dict = {}
            for ind in range(len(fields)):
                row_dict[fields[ind]] = row[ind]
            result.append(row_dict)
        return result

    @try_make_conn
    @catch_db_exception
    def exec_sel_query(self, query: str) -> List:
        results = self.__dbc.execute(query).fetchall()
        return [row for row in results]

    @try_make_conn
    @catch_db_exception
    def select_single_f(self, query: str):
        return [row[0] for row in self.__dbc.execute(query).fetchall()]

    @try_make_conn
    @catch_db_exception
    def exec_covered_query(self, query: str, covered_args):
        return self.__dbc.execute(query, covered_args)

    @try_make_conn
    @catch_db_exception
    def exec_query(self, query: str):
        return self.__dbc.execute(query)

    def get_tab_dict(self, query) -> Dict[Any, List]:
        """Вернет словарь на основе данных полученных в результате выполнения запроса.
            :key - первый параметр запроса
            :value - список оставшихся параметров"""
        rc_dict = {}
        rc_rows = self.exec_sel_query(query)
        if isinstance(rc_rows, list):
            for row in rc_rows:
                rc_dict[row[0]] = list(row[1:])
            return rc_dict
        else:
            return {}

    def get_tab_list(self, query) -> List:
        result = self.exec_sel_query(query)
        if isinstance(result, list):
            return result
        else:
            return []

    def guarantee_dbf_exists(self, template_path):
        if not os.path.isfile(self.db_f_path):
            # templ = os.path.join(templ_path, "template.mdb")
            if os.path.isfile(template_path):
                try:
                    shutil.copyfile(src=template_path, dst=self.db_f_path)
                except Exception:
                    raise DbError("err_create_file", self.db_f_path)
            else:
                raise DbError("tmpl_empty", template_path)

    def __del__(self):
        self.close_conn()
