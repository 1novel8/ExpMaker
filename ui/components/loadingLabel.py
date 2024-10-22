from PyQt5.QtWidgets import QLabel

from threads.loadingThread import LoadingThread
from ui.styles import loading_label


class LoadingLabel(QLabel):
    def __init__(self, parent=None, message="", hidden=True):
        QLabel.__init__(self, parent)
        self.setText(message)
        self.loading_message = message
        self.setStyleSheet(loading_label)
        self.setHidden(hidden)
        self.load_thr = LoadingThread()
        self.load_thr.tick_signal.connect(self._on_tick)

    def _on_tick(self, dots):
        self.setText(self.loading_message+dots)

    def start_loading(self, process_message):
        self.setHidden(False)
        self.loading_message = process_message
        self.setText(process_message)
        if not self.load_thr.isRunning():
            self.load_thr.start()

    def stop_loading(self):
        self.load_thr.terminate()
        self.setHidden(True)
