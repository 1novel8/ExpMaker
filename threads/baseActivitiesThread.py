from PyQt5.QtCore import QThread, pyqtSignal
from constants import baseActions
from workers import BaseWorker
from core.errors import CustomError
from constants import errTypes


class BaseActivityThread(QThread):
    success_signal = pyqtSignal('PyQt_PyObject')
    error_signal = pyqtSignal('PyQt_PyObject')
    current_action = None
    current_params = None

    def __init__(self, parent=None, success_handler=lambda x: x, error_handler=lambda x: x):
        super(BaseActivityThread, self).__init__(parent)
        self.success_signal.connect(success_handler)
        self.error_signal.connect(error_handler)
        self.worker = BaseWorker(self.emit_error)

    def start(self, action, kvargs):
        self.current_action = action
        self.current_params = kvargs
        super(BaseActivityThread, self).start()

    def emit_error(self, error):
        if not isinstance(error, CustomError):
            error = CustomError(errTypes.unexpected, str(error))
        self.error_signal.emit(error)

    def run_activity(self):
        activities = {
            baseActions.LOAD_DB: self.worker.run_initial_db_contol,
            baseActions.LOAD_PKL_SPRAV: self.worker.load_pkl_sprav,
            baseActions.LOAD_MDB_SPRAV: self.worker.load_mdb_sprav,
            baseActions.SAVE_SPRAV: self.worker.save_sprav,
            baseActions.LOAD_PKL_SESSION: self.worker.load_pkl_session,
            # baseActions.SAVE_PKL_SESSION: self.worker.save_pkl_session,
        }
        return activities[self.current_action](**self.current_params)

    def run(self):
        try:
            result = self.run_activity()
        except Exception as err:
            self.emit_error(err)
        else:
            self.success_signal.emit(result)
