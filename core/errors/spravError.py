from constants import spravErrTypes as errTypes
from locales import customErrors


class SpravError(Exception):
    def __init__(self, err_type, *args):
        if err_type not in errTypes.enum:
            err_type = errTypes.unexpected
        err_head = 'Ошибка в справочниках. \n'
        args_err = 'Переданы неверные аргументы. ' \
                   '\nПожалуйста зафиксируйте условия возникновения данной ошибки и обратитесь к разработчику.'
        errors = {
            errTypes.unexpected:
                lambda: args[0],
            errTypes.connection_failed:
                lambda: err_head + str(args[0]) if len(args) >= 1 else args_err,
            errTypes.changes_rejected:
                lambda: customErrors.spr_not_changed if args[0] else customErrors.spr_wrong_default,
            errTypes.no_db_conn: lambda: err_head + customErrors.no_db_conn % args[0],
            errTypes.empty_spr_tabs: lambda: err_head + customErrors.get_empty_spr_tabs_msg(args[0]),
            errTypes.empty_spr_fields: lambda: err_head + customErrors.get_empty_spr_fields_msg(args[0]),
            errTypes.failed_to_save: lambda: customErrors.failed_to_save_sprav,

            1: lambda: err_head + 'Не удалось выполнить запрос: < %s >. Проверьте корректность базы данных'
                       % str(args[0]) if len(args)>=1 else args_err,
            #errors[2] used when error occured in row, so [args] must contain table_name and row_name as first 2 parameters
            2: lambda: err_head + 'Проверьте строку %s в таблице %s. ' % (args[1], args[0]) if len(args) >= 2 else args_err,
            3: lambda: errors[2]() + args[2] if len(args) >= 3 else args_err,
            4: lambda: errors[2]() + 'Отсутствует соответствующее значение %s, на которое произведена ссылка.'
                       % args[2] if len(args) >= 3 else args_err,
            5: lambda: errors[2]() + 'Не указана ссылка на суммарную строку.' if len(args) >= 2 else args_err,
        }
        self.type = err_type
        self.message = str(errors[err_type]())
        super(SpravError, self).__init__(self.message)

    def empty_spr_tabs(tabs):
        _end = u'ет таблица' if len(tabs) < 2 else u'ют таблицы'
        _tabs = u', '.join(tabs)
        return u'''В выбранной базе данных отсутству%s:\n%s\n
    Для работы программы необходимо
    предоставить справочную информацию в полном объеме.''' % (_end, _tabs)
