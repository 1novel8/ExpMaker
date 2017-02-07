# coding=utf-8


class WidgetTitles(object):
    main_name = u'Загрузчик кадастровой оценки'
    base_mdb_file_lbl = u'Выберите базу данных .mdb в качестве источника информации'
    choose_out_dir = u'Выберите путь для экспорта...'
    choose_raion_lbl = u'Наименование района'
    choose_land_lbl = u'Наименование землепользователя'
    choose_src_mdb = u'Выберите .mdb базу данных в качестве источника данных по области'
    choose_table_lbl = u'Выходные таблицы'
    btn_run = u'Сформировать .xls файл'
    tooltip_run = u'Будет произведена выгрузка данных в соответствии с заложенными в программу формами Excel'
    src_mdb_folder = u'Выберите источник данных....'
    choose_out_dir_lbl = u'Выберите директорию для экспорта таблиц Excel'

class ErrorTitles(object):
    no_css = u'Css стили не применены'
    no_src_mdb = u'Не задан путь к .mdb базе данных'
    wrong_path = u'Не верно задан путь к файлу...'
    has_error = u'Произошла ошибка...'
    collecting_data_failed = u'Получение данных для отображения завершилось ошибкой.'
    options_error = u'Ошибка при загрузке исходных параметров'
    warning = u'Предупреждение'
    no_out_xls = u'Укажите путь для экспорта файлов [out_DD-MM-YYYY].xlsx'
    src_mdb_connection_failed = u'Не удалось подключиться к источнику данных Base_db.mdb'
    insert_error = u'Слияние завершено. Некоторые insert операции завершились с ошибкой. Проверьте соответствие типов данных. \n\n'
    has_failed_dbfs = u'Слияние завершено. Некоторые dbf файлы не удалось загрузить.\n\n'


class StatusTitles(object):
    ready = u'Готов к выполнению новой задачи'
    collecting_data_running = u'Производится обработка данных'
    redefining_running = u'Производится выгрузка данных'


class MessageTitles(object):
    success = u'Операция успешно завершена'
    successfully_collected = u'Данные успешно загружены'
