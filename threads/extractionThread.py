from PyQt5.QtCore import QThread, pyqtSignal

from constants import errTypes, extractionActions
from core.errors import CustomError
from locales import customErrors
from workers import ExtractionWorker


class ExtractionThread(QThread):
    success_signal = pyqtSignal('PyQt_PyObject')
    error_signal = pyqtSignal('PyQt_PyObject')
    warnings_signal = pyqtSignal('PyQt_PyObject')
    current_action = None
    current_params = None

    def __init__(
            self,
            parent=None,
            success_handler=lambda x: x,
            warnings_handler=lambda x: x,
            error_handler=lambda x: x
    ):
        super().__init__(parent)
        self.success_signal.connect(success_handler)
        self.warnings_signal.connect(warnings_handler)
        self.error_signal.connect(error_handler)
        self.worker = ExtractionWorker(self.emit_error)
        self.activities = {
            extractionActions.CONTROL: self.worker.run_contol,
            extractionActions.CONVERTATION: self.worker.run_convertation,
        }

    def start(self, action, **kwargs):
        self.current_action = action
        self.current_params = kwargs
        super().start()

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
            if self.current_action == extractionActions.CONTROL:
                if result:
                    self.warnings_signal.emit(result)
                    raise CustomError(errTypes.general, customErrors.failed_with_protocol)
                else:
                    self.success_signal.emit('passed')
            elif self.current_action == extractionActions.CONVERTATION:
                if isinstance(result, dict):
                    self.warnings_signal.emit(result)
                    raise CustomError(errTypes.general, customErrors.failed_with_protocol)
                elif isinstance(result, list):
                    self.success_signal.emit(result)
                else:
                    raise CustomError(errTypes.general, customErrors.no_result)
        except Exception as err:
            self.emit_error(err)
