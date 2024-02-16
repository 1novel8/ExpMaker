from constants import coreFiles
from core.db import DbConnector


class DbExporter(DbConnector):
    def __init__(self, dbf_path, template_path=coreFiles.templ_db_path):
        self.db_f_path = dbf_path
        self.guarantee_dbf_exists(template_path)
        super(DbExporter, self).__init__(dbf_path)
        self.created_tables = {}

    def create_table(self, tab_name, field_str, f_order=None):
        create_query = 'create table %s( ID Autoincrement' % tab_name
        if not f_order:
            f_order = field_str.keys()
        for f in f_order:
            create_query += ', %s %s' % (f, field_str[f])
        create_query += ', PRIMARY KEY(ID));'
        self.exec_query(create_query)
        self.created_tables[tab_name] = field_str

    def run_export(self, tab_name, export_rows, field_order):
        if tab_name in self.created_tables:
            flds = self.created_tables[tab_name].keys()
            flds.extend(field_order)
            if len(set(flds)) == len(self.created_tables[tab_name]):
                for row in export_rows:
                    self.insert_row(tab_name, field_order, row)
                self.close_conn()
            else:
                raise Exception('Field structure can\'t be egnored!')
        else:
            raise Exception(u"Table not exists!")

    def insert_row(self, t_name, fields, vals):
        fields = ','.join(fields)
        vals = map(lambda x: "'%s'" % x if isinstance(x, str) else str(x), vals)
        vals = ','.join(vals)
        ins_query = 'INSERT into %s(%s) values (%s)' % (t_name, fields, vals)
        self.exec_query(ins_query)
