
class ControlsStates:
    INITIAL = 'initial'
    LOADING = 'loading'
    DB_LOADED = 'db data loaded'
    CONTROL_PASSED = 'control passed'
    CONTROL_FAILED = 'control failed'
    CONVERTATION_PASSED = 'convertation passed'
    CONVERTATION_FAILED = 'convertation failed'
    SESSION_LOADED = 'session loaded'
    enum = [
        INITIAL,
        LOADING,
        DB_LOADED,
        CONTROL_PASSED,
        CONTROL_FAILED,
        CONVERTATION_PASSED,
        CONVERTATION_FAILED,
        SESSION_LOADED,
    ]
