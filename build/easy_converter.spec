# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Definir la ruta base del código fuente
base_path = os.path.abspath(os.path.join(os.getcwd(), 'src'))

# Recopilar submódulos de dependencias críticas
hidden_imports = [
    'pkg_resources.py2_warn',
    'docx2pdf',
    'tkinterdnd2',
    'pdf2docx',
    'customtkinter',
    'comtypes',
]
hidden_imports += collect_submodules('pdf2docx')
hidden_imports += collect_submodules('customtkinter')

a = Analysis(
    ['src/main.py'],
    pathex=[os.getcwd(), base_path],
    binaries=[],
    datas=[
        ('assets', 'assets'),
    ],
    hiddenimports=hidden_imports,
    hookspath=['build/hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['notebook', 'matplotlib', 'numpy'], # Excluir para reducir tamaño si no se usan
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
    console=False, 
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None, # Assets/icon.ico se puede añadir en Fase 8
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
