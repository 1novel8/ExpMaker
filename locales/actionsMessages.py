from constants import (baseActions, expActions, extractionActions,
                       settingsActions)


class ActionMessages:
    db_has_data = "В базе данных %s присутствуют данные, необходимые для расчета экспликации." \
                  "\nЗапустите контроль данных для дальнейшей работы"

    start_process_logs = {
        baseActions.LOAD_DB: "Инициалицация базы данных",
        baseActions.LOAD_PKL_SPRAV: "",
        baseActions.LOAD_MDB_SPRAV: "",
        baseActions.SAVE_SPRAV: "",
        baseActions.LOAD_PKL_SESSION: "Инициализация сессии",
        baseActions.SAVE_PKL_SESSION: "Запуск сохранения сессии",

        extractionActions.CONTROL: "Запуск контроля данных",
        extractionActions.CONVERTATION: "Запуск конвертации данных",
        expActions.INIT_A_MAKER: "",
        expActions.EXP_A_SINGLE: "Запуск одиночной экспликации А",
        expActions.EXP_A_MULTI: "Запуск пакетной экспликации А",
        expActions.EXP_A_SV: "Запуск сводной экспликации",
        expActions.EXP_B: "Запуск экспликации F22",
    }
    success_logs = {
        baseActions.LOAD_DB: "База данных успешно загружена",
        baseActions.LOAD_PKL_SPRAV: "Загрузка справочной информации завершена успешно",
        baseActions.LOAD_MDB_SPRAV: "Загрузка справочной информации завершена успешно",
        baseActions.SAVE_SPRAV: "Текущие настройки и справочники успешно сохранены",
        baseActions.LOAD_PKL_SESSION: "Сессия успешно загружена",
        baseActions.SAVE_PKL_SESSION: "Сессия успешно сохранена как %s",

        extractionActions.CONTROL: "Контроль данных пройден",
        extractionActions.CONVERTATION: "Конвертация данных успешно завершена. Доступно создание экспликаций.",
        expActions.INIT_A_MAKER: "Инициализация данных для расчета экспликаций успешно проведена",
        expActions.EXP_A_SINGLE: "Выборочная экспликация А успешно создана",
        expActions.EXP_A_MULTI: "Пакентая экспликация А успешло завершена",
        expActions.EXP_A_SV: "Сводная экспликация успешно создана",
        expActions.EXP_B: "Экспликация F22 успешно создана",

    }
    error_logs = {
        baseActions.LOAD_DB: "Ошибка при загрузке базы данных",
        baseActions.LOAD_PKL_SPRAV: "Ошибка при загрузке справочников",
        baseActions.LOAD_MDB_SPRAV: "Ошибка при загрузке справочников",
        baseActions.SAVE_SPRAV: "Ошибка при сохранении справочников",
        baseActions.LOAD_PKL_SESSION: "Ошибка при загрузке сессии",
        baseActions.SAVE_PKL_SESSION: "Ошибка при сохранении сессии",

        extractionActions.CONTROL: "Не пройден контроль данных",
        extractionActions.CONVERTATION: "Конвертация данных завершена с ошибками",
        expActions.INIT_A_MAKER: "Инициализация данных для расчета экспликаций завершилась с ошибкой",
        expActions.EXP_A_SINGLE: "Ошибка при создании экспликации А",
        expActions.EXP_A_MULTI: "Ошибка пакетной экспликации А",
        expActions.EXP_A_SV: "Ошибка при создании  сводной экспликации",
        expActions.EXP_B: "Ошибка при создании экспликации F22",

    }
    loading_messages = {
        baseActions.LOAD_DB: "База данных загружается",
        baseActions.LOAD_PKL_SPRAV: "Загрузка справочной информации",
        baseActions.LOAD_MDB_SPRAV: "Загрузка справочной информации",
        baseActions.SAVE_SPRAV: "Сохранение справочной информаци",
        baseActions.LOAD_PKL_SESSION: "Сессия загружается",
        baseActions.SAVE_PKL_SESSION: "Сессия сохраняется",

        extractionActions.CONTROL: "Контроль данных",
        extractionActions.CONVERTATION: "Конвертация данных",
        expActions.INIT_A_MAKER: "Инициализация данных",
        expActions.RELOAD_A_MAKER: "Перестроение дерева экспликаций",
        expActions.EXP_A_SINGLE: "Создание экспликации А",
        expActions.EXP_A_MULTI: "Создание пакентой экспликации А",
        expActions.EXP_A_SV: "Создание сводной экспликации",
        expActions.EXP_B: "Создание экспликации F22",
        expActions.MAKE_BALANCE: "Уравнивание",
        expActions.EXPORT_EXP: "Экспорт даннных",
    }

    save_settings_messages = {
        settingsActions.SHOW_XLS: "Установлены новые настройки экспорта в Excel",
        settingsActions.SHOW_BALANCE: "Установлены новые настройки запуска уравнивания",
        settingsActions.SHOW_ACCURACY: "Установлены новые настройки округления",
        settingsActions.SHOW_CONDITIONS: "Установлены новые настройки выборки и группировки данных",
        settingsActions.SHOW_DROP: "Установлены настройки по умолчанию",
    }

    balance_log_messages = {
        expActions.EXP_B: "Уравнивание экспликации F22 не удалось. Необходимо выполнить уравнивание вручную",
    }

    def get_start_log(self, action_type):
        return ActionMessages.get_message_by_action(action_type, self.start_process_logs)

    def get_success_log(self, action_type):
        return ActionMessages.get_message_by_action(action_type, self.success_logs)

    def get_error_log(self, action_type):
        return ActionMessages.get_message_by_action(action_type, self.error_logs)

    def get_loading_msg(self, action_type):
        return ActionMessages.get_message_by_action(action_type, self.loading_messages)

    def get_save_setts_msg(self, action_type):
        return ActionMessages.get_message_by_action(action_type, self.save_settings_messages)

    def get_balance_log(self, action_type):
        return ActionMessages.get_message_by_action(action_type, self.balance_log_messages)

    @staticmethod
    def get_message_by_action(action_type, available_messages):
        if action_type in available_messages:
            return available_messages[action_type]
        else:
            return ""
