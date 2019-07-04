
# import sys
# import py2exe
# from distutils.core import setup
# import glob
#
# sys.argv.append('py2exe')
#
# data = [('Images', glob.glob('Images\\*')),
#         ('Conf', glob.glob('conf\\*')),
#         ('Style', glob.glob('Style\\*.css')),
#         # ('Spr\\XL_forms', glob.glob('Spr\\XL_forms\\*')),
#         # ('Spr', glob.glob('Spr\\*')),
#         ('', glob.glob('*.mdb')),
#         ('', glob.glob('template.xlsx'))
# ]
# target = {
# 'script' : "executor.py",
# 'version' : "1.0",
# 'company_name' : "BELGIPROZEM",
# 'copyright' : "",
# 'name' : "KOc_Viewer",
# 'dest_base' : "KOc_Viewer",
# "icon_resources": [(1, "Images\\excel.ico")]
# }
# setup(
#     data_files =data,
#     windows = [target],
#     options = {"py2exe": {"includes":["sip", "packages", "openpyxl", "os", "pyodbc", "time", "re", "decimal", "datetime", "shutil", "sys", "PyQt4"],
#                     "dll_excludes": ["MSVCP90.dll", "CRYPT32.dll" , "COMDLG32.dll", "IMM32.dll" , "ole32.dll", "WINSPOOL.DRV", "WINMM.dll","USER32.dll", "SHELL32.dll", "ODBC32.dll", "ADVAPI32.dll", "WS2_32.dll", "GDI32.dll", "KERNEL32.dll"],
#                     "bundle_files": 1,
#                     "compressed": 1,
#                     "unbuffered": True,
#                     "optimize": 2,
#     }},
#     zipfile=None,
# )

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [Executable('executor.py', base=base)]

packages = [
    'sip', 'threads', 'uiWidgets', 'os', 'decimal', 'datetime',
    'sys', 'pyodbc', 'PyQt5', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
]
options = {
    'build_exe': {
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
    name='KOviever 2.0',
    options=options,
    version='2.0.0',
    description='Kad Oc extraction tool',
    executables=executables
)
