# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
from PyInstaller.utils.win32.versioninfo import (
    VSVersionInfo, FixedFileInfo, StringFileInfo, StringTable,
    StringStruct, VarFileInfo, VarStruct
)

block_cipher = None

base_path = os.path.abspath(os.path.join(os.getcwd(), 'src'))
icon_path = os.path.abspath(os.path.join(os.getcwd(), 'assets', 'icon.ico'))

hidden_imports = [
    'docx2pdf',
    'tkinterdnd2',
    'pdf2docx',
    'customtkinter',
    'win32com',
    'win32com.client',
    'pythoncom',
    'fitz',
    'PIL',
    'PIL._tkinter_finder',
    'docx',
    'lxml',
    'lxml.etree',
    'lxml._elementpath',
    'pytesseract',
    'numpy',
    'cv2',
    'fire',
    'fonttools',
    'tqdm',
    'darkdetect',
    'packaging',
    'colorama',
]
hidden_imports += collect_submodules('pdf2docx')
hidden_imports += collect_submodules('customtkinter')
hidden_imports += collect_submodules('lxml')

datas = [
    (os.path.join(os.getcwd(), 'assets'), 'assets'),
]
datas += collect_data_files('tkinterdnd2')
datas += collect_data_files('customtkinter')

version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(2, 0, 0, 0),
        prodvers=(2, 0, 0, 0),
        mask=0x3F,
        flags=0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo(kids=[
            StringTable(
                name='040A04B0',
                kids=[
                    StringStruct('CompanyName', 'EasyConverter'),
                    StringStruct('FileDescription', 'Conversor bidireccional PDF a Word'),
                    StringStruct('FileVersion', '2.0.0.0'),
                    StringStruct('InternalName', 'EasyConverter'),
                    StringStruct('LegalCopyright', '2026 EasyConverter'),
                    StringStruct('OriginalFilename', 'EasyConverter.exe'),
                    StringStruct('ProductName', 'Easy Converter'),
                    StringStruct('ProductVersion', '2.0.0.0'),
                ]
            )
        ]),
        VarFileInfo(kids=[VarStruct('Translation', [0x040A, 0x04B0])])
    ]
)

a = Analysis(
    ['../src/main.py'],
    pathex=[os.getcwd(), base_path],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=['build/hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'notebook', 'matplotlib',
        'torch', 'torchvision', 'torchaudio',
        'tensorflow', 'keras',
        'onnxruntime', 'onnx',
        'scipy', 'scipy.signal', 'scipy.stats', 'scipy.spatial', 'scipy.linalg', 'scipy.io',
        'pandas',
        'numba',
        'pyarrow',
        'sklearn', 'scikit_learn',
        'Cython',
        'PIL.ImageShow', 'PIL.ImageGrab',
        'jedi', 'parso',
        'IPython', 'jupyter',
        'tkinter.test',
        'pygments',
        'rich',
        'fsspec',
        's3fs',
        'gcsfs',
        'openpyxl',
        'xlrd', 'xlwt',
        'h5py',
        'matlab', 'matlab.engine',
        'zmq', 'pyzmq',
        'bs4', 'BeautifulSoup',
        'psutil',
        'pytz',
        'dateutil',
        'cryptography',
        'setuptools',
        'pkg_resources',
        'pycparser',
        'pytest',
        'unittest',
        'test',
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
    name='EasyConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
    version=version_info,
)
