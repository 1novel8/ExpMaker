from ui.components import TableWidget, TableLabel
from locales import titleLocales
import time


class LogTable(TableWidget):
    def __init__(self, parent=None):
        self.headers = titleLocales.log_table_head
        TableWidget.__init__(self, parent=parent, headers=self.headers, with_clear=True)

    def add_row(self, log_msg, time_label=None):
        if not time_label:
            time_label = time.strftime(u"%H:%M:%S  \n%d.%m.%y")
        super(LogTable, self).add_representation_row(time_label, with_span=False)
        row_count = super(LogTable, self).get_row_count()
        self.table.setCellWidget(row_count - 1, 1, TableLabel(log_msg))
