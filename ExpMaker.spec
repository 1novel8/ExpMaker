# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(
    ['ExpMaker.py'],
    pathex=['D:\\Lora\\minskgiprozem\\P07_ExpMaker\\P07_ExpMaker\\SCRIPT\\explication64_ready_1_2_3_4_stage_1204221\\explication64_куфвн_140121_зфке2\\explication64'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ExpMaker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False ,
    icon='Images\\map.ico'
)
