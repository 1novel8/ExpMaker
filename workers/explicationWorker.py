import pickle
from constants import appKey, coreFiles, errTypes, spravErrTypes
from core.errors import CustomError, SpravError
from core.extractors import CtrControl
from locales import customErrors
from constants import expActions
from core.expBuilders import ExpAMaker, balanceMaker

class ExplicationWorker:
    def __init__(self, process_event_handler=lambda x: x):
        self.emit_process_event = process_event_handler

    @staticmethod
    def init_exp_a_maker(rows=None, users=None, soato=None, sprav_holder=None, options=None):
        exp_maker = ExpAMaker(rows, users, soato, sprav_holder, options)
        exp_maker.make_exp_tree()
        return exp_maker

    def run_exp_a(self, sprav_holder=None, settings_holder=None, exp_data=None):
        with_balance = settings_holder.balance.include_a_sv_balance
        if with_balance:
            self.emit_process_event(expActions.MAKE_BALANCE)
            balanceMaker.run_asv_balancer([], sprav_holder.expa_f_str, sprav_holder.expa_r_str)
        self.emit_process_event(expActions.EXPORT_EXP)

    def run_exp_a_sv(self, sprav_holder=None, settings_holder=None, exp_data=None):
        group_sv_by = settings_holder.conditions.groupping_by
        with_balance = settings_holder.balance.include_a_sv_balance

        if with_balance:
            self.emit_process_event(expActions.MAKE_BALANCE)
            balanceMaker.run_asv_balancer([], sprav_holder.expa_f_str, sprav_holder.expa_r_str)
        self.emit_process_event(expActions.EXPORT_EXP)

        print(settings_holder)

    def run_exp_b(self, sprav_holder=None, settings_holder=None, exp_data=None):

        with_balance = settings_holder.balance.include_a_sv_balance
        if with_balance:
            self.emit_process_event(expActions.MAKE_BALANCE)
            balanceMaker.run_asv_balancer([], sprav_holder.expa_f_str, sprav_holder.expa_r_str)
        self.emit_process_event(expActions.EXPORT_EXP)

    def balance_exp(self):
        pass


