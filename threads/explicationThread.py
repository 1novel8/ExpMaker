from PyQt5.QtCore import QThread, pyqtSignal

from constants import errTypes, expActions
from core.errors import CustomError
from workers import ExplicationWorker


class ExplicationThread(QThread):
    """
    Поток для выполнения создания отчета
    """

    success_signal = pyqtSignal('PyQt_PyObject')
    progress_signal = pyqtSignal('PyQt_PyObject')
    error_signal = pyqtSignal('PyQt_PyObject')
    current_action = None
    current_params = None

    def __init__(
            self,
            parent=None,
            success_handler=lambda x: x,
            progress_handler=lambda x: x,
            error_handler=lambda x: x
    ):
        super(ExplicationThread, self).__init__(parent)
        # сигнали для демонстрации показа состояния потока
        self.success_signal.connect(success_handler)
        self.progress_signal.connect(progress_handler)
        self.error_signal.connect(error_handler)
        # класс который фактически выполняет действие
        self.worker = ExplicationWorker(process_event_handler=self.emit_progress)
        # словарь {"действие пользователя": "ответ со стороны программ"}
        self.activities = {
            expActions.INIT_A_MAKER: self.worker.init_exp_a_maker,
            expActions.RELOAD_A_MAKER: self.worker.init_exp_a_maker,
            expActions.EXP_A_SINGLE: self.worker.create_exp_a,
            expActions.EXP_A_SV: self.worker.create_exp_a_sv,
            expActions.EXP_B: self.worker.create_exp_b,
        }

    def start(self, action, **kwargs):
        """ Запуск процесса, который вызывает метод run"""
        self.current_action = action
        self.current_params = kwargs
        super(ExplicationThread, self).start()

    def emit_progress(self, progress_meta):
        self.progress_signal.emit(progress_meta)

    def emit_error(self, error):
        if not isinstance(error, CustomError):
            error = CustomError(errTypes.unexpected, str(error))
        error.action_id = self.current_action
        self.error_signal.emit(error)

    def run_activity(self):
        return self.activities[self.current_action](**self.current_params)

    def run(self):
        try:
            result = self.run_activity()
        except Exception as err:
            self.emit_error(err)
        else:
            self.success_signal.emit(result)
