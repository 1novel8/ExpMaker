__author__ = 'Aleksei'

from .. import DbTools


class DbExporter(DbTools.DBConn):
    def __init__(self, dbf_path, template_path):
        self.db_f_path = dbf_path
        self.guarantee_dbf_exists(template_path)
        super(DbExporter, self).__init__(dbf_path)
        self.created_tables = {}

    def create_table(self, tab_name, field_str, f_order = None):
        create_query = u'create table %s( ID Autoincrement'% tab_name
        if not f_order:
            f_order = field_str.keys()
        for f  in f_order:
            create_query += ', %s %s' %(f, field_str[f])
        create_query += u', PRIMARY KEY(ID));'
        try:
            self.exec_query(create_query)
        except DbTools.DbError:
            raise DbTools.DbError(u'create_t_fail', )
        else:
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
                raise Exception(u'Field structure can\'t be egnored!')
        else:
            raise Exception(u"Table not exists!")

    def insert_row(self, t_name, fields, vals):
        fields = u','.join(fields)
        vals = map(lambda x: "'%s'" % x if isinstance(x, str) else str(x), vals)
        vals = u','.join(vals)
        ins_query = u'INSERT into %s(%s) values (%s)' % (t_name, fields, vals)
        self.exec_query(ins_query)



    # def create_e_table(self):
    #     """
    #     :return: list of created fields if create table operation finished with success, else returns false
    #     """
    #     create_fb = u'create table %s(ID AUTOINCREMENT, f_F22 text(8) Null, f_description text(150), ' % self.exp_name
    #     created_fields = [u'F22', u'description']
    #     sort_f_d = {}
    #     f_str = self.f_structure
    #     for key in f_str:
    #         sort_key = f_str[key].get(u'f_num')
    #         if sort_key:
    #             sort_f_d[sort_key] = key
    #     for key in sorted(sort_f_d):
    #         create_fb+= u'f_%s DOUBLE NULL, ' % sort_f_d[key]
    #         created_fields.append(sort_f_d[key])
    #     create_fb += u'PRIMARY KEY(ID));'
    #     self.make_connection()
    #     if self.exec_query(create_fb):
    #         self.close_conn()
    #         return created_fields
    #     else: return False
    #
    # def fill_razv_edb(self, matrix):
    #     self.__expname = u'ExpA_%s' % time.strftime(u"%d\%m\%Y_%H:%M")
    #     created_fields = self.create_edb_table(True)
    #     if created_fields:
    #         if len(created_fields) == len(matrix[0]):
    #             self.__exp_conn.make_connection()
    #             joined_f = u','.join(created_fields)
    #             for row in matrix:
    #                 # row = row[1:]
    #                 row = map(lambda x: u"'%s'" % x if isinstance(x, unicode) else x, row)
    #                 row = map(lambda x: (u'Null' if x is None else unicode(x)), row)
    #                 f_values = u','.join(row)
    #                 ins_query = u'insert into %s(%s) values (%s);' % (self.__expname, joined_f, f_values)
    #                 row_insert = self.__exp_conn.exec_query(ins_query)
    #                 if not row_insert: break
    #             self.__exp_conn.close_conn()
    #         self.__exp_conn.run_db()
    #
    # def create_edb_table(self, razv = False):
    #     """
    #     :param razv: Makes tab structure like xls if parameter is true
    #     :return: list of created fields if create table operation finished with success, else returns false
    #     """
    #     create_fa = u'create table %s(ID AUTOINCREMENT, f_F22 text(8) Null, f_UsN text(100), ' % self.__expname
    #     created_fields = [u'ID', u'f_F22', u'f_UsN']
    #     def add_fields(f_dict, f_name_ki):
    #         query_part = u''
    #         for f_k, f_v in sorted(f_dict.items()):
    #             if f_v[f_name_ki]:
    #                 query_part+= u'f_%s DOUBLE NULL, ' % f_v[f_name_ki]
    #                 created_fields.append(u'f_%s' % f_v[f_name_ki])
    #         return query_part
    #     create_fa += add_fields(self.sprav_holder.expa_f_str, u'f_name')
    #     if razv:
    #         create_fa += add_fields(self.sprav_holder.expa_r_str, 0)
    #     create_fa += u'PRIMARY KEY(ID));'
    #     self.__exp_conn.make_connection()
    #     if self.__exp_conn.exec_query(create_fa):
    #         self.__exp_conn.close_conn()
    #         return created_fields
    #     else: return False




