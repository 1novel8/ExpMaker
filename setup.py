import sys
from cx_Freeze import setup, Executable

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
        # 'packages': packages,
        'include_msvcr': True,
        'optimize': 2,
        'excludes': ['tkinter'],
        # 'zip_include_packages': '*'
        # 'include_files': [
        #     (r'C:\Windows\System32\msvcr100.dll', 'msvcr100.dll'),
        # ],
        # 'exclude_dlls': ['MSVCP90.dll', 'CRYPT32.dll', 'COMDLG32.dll', 'IMM32.dll', 'ole32.dll', 'WINSPOOL.DRV', 'WINMM.dll', 'USER32.dll', 'SHELL32.dll', 'ODBC32.dll', 'ADVAPI32.dll', 'WS2_32.dll', 'GDI32.dll', 'KERNEL32.dll'],            'bundle_files': 1,
    },
}

setup(
    name='ExpMaker 2.0',
    options=options,
    version='2.0.0',
    description='Explication maker tool',
    executables=executables
)
