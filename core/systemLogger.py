import logging


def create_logger(logger_id, path):
    log = logging.getLogger(logger_id)
    log.setLevel(logging.DEBUG)

    file_formatter = logging.Formatter(
        ('#%(levelname)-s, %(pathname)s, line %(lineno)d, [%(asctime)s]: '
         '%(message)s'), datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(('#%(levelname)-s, %(pathname)s, '
                                           'line %(lineno)d: %(message)s'))
    file_handler = logging.FileHandler(path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(console_formatter)
    log.addHandler(file_handler)
    log.addHandler(console_handler)


def get_logger(logger_id):
    return logging.getLogger(logger_id)


def log_error(err, message='', is_critical=False, logger_id='main'):
    logger = get_logger(logger_id)
    print(err)
    if is_critical:
        logger.critical('Critical Error: ' + err.__str__())
    else:
        logger.error('Error: ' + message + err.__str__())
