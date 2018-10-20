from locales import titleLocales
from os import path, getcwd
icons_dir = path.join(getcwd(), 'Images\\menu')


class MenuConf:
    quit_app = {
        "action_title": titleLocales.exit_main_2,
        "icon_path": path.join(icons_dir, 'stop1.png'),
        "shortcut": 'Ctrl+Q',
        "tip": titleLocales.exit_main_2,
    }
    open_file = {
        "action_title": titleLocales.exit_main_1,
        "icon_path": path.join(icons_dir, 'db.png'),
        "shortcut": 'Ctrl+O',
        "tip": titleLocales.exit_main_1,
    }
    spr_default = {
        "action_title": titleLocales.spr_default_action,
        "icon_path": path.join(icons_dir, 'refresh.png'),
        "shortcut": 'Ctrl+D',
        "tip": titleLocales.spr_default_action,
    }
    spr_pkl = {
        "action_title": titleLocales.spr_pkl_action,
        "icon_path": path.join(icons_dir, 'refresh.png'),
        "shortcut": 'Ctrl+P',
        "tip": titleLocales.spr_pkl_action,
    }
    spr_mdb = {
        "action_title": titleLocales.spr_mdb_action,
        "icon_path": path.join(icons_dir, 'refresh.png'),
        "shortcut": 'Ctrl+M',
        "tip": titleLocales.spr_mdb_action,
    }
    spr_save = {
        "action_title": titleLocales.spr_save_pkl,
        "icon_path": path.join(icons_dir, 'save.png'),
        "shortcut": 'Ctrl+S',
        "tip": titleLocales.spr_save_pkl,
    }
    spr_info = {
        "action_title": titleLocales.spr_info,
        "icon_path": path.join(icons_dir, 'info.ico'),
        "shortcut": 'Ctrl+I',
        "tip": titleLocales.spr_info,
    }
    settings_xls = {
        "action_title": titleLocales.settings_xls,
        "icon_path": path.join(icons_dir, 'excel.ico'),
        "shortcut": 'Ctrl+X',
        "tip": titleLocales.settings_xls,
    }
    settings_balance = {
        "action_title": titleLocales.settings_balance,
        "icon_path": path.join(icons_dir, 'excel.ico'),
        "shortcut": 'Ctrl+B',
        "tip": titleLocales.settings_balance,
    }
    settings_accuracy = {
        "action_title": titleLocales.settings_accuracy,
        "icon_path": path.join(icons_dir, 'excel.ico'),
        "shortcut": 'Ctrl+A',
        "tip": titleLocales.settings_accuracy,
    }
    settings_conditions = {
        "action_title": titleLocales.settings_conditions,
        "icon_path": path.join(icons_dir, 'excel.ico'),
        "shortcut": 'Ctrl+C',
        "tip": titleLocales.settings_conditions,
    }

