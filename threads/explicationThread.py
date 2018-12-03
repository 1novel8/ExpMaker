from PyQt5.QtCore import QThread, pyqtSignal
from constants import expActions
from workers import ExplicationWorker
from core.errors import CustomError
from constants import errTypes


class ExplicationThread(QThread):
    success_signal = pyqtSignal('PyQt_PyObject')
    error_signal = pyqtSignal('PyQt_PyObject')
    current_action = None
    current_params = None

    def __init__(self, parent=None, success_handler=lambda x: x, error_handler=lambda x: x):
        super(ExplicationThread, self).__init__(parent)
        self.success_signal.connect(success_handler)
        self.error_signal.connect(error_handler)
        self.worker = ExplicationWorker(self.emit_error)

    def start(self, action, **kvargs):
        self.current_action = action
        self.current_params = kvargs
        super(ExplicationThread, self).start()

    def emit_error(self, error):
        if not isinstance(error, CustomError):
            error = CustomError(errTypes.unexpected, str(error))
        error.action_id = self.current_action
        self.error_signal.emit(error)

    def run_activity(self):
        activities = {
            expActions.INIT_A_MAKER: self.worker.init_exp_a_maker,
            expActions.EXP_A_SINGLE: self.worker.run_exp_a,
            expActions.EXP_A_SV: self.worker.run_exp_a_sv,
            expActions.EXP_B: self.worker.run_exp_b,
        }
        return activities[self.current_action](**self.current_params)

    def run(self):
        try:
            result = self.run_activity()
        except Exception as err:
            self.emit_error(err)
        else:
            self.success_signal.emit(result)
