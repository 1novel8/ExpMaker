#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Aleksei Konkov'

from TableConfigData import T1Poch_Pokr_OB


import sys

thismodule = sys.modules[__name__]

class TableSettings(object):
    def __init__(self, dict_data):
        TableSettings.check_is_init_valid(dict_data)
        self.__dict__.update(dict_data)


    @staticmethod
    def check_is_init_valid(init_dict):
        required_fields = []
        if not TableSettings.validate_settings_fields(init_dict, required_fields):
            raise Exception('TableSettings constructor data is not valid')


    @staticmethod
    def validate_dynamic_settings(dynamic_dict):
        required_fields = ['table_name', 'new_file_name', 'rayon_name', 'shz_name']
        if not TableSettings.validate_settings_fields(dynamic_dict, required_fields):
            raise Exception('Dynamic settings data is not valid')


    @staticmethod
    def validate_settings_fields(init_dict, required_fields):
        dict_ok = True
        if not isinstance(init_dict, dict):
            return False
        for rf in required_fields:
            if not rf in init_dict:
                dict_ok = False
        return dict_ok



class ConfListKeysHelper(object):
    header_title = 'header_title'
    include_title = 'include_title'
    include_rowspan = 'include_rowspan'
    db_fields = 'db_fields'
    loaded_data = 'loaded_data'
    where_cases = 'where_cases'


class OutSettings(object):
    def __init__(self):
        self.conf_keys = ConfListKeysHelper()

    def get_table_settings(self, dynamic_settings):
        """
        :dynamic_settings: dict. Should include required fields
        :rtype: object
        """
        TableSettings.validate_dynamic_settings(dynamic_settings)
        tab_name = dynamic_settings['table_name']

        if hasattr(self, tab_name):
            return getattr(self, tab_name)

        table_data = OutSettings._get_table_settings_data(tab_name)
        table_data.update(dynamic_settings)
        table_settings = TableSettings(table_data)
        setattr(self, tab_name, table_settings)
        return table_settings


    @staticmethod
    def _get_table_settings_data(tab_name):
        try:
            table_settings = getattr(thismodule, tab_name).get_config()
            return table_settings
        except Exception as err:
            print err
            raise Exception('No settings data specified for table ' + tab_name)
