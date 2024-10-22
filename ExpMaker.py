import sys
import time
from os import getcwd, path, remove

from PyQt5.QtCore import QCoreApplication, QSemaphore, QSize, QThreadPool
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QFileDialog, QGridLayout,
                             QMainWindow, QMessageBox, QSplitter, QWidget, QAction)

from constants import (ExplicationActions, baseActions, controlsStates,
                       coreFiles, errTypes, expActions, extractionActions,
                       settingsActions, sprActions)
from core.settingsHolders.settingsHolder import SettingsHolder
from core.settingsHolders.spravHolder import SpravHolder
from core.system_logger import create_logger, log_error
from locales import actionLocales, customErrors, titleLocales
from menu import MenuBar, MenuConf
from threads import BaseActivityThread, ExplicationThread, ExtractionThread
from ui.components import LoadingLabel, SrcFrame, TableWidget
from ui.custom import ControlsFrame, ExpSelector, LogoFrame, LogTable
from ui.custom.editSettingsWindow import EditSettingsWindow
from ui.styles import splitter as splitter_styles

project_dir = getcwd()
sem = QSemaphore(1)


class ExpWindow(QMainWindow):
    def __init__(self):
        # Инициализация окна
        QMainWindow.__init__(self)
        self.setMinimumSize(QSize(640, 480))
        self.resize(1400, 840)
        self.setWindowTitle('Explication 2024.2.0')
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.setWindowIcon(QIcon(path.join(project_dir, 'Images\\exp.png')))

        # Фрейм для кнопок слева (Контроль, Конвертация, ...)
        self.controls_frame = ControlsFrame(
            self,
            on_click=self.handle_controls_click,  # При нажатии на любую из кнопок запустится это
        )
        self.controls_frame.hide()

        # Логгер
        self.log_table = LogTable(central_widget)
        self.sprav_holder = SpravHolder()
        self.settings_holder = SettingsHolder(
            xls_templates_dir=coreFiles.xls_templates_dir,
            store_source=coreFiles.spr_default_path,
            on_save=self.save_sprav_settings,
        )
        # WARNING Что это такое?
        self.control_table = TableWidget(central_widget, headers=titleLocales.control_table_head)
        self.convert_table = TableWidget(central_widget, headers=titleLocales.convert_table_head)

        # таблица для Расчет сводной экспликации - форма F22 ДЛЯ ОДНОЙ ОБЛ или пакетно
        self.exp_selector = ExpSelector(
            parent=central_widget,
            settings=self.settings_holder,
            sprav=self.sprav_holder,
            reinit_exp_hook=lambda rows: self.initialize_exp_a_maker(rows, reload=True),
            handle_exp_click=lambda exp, sub_dir_name, action_id=expActions.EXP_A_SINGLE: self.handle_controls_click(
                action_id=action_id,
                sub_dir_name=sub_dir_name,
                attachment=exp,
            ),
            # при выборе определенного поля в таблице вызывается handle_exp_click
        )
        # Укажите путь для сохранения экспликаций
        # ввод пути для создания отчета
        self.save_exp_as_frame = SrcFrame(
            self,
            title=titleLocales.src_exp_save_as,
            get_dir=True,
            placeholder=titleLocales.src_frame_no_dir_chosen,
        )
        # Источник Данных
        # ввод пути к БД
        self.src_frame = SrcFrame(
            self,
            title=titleLocales.src_frame_default,
            on_select=self.on_file_opened,
            placeholder=titleLocales.src_frame_no_file_chosen,
        )
        self.src_frame.path_selected_signal.connect(
            self.save_exp_as_frame.set_selected_file,
        )  # при выбора файла ввода, отправляется сигнал для изменения пути файла вывода

        self.init_widgets_positions(central_widget)
        # Выпадающее меню сверху (Файл, справочники, настройки)
        self.menu = None
        self.init_menu_bar()

        self._from_session = False
        self.baseThread = BaseActivityThread(
            self,
            error_handler=self.handle_activity_error,
            success_handler=self.handle_base_activity_success,
        )
        self.extractionThread = ExtractionThread(
            self,
            error_handler=self.handle_activity_error,
            warnings_handler=self.handle_extraction_warnings,
            success_handler=self.handle_extraction_success,
        )
        self.explicationThread = ExplicationThread(
            self,
            error_handler=self.handle_activity_error,
            progress_handler=self.handle_explication_progress,
            success_handler=self.handle_explication_success,
        )

        action = QAction('stop action', self)
        action.setShortcut('Esc')
        action.triggered.connect(self.stop_all_actions)
        self.addAction(action)

        self.explicationThreadPool = QThreadPool()
        # progress bar снизу справа
        self.loading_process_label = LoadingLabel(self)
        self.statusBar().addPermanentWidget(self.loading_process_label)
        self.clear_workspace(controlsStates.INITIAL)

        self.explication_data = None
        self.exp_a_maker = None
        self._not_filtered_data = []
        self.settings_window = None

        self.run_sprav_action(sprActions.SET_DEFAULT)  # устанавливаем справочник по-дефолту

    def show_modal(self, message, modal_type='error', title=None):
        if modal_type == 'error':
            title = title or titleLocales.error_modal_title
            log_error(message, is_critical=True)
            QMessageBox.critical(self, title, message, QMessageBox.Ok)
        if modal_type == 'warning':
            title = title or titleLocales.warning_modal_title
            QMessageBox.warning(self, title, message, QMessageBox.Ok)
        elif modal_type == 'information':
            title = title or "Информация"
            QMessageBox.information(self, title, message, QMessageBox.Ok)
        elif modal_type == 'question':
            title = title or "Подтвердите действие"
            QMessageBox.question(self, title, message, QMessageBox.Ok)

    def show_loading(self, message='', log_message=''):
        self.loading_process_label.start_loading(message)
        self.controls_frame.set_state(controlsStates.LOADING)
        if log_message:
            self.add_event_log(log_message)

    def finish_loading(self, log_message=''):
        self.controls_frame.set_previous_state()
        self.loading_process_label.stop_loading()
        if log_message:
            self.add_event_log(log_message)

    def add_event_log(self, log_msg, with_time=True):
        if with_time:
            self.log_table.add_row(log_msg)
        else:
            self.log_table.add_row(log_msg, '- // -')

    def init_menu_bar(self):
        """
        Выпадающее меню сверху [Файл, справочники, настройки]
        """
        menu = MenuBar(self)
        file_section_key = menu.create_section(titleLocales.menu_1, 1)
        sprav_section_key = menu.create_section(titleLocales.menu_2, 2)
        settings_section_key = menu.create_section(titleLocales.menu_3, 3)
        menu.init_sections()
        menu.add_section_action(
            file_section_key,
            MenuConf.open_file,
            self.src_frame.click_file_selection,
        )
        menu.add_section_action(
            file_section_key, MenuConf.quit_app,
            QCoreApplication.instance().quit,
        )
        menu.add_section_action(
            file_section_key,
            MenuConf.save_session,
            self.save_pkl_session,
        )
        menu.disable_item(file_section_key, MenuConf.save_session['action_id'])
        menu.add_section_action(
            sprav_section_key,
            MenuConf.spr_default,
            lambda x: self.run_sprav_action(sprActions.SET_DEFAULT),
        )
        menu.add_section_action(
            sprav_section_key,
            MenuConf.spr_pkl,
            lambda x: self.run_sprav_action(sprActions.CHOOSE_PKL),
        )
        menu.add_section_action(
            sprav_section_key,
            MenuConf.spr_mdb,
            lambda x: self.run_sprav_action(sprActions.CHOOSE_MDB),
        )
        menu.add_section_action(
            sprav_section_key,
            MenuConf.spr_save,
            lambda x: self.run_sprav_action(sprActions.SAVE),
        )
        menu.add_section_action(
            sprav_section_key,
            MenuConf.spr_save_as_default,
            lambda x: self.run_sprav_action(sprActions.SAVE_AS_DEFAULT),
        )
        menu.add_section_action(
            sprav_section_key,
            MenuConf.spr_info,
            lambda x: self.run_sprav_action(sprActions.INFO),
        )
        menu.add_section_action(
            settings_section_key,
            MenuConf.settings_xls,
            lambda x: self.run_settings_action(settingsActions.SHOW_XLS),
        )
        menu.add_section_action(
            settings_section_key,
            MenuConf.settings_balance,
            lambda x: self.run_settings_action(settingsActions.SHOW_BALANCE),
        )
        menu.add_section_action(
            settings_section_key,
            MenuConf.settings_accuracy,
            lambda x: self.run_settings_action(settingsActions.SHOW_ACCURACY),
        )
        menu.add_section_action(
            settings_section_key,
            MenuConf.settings_conditions,
            lambda x: self.run_settings_action(settingsActions.SHOW_CONDITIONS),
        )
        menu.add_section_action(
            settings_section_key,
            MenuConf.settings_drop,
            lambda x: self.run_settings_action(settingsActions.SHOW_DROP),
        )
        menu.file_section_key = file_section_key
        self.menu = menu

    def stop_all_actions(self):
        if self.explicationThread.isRunning():
            self.explicationThread.terminate()
            self.explicationThread.wait(5000)
            self.finish_loading('Расчет экспликации прерван пользователем')

    def run_sprav_action(self, action_type):
        """
        Выбор справочника
        """
        if action_type == sprActions.SET_DEFAULT:
            return self.run_base_action(
                baseActions.LOAD_PKL_SPRAV,
                settings_holder=self.settings_holder,
                sprav_holder=self.sprav_holder,
            )
        elif action_type == sprActions.CHOOSE_PKL:
            sprav_source = self.get_file_path(
                titleLocales.load_sprav_source_finder_title + '*.pkl',
                f_extension='*.pkl',
            )
            if sprav_source:
                self.run_base_action(
                    baseActions.LOAD_PKL_SPRAV,
                    sprav_path=sprav_source,
                    settings_holder=self.settings_holder,
                    sprav_holder=self.sprav_holder,
                )
                self.clear_workspace(controlsStates.SESSION_LOADED)

        elif action_type == sprActions.CHOOSE_MDB:
            sprav_source = self.get_file_path(titleLocales.load_sprav_source_finder_title + '*.mdb')
            if sprav_source:
                self.run_base_action(
                    baseActions.LOAD_MDB_SPRAV,
                    sprav_holder=self.sprav_holder,
                    sprav_path=sprav_source,
                )
                if self.src_frame.selected_file:
                    # если база уже выбрана, то просто DB_LOADED, else INITIAL
                    self.clear_workspace(controlsStates.DB_LOADED)
                else:
                    self.clear_workspace(controlsStates.INITIAL)

        elif action_type == sprActions.SAVE:
            if not self.sprav_holder.current_sprav_data:
                self.show_modal(customErrors.spr_not_loaded)
                return
            save_as = self.get_file_path(titleLocales.save_sprav_source_finder_title, save=True)
            self.settings_holder.should_save_as = save_as
            self.save_sprav_settings(save_as, self.settings_holder.get_settings_dict())
        elif action_type == sprActions.SAVE_AS_DEFAULT:
            if not self.sprav_holder.current_sprav_data:
                self.show_modal(customErrors.spr_not_loaded)
                return
            self.settings_holder.should_save_as = coreFiles.spr_default_path
            self.save_sprav_as_default(current_settings=self.settings_holder.get_settings_dict())
            self.show_modal('Справочник сохранена как "справочник по умолчанию".',
                            modal_type='information', title=titleLocales.spr_save_as_default)
        elif action_type == sprActions.INFO:
            info = self.sprav_holder.get_info()
            if info:
                self.show_modal(info, modal_type='information', title=titleLocales.spr_info)
            else:
                self.show_modal(customErrors.spr_not_loaded)

    def save_sprav_settings(self, save_as, current_settings):
        if save_as:
            self.run_base_action(
                baseActions.SAVE_SPRAV,
                sprav_data=self.sprav_holder.current_sprav_data,
                settings_data=current_settings,
                save_as=save_as,
            )

    def save_sprav_as_default(self, current_settings):
        self.run_base_action(
            baseActions.SAVE_SPRAV_AS_DEFAULT,
            sprav_data=self.sprav_holder.current_sprav_data,
            settings_data=current_settings,
            sprav_holder=self.sprav_holder,
            settings_holder=self.settings_holder,
        )

    def run_base_action(self, action_id: str, **kwargs):
        loading_message = actionLocales.get_loading_msg(action_id)
        log_message = actionLocales.get_start_log(action_id)
        self.show_loading(loading_message, log_message)
        self.baseThread.start(action_id, **kwargs)

    def handle_controls_click(
            self,
            action_id: ExplicationActions,
            sub_dir_name: str = None,
            attachment=None,
    ):
        """ Действие на нажатие кнопок """

        loading_message = actionLocales.get_loading_msg(action_id)
        log_message = actionLocales.get_start_log(action_id)
        if action_id == extractionActions.CONTROL:
            self.extractionThread.start(
                action_id,
                sprav_holder=self.sprav_holder,
                db_file=self.src_frame.selected_file
            )
        elif action_id == extractionActions.CONVERTATION:
            self.extractionThread.start(
                action_id,
                sprav_holder=self.sprav_holder,
                settings_holder=self.settings_holder
            )
        else:
            exp_out = self.check_exp_path()
            if not exp_out:
                return
            elif action_id == expActions.EXP_A_SINGLE:  # Расчет сводной экспликации - форма В для 1 обл.
                self.explicationThread.start(
                    action_id,
                    exp_provider=attachment,
                    out_exp_file=exp_out,
                    sprav_holder=self.sprav_holder,
                    settings_holder=self.settings_holder,
                    sub_dir_name=sub_dir_name,
                )

            elif action_id == expActions.EXP_A_MULTI:
                self.explicationThread.start(
                    action_id,
                    exp_provider=attachment,
                    out_exp_file=exp_out,
                    sprav_holder=self.sprav_holder,
                    settings_holder=self.settings_holder,
                    sub_dir_name=sub_dir_name,
                )
            elif action_id == expActions.EXP_A_SV:  # Расчет сводной экспликации - форма В
                self.explicationThread.start(
                    action_id,
                    out_exp_file=exp_out,
                    exp_maker=self.exp_a_maker,
                    sprav_holder=self.sprav_holder,
                    settings_holder=self.settings_holder,
                )
            elif action_id == expActions.EXP_B:  # отчет по форме 22
                self.explicationThread.start(
                    action_id,
                    out_exp_file=exp_out,
                    rows_data=self.explication_data['rows'],
                    sprav_holder=self.sprav_holder,
                    settings_holder=self.settings_holder,
                )

        self.show_loading(loading_message, log_message)

    def check_exp_path(self):
        exp_dir = self.save_exp_as_frame.get_selected_file()
        if not exp_dir or not path.exists(exp_dir):
            self.show_modal("Выберите директорию для сохранения экспликаций", modal_type='warning')
            return
        return path.join(exp_dir, '%s' % (self.explication_data['db_name']))

    def initialize_exp_a_maker(self, exp_rows, reload=False):
        action_id = expActions.RELOAD_A_MAKER if reload else expActions.INIT_A_MAKER
        if not reload:
            loading_message = actionLocales.get_loading_msg(action_id)
            log_message = actionLocales.get_start_log(action_id)
            self.show_loading(loading_message, log_message)
        self.explicationThread.start(
            action_id,
            sprav_holder=self.sprav_holder,
            rows=exp_rows,
            soato=self.explication_data['soato'],
            users=self.explication_data['users'],
            options=self.explication_data['options'],
        )

    def handle_base_activity_success(self, result):
        action_id = self.baseThread.current_action
        success_message = actionLocales.get_success_log(action_id)
        if action_id == baseActions.LOAD_DB:
            self.set_sources_initialized()
        elif action_id == baseActions.LOAD_PKL_SESSION:
            self.explication_data = result['exp_data']  # тут
            self.set_sources_initialized(True)
            exp_path = result['exp_save_path']
            if path.isdir(exp_path):
                self.save_exp_as_frame.set_selected_file(exp_path)
            self.initialize_exp_a_maker(self.explication_data['rows'])
        elif action_id == baseActions.SAVE_PKL_SESSION:
            success_message = success_message % result
        elif action_id == baseActions.LOAD_PKL_SPRAV:
            checks = self.settings_holder.check_xl_templates()
            if 'set_to_default_templates' in checks and len(checks['set_to_default_templates']):
                self.show_modal(
                    """Установлены пути по умолчанию к исходным файлам *.xls шаблонов для экспорта экспликаций %s.
                    \nНеобходимые пути можно выбрать в настройках экспорта в Excel
                """ % ', '.join(map(lambda x: x['name'], checks['set_to_default_templates'])), modal_type='warning')
            if 'unresolved_templates' in checks and len(checks['unresolved_templates']):
                self.show_modal("""Обнаружены некорректные пути к шаблонам Excel файлов форм %s.\n
                На вкладке Настройки -> 
                Экспорт в Excel укажите место расположения шаблонов Excel файлов.
                """ % ', '.join(map(lambda x: x['name'], checks['unresolved_templates'])),
                                title='Не найдены шаблоны Excel файлов форм')
        self.finish_loading(success_message)

    def handle_extraction_success(self, result):
        """тут"""
        action_id = self.extractionThread.current_action
        self.finish_loading(actionLocales.get_success_log(action_id))
        if action_id == extractionActions.CONTROL:
            self.control_table.clear_rows(hide=True)
            self.controls_frame.set_state(controlsStates.CONTROL_PASSED)
        elif action_id == extractionActions.CONVERTATION:
            self.convert_table.clear_rows(hide=True)
            self.controls_frame.set_state(controlsStates.CONVERTATION_PASSED)
            self.explication_data = {
                'rows': result[0],
                'users': result[1],
                'soato': result[2],
                'options': result[3],
                'db_name': self.src_frame.get_selected_file(name_only=True)
            }
            self.save_exp_as_frame.hide()
            self.initialize_exp_a_maker(result[0])

    def handle_explication_success(self, result):
        action_id = self.explicationThread.current_action

        if action_id == expActions.INIT_A_MAKER:
            self.exp_a_maker = result
            self.menu.enable_item(self.menu.file_section_key, MenuConf.save_session['action_id'])
            self.exp_selector.enable(self.explication_data, self.exp_a_maker.exp_tree)
            self.finish_loading(actionLocales.get_success_log(action_id))
        elif action_id == expActions.RELOAD_A_MAKER:
            self.exp_a_maker = result
            self.exp_selector.remake_tree(self.exp_a_maker.exp_tree)
        elif action_id in (expActions.EXP_A_SINGLE, expActions.EXP_A_SV, expActions.EXP_B, expActions.EXP_A_MULTI):
            self.finish_loading(actionLocales.get_success_log(action_id))

    def handle_explication_progress(self, next_action_meta) -> None:
        process_message = actionLocales.get_loading_msg(next_action_meta['action'])
        self.show_loading(process_message + ' ' + next_action_meta['message'])

    def handle_extraction_warnings(self, warnings) -> None:
        action_id = self.extractionThread.current_action
        if action_id == extractionActions.CONTROL:
            self.control_table.add_control_protocol(warnings)
            self.controls_frame.set_state(controlsStates.CONTROL_FAILED)
        elif action_id == extractionActions.CONVERTATION:
            self.convert_table.add_convert_protocol(warnings)
            self.controls_frame.set_state(controlsStates.CONVERTATION_FAILED)

    def handle_activity_error(self, error) -> None:
        try:
            self.show_modal(error.message)
            if error.type == errTypes.control_warning:
                return
        except Exception as err:
            log_error(err)
            self.show_modal(str(error))
        error_log = actionLocales.get_error_log(error.action_id)
        if error_log:
            self.finish_loading(error_log)

    def get_file_path(self, dialog_title, save=False, f_extension='*.mdb'):
        options = QFileDialog.DontUseNativeDialog
        if save:
            selected = QFileDialog(self).getSaveFileName(self, dialog_title, options=options)
        else:
            selected = QFileDialog(self).getOpenFileName(
                self,
                dialog_title,
                project_dir,
                'Valid files (%s);; All files (*)' % f_extension,
                options=options,
            )
        return selected[0]

    def run_settings_action(self, action_type) -> None:
        self.settings_window = EditSettingsWindow(
            initial_settings=self.settings_holder,
            sprav_holder=self.sprav_holder,
            parent=self,
            edit_action_type=action_type,
            on_save=self.set_updated_settings,
        )
        self.settings_window.show()

    def set_updated_settings(self, result) -> None:
        self.settings_window.close()
        self.settings_holder.save()
        if not self._from_session \
                and result['setts_type'] == settingsActions.SHOW_CONDITIONS \
                and result['active_condition_changed']:
            self.clear_workspace(controlsStates.DB_LOADED)
        self.add_event_log(actionLocales.get_save_setts_msg(result['setts_type']))

    def init_widgets_positions(self, central_widget: QWidget) -> None:
        main_grid = QGridLayout(central_widget)
        central_widget.setLayout(main_grid)
        splitter = self.init_splitter()
        logo = LogoFrame(self, titleLocales.logo)
        main_grid.addWidget(logo, 0, 0, 1, 11)
        main_grid.addWidget(self.src_frame, 1, 0, 1, 2)
        main_grid.addWidget(self.controls_frame, 2, 0, 6, 2)
        main_grid.addWidget(self.save_exp_as_frame, 8, 0, 1, 2)
        main_grid.addWidget(splitter, 1, 2, 15, 11)

    def init_splitter(self) -> QSplitter:
        splitter = QSplitter(self)
        splitter.setStyleSheet(splitter_styles)
        splitter.addWidget(self.control_table)
        splitter.addWidget(self.convert_table)
        splitter.addWidget(self.exp_selector)
        splitter.addWidget(self.log_table)
        return splitter

    def on_file_opened(self, file_path: str) -> None:
        splitted = path.splitext(file_path)
        extension = splitted[-1]
        supported_actions = {
            '.mdb': baseActions.LOAD_DB,
            '.pkl': baseActions.LOAD_PKL_SESSION,
        }
        self.clear_workspace(controlsStates.INITIAL)
        if extension in supported_actions:
            self.run_base_action(supported_actions[extension], file_path=file_path)
        else:
            self.show_modal('Необходимо указать файл с расширением *.mdb или *.pkl', modal_type='warning')

    def save_pkl_session(self) -> None:
        default_name = '%s_%s.pkl' % (self.explication_data['db_name'], time.strftime('_%d_%m_%y'))
        save_as = QFileDialog(self).getSaveFileName(
            self,
            titleLocales.session_save_as_dialog,
            default_name,
            options=QFileDialog.DontUseNativeDialog,
        )[0]
        if save_as:
            if save_as[-4:] != '.pkl':
                save_as += '.pkl'
            dump_data = {
                'exp_data': self.explication_data,
                'exp_save_path': self.save_exp_as_frame.get_selected_file()
            }
            self.run_base_action(
                baseActions.SAVE_PKL_SESSION,
                save_as=save_as,
                dump_data=dump_data,
            )

    def set_sources_initialized(self, from_session: bool = False):
        self.src_frame.set_src_text()
        ind = 0
        for i in range(len(self.src_frame.selected_file)):
            if self.src_frame.selected_file[ind] == '\\':
                ind = i

        self._from_session = from_session
        session_action = MenuConf.save_session['action_id']
        if from_session:
            self.menu.enable_item(self.menu.file_section_key, session_action)
            self.clear_workspace(controlsStates.SESSION_LOADED)
        else:
            self.menu.disable_item(self.menu.file_section_key, session_action)
            self.clear_workspace(controlsStates.DB_LOADED)
            self.add_event_log(actionLocales.db_has_data % path.basename(self.src_frame.selected_file), with_time=False)

    def clear_workspace(self, controls_state: str):
        self.controls_frame.set_state(controls_state)
        self.control_table.clear_rows(hide=True)
        self.convert_table.clear_rows(hide=True)
        not_from_session = controls_state != controlsStates.SESSION_LOADED
        self.exp_selector.setHidden(not_from_session)
        self.save_exp_as_frame.hide(hide=not_from_session)


def rm_temp_db(file_rm=coreFiles.tempDB_path):
    if path.isfile(file_rm):
        remove(file_rm)


if __name__ == '__main__':
    create_logger('main', './error.log')
    app = QApplication(sys.argv)
    mainWin = ExpWindow()
    mainWin.show()


    def execute():
        try:
            app.exec_()
        except Exception as err:
            log_error(err, is_critical=True)
        finally:
            rm_temp_db()


    sys.exit(execute())
