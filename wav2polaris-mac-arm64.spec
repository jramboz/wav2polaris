# -*- mode: python ; coding: utf-8 -*-

import os


codesign_identity = os.environ.get("MACOS_CODESIGN_IDENTITY")
entitlements_file = os.environ.get("MACOS_ENTITLEMENTS_FILE")


a = Analysis(
    ['src/wav2polaris/app.py'],
    pathex=['src/wav2polaris'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='wav2polaris',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch="arm64",
    codesign_identity=codesign_identity,
    entitlements_file=entitlements_file,
    icon=['wav2polaris.png'],
)
