# coding=utf-8


class WidgetTitles(object):
    main_name = u'Просмотрщик кадастровой оценки'
    base_mdb_file_lbl = u'Выберите базу данных .mdb в качестве источника информации'
    choose_raion_lbl = u'Населенный пункт'
    choose_land_lbl = u'Рабочий участок'
    choose_src_mdb = u'Выберите .mdb базу данных в качестве источника данных по области'
    choose_table_lbl = u'Выходная форма'
    btn_run = u'Сформировать .xls файл'
    tooltip_run = u'Будет произведена выгрузка данных в соответствии с заложенными в программу формами Excel'


class ErrorTitles(object):
    no_css = u'Css стили не применены'
    no_src_mdb = u'Не задан путь к .mdb базе данных'

    has_error = u'Something went wrong'
    collecting_data_failed = u'Получение данных для отображения завершилось ошибкой.'
    options_error = u'Ошибка при загрузке исходных параметров'


    insert_error = u'Слияние завершено. Некоторые insert операции завершились с ошибкой. Проверьте соответствие типов данных. \n\n'
    has_failed_dbfs = u'Слияние завершено. Некоторые dbf файлы не удалось загрузить.\n\n'


class StatusTitles(object):
    ready = u'Готов к выполнению новой задачи'
    collecting_data_running = u'Производится обработка данных'



class MessageTitles(object):
    success = u'Операция успешно завершена'
    successfully_collected = u'Данные успешно загружены'
