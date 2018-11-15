import sys
from cx_Freeze import setup, Executable

base = "Win32GUI"

executables = [Executable("Explication.py", base=base)]

packages = [
    "sip", "threads", "uiWidgets", "os", "decimal", "datetime",
    "sys", "pyodbc", "PyQt5", 'PyQt5.QtGui', 'PyQt5.QtWidgets',
]
options = {
    'build_exe': {
        'packages': packages,
        'include_msvcr': True,
        'compressed': True,
        # 'include_files': [
        #     (r'C:\Windows\System32\msvcr100.dll', 'msvcr100.dll'),
        # ],
        # "exclude_dlls": ["MSVCP90.dll", "CRYPT32.dll", "COMDLG32.dll", "IMM32.dll", "ole32.dll", "WINSPOOL.DRV", "WINMM.dll", "USER32.dll", "SHELL32.dll", "ODBC32.dll", "ADVAPI32.dll", "WS2_32.dll", "GDI32.dll", "KERNEL32.dll"],            "bundle_files": 1,
    },
}

setup(
    name="XConverter",
    options=options,
    version="1.0.0",
    description='Media encryption tool',
    executables=executables
)
