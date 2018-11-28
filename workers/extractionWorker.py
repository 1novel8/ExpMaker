import pickle
from constants import appKey, coreFiles, errTypes, spravErrTypes
from core.errors import CustomError, SpravError
from core.extractors import CtrControl
from locales import customErrors


class ExtractionWorker:
    def __init__(self, process_event_handler=lambda x: x):
        self.emit_process_event = process_event_handler

    def run_contol(self, sprav_holder=None, settings_holder=None):
        print(sprav_holder)

    def run_convertation(self, sprav_holder=None, settings_holder=None):
        print(settings_holder)