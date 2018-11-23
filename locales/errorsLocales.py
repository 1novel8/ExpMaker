#!/usr/bin/env python
# -*- coding: utf-8 -*-


class AppErrorsLocales:
    empty_crostab = 'Отсутствуют данные для дальнейшей обработки. Не заполнена таблица crostab'


class ControlErrorsLocales:
    empty_crostab = 'Отсутствуют данные для дальнейшей обработки. Не заполнена таблица crostab'
    empty_tables = 'Отсутствуют таблицы: %s'
    empty_table_data = 'Таблицы должны быть заполнены: %s'
    warning_no_pref = 'В таблице SOATO найдены строки с незаполненными значениями поля Pref и не будут учтены: %s'
    field_control_failed = 'Не пройден контроль наличия и соответствия типов полей'
    lost_field_msg = '\nВ таблице %s отсутствуют либо не соответствуют типу поля:'
    lost_fields_msg = '\nВ таблице %s отсутствует либо не соответствует типу поле:'
    wrong_session = 'Загруженный файл содержит некорректные данные'
    failed_to_save_session = 'Не удалось сохранить выбранный файл. \n Возможно он поврежден.'
    loaded_sprav_not_valid = 'Загруженный файл не является валидным.'
    spr_default_io_error = 'Ошибка при загрузке файла справочников. Провеpьте наличие файла DefaultSpr.pkl '
    spr_io_error = 'Ошибка при загрузке файла справочников. Возможно файл не содержит необходимой информации'
    spr_err_in_data = 'Загружаемый файл содержит некорректные данные'

    def get_lost_fields(self, tab, failed_fields):
        msg = self.lost_fields_msg % tab if len(failed_fields) > 1 else self.lost_field_msg % tab
        for f in failed_fields:
            if isinstance(f, (tuple, list)):
                f = f[0] + ' --> требуемый тип данных: ' + ' или '.join(f[1])
            msg += u'\n%s' % f
        return msg
