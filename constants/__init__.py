__author__ = 'Alex Konkov'

from .actions import SprActions, SettingsActions, BaseActivityActions, ExplicationActions, ExtractionActions
from .pathDefaults import CoreFilesPaths

appKey = 'RXhwbGljYXRpb24gMi4wIEFwcA=='
sprActions = SprActions()
settingsActions = SettingsActions()
baseActions = BaseActivityActions()
extractionActions = ExtractionActions()
expActions = ExplicationActions()
coreFiles = CoreFilesPaths()
