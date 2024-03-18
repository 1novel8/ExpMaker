import time

from locales import titleLocales
from ui.components import TableLabel, TableWidget


class LogTable(TableWidget):
    def __init__(self, parent=None):
        self.headers = titleLocales.log_table_head
        TableWidget.__init__(self, parent=parent, headers=self.headers, with_clear=True)

    def add_row(self, log_msg, time_label=None):
        if not time_label:
            time_label = time.strftime(u"%H:%M:%S  \n%d.%m.%y")
        super().add_representation_row(time_label, with_span=False)
        row_count = super().get_row_count()
        self.table.setCellWidget(row_count - 1, 1, TableLabel(log_msg))
