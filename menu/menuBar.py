import string
import random
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon


class MenuSection:
    def __init__(self, app, menu_parent, title, position=100):
        self._section = None
        self.app = app
        self.menu_parent = menu_parent
        self.title = title
        self.position = position

    def activate(self):
        self._section = self.menu_parent.addMenu(self.title)

    def add_action(self, action_title='', icon_path=None, shortcut=None, tip=None, on_click=lambda x: x):
        if not self._section:
            raise Exception('%s menu section is not activated' % self.title)
        icon = QIcon(icon_path) if icon_path else None
        action = QAction(icon, action_title, self.app)
        if shortcut:
            action.setShortcut(shortcut)
        if tip:
            action.setStatusTip(tip)
        action.triggered.connect(on_click)
        self._section.addAction(action)


class MenuBar:
    def __init__(self, parent):
        self.app = parent
        self.menu = parent.menuBar()
        self._sections = {}

    @staticmethod
    def gen_section_key(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def create_section(self, section_title, section_position=None):
        key = MenuBar.gen_section_key()
        self._sections[key] = MenuSection(self.app, self.menu, section_title, section_position)
        return key

    def init_sections(self):
        """
        Activates sections according to specified positions
        :return:
        """
        for key in self._sections.keys():
            self._sections[key].activate()

    def add_section_action(self, section_key, action_conf, click_handler):
        """
        Adds action to section
        Section related to specified key should be activated
        :param section_key:
        :param action_conf: args for section initialization
        :param click_handler:
        :return: None
        """
        if section_key not in self._sections:
            raise Exception('Section is not initialized for %s' % section_key)
        self._sections[section_key].add_action(on_click=click_handler, **action_conf)

