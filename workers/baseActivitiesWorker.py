import pickle
from constants import appKey, coreFiles, errTypes
from core.errors import CustomError
from core.extractors import CtrControl
from locales import controlErrors


class BaseWorker:
    def __init__(self, process_event_handler=lambda x: x):
        self.emit_process_event = process_event_handler


    def load_work_pkl(self, db_file_path, ):
        try:
            with open(db_file_path, 'rb') as inp:
                exp_data = pickle.load(inp)
                inp.close()
            loading_password = exp_data.pop()
        except Exception as err:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), ErrMessage.wrong_session + err.message)
        else:
            if loading_password == appKey:
                self.emit(QtCore.SIGNAL(u'session_loaded(PyQt_PyObject)'), exp_data)
            else:
                self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), ErrMessage.wrong_session)

    def save_work_pkl(self):
        try:
            with open(self.__file_path, u'wb') as output:
                pickle.dump(self.__args[0], output, 2)
            self.__args = []
            self.emit(QtCore.SIGNAL(u'successfully_saved(const QString&)'), Events.session_saved % self.__file_path)
        except:
            self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), ErrMessage.bad_session)

    # def load_work_db(self, db_file_path):
    #     err_message = self.run_initial_db_contol(db_file_path)
    #     result = {}
    #     if err_message:
    #         self.emit(QtCore.SIGNAL(u'error_occured(const QString&)'), message)
    #     return result

    def run_initial_db_contol(self, file_path):
        try:
            contr = CtrControl(file_path, coreFiles.tempDB_path)
            failed_tables = contr.contr_tables()
            if failed_tables:
                err_message = controlErrors.empty_tables % ', '.join(failed_tables)
                return CustomError(errTypes.control_failed, err_message)
            failed_tables = contr.is_tables_empty()
            if failed_tables:
                err_message = controlErrors.empty_table_data % ', '.join(failed_tables)
                return CustomError(errTypes.control_failed, err_message)
            failed_fields = contr.contr_field_types()
            if failed_fields:
                for tab, fields in failed_fields.items():
                    err_message = controlErrors.get_lost_fields(tab, fields)
                    self.emit_process_event(
                        CustomError(errTypes.control_warning, err_message))
                return CustomError(errTypes.control_failed, controlErrors.field_control_failed)
            empty_pref_ids = contr.is_empty_f_pref()
            if empty_pref_ids:
                err_message = controlErrors.warning_no_pref % empty_pref_ids
                self.emit_process_event(
                    CustomError(errTypes.control_warning, err_message))
                return CustomError(errTypes.control_failed, controlErrors.field_control_failed)
            return {'result': 'ok'}
        except Exception as err:
            return CustomError(errTypes.unexpected, err)


    def set_spr_changes(self, change_di):
        if self.s_h.set_parameters(change_di):
            self.current_sprav_dict = change_di
            if self.__op == 1:
                self.spr_path_info = u'Default'
            else:
                self.spr_path_info = self.__file_path
            self.emit(QtCore.SIGNAL(u'sprav_holder(PyQt_PyObject)'), self.s_h)
        else:
            if self.current_sprav_dict:
                self.s_h.set_parameters(self.current_sprav_dict)
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.sh_not_changed)
            else:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_wrong_default)

    def set_settings_changes(self, loaded_settings):
        self.emit(QtCore.SIGNAL(u'new_settings_loaded(PyQt_PyObject)'), loaded_settings)

    def load_pkl_op1_2(self):
        try:
            with open(self.__file_path, 'rb') as inp:
                loaded_data = pickle.load(inp)
                inp.close()
            loading_password = loaded_data[-1]
            if loading_password == u'Sprav':
                self.set_spr_changes(loaded_data[0])
                self.set_settings_changes(loaded_data[1])
            else:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_not_valid)
        except IOError:
            if self.__op == 1:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_default_io_error)
            else:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_io_error)
        except:
            # TODO: rename error message and add exceptions
            self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.spr_err_in_data)

    def load_mdb_op3(self):
        if self.control_spr_db():
            try:
                sprav_data = self.s_h.get_data_from_db(self.__file_path)
                sprav_data[u"create_time"] = time.strftime(u"%H:%M__%d.%m.%Y")
                self.set_spr_changes(sprav_data)
            except Sprav.SpravError as err:
                self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), unicode(err.message))

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

    def control_spr_db(self, full=True):
        sprav_contr = Sprav.SprControl(self.__file_path, full)
        if not sprav_contr.is_connected:
            self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.no_db_conn % self.__file_path)
            return False
        bad_tbls = sprav_contr.contr_tables()
        if bad_tbls:
            self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), ErrMessage.empty_spr_tabs(bad_tbls))
            return False
        bad_fields = sprav_contr.contr_field_types()
        if bad_fields:
            msg = u''
            for tbl, fails in bad_fields.items():
                msg += u'\n%s' % ErrMessage.lost_fields(tbl, fails)
            self.emit(QtCore.SIGNAL(u'spr_error_occured(const QString&)'), msg)
            return False
        else:
            # TODO: call exp structure control here. {f_num : not Null; Expa_f_str.f_num : LandCodes.NumberGRAF WHERE f_num is NUll
            return True