import pickle

from constants import appKey, coreFiles, errTypes, spravErrTypes
from core.errors import CustomError, SpravError
from core.extractors.initializer import CtrController
from core.settingsHolders.settingsHolder import SettingsHolder
from core.settingsHolders.spravHolder import SpravHolder
from locales import customErrors


class BaseWorker:
    def __init__(self, process_event_handler=lambda x: x):
        self.emit_process_event = process_event_handler

    @staticmethod
    def load_pkl_session(file_path=None):
        try:
            with open(file_path, "rb") as inp:
                dump_data = pickle.load(inp)
                inp.close()
            loading_password = dump_data["app_key"]
        except Exception as err:
            raise CustomError(errTypes.general, customErrors.wrong_session + err)
        else:
            if loading_password == appKey:
                return dump_data
            else:
                raise CustomError(errTypes.general, customErrors.wrong_session)

    @staticmethod
    def save_pkl_session(save_as: str, dump_data):
        try:
            dump_data["app_key"] = appKey
            with open(save_as, "wb") as output:
                pickle.dump(dump_data, output, 2)
            return save_as
        except Exception as err:
            print(err)
            raise CustomError(errTypes.general, customErrors.failed_to_save_session)

    def run_initial_db_contol(self, file_path: str):
        """
        Проходят проверки над базой
        """
        contr = CtrController(file_path, coreFiles.tempDB_path)
        # получение табиц, которые нужны, но не представлены
        not_found_tables = contr.get_not_found_tables()
        if len(not_found_tables) != 0:
            err_message = customErrors.empty_tables % "", "".join(not_found_tables)
            raise CustomError(errTypes.control_failed, err_message)
        # получить все пустые таблицы
        empty_tables = contr.get_empty_tables()
        if len(empty_tables) != 0:
            err_message = customErrors.empty_table_data % "", "".join(empty_tables)
            raise CustomError(errTypes.control_failed, err_message)
        # получение столбцов и их типов
        wrong_typed_fields = contr.validate_field_types()  # если что-то не совпадает
        if wrong_typed_fields:
            for tab, fields in wrong_typed_fields.items():
                err_message = customErrors.get_lost_fields(tab, fields)
                self.emit_process_event(
                    CustomError(errTypes.control_warning, err_message)
                )
            raise CustomError(errTypes.control_failed, customErrors.field_control_failed)
        # если есть записи с полем префикса (д. р-н. и тд) None
        empty_pref_ids = contr.is_empty_f_pref()
        if empty_pref_ids:
            err_message = customErrors.warning_no_pref % empty_pref_ids
            self.emit_process_event(
                    CustomError(errTypes.control_warning, err_message))
        # проверяем чтобы все объекты имели правильный SOATO
        wrong_pref_ids = contr.is_wrong_f_pref()
        if wrong_pref_ids:
            err_message = customErrors.warning_wrong_pref % wrong_pref_ids
            raise CustomError(errTypes.control_warning, err_message)
        # проверяем чтобы все объекты имели правильный SOATO
        wrong_pref_ids_sez = contr.is_wrong_f_pref_sez()
        if wrong_pref_ids_sez:
            err_message = customErrors.warning_wrong_pref_sez % wrong_pref_ids_sez
            raise CustomError(errTypes.control_warning, err_message)
        return "Ok"

    @staticmethod
    def load_mdb_sprav(sprav_holder=None, sprav_path=coreFiles.spr_default_path):
        try:
            sprav_holder.check_spr_db(sprav_path)
            sprav_data = sprav_holder.get_data_from_db()
            sprav_holder.set_changes(sprav_data, sprav_path)
        except SpravError as err:
            raise err
        except Exception as err:
            print(err)
            raise SpravError(spravErrTypes.unexpected, err)
        finally:
            sprav_holder.close_db_connection()

    @staticmethod
    def load_pkl_sprav(
            sprav_holder: SpravHolder = None,
            settings_holder: SettingsHolder = None,
            sprav_path: str = coreFiles.spr_default_path,
    ) -> None:
        """
        Загрузка справочника и настроек из .pkl
        """
        is_default = sprav_path == coreFiles.spr_default_path
        try:
            with open(sprav_path, "rb") as inp:
                loaded_data = pickle.load(inp)
                inp.close()
            if loaded_data["spravKey"] == appKey + "_sprav":
                sprav_holder.set_changes(loaded_data["sprav_data"], sprav_path)
                settings_holder.update_settings(loaded_data["settings_data"])
                settings_holder.set_default_active_cond(sprav_holder.select_conditions)
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

    @staticmethod
    def save_sprav(save_as=None, sprav_data=None, settings_data=None):
        if not save_as or not sprav_data or not settings_data:
            raise SpravError(spravErrTypes.failed_to_save, customErrors.failed_to_save_sprav)
        try:
            with open(save_as, "wb") as output:
                pickle.dump({
                    "sprav_data": sprav_data,
                    "settings_data": settings_data,
                    "spravKey": appKey + "_sprav",
                }, output, 2)
        except Exception as err:
            print("save error: ", err)
            raise SpravError(spravErrTypes.failed_to_save, customErrors.failed_to_save_sprav)

    def save_sprav_as_default(
        self,
        sprav_data=None,
        settings_data=None,
        sprav_holder: SpravHolder = None,
        settings_holder: SettingsHolder = None,
    ) -> None:
        self.save_sprav(save_as=coreFiles.spr_default_path, sprav_data=sprav_data, settings_data=settings_data)
        self.load_pkl_sprav(sprav_holder=sprav_holder, settings_holder=settings_holder)
