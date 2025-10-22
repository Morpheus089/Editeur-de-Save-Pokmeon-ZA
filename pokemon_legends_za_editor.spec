# -*- mode: python ; coding: utf-8 -*-
"""
Configuration PyInstaller pour Pokemon Legends Z-A Save Editor
"""

import os
import sys
from PyInstaller.utils.hooks import collect_all

# Nom de l'application
app_name = "Pokemon_Legends_ZA_Save_Editor"

# Répertoires source
src_dir = "src"
assets_dir = "assets"

# Collecte automatique des modules plaza
plaza_datas, plaza_binaries, plaza_hiddenimports = collect_all('plaza')

# Données à inclure
added_files = [
    (os.path.join(assets_dir, 'presets'), 'assets/presets'),
    (os.path.join(src_dir, 'plaza'), 'plaza'),
]

a = Analysis(
    ['run.py'],
    pathex=['.', src_dir],
    binaries=plaza_binaries,
    datas=added_files + plaza_datas,
    hiddenimports=plaza_hiddenimports + [
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'plaza.crypto',
        'plaza.types',
        'plaza.util.items',
        'pokemon_legends_za_editor.plza_config',
        'pokemon_legends_za_editor.plza_utils',
        'pokemon_legends_za_editor.preset_manager',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

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
    console=False,  # Interface graphique, pas de console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Vous pouvez ajouter un icône ici
    version_file=None,
)

# Pour créer un répertoire de distribution
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)