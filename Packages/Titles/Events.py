#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Aleksei Konkov'

control_failed = u'Контроль данных завершен. Найдены ошибки.'
control_passed = u'Контроль завершен успешно, несоответствий не обнаружено. Можно приступить к конвертации данных.'
convert_failed = u'Конвертация данных завершена. Найдены несоответствия с таблицами BGDtoEKP…'
convert_passed = u'Данные успешно сконвертированы. Доступен расчет экспликаций.'
opened_file = u'Открыт файл %s'
db_has_data = u'В базе данных %s присутствуют данные, необходимые для расчета экспликации.\nЗапустите контроль данных для дальнейшей работы'
session_loaded = u'Загружен файл сессии %s'
session_saved = u'Сохранена сессия %s'

set_sprav_default = u'Установлены исходные справочные данные.'
run_control = u'Запущен контроль данных.'
run_convert = u'Запущено конвертирование данных.'

started_sv_exp_a =u'Запущен полный расчет экспликации А.'
started_s_exp_a =u'Запущен расчет экспликации А: \n%s'

run_exp_b =u'Запущен расчет Формы 22.зем.'
finished_exp_a_sv =u'Завершен расчет сводной экспликации А.'
finished_exp_a_s =u'Выборочный расчет экспликации А завершен успешно.'
finish_exp_b =u'Завершен расчет Формы 22.зем.'
exp_a_finished_with_err = u'Расчет экспликации А завершен с ошибкой'
exp_b_finished_with_err = u'Расчет экспликации B завершен с ошибкой'

spr_default_failed = u'Ошибка при загрузке справочных данных по умолчанию.'
set_previous_spr = u'Ошибка при обновлении справочных данных. Откат к предыдущим справочникам'
spr_saved = u"Сохранена текущая версия справочников"
load_sprav_success = u'Загрузка справочной информации завершена успешно'

def spr_info(date, _file):
    return u"""
Создан:
        %s

Загружен из:
        %s
""" % (date, _file)