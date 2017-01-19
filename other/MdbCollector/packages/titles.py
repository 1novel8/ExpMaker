# coding=utf-8


class WidgetTitles(object):
    dbfFilesSrc = u'Выберите источник данных с файлами dbf'
    l1_title = u'Выберите базу данных .mdb содержащую таблицы для экспорта данных'
    l2_title = u'Выберите путь к .dbf файлам'
    l3_title = u'Выберите путь для базы данных с результатами'
    main_name = 'CollectorBeta'
    choose_dbf_dir = u'Выберите директорию в которой расположены .dbf файлы'
    choose_src_mdb = u'Выбериту путь к файлу .mdb на основе которого будет произведен экспорт'
    choose_out_dir = u'Выбериту директорию в которую будет сохранен выходной файл'
    dbf_folder = u'Выберите путь к .dbf файлам'
    src_mdb_folder = u'Выберите базу данных .mdb'
    out_mdb_folder = u'Выберите путь для базы данных с результатами'
    btn_run = u'Слияние'
    tooltip_run = u'Обьединение данных из .dbf файлов в базу данных .mdb'


class ErrorTitles(object):
    no_css = 'No css'
    no_out_mdb = u'Не задан путь к .mdb файлу для выгрузки данных'
    no_src_mdb = u'Не задан путь к .mdb файлу для выгрузки данных'
    no_dbf_dir = u'Не задан путь к .dbf файлам'
    not_enough_data = u'Не заданы параметры необходимые для старта слияния'
    has_error = u'Something went wrong'
    collecting_failed = u'Объединение данных завершилось ошибкой.'
    insert_error = u'Слияние завершено. Некоторые insert операции завершились с ошибкой. Проверьте соответствие типов данных. \n\n'
    has_failed_dbfs = u'Слияние завершено. Некоторые dbf файлы не удалось загрузить.\n\n'

class StatusTitles(object):
    ready = u'Готов к выполнению новой задачи'
    collecting_running = u'Производится слияние данных'
class MessageTitles(object):
    success = u'Операция успешно завершена'
    successfully_collected = u'Данные успешно загружены в базу данных'
