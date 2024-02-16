from constants import coreFiles, errTypes
from core.errors import CustomError
from core.extractors import CtrConverter, DataControl


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
        select_condition = {}
        if isinstance(sprav_holder.select_conditions, list):
            for select_op in sprav_holder.select_conditions:
                if select_op['Id'] == settings_holder.conditions.active_cond:
                    select_condition = select_op
        try:
            converted_data = CtrConverter.convert(sprav_holder, coreFiles.tempDB_path, select_condition)
        except Exception as err:
            if isinstance(err, CustomError):
                raise err
            raise CustomError(errTypes.convert_failed, str(err))
        else:
            return converted_data
