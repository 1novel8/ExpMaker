__author__ = 'Alex Konkov'


class SprActions:
    SET_DEFAULT = 'set_default'
    CHOOSE_PKL = 'choose_pkl'
    CHOOSE_MDB = 'choose_mdb'
    SAVE = 'save_spr'
    INFO = 'info'


class SettingsActions:
    SHOW_XLS = 'show_xls'
    SHOW_BALANCE = 'show_balance'
    SHOW_ACCURACY = 'show_accuracy'
    SHOW_CONDITIONS = 'show_conditions'


class BaseActivityActions:
    LOAD_DB = 'load_work_database'
    LOAD_PKL_SPRAV = 'load_pkl_sprav'
    LOAD_MDB_SPRAV = 'load_mdb_sprav'
    SAVE_SPRAV = 'save_pkl_sprav'
    LOAD_PKL_SESSION = 'load_work_session'
    SAVE_PKL_SESSION = 'save_work_session'


class ExtractionActions:
    CONTROL = 'control'
    CONVERTATION = 'convertation'


class ExplicationActions:
    EXP_A_SINGLE = 'single_exp'
    EXP_A_SV = 'sv_exp'
    EXP_B = 'exp_f22'
