from constants import baseActions


class ActionMessages:
    start_process_logs = {
        baseActions.LOAD_DB: 'Инициалицация базы данных',
        baseActions.LOAD_PKL_SPRAV: '',
        baseActions.LOAD_MDB_SPRAV: '',
        baseActions.SAVE_SPRAV: '',
        baseActions.LOAD_PKL_SESSION: '',
        baseActions.SAVE_PKL_SESSION: '',
    }
    success_logs = {
        baseActions.LOAD_DB: 'База данных успешно загружена',
        baseActions.LOAD_PKL_SPRAV: '',
        baseActions.LOAD_MDB_SPRAV: '',
        baseActions.SAVE_SPRAV: '',
        baseActions.LOAD_PKL_SESSION: '',
        baseActions.SAVE_PKL_SESSION: '',
    }
    error_logs = {
        baseActions.LOAD_DB: 'Ошибка при загрузке базы данных',
        baseActions.LOAD_PKL_SPRAV: '',
        baseActions.LOAD_MDB_SPRAV: '',
        baseActions.SAVE_SPRAV: '',
        baseActions.LOAD_PKL_SESSION: '',
        baseActions.SAVE_PKL_SESSION: '',
    }
    loading_messages = {
        baseActions.LOAD_DB: 'База данных загружается',
        baseActions.LOAD_PKL_SPRAV: 'Загрузка справочной информации',
        baseActions.LOAD_MDB_SPRAV: 'Загрузка справочной информации',
        baseActions.SAVE_SPRAV: 'Сохранение справочной информаци',
        baseActions.LOAD_PKL_SESSION: 'Сессия загружается',
        baseActions.SAVE_PKL_SESSION: 'Сессия сохраняется',
    }

    def get_start_log(self, action_type):
        return ActionMessages.get_message_by_action(action_type, self.start_process_logs)

    def get_success_log(self, action_type):
        return ActionMessages.get_message_by_action(action_type, self.success_logs)

    def get_error_log(self, action_type):
        return ActionMessages.get_message_by_action(action_type, self.error_logs)

    def get_loading_msg(self, action_type):
        return ActionMessages.get_message_by_action(action_type, self.loading_messages)

    @staticmethod
    def get_message_by_action(action_type, available_messages):
        if action_type in available_messages:
            return available_messages[action_type]
        else:
            return ''
