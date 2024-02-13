__author__ = 'Alex Konkov'

from .actions import (BaseActivityActions, ContolsActions, ExplicationActions,
                      ExtractionActions, SettingsActions, SprActions)
from .controlsVariants import ControlsStates
from .errors import DbErrors
from .errorTypes import CustomErrorTypes, SpravErrorTypes
from .pathDefaults import CoreFilesPaths

appKey = 'RXhwbGljYXRpb24gMi4wIEFwcA=='
sprActions = SprActions()
controlActions = ContolsActions()
settingsActions = SettingsActions()
baseActions = BaseActivityActions()
extractionActions = ExtractionActions()
expActions = ExplicationActions()
coreFiles = CoreFilesPaths()
dbErrors = DbErrors()
errTypes = CustomErrorTypes()
spravErrTypes = SpravErrorTypes()
controlsStates = ControlsStates()
