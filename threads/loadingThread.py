from PyQt5.QtCore import QThread, pyqtSignal


class LoadingThread(QThread):
    tick_signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent=None, tick_handler=lambda x:x):
        super(LoadingThread, self).__init__(parent)
        self.tick_signal.connect(tick_handler)

    def run(self):
        dots = [" ",]*4
        count = 0
        is_dot = True
        while True:
            if count == len(dots):
                count = 0
                is_dot = not is_dot
            self.tick_signal.emit(" ".join(dots))
            self.msleep(300)
            if is_dot:
                dots[count] = "."
            else:
                dots[count] = " "
            count += 1