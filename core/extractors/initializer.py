from ..db import DbControl, ctrStructure, sprStructure


class CtrControl(DbControl):
    def __init__(self, db_path, tmp_db_path):
        super(CtrControl, self).__init__(db_path, ctrStructure, tmp_db_path)

    def is_empty_f_pref(self):
        soato_tab_str = ctrStructure.get_tab_str(self.db_schema.soato_tab)
        all_soato = self.conn.select_single_f(
            'select %s from %s where %s is Null' % (
                soato_tab_str['code']['name'],
                self.db_schema.soato_tab, soato_tab_str['pref']['name']
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

    def is_wrong_f_pref(self):
        soato_tab_str = ctrStructure.get_tab_str(self.db_schema.soato_tab)
        all_soato = self.conn.select_single_f(
            'select %s from %s ' % (
                soato_tab_str['code']['name'],
                self.db_schema.soato_tab)
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

    def is_wrong_f_pref_sez(self):
        soato_tab_str = ctrStructure.get_tab_str(self.db_schema.soato_tab)
        all_soato = self.conn.select_single_f(
            'select %s from %s where %s is not Null ' % (
                soato_tab_str['code']['name'],
                self.db_schema.soato_tab, soato_tab_str['pref']['name']
            )
        )

        failed_obj = []
        for i in all_soato:
            if i[4] == "9":  # если СЭЗ
                failed_obj.append(i)

        if failed_obj:
            failed_obj = str(tuple(failed_obj))
            return failed_obj
        else:
            return False


class SprControl(DbControl):
    def __init__(self, db_path):
        super(SprControl, self).__init__(db_path, sprStructure)
