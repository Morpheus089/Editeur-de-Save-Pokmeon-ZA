# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

app_name = "Pokemon_Legends_ZA_Save_Editor"

src_dir = "src"
assets_dir = "assets"

plaza_datas, plaza_binaries, plaza_hiddenimports = collect_all('plaza')
plaza_submodules = collect_submodules('plaza')

added_files = [
    (os.path.join(assets_dir, 'presets'), 'assets/presets'),
    (os.path.join(src_dir, 'plaza', 'util', 'item_db.json'), 'plaza/util'),
]

hidden_imports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.simpledialog',
    '_tkinter',
    'plaza',
    'plaza.crypto',
    'plaza.crypto.fnvhash',
    'plaza.crypto.hashdb',
    'plaza.crypto.scblock',
    'plaza.crypto.sctypecode',
    'plaza.crypto.scxorshift',
    'plaza.crypto.swishcrypto',
    'plaza.types',
    'plaza.types.accessors',
    'plaza.types.bagsave',
    'plaza.types.coredata',
    'plaza.types.pokedex',
    'plaza.util',
    'plaza.util.items',
    'pokemon_legends_za_editor',
    'pokemon_legends_za_editor.main',
    'pokemon_legends_za_editor.plza_config',
    'pokemon_legends_za_editor.plza_utils',
    'pokemon_legends_za_editor.preset_manager',
] + plaza_hiddenimports + plaza_submodules

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=['.', src_dir],
    binaries=plaza_binaries,
    datas=added_files,
    hiddenimports=list(set(hidden_imports)),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'pytest',
        'setuptools',
        'pip',
        'wheel',
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
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
