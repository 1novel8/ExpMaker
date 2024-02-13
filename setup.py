import sys

from cx_Freeze import Executable, setup

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [Executable('ExpMaker.py', base=base)]

packages = [
    'sip', 'threads', 'uiWidgets', 'os', 'decimal', 'datetime',
    'sys', 'pyodbc', 'PyQt5', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
]
options = {
    'build_exe': {
        'include_msvcr': True,
        'optimize': 2,
        'excludes': ['tkinter'],
    },
}

setup(
    name='ExpMaker 2.0',
    options=options,
    version='2.0.0',
    description='Explication maker tool',
    executables=executables
)
