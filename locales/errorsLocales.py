#!/usr/bin/env python
# -*- coding: utf-8 -*-


class AppErrorsLocales:
    empty_crostab = "Отсутствуют данные для дальнейшей обработки. Не заполнена таблица crostab"


class CustomErrorsLocales:
    empty_crostab = "Отсутствуют данные для дальнейшей обработки. Не заполнена таблица crostab"
    empty_tables = "Отсутствуют таблицы: %s"
    empty_table_data = "Таблицы должны быть заполнены: %s"
    warning_no_pref = "В таблице SOATO найдены строки с незаполненными значениями поля Pref и не будут учтены: %s"
    field_control_failed = "Не пройден контроль наличия и соответствия типов полей"
    lost_field_msg = "\nВ таблице %s отсутствуют либо не соответствуют типу поля:"
    lost_fields_msg = "\nВ таблице %s отсутствует либо не соответствует типу поле:"
    wrong_session = "Загруженный файл содержит некорректные данные"
    failed_to_save_session = "Не удалось сохранить выбранный файл. \n Возможно он поврежден."
    loaded_sprav_not_valid = "Загруженный файл не является валидным."
    spr_default_io_error = "Ошибка при загрузке данных справочников. Провеpьте наличие файла DefaultSpr.pkl "
    spr_io_error = "Ошибка при загрузке данных справочников. Загружаемый файл не содержит необходимой информации"
    spr_err_in_data = "Не удалось загрузить справочники. Загружаемый файл содержит невалидные или устаревшие данные"
    spr_not_changed = "Ошибка при попытке обновления справочника. Будет использоваться предыдущая версия"
    no_db_conn = "Не удалось подключиться к базе данных %s"
    spr_wrong_default = "Не удалось загрузить справочные и конфигурационные данные.\n" \
                        "Необходимо выбрать корректный источник исходных данных"

    def get_empty_spr_tabs_msg(self, tabs):
        _end = 'ет таблица' if len(tabs) < 2 else 'ют таблицы'
        _tabs = ', '.join(tabs)
        return '''В выбранной базе данных отсутству%s:\n%s\n
    Для работы программы необходимо
    предоставить справочную информацию в полном объеме.''' % (_end, _tabs)

    def get_empty_spr_fields_msg(self, fields_items):
        res = ''
        for tbl, fails in fields_items:
            if len(fails) > 1:
                msg = '\nВ таблице %s отсутствуют либо не соответствуют типу поля:' % tbl
            else:
                msg = '\nВ таблице %s отсутствует либо не соответствует типу поле:' % tbl
            for f in fails:
                if isinstance(f, (tuple, list)):
                    f = f[0] + ' --> требуемый тип данных: ' + ' или '.join(f[1])
                msg += '\n%s' % f
            res += msg
        return res

    def get_lost_fields(self, tab, failed_fields):
        msg = self.lost_fields_msg % tab if len(failed_fields) > 1 else self.lost_field_msg % tab
        for f in failed_fields:
            if isinstance(f, (tuple, list)):
                f = f[0] + "\" --> требуемый тип данных: \"" + "\" или \"".join(f[1])
            msg += u"\n%s" % f
        return msg
