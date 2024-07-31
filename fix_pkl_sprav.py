import pickle

from constants import coreFiles

sprav_path = coreFiles.spr_default_path
try:
    loaded_data = None
    with open(sprav_path, "rb") as inp:
        loaded_data = pickle.load(inp)
except Exception:
    pass
finally:
    try:
        loaded_data['settings_data']['xls']['a_path'] = '.\\Spr\\xls_forms\\FA.xlsx'
        loaded_data['settings_data']['xls']['a_sv_path'] = '.\\Spr\\xls_forms\\FV_svod.xlsx'
        loaded_data['settings_data']['xls']['b_path'] = '.\\Spr\\xls_forms\\F22_I.xlsx'

        loaded_data['settings_data']['xls']['default_paths']['a_path'] = '.\\Spr\\xls_forms\\FA.xlsx'
        loaded_data['settings_data']['xls']['default_paths']['a_sv_path'] = '.\\Spr\\xls_forms\\FV.xlsx'
        loaded_data['settings_data']['xls']['default_paths']['b_path'] = '.\\Spr\\xls_forms\\F22_I.xlsx'

        with open(sprav_path, "wb") as output:
            pickle.dump(loaded_data, output, 2)
    except Exception:
        pass
    finally:
        print('Done')
