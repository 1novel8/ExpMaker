
class CustomErrorTypes:
    unexpected = 'unexpected'
    control_failed = 'control failed'
    control_warning = 'control warning'
    general = 'general'
    types_enum = [general, control_warning, unexpected, control_failed]


class SpravErrorTypes:
    unexpected = 'unexpected'
    connection_failed = 'failed to connect'
    changes_rejected = 'changes rejected'
    no_db_conn = 'no db connection'
    empty_spr_tabs = 'empty sprav tables'
    empty_spr_fields = 'empty sprav fields'
    control_warning = 'control warning'
    enum = [connection_failed, unexpected, control_warning, changes_rejected, no_db_conn, empty_spr_tabs, empty_spr_fields]
