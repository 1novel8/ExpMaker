#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Aleksei Konkov'
from TableConfigData  import T1Poch_Pokr_OB, \
    T2Pochv_MSOK_OB, \
    T3KultTehnSost_OB,\
    T4Poch_IshBall_OB, \
    T5Poch_OcenBall_OB, \
    T6TehnSvoistMest_OB, \
    T7Inx_NormZatUbRab_OB,\
    T8Inx_NormZatOptUsl_OB,\
    T9Inx_TrZatOptUsl_OB,\
    T10NormUrozh_OB,\
    T11NormZatrat_OB,\
    T12NormSeb_1C_OB,\
    T13PK_k_oc_bal_OB,\
    T14NormChDoh_OB,\
    T15DifDoh_k_P_U_OB,\
    T16Obsh_Ball_OB,\
    T17PochEkolBonit_EL,\
    T18TehnSvoist_EL,\
    T19ObobOcen_EL,\
    T20OcenMestUdal, \
    T21PK_k_NV_i_RT_OB,\
    T22Itog_VidZem

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
        required_fields = ['rayon_name', 'shz_name']
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



    def get_table_settings(self, tab_name, dynamic_settings = None):
        """
        :dynamic_settings: dict. Should include required fields
        :rtype: object
        """
        if dynamic_settings is None:
            dynamic_settings = {}
        else:
            TableSettings.validate_dynamic_settings(dynamic_settings)

        if hasattr(self, tab_name):
            table_settings = getattr(self, tab_name)
            table_settings.__dict__.update(dynamic_settings)
            return table_settings
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
