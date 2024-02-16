from constants import dbErrors

err_messages = {
    'failed': dbErrors.connection_failed,
    'query_stack': dbErrors.query_stack,
    'tmpl_empty': dbErrors.tmpl_empty,
    'err_create_file': dbErrors.failed_to_create_file,
    'shutil_err': dbErrors.shutil_copy_err,
    'create_t_fail': dbErrors.failed_to_create_table
}


class DbError(Exception):
    def __init__(self, err_type, *args):
        super(DbError, self).__init__(DbError.get_message_by_type(err_type, args))

    @staticmethod
    def get_message_by_type(err_type, args):
        # TODO: fill error types in constants
        fill_params = args if args else ''
        return err_messages[err_type] % fill_params
