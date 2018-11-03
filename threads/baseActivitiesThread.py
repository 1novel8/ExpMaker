from PyQt5.QtCore import QThread, pyqtSignal
from constants import baseActions
from workers import BaseWorker


class BaseActivityThread(QThread):
    success_signal = pyqtSignal('PyQt_PyObject')
    error_signal = pyqtSignal('PyQt_PyObject')
    current_action = None
    current_params = None

    def __init__(self, parent=None, success_handler=lambda x: x, error_handler=lambda x: x):
        super(BaseActivityThread, self).__init__(parent)
        self.success_signal.connect(success_handler)
        self.error_signal.connect(error_handler)
        self.worker = BaseWorker()

    def start(self, action, *params):
        self.current_action = action
        self.current_params = params
        super(BaseActivityThread, self).start()

    def run_activity(self):
        activities = {
            baseActions.LOAD_DB: baseWorker.run_initial_db_contol,
            baseActions.LOAD_PKL_SPRAV: lambda x: x,
            baseActions.LOAD_MDB_SPRAV: lambda x: x,
            baseActions.SAVE_SPRAV: lambda x: x,
            baseActions.LOAD_PKL_SESSION: lambda x: x,
            baseActions.SAVE_PKL_SESSION: lambda x: x,
        }
        return activities[self.current_action](*self.current_params)

    def run(self):
        try:
            result = self.run_activity()
        except Exception as err:
            result = {'error': err, 'type': 'general'}
        if isinstance(result, dict) and 'error' in result:
            result['action'] = self.current_action
            self.error_signal.emit(result)
        else:
            self.success_signal.emit({
                'action': self.current_action,
                'result': result
            })
