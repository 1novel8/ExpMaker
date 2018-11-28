from core.extractors import DataControl
from constants import appKey, coreFiles, errTypes, spravErrTypes
from core.errors import CustomError, SpravError


class ExtractionWorker:
    def __init__(self, process_event_handler=lambda x: x):
        self.emit_process_event = process_event_handler

    def run_contol(self, sprav_holder=None, db_file=None):
        contr = DataControl(sprav_holder, db_file, coreFiles.tempDB_path)
        try:
            errors = contr.run_field_control()
        except Exception as err:
            if isinstance(err, CustomError):
                raise err
            raise CustomError(errTypes.control_failed, str(err))
        else:
            return errors

    def run_convertation(self, sprav_holder=None, settings_holder=None):
        print(settings_holder)
