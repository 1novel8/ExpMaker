
import shutil
from ..errors import DbError
from .connector import DbConnector


class DbControl(object):
    def __init__(self, db_path, db_schema_pattern, temp_db_path=None):
        self.db_path = db_path
        self.db_schema = db_schema_pattern
        if temp_db_path:
            try:
                shutil.copyfile(db_path, temp_db_path)
            except shutil.Error:
                raise DbError("shutil_err", db_path)
            self.db_path = temp_db_path
        self.conn = DbConnector(self.db_path)

    def __del__(self):
        del self.conn

    @property
    def is_connected(self):
        return self.conn.has_dbc

    def contr_tables(self):
        lost_tables = []
        tab_names = self.conn.get_tab_names()
        for tab in self.db_schema.tabs_enum:
            if tab not in tab_names:
                lost_tables.append(tab)
        return lost_tables

    def is_tables_empty(self):
        """
        :return: Tables from __need_tabs that has no any data
        """
        no_data = []
        for tab in self.db_schema.tabs_enum:
            if not self.conn.exec_sel_query("select * from %s" % tab):
                no_data.append(tab)
        if no_data:
            return no_data
        else:
            return False

    def contr_field_types(self):
        """
        the method compares default db field schema with connected db
        :return: nested dictionary like "tab_name" : "field_name" : [field, (field, type), field, ....]
        """
        fails = {}
        for tab in self.db_schema.tabs_enum:
            try:
                loaded_tab_schema = self.conn.get_f_names_types(tab)
                bad_fields = []
                tab_str = self.db_schema.get_tab_str(tab)
                for field in tab_str:
                    f_name = tab_str[field]["name"]
                    f_types = tab_str[field]["type"]
                    if f_name not in loaded_tab_schema:
                        bad_fields.append(f_name)
                    elif loaded_tab_schema[f_name] not in f_types:
                        bad_fields.append((f_name, f_types))
                if bad_fields:
                    fails[tab] = tuple(bad_fields)
            except Exception as err:
                print(err)
        return fails

    def get_all_fields(self):
        all_fields = {}
        for tab in self.db_schema.tabs_enum:
            all_fields[tab] = self.conn.get_f_names_types(tab)
        return all_fields
