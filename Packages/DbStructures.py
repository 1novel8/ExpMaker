__author__ = 'Aleksei'

s_lc = 'S_LandCodes'
s_r_alias = 'Alias_F_Config'
s_a_r_str = 'ExpA_R_Structure'
s_a_f_str = 'ExpA_F_Structure'
s_b_r_str = 'ExpB_R_Structure'
s_b_f_str = 'ExpB_F_Structure'
s_b2e_1 = 'BGDToEkp1'
s_b2e_2 = 'BGDToEkp2'
s_soato = 'S_SOATO'
s_state = 'S_State'
s_f22 = 'S_Forma22'
s_mc = 'S_MelioCode'
s_slnad = 'S_SlNad'
s_ustype = 'S_Usertype'
s_select_conditions = 'Select_Conditions'

str_db_cfg = {
    s_lc: {
        'lc': {'name': 'LandCode',
               'type': 'SMALLINT'},
        'f_num': {'name': 'field_Num',
                  'type': 'SMALLINT'}
    },
    s_r_alias: {
        'alias': {'name': 'alias',
                  'type': 'VARCHAR'},
        'match_f': {'name': 'match_field',
                    'type': 'VARCHAR'},
        'f_type': {'name': 'field_type',
                   'type': 'VARCHAR'},
    },
    s_a_r_str: {
        'row_id': {'name': 'row_id',
                   'type': 'INTEGER'},
        'codes': {'name': 'codes',
                  'type': 'VARCHAR'},
        'row_name': {'name': 'row_name',
                     'type': 'VARCHAR'},
        'group_field': {'name': 'group_field',
                        'type': 'VARCHAR'},
        'balance_lvl': {'name': 'balance_level',
                        'type': 'SMALLINT'},
        'balance_by': {'name': 'balance_by',
                       'type': 'VARCHAR'}
    },
    s_a_f_str: {
        'f_num': {'name': 'f_num',
                  'type': 'INTEGER'},
        'f_name': {'name': 'f_name',
                   'type': 'VARCHAR'},
        'sum_fields': {'name': 'sum_fields',
                       'type': 'VARCHAR'},
        'balance_lvl': {'name': 'balance_level',
                        'type': 'SMALLINT'},
        'balance_by': {'name': 'balance_by',
                       'type': 'VARCHAR'}
    },
    s_b_r_str: {
        'row_id': {'name': 'row_id',
                   'type': 'INTEGER'},
        'row_key': {'name': 'row_key',
                    'type': 'VARCHAR'},
        'f22_value': {'name': 'f22_value',
                      'type': 'VARCHAR'},
        'sort_filter': {'name': 'sort_filter',
                        'type': 'VARCHAR'},
        'sum_conditions': {'name': 'sum_conditions',
                           'type': 'VARCHAR'},
        'balance_lvl': {'name': 'balance_level',
                        'type': 'SMALLINT'},
        'balance_by': {'name': 'balance_by',
                       'type': 'VARCHAR'}
    },
    s_b_f_str: {
        'f_num': {'name': 'f_num',
                  'type': 'INTEGER'},
        'f_name': {'name': 'f_name',
                   'type': 'VARCHAR'},
        'alias_codes': {'name': 'alias_codes',
                        'type': 'VARCHAR'},
        'sum_fields': {'name': 'sum_fields',
                       'type': 'VARCHAR'},
        'balance_lvl': {'name': 'balance_level',
                        'type': 'SMALLINT'},
        'balance_by': {'name': 'balance_by',
                       'type': 'VARCHAR'}
    }
}

spr_db_cfg = {
    s_b2e_1: {
        'f22': {'name': 'F22',
                'type': 'VARCHAR'},
        'u_type': {'name': 'UTYPE',
                   'type': 'VARCHAR'},
        'np_type': {'name': 'NPTYPE',
                    'type': 'VARCHAR'},
        'state': {'name': 'STATE',
                  'type': 'VARCHAR'},
        'sl_nad': {'name': 'SLNAD',
                   'type': 'VARCHAR'},
        'new_us_name': {'name': 'NEWUSNAME',
                        'type': 'SMALLINT'},
        'dop_us_name': {'name': 'DOPUSNAME',
                        'type': 'VARCHAR'}
    },
    s_b2e_2: {
        'f22': {'name': 'F22',
                'type': 'VARCHAR'},
        'new_f22': {'name': 'NEWF22',
                    'type': 'VARCHAR'},
        'u_type': {'name': 'UTYPE',
                   'type': 'VARCHAR'},
        'np_type': {'name': 'NPTYPE',
                    'type': 'VARCHAR'},
        'lc_min': {'name': 'LCODE_MIN',
                   'type': 'SMALLINT'},
        'lc_max': {'name': 'LCODE_MAX',
                   'type': 'SMALLINT'},
        'new_lc': {'name': 'NewLCODE',
                   'type': 'SMALLINT'},
        'state': {'name': 'STATE',
                  'type': 'VARCHAR'},
        'new_state': {'name': 'NewSTATE',
                      'type': 'SMALLINT'},
        'sl_nad': {'name': 'SLNAD',
                   'type': 'VARCHAR'},
        'new_us_name': {'name': 'NEWUSNAME',
                        'type': 'SMALLINT'},
        'dop_us_name': {'name': 'DOPUSNAME',
                        'type': 'VARCHAR'}
    },
    s_soato: {
        # 'id':   {'name': 'OBJECTID',
        #          'type': 'COUNTER'},
        'zn_1': {'name': 'znak1',
                 'type': 'VARCHAR'},
        'zn_2': {'name': 'znak2',
                 'type': 'SMALLINT'},
        'zn_57min': {'name': 'znak57min',
                     'type': 'SMALLINT'},
        'zn_57max': {'name': 'znak57max',
                     'type': 'SMALLINT'},
        'zn_810max': {'name': 'znak810max',
                      'type': 'SMALLINT'},
        'zn_810min': {'name': 'znak810min',
                      'type': 'SMALLINT'},
        'type_np': {'name': 'TypeNP',
                    'type': 'SMALLINT'}
    },
    s_state: {
        # 'id':    {'name': 'OBJECTID',
        #                  'type': 'COUNTER'},
        'state_code': {'name': 'StateCode',
                       'type': 'SMALLINT'},
    },
    s_f22: {
        # 'id':   {'name': 'OBJECTID',
        #          'type': 'COUNTER'},
        'f22_code': {'name': 'F22Code',
                     'type': 'VARCHAR'},
        'f22_name': {'name': 'F22Name',
                     'type': 'VARCHAR'}
    },
    s_mc: {
        # 'id':   {'name': 'OBJECTID',
        #          'type': 'COUNTER'},
        'mc': {'name': 'MelioCode',
               'type': 'SMALLINT'},
    },
    s_slnad: {
        # 'id':  {'name': 'OBJECTID',
        #          'type': 'COUNTER'},
        'sl_nad_code': {'name': 'SLNADCode',
                        'type': 'BYTE'},
    },
    s_ustype: {
        # 'id':   {'name': 'OBJECTID',
        #          'type': 'COUNTER'},
        'user_type': {'name': 'UsertypeCode',
                      'type': 'BYTE'}
    },
    s_select_conditions: {
        'id': {'name': 'Id',
               'type': ['INTEGER', 'SMALLINT', 'COUNTER']},
        'title': {'name': 'Title',
                  'type': ['VARCHAR']},
        'where_case': {'name': 'WhereCase',
                       'type': ['VARCHAR']}
    }
}
"""
Crostab_razv configuration>>>>>>>>>>>>>>>
"""
crs_tab = 'crostab_razv'
soato_tab = 'SOATO'
users_tab = 'Users'

db_structure = {
    crs_tab: {
        'id': {'name': 'OBJECTID',
               'type': ['COUNTER', ]},
        'shape_area': {'name': 'Shape_Area',
                       'type': ['DOUBLE', ]},
        'soato': {'name': 'SOATO',
                  'type': ['VARCHAR', ]},
        'part_n': {'name': 'Part_1',
                   'type': ['DOUBLE', ],
                   'part_name': 'Part_'},
        'user_n': {'name': 'UserN_1',
                   'type': ['INTEGER', 'SMALLINT'],
                   'part_name': 'UserN_'},
        'f22': {'name': 'Forma22_1',
                'type': ['VARCHAR', ],
                'part_name': 'Forma22_'},
        'srv_type': {'name': 'ServType08',
                     'type': ['INTEGER', 'SMALLINT']},
        'sl_nad': {'name': 'SLNAD',
                   'type': ['INTEGER', 'SMALLINT']},
        'state': {'name': 'State_1',
                  'type': ['INTEGER', 'SMALLINT']},
        'lc': {'name': 'LANDCODE',
               'type': ['INTEGER', 'SMALLINT']},
        'mc': {'name': 'MELIOCODE',
               'type': ['INTEGER', 'SMALLINT']},
        'user_n_sad': {'name': 'UserN_Sad',
                       'type': ['INTEGER', 'SMALLINT']}
    },
    soato_tab: {
        'name': {'name': 'NAME',
                 'type': ['VARCHAR', ]},
        'id': {'name': 'OBJECTID',
               'type': ['COUNTER']},
        'pref': {'name': 'PREF',
                 'type': ['VARCHAR', ]},
        'code': {'name': 'KOD',
                 'type': ['VARCHAR', ]}
    },
    users_tab: {
        'id': {'name': 'OBJECTID',
               'type': ['COUNTER']},
        'user_type': {'name': 'UserType',
                      'type': ['INTEGER', 'SMALLINT']},
        'us_name': {'name': 'UsName',
                    'type': ['VARCHAR', ]},
        'user_n': {'name': 'UserN',
                   'type': ['INTEGER', 'SMALLINT']}
    }
}
