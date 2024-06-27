import sys

from cx_Freeze import Executable, setup

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [Executable('ExpMaker.py', base=base, icon='Images/i.ico')]

packages = [
    'threads', 'os', 'decimal', 'datetime',
    'sys', 'pyodbc', 'PyQt5', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
]

static_files = [
    ('Spr', 'Spr'),
    ('Images', 'Images'),
    ('Style', 'Style'),
]

options = {
    'build_exe': {
        'include_msvcr': True,
        'optimize': 2,
        'excludes': ['tkinter'],
        'include_files': static_files,
    },
}

setup(
    name='ExpMaker 2024.2.0',
    options=options,
    version='2024.2.0',
    description='Explication maker tool',
    executables=executables,
)
