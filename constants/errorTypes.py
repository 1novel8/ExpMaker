class CustomErrorTypes:
    unexpected = 'unexpected'
    control_failed = 'control failed'
    control_warning = 'control warning'
    convert_failed = 'convert failed'
    convert_warning = 'convert warning'
    general = 'general'
    types_enum = [general, control_warning, unexpected, control_failed, convert_failed, convert_warning]


class SpravErrorTypes:
    unexpected = 'unexpected'
    connection_failed = 'failed to connect'
    changes_rejected = 'changes rejected'
    no_db_conn = 'no db connection'
    empty_spr_tabs = 'empty sprav tables'
    empty_spr_fields = 'empty sprav fields'
    control_warning = 'control warning'
    failed_to_save = 'failed to save'
    enum = [connection_failed, unexpected, control_warning, changes_rejected, no_db_conn,
            empty_spr_tabs, empty_spr_fields, failed_to_save]
