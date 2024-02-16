import time
from os import path

from constants import expActions
from core.expBuilders import ExpAMaker, ExpF22Maker, balanceMaker
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
        self.export_selected_to_xl(
            matrix, settings_holder.xls, out_exp_file,
            f22_ind=exp_provider.full_obj_name,
            obj_name=exp_provider.obj_name)

    def create_exp_a_sv(self, exp_maker=None, sprav_holder=None, settings_holder=None, out_exp_file=None):
        group_sv_by = settings_holder.conditions.groupping_by
        with_balance = settings_holder.balance.include_a_sv_balance
        is_xls_mode = True
        if group_sv_by == 'cc':
            sv_data = exp_maker.calc_all_exps_by_ss(settings_holder.rnd)
        # elif group_sv_by == 'np':
        #     sv_data = self.expsA.calc_all_exps_by_np(self.rnd_settings)
        else:
            try:
                sv_data = exp_maker.calc_all_exps_by_np(settings_holder.rnd)
            except Exception as err:
                print(err)
                raise err

        if exp_maker.errors_occured:
            for key in exp_maker.errors_occured:
                # msg = ErrMessage.expa_errors[key] % errs_occured[key]
                msg = 'not yet implemented'
                self.__emit_process_changes(expActions.EXP_ERROR, msg)
            # raise Exception(expActions.EXP_ERROR)
        if with_balance:
            self.__emit_process_changes(expActions.MAKE_BALANCE)
            balanceMaker.run_asv_balancer(sv_data, sprav_holder.expa_f_str, sprav_holder.expa_r_str)
        self.__emit_process_changes(expActions.EXPORT_EXP)
        matrix = exp_maker.prepare_sv_matrix(sv_data, for_xls=is_xls_mode)
        matrix_total = exp_maker.prepare_sv_matrix(sv_data, for_xls=is_xls_mode)
        if is_xls_mode:
            xl_s = settings_holder.xls
            out_settings = {
                'start_f': xl_s.a_sv_l,
                'start_r': xl_s.a_sv_n,
                'start_r_total': xl_s.a_sv_n,
                'sh_name': xl_s.a_sv_sh_name,
                'is_xls_start': xl_s.is_xls_start
            }
            print(out_settings)
            self.export_matr_to_xl(
                matrix,
                self.gen_xl_out_file('FV_svod', out_exp_file),
                xl_s.a_sv_path,
                out_settings
            )
        else:
            save_as_table = 'ExpA_%s' % time.strftime('%d\%m\%Y_%H:%M')
            self.export_to_mdb(matrix, out_exp_file, save_as_table, start_when_ready=True)

    # формирование матрицы В
    def create_exp_b(
            self,
            rows_data,
            sprav_holder=None,
            settings_holder=None,
            out_exp_file=None
    ):  # (self, rows_data, sprav_holder=None, settings_holder=None, out_exp_file=None):
        with_balance = settings_holder.balance.include_b_balance
        is_xls_mode = True
        exp_maker = ExpF22Maker(rows_data, sprav_holder)
        exp_dict = exp_maker.create_exp_dict(settings_holder.rnd)

        if with_balance:
            print("---------экспликация с Балансировкой----------------")
            self.__emit_process_changes(expActions.MAKE_BALANCE)
            balanceMaker.run_b_balancer(exp_dict,
                                        sprav_holder.expb_f_str,
                                        sprav_holder.expb_r_str,
                                        settings_holder.rnd.b_accuracy)
        self.__emit_process_changes(expActions.EXPORT_EXP)
        matrix = exp_maker.prepare_matrix(exp_dict, sprav_holder)
        matrix_total = exp_maker.prepare_matrix_total(exp_dict, sprav_holder)
        print("\n---------------------матрица данных --------------------")
        print(matrix)
        print("\n------ матрица итогов   --------")
        print(matrix_total)
        if is_xls_mode:
            xls = settings_holder.xls
            out_settings = {
                'start_f': xls.b_l,
                'start_r': xls.b_n,
                'start_r_total': xls.b_n + 42,
                'sh_name': xls.b_sh_name,
                'is_xls_start': xls.is_xls_start,
            }
            self.export_matr_to_xl_F22(
                matrix,
                matrix_total,
                self.gen_xl_out_file('F22_I_', out_exp_file),
                xls.b_path,
                out_settings
            )

        else:
            save_as_table = 'ExpF22_%s' % time.strftime('%d\%m\%Y_%H:%M')
            self.export_to_mdb(matrix, out_exp_file, save_as_table, start_when_ready=True)

    @staticmethod
    def export_selected_to_xl(matrix, out_settings, out_db_file, f22_ind="", obj_name=""):
        try:
            out_dir = path.dirname(out_db_file) + '\\FA_%s_xlsx_files' % path.basename(out_db_file)
            save_as = '%s\\%s.xlsx' % (out_dir, f22_ind)
            exporter = XlExporter(save_as, out_settings.a_path)
            exporter.exp_single_fa(matrix, obj_name, **out_settings.__dict__)
        except XlsError as err:
            print(err)
            raise err

    @staticmethod
    def gen_xl_out_file(prefix, out_db_file):
        exl_file_name = '%s_%s_%s.xlsx' % (prefix, path.basename(out_db_file), time.strftime('%d-%m-%Y'))
        return path.join(path.dirname(out_db_file), exl_file_name)

    @staticmethod
    def export_matr_to_xl(matrix, out_db_file, template_path, out_settings):
        try:
            exporter = XlExporter(out_db_file, template_path)
            exporter.export_matrix(matrix, **out_settings)
            if out_settings['is_xls_start']:
                exporter.start_excel()
        except XlsError as err:
            print(err)
            raise err

    @staticmethod
    def export_matr_to_xl_F22(matrix, matrix_total, out_db_file, template_path, out_settings):
        try:
            exporter = XlExporter(out_db_file, template_path)
            exporter.export_matrix_F22(matrix, matrix_total, **out_settings)
            if out_settings['is_xls_start']:
                exporter.start_excel()
        except XlsError as err:
            print(err)
            raise err

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
