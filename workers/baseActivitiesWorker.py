import pickle
from constants import appKey, coreFiles, errTypes, spravErrTypes
from core.errors import CustomError, SpravError
from core.extractors import CtrControl
from locales import customErrors


class BaseWorker:
    def __init__(self, process_event_handler=lambda x: x):
        self.emit_process_event = process_event_handler

    def load_pkl_session(self, db_file_path):
        try:
            with open(db_file_path, 'rb') as inp:
                exp_data = pickle.load(inp)
                inp.close()
            loading_password = exp_data.pop()
        except Exception as err:
            raise CustomError(errTypes.general, customErrors.wrong_session + err)
        else:
            if loading_password == appKey:
                return exp_data
            else:
                raise CustomError(errTypes.general, customErrors.wrong_session)

    def save_work_pkl(self, save_as, dump_data):
        try:
            with open(save_as, u'wb') as output:
                pickle.dump(dump_data, output, 2)
            return save_as
        except Exception as err:
            print(err)
            raise CustomError(errTypes.general, customErrors.failed_to_save_session)

    def run_initial_db_contol(self, file_path):
        contr = CtrControl(file_path, coreFiles.tempDB_path)
        failed_tables = contr.contr_tables()
        if failed_tables:
            err_message = customErrors.empty_tables % ', '.join(failed_tables)
            raise CustomError(errTypes.control_failed, err_message)
        failed_tables = contr.is_tables_empty()
        if failed_tables:
            err_message = customErrors.empty_table_data % ', '.join(failed_tables)
            raise CustomError(errTypes.control_failed, err_message)
        failed_fields = contr.contr_field_types()
        if failed_fields:
            for tab, fields in failed_fields.items():
                err_message = customErrors.get_lost_fields(tab, fields)
                self.emit_process_event(
                    CustomError(errTypes.control_warning, err_message))
            raise CustomError(errTypes.control_failed, customErrors.field_control_failed)
        empty_pref_ids = contr.is_empty_f_pref()
        if empty_pref_ids:
            err_message = customErrors.warning_no_pref % empty_pref_ids
            self.emit_process_event(
                CustomError(errTypes.control_warning, err_message))
            raise CustomError(errTypes.control_failed, customErrors.field_control_failed)
        return 'Ok'

    def load_mdb_sprav(self, sprav_holder=None, sprav_path=coreFiles.spr_default_path):
        db_conn = sprav_holder.check_spr_db(sprav_path)
        if db_conn:
            try:
                sprav_data = sprav_holder.get_data_from_db()
                sprav_holder.set_changes(sprav_data, sprav_path)
            except SpravError as err:
                raise err
            except Exception as err:
                print(err)
                raise SpravError(spravErrTypes.unexpected, err)
            finally:
                sprav_holder.close_db_connection()

    def set_settings_changes(self, loaded_settings):
        self.emit(QtCore.SIGNAL(u'new_settings_loaded(PyQt_PyObject)'), loaded_settings)

    def load_pkl_sprav(self, sprav_holder=None, sprav_path=coreFiles.spr_default_path):
        is_default = sprav_path == coreFiles.spr_default_path
        try:
            with open(sprav_path, 'rb') as inp:
                loaded_data = pickle.load(inp)
                inp.close()
            if loaded_data['spravKey'] == appKey + '_sprav':




                return loaded_data
            else:
                raise CustomError(errTypes.control_failed, customErrors.loaded_sprav_not_valid)
        except IOError:
            if is_default:
                raise CustomError(errTypes.control_failed, customErrors.spr_default_io_error)
            else:
                raise CustomError(errTypes.control_failed, customErrors.spr_io_error)
        except Exception as err:
            print(err)
            raise CustomError(errTypes.control_failed, customErrors.spr_err_in_data)

    def save_pkl_op4(self):
        if self.__file_path:
            if self.__file_path[-4:] != u'.pkl':
                self.__file_path += u'.pkl'
            try:
                with open(self.__file_path, u'wb') as output:
                    pickle.dump([self.current_sprav_dict, self.settings_dict, u"Sprav"], output, 2)
                    self.emit(QtCore.SIGNAL(u'successfully_saved(const QString&)'), Events.spr_saved)
            except:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_not_saved)
