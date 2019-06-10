__author__ = 'Alex Konkov'


import pyodbc
from core.errors import DbError
from core import log_error


def catch_db_exception(func_runs_query):
    """
    Decorator for functions with connection to database
    decorator is decorated to take parameter self
    """
    def wrapper(self, *args, **kwargs):
        try:
            return func_runs_query(self, *args, **kwargs)
        except pyodbc.ProgrammingError:
            log_error(pyodbc.ProgrammingError)
            raise DbError('query_stack', args)
        except pyodbc.Error:
            log_error(pyodbc.ProgrammingError)
            raise DbError('failed', args)
        except Exception as err:
            log_error(err)
            raise err

    return wrapper


def try_make_conn(func_with_connect):
    """
    Decorator for functions with connection to database
    decorator is decorated to take parameter self
    """
    conn_attempt = {1: True}

    def wrapper(self,  *args, **kwargs):
        if self.get_dbc:
            conn_attempt[1] = True
            return func_with_connect(self, *args, **kwargs)
        elif conn_attempt[1]:
            conn_attempt[1] = False
            self.make_connection()
            return wrapper(self, *args, **kwargs)
        else:
            err = Exception('Database connection failed')
            log_error(err)
            raise err
    return wrapper
