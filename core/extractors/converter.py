from pyodbc import Row

from core.db import ctrStructure
from core.db.connector import DbConnector

from .ctrRow import CtrRow


class CtrConverter:
    """ Испольщуется при конвертации """
    @staticmethod
    def convert(sprav_holder, temp_db_path: str, select_condition: dict):
        n_max = sprav_holder.max_n
        ctr_conn = DbConnector(db_path=temp_db_path)

        CtrConverter.add_nasp_name_to_soato(ctr_conn)  # добавляем NameNasp (д. Чучевичи, Брестский р-н) в SOATO
        CtrConverter.add_utype_to_crtab(ctr_conn, n_max)  # добавляем UserType в crosstab_razv
        users_d, soato_d = CtrConverter.data_users_soato(ctr_conn)  # достаем  Users(UserN, UsName) + Soato(Code, NameNasp)
        query_structure: tuple = sprav_holder.attr_config['ctr_structure']  # все атрибуты
        select_ctr_all = CtrConverter._make_crtab_query(fields=query_structure, n_max=n_max, where_case=select_condition['WhereCase'])
        try:
            # Hint: Check Sprav fields when failes here.
            sel_result = ctr_conn.exec_sel_query(select_ctr_all)
        except Exception as err:
            raise Exception('Ошибка при загрузке данных из crostab: %s' % err)
        shape_area_sum = CtrConverter.get_shape_area_sum(ctr_conn)  # Сумма всей прощади

        rows_ok = []
        whats_err = {1: {}, 2: {}, 3: {}, 4: {}}
        got_errors = False
        if not sel_result:
            raise Exception('Данные по установленным параметрам выборки не найдены.')
        for row in sel_result:
            modified_r = CtrConverter.collapse_row(row=row, structure=query_structure, n_max=n_max)  # Удаление пустых значений и None
            new_row = CtrRow(sprav_holder, *modified_r)
            if new_row.has_err:
                err_part = 'Part_%d' % new_row.err_in_part
                try:
                    whats_err[new_row.has_err][err_part].append(new_row.object_id)
                except KeyError:
                    whats_err[new_row.has_err][err_part] = [new_row.object_id, ]
                    got_errors = True
            else:
                rows_ok.append(new_row)
        if got_errors:
            return whats_err
        else:
            additional_params = {
                'shape_sum': shape_area_sum,
                'shape_sum_enabled': True
            }
            save_info = [rows_ok, users_d, soato_d, additional_params]
            return save_info

    @staticmethod
    def add_column(connection: DbConnector, table_name: str, column_name: str, column_type: str = 'int Null'):
        """ Добавляет столбец (удаляет если он уже существует) """
        try:
            connection.exec_query('ALTER TABLE %s DROP "%s";' % (table_name, column_name))
        except:
            pass
        connection.exec_query('ALTER TABLE %s ADD %s %s;' % (table_name, column_name, column_type))

    @staticmethod
    def add_nasp_name_to_soato(connection: DbConnector) -> None:
        """
        Добавляем столбец NameNasp в таблицу SOATO, а в него записываем префикс + название района.
        Пример: д. Чучевичи / Лунинецкий р-н.
        """

        tab_name = ctrStructure.soato_tab
        format_d = {
            'nasp': 'NameNasp',
            'tab': tab_name,
            'pref': ctrStructure.get_tab_str(tab_name)['pref']['name'],
            'name': ctrStructure.get_tab_str(tab_name)['name']['name'],
        }
        CtrConverter.add_column(connection, tab_name, format_d['nasp'], 'varchar(80) NULL')
        updnamenasp1 = u"update %(tab)s set %(nasp)s = %(name)s +' '+%(pref)s where %(pref)s in ('р-н','с/с');" % format_d
        updnamenasp2 = u"update %(tab)s set %(nasp)s = %(pref)s +' '+ %(name)s where  %(nasp)s is Null" % format_d
        connection.exec_query(updnamenasp1)
        connection.exec_query(updnamenasp2)

    @staticmethod
    def add_utype_to_crtab(connection: DbConnector, max_n: int = None) -> None:
        """
        Создаем несколько столбцов UserType_{n} n=max_n в тaблицу Users
        """

        us_tab = ctrStructure.users_tab
        cr_tab = ctrStructure.crs_tab
        format_d = {
            'us_t': us_tab,
            'cr_t': cr_tab,
            'u_utype': ctrStructure.get_tab_str(us_tab)['user_type']['name'],  # UserType
            'u_usern': ctrStructure.get_tab_str(us_tab)['user_n']['name']  # UserN
        }
        for n in range(1, max_n + 1):
            # ---------------------------UserType_n----------------------------------------------
            format_d['c_utype'] = 'UserType_' + str(n)  # UserType_{n}
            format_d['c_usern'] = ctrStructure.get_tab_str(cr_tab)['user_n']['part_name'] + str(n)  # UserN_{n}
            CtrConverter.add_column(connection, table_name=cr_tab, column_name=format_d['c_utype'])  # <--- Добавление UserType_{n} = Null в таблицу crostab_razv
            # написано обновить user_table, но обновляется crostab.
            # UserType_{n} в crostab приравнимаем с UserType у Users
            query = 'UPDATE %(us_t)s u INNER JOIN %(cr_t)s c ON u.%(u_usern)s = c.%(c_usern)s SET c.%(c_utype)s = u.%(u_utype)s;' % format_d
            connection.exec_query(query)

    @staticmethod
    def _make_crtab_query(fields: tuple, n_max: int, where_case=None) -> str:
        """ Создание щапросов """

        query = 'SELECT '
        for f in fields:
            if '*' in f:
                for n in range(1, n_max + 1):
                    query += f.replace('*', str(n)) + ', '
            else:
                query += f + ', '
        query = query[:-2] + ' FROM %s' % ctrStructure.crs_tab

        if where_case:
            query += ' WHERE %s;' % str(where_case)
        return query

    @staticmethod
    def collapse_row(row: Row, structure: tuple, n_max: int) -> tuple[list, int]:
        """ Удаление пустых значений и None """
        return_row = []
        row = list(row)
        n_survived = 0
        for f in structure:
            if '*' in f:
                f_elements = row[:n_max]
                row = row[n_max:]
                if not n_survived:
                    for i in f_elements:
                        if i:
                            n_survived += 1
                        else:
                            break
                return_row.append(f_elements[:n_survived])
            else:
                return_row.append(row.pop(0))
        return return_row, n_survived

    @staticmethod
    def get_shape_area_sum(ct_conn: DbConnector) -> float:
        """Сумма всех прощадей"""

        format_d = {
            'cr_tab': ctrStructure.crs_tab,
            'sh_area': ctrStructure.get_tab_str(ctrStructure.crs_tab)['shape_area']['name']
        }
        sel_result = ct_conn.exec_sel_query('select sum(%(sh_area)s) from %(cr_tab)s' % format_d)
        return sel_result[0][0]

    @staticmethod
    def data_users_soato(ct_conn: DbConnector) -> tuple[dict, dict]:
        """
        returns UsersDict and SoatoDict with keys usern and soato
        and values in unicode
        """
        users_tab = ctrStructure.users_tab
        soato_tab = ctrStructure.soato_tab
        format_d = {
            'users': users_tab,
            'soato': soato_tab,
            'user_n': ctrStructure.get_tab_str(users_tab)['user_n']['name'],
            'us_name': ctrStructure.get_tab_str(users_tab)['us_name']['name'],
            'code': ctrStructure.get_tab_str(soato_tab)['code']['name'],
            'name_nas_p': 'NameNasp'
        }
        sel_result = ct_conn.exec_sel_query('select %(user_n)s, %(us_name)s from %(users)s' % format_d)
        users_dict = dict(sel_result)
        sel_result = ct_conn.exec_sel_query('select %(code)s, %(name_nas_p)s from %(soato)s' % format_d)
        soato_dict = dict(sel_result)
        return users_dict, soato_dict

    # @staticmethod
    # def make_soato_group(s_kods):
    #     soato_group = {}
    #     ate_soato = []
    #     for s in s_kods:
    #         ate_key = s[:-3]
    #         if not s[-3:] == '000':
    #             try:
    #                 soato_group[ate_key].append(s)
    #             except KeyError:
    #                 soato_group[ate_key] = [s]
    #         else:
    #             ate_soato.append(ate_key)
    #         for soato in ate_soato:
    #             if soato not in soato_group.keys():
    #                 soato_group[soato] = []
    #     return soato_group
