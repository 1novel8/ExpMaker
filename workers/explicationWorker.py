import pickle
from constants import appKey, coreFiles, errTypes, spravErrTypes
from core.errors import CustomError, SpravError
from core.extractors import CtrControl
from locales import customErrors
from core.expBuilders import ExpAMaker


class ExplicationWorker:
    def __init__(self, process_event_handler=lambda x: x):
        self.emit_process_event = process_event_handler

    def init_exp_a_maker(self, rows=None, users=None, soato=None, sprav_holder=None, options=None):
        exp_maker = ExpAMaker(rows, users, soato, sprav_holder, options)
        return exp_maker

    def run_exp_a(self, sprav_holder=None, settings_holder=None):
        print(sprav_holder)

    def run_exp_a_sv(self, sprav_holder=None, settings_holder=None):
        print(settings_holder)

    def run_exp_b(self, sprav_holder=None, settings_holder=None):
        print(settings_holder)
