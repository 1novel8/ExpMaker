import pyodbc

from core import log_error
from core.errors import DbError


def catch_db_exception(wrapped_querying_func):
    """
    Decorator for methods responsible for database querying
    """
    def wrapper(self, *args, **kwargs):
        try:
            return wrapped_querying_func(self, *args, **kwargs)
        except pyodbc.ProgrammingError as db_error:
            log_error(db_error)
            raise DbError('query_stack', args)
        except pyodbc.Error as db_error:
            log_error(db_error)
            raise DbError('failed', args)
        except Exception as err:
            log_error(err)
            raise err

    return wrapper


def try_make_conn(decorated_func):
    """
    Decorator. Checks connection initialization
    """
    def wrapper(self,  *args, **kwargs):
        if self.get_dbc:
            self.conn_attempt_available = True
            return decorated_func(self, *args, **kwargs)
        elif self.conn_attempt_available:
            self.conn_attempt_available = False
            self.make_connection()
            return wrapper(self, *args, **kwargs)
        else:
            err = Exception('Database connection failed')
            log_error(err)
            raise err
    return wrapper
