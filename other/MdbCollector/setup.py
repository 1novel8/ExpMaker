
import sys
import py2exe
from distutils.core import setup
import glob

sys.argv.append('py2exe')

data = [('Images', glob.glob('Images\\*')),
        ('Style', glob.glob('Style\\*.css')),
        # ('Spr\\XL_forms', glob.glob('Spr\\XL_forms\\*')),
        # ('Spr', glob.glob('Spr\\*')),
        ('', glob.glob('*.mdb'))
]
target = {
'script' : "executor.py",
'version' : "1.0",
'company_name' : "BELGIPROZEM",
'copyright' : "",
'name' : "Collector",
'dest_base' : "Collector",
"icon_resources": [(1, "Images\\e.ico")]
}
setup(
    data_files =data,
    windows = [target],
    options = {"py2exe": {"includes":["sip", "packages", "openpyxl", "os", "pyodbc", "time", "decimal", "datetime", "shutil", "sys", "PyQt4"],
                    "dll_excludes": ["MSVCP90.dll", "CRYPT32.dll" , "COMDLG32.dll", "IMM32.dll" , "ole32.dll", "WINSPOOL.DRV", "WINMM.dll","USER32.dll", "SHELL32.dll", "ODBC32.dll", "ADVAPI32.dll", "WS2_32.dll", "GDI32.dll", "KERNEL32.dll"],
                    "bundle_files": 1,
                    "compressed": 1,
                    "unbuffered": True,
                    "optimize": 2,
    }},
    zipfile=None,
)