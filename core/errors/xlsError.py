
class XlsError(Exception):
    def __init__(self, err_type, *args):
        self.type = err_type
        self.message = self.get_err_message(err_type, args)
        super(Exception, self).__init__(self.message)

    @staticmethod
    def get_err_message(err_type, args):
        errors = {
            'unexpected': 'Unhandled error',
            'already_opened': 'Файл %s открыт для редактирования.',
            'not_found': 'Не удалось загрузить шаблон для экспорта. Проверьте наличие файла %s . Файл открыт для '
                         'редактирования, необходимо его закрыть.',
            'file_rewritten': 'Файл %s был перезаписан.',
            'load_failed': 'Не удалось загрузить файл %s',
        }
        if err_type not in errors:
            return errors['unexpected']
        return errors[err_type] % args
