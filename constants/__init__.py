__author__ = 'Alex Konkov'

from .actions import SprActions, SettingsActions, BaseActivityActions, ExplicationActions, ExtractionActions, ContolsActions
from .pathDefaults import CoreFilesPaths
from .errors import DbErrors
from .errorTypes import CustomErrorTypes, SpravErrorTypes
from .controlsVariants import ControlsStates

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
