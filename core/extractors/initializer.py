#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..db import DbControl, ctrStructure


class CtrControl(DbControl):
    def __init__(self, db_path, tmp_db_path):
        self.db_strct = ctrStructure
        super(CtrControl, self).__init__(db_path, self.db_strct, tmp_db_path)

    def is_empty_f_pref(self):
        soato_tab_str = ctrStructure.get_tab_str(self.db_strct.soato_tab)
        failed_obj = self.conn.select_single_f(
            'select %s from %s where %s is Null' % (
                soato_tab_str['code']['name'],
                self.db_strct.soato_tab, soato_tab_str['pref']['name']
            )
        )
        if failed_obj:
            failed_obj = str(tuple(failed_obj))
            return failed_obj
        else:
            return False
