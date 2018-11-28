from PyQt5.QtCore import QThread, pyqtSignal
from constants import extractionActions
from workers import ExtractionWorker
from core.errors import CustomError
from constants import errTypes
from locales import customErrors


class ExtractionThread(QThread):
    success_signal = pyqtSignal('PyQt_PyObject')
    error_signal = pyqtSignal('PyQt_PyObject')
    warnings_signal = pyqtSignal('PyQt_PyObject')
    current_action = None
    current_params = None

    def __init__(self, parent=None,
                 success_handler=lambda x: x,
                 warnings_handler=lambda x: x,
                 error_handler=lambda x: x):
        super(ExtractionThread, self).__init__(parent)
        self.success_signal.connect(success_handler)
        self.warnings_signal.connect(warnings_handler)
        self.error_signal.connect(error_handler)
        self.worker = ExtractionWorker(self.emit_error)

    def start(self, action, kvargs):
        self.current_action = action
        self.current_params = kvargs
        super(ExtractionThread, self).start()

    def emit_error(self, error):
        if not isinstance(error, CustomError):
            error = CustomError(errTypes.unexpected, str(error))
        error.action_id = self.current_action
        self.error_signal.emit(error)

    def run_activity(self):
        activities = {
            extractionActions.CONTROL: self.worker.run_contol,
            extractionActions.CONVERTATION: self.worker.run_convertation,
        }
        return activities[self.current_action](**self.current_params)

    def run(self):
        try:
            warnings = self.run_activity()
        except Exception as err:
            self.emit_error(err)
        else:
            if warnings:
            #     self.warnings_signal.emit(warnings)
            #     self.emit_error(CustomError(errTypes.general, customErrors.failed_with_protocol))
            # else:
                self.success_signal.emit('ok')
