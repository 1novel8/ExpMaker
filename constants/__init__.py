__author__ = 'Alex Konkov'

from .actions import SprActions, SettingsActions, BaseActivityActions, ExplicationActions, ExtractionActions
from .pathDefaults import CoreFilesPaths
from .errors import DbErrors
from .errorTypes import ProcessErrorTypes


appKey = 'RXhwbGljYXRpb24gMi4wIEFwcA=='
sprActions = SprActions()
settingsActions = SettingsActions()
baseActions = BaseActivityActions()
extractionActions = ExtractionActions()
expActions = ExplicationActions()
coreFiles = CoreFilesPaths()
dbErrors = DbErrors()
errTypes = ProcessErrorTypes()
