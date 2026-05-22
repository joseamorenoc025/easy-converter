# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Definir la ruta base del código fuente
base_path = os.path.abspath(os.path.join(os.getcwd(), 'src'))

# Recopilar submódulos y dependencias "ocultas" que PyInstaller no detecta automáticamente
hidden_imports = [
    'docx2pdf',
    'tkinterdnd2',
    'pdf2docx',
    'customtkinter',
    'comtypes',
    'win32com',
    'win32com.client',
    'pythoncom',
    'fitz',  # PyMuPDF
]
hidden_imports += collect_submodules('pdf2docx')
hidden_imports += collect_submodules('customtkinter')

# Recopilar datos de tkinterdnd2 y otras librerías
datas = [
    ('../assets', 'assets'),
]
datas += collect_data_files('tkinterdnd2')
datas += collect_data_files('customtkinter')

a = Analysis(
    ['../src/main.py'],
    pathex=[os.getcwd(), base_path],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=['build/hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['notebook', 'matplotlib', 'numpy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EasyConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # Importante: No mostrar ventana de comandos
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../assets/icon.ico',  
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EasyConverter',
)
