# from constants import appKey, coreFiles, errTypes, spravErrTypes
# from locales import customErrors
import time
from os import path
from constants import expActions
from core.expBuilders import ExpAMaker, balanceMaker
from core.exporters import DbExporter, XlExporter, XlsError


class ExplicationWorker:
    def __init__(self, process_event_handler=lambda action_meta: action_meta):
        self.__emit_process_event = process_event_handler

    def __emit_process_changes(self, next_action, message=""):
        self.__emit_process_event({
            "action": next_action,
            "message": message,
        })

    @staticmethod
    def init_exp_a_maker(rows=None, users=None, soato=None, sprav_holder=None, options=None):
        exp_maker = ExpAMaker(rows, users, soato, sprav_holder, options)
        exp_maker.make_exp_tree()
        return exp_maker

    def create_exp_a(self, exp_provider=None, sprav_holder=None, settings_holder=None, out_exp_file=None):
        with_balance = settings_holder.balance.include_a_sv_balance
        exp_provider.add_data(sprav_holder)
        counted_exp = exp_provider.round_expl_data(settings_holder.rnd)
        if with_balance:
            self.__emit_process_changes(expActions.MAKE_BALANCE)
            balanceMaker.run_asv_balancer(counted_exp, sprav_holder.expa_f_str, sprav_holder.expa_r_str)
        self.__emit_process_changes(expActions.EXPORT_EXP)
        matrix = exp_provider.prepare_out_matrix(counted_exp, sprav_holder)
        self.export_s_to_xl(matrix, settings_holder.xls, out_exp_file, 
                            f22_ind=exp_provider.f22_ind,  obj_name=exp_provider.obj_name)

    def create_exp_a_sv(self, exp_maker=None, sprav_holder=None, settings_holder=None, out_exp_file=None):
        group_sv_by = settings_holder.conditions.groupping_by
        with_balance = settings_holder.balance.include_a_sv_balance
        is_xls_mode = True
        if group_sv_by == 'cc':
            sv_data = exp_maker.calc_all_exps_by_ss(settings_holder.rnd)
        # elif group_sv_by == 'np':
        #     sv_data = self.expsA.calc_all_exps_by_np(self.rnd_settings)
        else:
            sv_data = exp_maker.calc_all_exps_by_np(settings_holder.rnd)
        if exp_maker.errors_occured:
            for key in exp_maker.errors_occured:
                # msg = ErrMessage.expa_errors[key] % errs_occured[key]
                # TODO:  handle error
                msg = 'not yet implemented'
                self.__emit_process_changes(expActions.EXP_ERROR, msg)
            raise Exception(expActions.EXP_ERROR)
        if with_balance:
            self.__emit_process_changes(expActions.MAKE_BALANCE)
            balanceMaker.run_asv_balancer(sv_data, sprav_holder.expa_f_str, sprav_holder.expa_r_str)
        self.__emit_process_changes(expActions.EXPORT_EXP)
        matrix = exp_maker.prepare_sv_matrix(sv_data, for_xls=is_xls_mode)
        if is_xls_mode:
            self.export_sv_to_xl(matrix, settings_holder.xls, out_exp_file)
        else:
            save_as_table = 'ExpA_%s' % time.strftime('%d\%m\%Y_%H:%M')
            self.export_to_mdb(matrix, out_exp_file, save_as_table, start_when_ready=True)

    def create_exp_b(self, rows_data=(), sprav_holder=None, settings_holder=None):
        with_balance = settings_holder.balance.include_a_sv_balance
        if with_balance:
            self.__emit_process_event(expActions.MAKE_BALANCE)
            balanceMaker.run_asv_balancer([], sprav_holder.expa_f_str, sprav_holder.expa_r_str)
        self.__emit_process_event(expActions.EXPORT_EXP)

    @staticmethod
    def export_s_to_xl(matrix, out_settings, out_db_file, f22_ind="", obj_name=""):
        try:
            out_dir = path.dirname(out_db_file) + '\\%s_xlsx_files' % path.basename(out_db_file)[4:-4]
            save_as = '%s\\%s.xlsx' % (out_dir, f22_ind)
            exporter = XlExporter(save_as, out_settings.a_s_path)
            exporter.exp_single_fa(matrix, obj_name, **out_settings.__dict__)
        except XlsError as err:
            print(err)
            raise err
            # self.emit(QtCore.SIGNAL('error_occured(const QString&)'), ErrMessage.xl_io_error[err.err_type](err.file_name))

    @staticmethod
    def export_sv_to_xl(matrix, out_settings, out_db_file):
        exl_file_name = 'fA_%s_%s.xlsx' % (path.basename(out_db_file)[4:-4], time.strftime('%d-%m-%Y'))
        exl_file_path = path.join(path.dirname(out_db_file), exl_file_name)
        try:
            exporter = XlExporter(exl_file_path, out_settings.a_sv_path)
            exporter.export_matrix(matrix, out_settings.a_sv_l, out_settings.a_sv_n,
                                   sh_name=out_settings.a_sv_sh_name)
            if out_settings.is_xls_start:
                exporter.start_excel()
        except XlsError as err:
            print(err)
            raise err
            # self.emit(QtCore.SIGNAL('error_occured(const QString&)'), ErrMessage.xl_io_error[err.err_type](err.file_name))

    @staticmethod
    def export_to_mdb(matrix, out_file, save_as_table=None, start_when_ready=False):
        fields = ['f_' + f for f in matrix[0]]
        f_str = {fields[0]: 'TEXT(8)', fields[1]: 'TEXT(150)'}
        for f in fields[2:]:
            f_str[f] = 'DOUBLE NULL'
        export_db = DbExporter(out_file)
        export_db.create_table(save_as_table, f_str, fields)
        export_db.run_export(save_as_table, matrix[1:], fields)
        if start_when_ready:
            export_db.run_db()

