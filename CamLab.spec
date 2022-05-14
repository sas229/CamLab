# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

added_files = [
    ('src/CamLab.css', '.'),
    ('src/assets', 'assets'),
    ('src/delegates', 'delegates'),
    ('src/local_gxipy', 'local_gxipy'),
    ('src/local_pyqtgraph', 'local_pyqtgraph'),
    ('src/local_qt_material', 'local_qt_material'),
    ('src/models', 'models'),
    ('src/views', 'views'),
]

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='main',
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
)