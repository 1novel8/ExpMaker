#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Aleksei Konkov'
import os.path



class DictAsObject(object):
    def __init__(self, dict_data):
        if isinstance(dict_data, dict):
            self.__dict__.update(dict_data)

class Settings(object):
    def __init__(self, xls_templates_dir, store_source):
        self.xls_templates_dir = xls_templates_dir
        self.last_hold_pkl_dir = store_source
        self.set_default_settings()
        # super(Settings, self).__init__(settings_data)

    def update_settings(self, settings_data):
        if self.validate_settings(settings_data):
            try:
                for k, v in settings_data.items():
                    self.set_settings_by_key(k, v)
            except Exception as err:
                print err
                self.set_default_settings()
        else:
            self.set_default_settings()

    @staticmethod
    def get_valid_settings_keys():
        return ['xls', 'rnd', 'balance']

    def get_settings_dict(self):
        out = {}
        for key in Settings.get_valid_settings_keys():
            out[key] = getattr(self, key).__dict__
        return out

    @staticmethod
    def validate_settings(settings_dict):
        ok = True
        if isinstance(settings_dict, dict):
            for k in settings_dict.keys():
                if k not in Settings.get_valid_settings_keys():
                    ok = False
        else:
            ok = False
        if ok:
            try:
                ok = os.path.isfile(settings_dict['xls']['a_sv_path'])
            except:
                ok = False
        return ok

    def set_settings_by_key(self, s_key, s_values):
        if s_key in ['xls', 'rnd', 'balance']:
            setattr(self, s_key, DictAsObject(s_values))

    def set_default_settings(self):
        d_settings = Settings.get_default_settings(self.xls_templates_dir)
        for k, v in d_settings.items():
            self.set_settings_by_key(k,v)


    @staticmethod
    def get_default_settings(xls_templates_dir):
        return {
            'xls': {
                'a_sv_l': u'A',
                'a_sv_n': 6,
                'a_l': u'F',
                'a_n': 16,
                'a_obj_l': u'M',
                'a_obj_n': 4,
                'b_l': u'B',
                'b_n': 7,
                'a_path': u'%s\\FA.xlsx' % xls_templates_dir,
                'a_sv_path': u'%s\\FA_svod.xlsx' % xls_templates_dir,
                'b_path': u'%s\\FB.xlsx' % xls_templates_dir,
                'a_sh_name': u'RB экспликация А',
                'a_sv_sh_name': u'Активный',
                'b_sh_name': u'Активный',  # RB Форма22 зем.
            },
            'rnd': {
                'a_s_accuracy': 4,
                'b_accuracy': 0,
                'small_accur': 3,
                'a_sv_accuracy': 4,
                'show_small': True
            },
            'balance': {
                'include_a_balance': False,
                'include_a_sv_balance': False,
                'include_b_balance': True,
            }
        }