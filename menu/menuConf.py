from locales import titleLocales
from os import path, getcwd
icons_dir = path.join(getcwd(), 'Images')


class MenuConf:
    open_file = {
        "action_title": titleLocales.exit_main_1,
        "icon_path": path.join(icons_dir, 'db.png'),
        "shortcut": 'Ctrl+O',
        "tip": titleLocales.exit_main_1,
    }
