from constants import errTypes


class CustomError(Exception):
    def __init__(self, err_type, err_message):
        if err_type not in errTypes.types_enum:
            err_type = errTypes.unexpected
        self.type = err_type
        self.message = err_message
        super(CustomError, self).__init__(err_message)
