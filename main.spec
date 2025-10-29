# -*- mode: python ; coding: utf-8 -*-

import sys
sys.setrecursionlimit(10000)  # 递归深度，不知道为什么系统的递归深度太深了，在这里调高10倍

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/fonts', 'data/fonts'),
        ('src/scorelang/config', 'src/scorelang/config'),
        ],
    hiddenimports=[
        'src.scorelang.visitors.pipa_analysis_pass',
        'src.scorelang.visitors.pipa_layout_pass',   
        'src.scorelang.renderers.pipa_text_renderer',

    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MusicScoreHub',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MusicScoreHub',
)
