__author__ = 'Aleksei'

s_lc = u'S_LandCodes'
s_r_alias = u'Alias_F_Config'
s_a_r_str = u'ExpA_R_Structure'
s_a_f_str = u'ExpA_F_Structure'
s_b_r_str = u'ExpB_R_Structure'
s_b_f_str = u'ExpB_F_Structure'
s_b2e_1 = u'BGDToEkp1'
s_b2e_2 = u'BGDToEkp2'
s_soato = u'S_SOATO'
s_state = u'S_State'
s_f22 = u'S_Forma22'
s_mc = u'S_MelioCode'
s_slnad =u'S_SlNad'
s_ustype = u'S_Usertype'

str_db_cfg = {
    s_lc: {
        'lc':   {'name': u'LandCode',
                 'type': u'SMALLINT'},
        'f_num':{'name': u'field_Num',
                 'type': u'SMALLINT'}
    },
    s_r_alias: {
        'alias':    {'name': u'alias',
                     'type': u'VARCHAR'},
        'match_f':  {'name': u'match_field',
                     'type': u'VARCHAR'},
        'f_type':   {'name': u'field_type',
                     'type': u'VARCHAR'},
    },
    s_a_r_str:{
        'row_id':   {'name': u'row_id',
                     'type': u'INTEGER'},
        'codes':    {'name': u'codes',
                     'type': u'VARCHAR'},
        'row_name': {'name': u'row_name',
                     'type': u'VARCHAR'},
        'group_field':  {'name': u'group_field',
                         'type': u'VARCHAR'},
        'balance_lvl': {'name': u'balance_level',
                        'type': u'SMALLINT'},
        'balance_by':  {'name': u'balance_by',
                        'type': u'VARCHAR'}
    },
    s_a_f_str: {
        'f_num':   {'name': u'f_num',
                    'type': u'INTEGER'},
        'f_name':  {'name': u'f_name',
                    'type': u'VARCHAR'},
        'sum_fields':  {'name': u'sum_fields',
                        'type': u'VARCHAR'},
        'balance_lvl': {'name': u'balance_level',
                        'type': u'SMALLINT'},
        'balance_by':  {'name': u'balance_by',
                        'type': u'VARCHAR'}
    },
    s_b_r_str: {
        'row_id':     {'name': u'row_id',
                        'type': u'INTEGER'},
        'row_key':     {'name': u'row_key',
                        'type': u'VARCHAR'},
        'f22_value':   {'name': u'f22_value',
                        'type': u'VARCHAR'},
        'sort_filter':     {'name': u'sort_filter',
                        'type': u'VARCHAR'},
        'sum_conditions':  {'name': u'sum_conditions',
                            'type': u'VARCHAR'},
        'balance_lvl': {'name': u'balance_level',
                        'type': u'SMALLINT'},
        'balance_by':  {'name': u'balance_by',
                        'type': u'VARCHAR'}
    },
    s_b_f_str:{
        'f_num':   {'name': u'f_num',
                    'type': u'INTEGER'},
        'f_name':  {'name': u'f_name',
                    'type': u'VARCHAR'},
        'alias_codes': {'name': u'alias_codes',
                        'type': u'VARCHAR'},
        'sum_fields':  {'name': u'sum_fields',
                        'type': u'VARCHAR'},
        'balance_lvl': {'name': u'balance_level',
                        'type': u'SMALLINT'},
        'balance_by':  {'name': u'balance_by',
                        'type': u'VARCHAR'}
    }
}

spr_db_cfg = {
    s_b2e_1 : {
        'f22':      {'name': u'F22',
                     'type': u'VARCHAR'},
        'u_type':   {'name': u'UTYPE',
                     'type': u'VARCHAR'},
        'np_type':  {'name': u'NPTYPE',
                     'type': u'VARCHAR'},
        'state':    {'name': u'STATE',
                     'type': u'VARCHAR'},
        'sl_nad':   {'name': u'SLNAD',
                     'type': u'VARCHAR'},
        'new_us_name':  {'name': u'NEWUSNAME',
                         'type': u'SMALLINT'},
        'dop_us_name':  {'name': u'DOPUSNAME',
                         'type': u'VARCHAR'}
    },
    s_b2e_2 : {
        'f22':      {'name': u'F22',
                     'type': u'VARCHAR'},
        'new_f22':  {'name': u'NEWF22',
                     'type': u'VARCHAR'},
        'u_type':   {'name': u'UTYPE',
                     'type': u'VARCHAR'},
        'np_type':  {'name': u'NPTYPE',
                     'type': u'VARCHAR'},
        'lc_min':   {'name': u'LCODE_MIN',
                     'type': u'SMALLINT'},
        'lc_max':   {'name': u'LCODE_MAX',
                     'type': u'SMALLINT'},
        'new_lc':   {'name': u'NewLCODE',
                     'type': u'SMALLINT'},
        'state':   {'name': u'STATE',
                     'type': u'VARCHAR'},
        'new_state':{'name': u'NewSTATE',
                     'type': u'SMALLINT'},
        'sl_nad':   {'name': u'SLNAD',
                     'type': u'VARCHAR'},
        'new_us_name':   {'name': u'NEWUSNAME',
                         'type': u'SMALLINT'},
        'dop_us_name':   {'name': u'DOPUSNAME',
                         'type': u'VARCHAR'}
    },
    s_soato: {
        # 'id':   {'name': u'OBJECTID',
        #          'type': u'COUNTER'},
        'zn_1':     {'name': u'znak1',
                     'type': u'VARCHAR'},
        'zn_2':     {'name': u'znak2',
                     'type': u'SMALLINT'},
        'zn_57min': {'name': u'znak57min',
                     'type': u'SMALLINT'},
        'zn_57max':{'name': u'znak57max',
                     'type': u'SMALLINT'},
        'zn_810max':{'name': u'znak810max',
                     'type': u'SMALLINT'},
        'zn_810min':{'name': u'znak810min',
                     'type': u'SMALLINT'},
        'type_np':  {'name': u'TypeNP',
                     'type': u'SMALLINT'}
    },
    s_state: {
        # 'id':    {'name': u'OBJECTID',
        #                  'type': u'COUNTER'},
        'state_code':{'name': u'StateCode',
                         'type': u'SMALLINT'},
    },
    s_f22: {
        # 'id':   {'name': u'OBJECTID',
        #          'type': u'COUNTER'},
        'f22_code': {'name': u'F22Code',
                     'type': u'VARCHAR'},
        'f22_name': {'name': u'F22Name',
                     'type': u'VARCHAR'}
    },
    s_mc: {
        # 'id':   {'name': u'OBJECTID',
        #          'type': u'COUNTER'},
        'mc':   {'name': u'MelioCode',
                 'type': u'SMALLINT'},
    },
    s_slnad: {
        # 'id':  {'name': u'OBJECTID',
        #          'type': u'COUNTER'},
        'sl_nad_code': {'name': u'SLNADCode',
                         'type': u'BYTE'},
    },
    s_ustype: {
        # 'id':   {'name': u'OBJECTID',
        #          'type': u'COUNTER'},
        'user_type':    {'name': u'UsertypeCode',
                         'type': u'BYTE'}
    }
}
"""
Crostab_razv configuration>>>>>>>>>>>>>>>
"""
crs_tab = u'crostab_razv'
soato_tab =u'SOATO'
users_tab = u'Users'

db_structure = {
    crs_tab: {
        'id':   {'name': u'OBJECTID',
                 'type': [u'COUNTER',]},
        'shape_area':   {'name': u'Shape_Area',
                         'type': [u'DOUBLE',]},
        'soato':    {'name': u'SOATO',
                     'type': [u'VARCHAR',]},
        'part_n':   {'name': u'Part_1',
                     'type': [u'DOUBLE',],
                     'part_name':u'Part_'},
        'user_n':  {'name': u'UserN_1',
                     'type': [u'INTEGER', u'SMALLINT'],
                     'part_name':u'UserN_'},
        'f22':    {'name': u'Forma22_1',
                     'type': [u'VARCHAR',],
                     'part_name':u'Forma22_'},
        'srv_type': {'name': u'ServType08',
                     'type': [u'INTEGER', u'SMALLINT']},
        'sl_nad':   {'name': u'SLNAD',
                     'type': [u'INTEGER', u'SMALLINT']},
        'state':    {'name': u'State_1',
                     'type': [u'INTEGER', u'SMALLINT']},
        'lc':   {'name': u'LANDCODE',
                 'type': [u'INTEGER', u'SMALLINT']},
        'mc':   {'name': u'MELIOCODE',
                 'type': [u'INTEGER', u'SMALLINT']},
        'user_n_sad':   {'name': u'UserN_Sad',
                         'type': [u'INTEGER', u'SMALLINT']}
    },
    soato_tab: {
        'name':         {'name': u'NAME',
                         'type': [u'VARCHAR',]},
        'id':           {'name': u'OBJECTID',
                         'type': [u'COUNTER']},
        'pref':         {'name': u'PREF',
                         'type': [u'VARCHAR',]},
        'code':         {'name': u'KOD',
                         'type': [u'VARCHAR',]}
    },
    users_tab: {
        'id':           {'name': u'OBJECTID',
                         'type': [u'COUNTER']},
        'user_type':    {'name': u'UserType',
                         'type': [u'INTEGER', u'SMALLINT']},
        'us_name':      {'name': u'UsName',
                         'type': [u'VARCHAR',]},
        'user_n':       {'name': u'UserN',
                         'type': [u'INTEGER', u'SMALLINT']}
    }
}