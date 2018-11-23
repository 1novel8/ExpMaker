import pickle
from constants import appKey, coreFiles, errTypes
from core.errors import CustomError
from core.extractors import CtrControl
from locales import controlErrors


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
            raise CustomError(errTypes.general, controlErrors.wrong_session + err)
        else:
            if loading_password == appKey:
                return exp_data
            else:
                raise CustomError(errTypes.general, controlErrors.wrong_session)

    def save_work_pkl(self, save_as, dump_data):
        try:
            with open(save_as, u'wb') as output:
                pickle.dump(dump_data, output, 2)
            return save_as
        except Exception as err:
            print(err)
            raise CustomError(errTypes.general, controlErrors.failed_to_save_session)

    def run_initial_db_contol(self, file_path):
        contr = CtrControl(file_path, coreFiles.tempDB_path)
        failed_tables = contr.contr_tables()
        if failed_tables:
            err_message = controlErrors.empty_tables % ', '.join(failed_tables)
            raise CustomError(errTypes.control_failed, err_message)
        failed_tables = contr.is_tables_empty()
        if failed_tables:
            err_message = controlErrors.empty_table_data % ', '.join(failed_tables)
            raise CustomError(errTypes.control_failed, err_message)
        failed_fields = contr.contr_field_types()
        if failed_fields:
            for tab, fields in failed_fields.items():
                err_message = controlErrors.get_lost_fields(tab, fields)
                self.emit_process_event(
                    CustomError(errTypes.control_warning, err_message))
            raise CustomError(errTypes.control_failed, controlErrors.field_control_failed)
        empty_pref_ids = contr.is_empty_f_pref()
        if empty_pref_ids:
            err_message = controlErrors.warning_no_pref % empty_pref_ids
            self.emit_process_event(
                CustomError(errTypes.control_warning, err_message))
            raise CustomError(errTypes.control_failed, controlErrors.field_control_failed)
        return 'Ok'

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

    def load_pkl_sprav(self, sprav_path=coreFiles.spr_default_path):
        is_default = sprav_path == coreFiles.spr_default_path
        try:
            with open(sprav_path, 'rb') as inp:
                loaded_data = pickle.load(inp)
                inp.close()
            if loaded_data['spravKey'] == appKey + '_sprav':
                return loaded_data
            else:
                raise CustomError(errTypes.control_failed, controlErrors.loaded_sprav_not_valid)
        except IOError:
            if is_default:
                raise CustomError(errTypes.control_failed, controlErrors.spr_default_io_error)
            else:
                raise CustomError(errTypes.control_failed, controlErrors.spr_io_error)
        except Exception as err:
            raise CustomError(errTypes.control_failed, controlErrors.spr_err_in_data)

    def load_mdb_sprav(self, sprav_path, sprav_holder):
        if self.control_spr_db():
            try:
                sprav_data = sprav_holder.get_data_from_db(sprav_path)
                sprav_data['create_time'] = time.strftime(u"%H:%M__%d.%m.%Y")
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