__author__ = 'Alex Konkov'

from .componentTitlesLocales import TitleLocales
from .toolTipsLocales import TooltipsLocales
from .errorsLocales import AppErrorsLocales, CustomErrorsLocales, ProtocolErrors
from .actionsMessages import ActionMessages

titleLocales = TitleLocales()
tooltipsLocales = TooltipsLocales()
appErrors = AppErrorsLocales()
customErrors = CustomErrorsLocales()
protocolErrors = ProtocolErrors()
actionLocales = ActionMessages()

