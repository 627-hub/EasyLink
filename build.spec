# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

sys.setrecursionlimit(5000)

block_cipher = None

a = Analysis(
    ['tray.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/stock-data.json', 'data'),
    ],
    hiddenimports=[
        'win32api', 'win32con', 'win32gui', 'win32process',
        'ctypes', 'ctypes.wintypes',
        'flask', 'flask.json',
        'requests',
        'schedule',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'tcl', 'tcl8', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
        'matplotlib', 'numpy', 'scipy', 'pandas',
        'PIL', 'cv2', 'tensorflow', 'torch', 'keras',
        'jupyter', 'ipython', 'notebook', 'nbformat',
        'unittest', 'pytest', 'test',
        'pip', 'setuptools', 'wheel',
        'docutils', 'sphinx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EasyLink',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
