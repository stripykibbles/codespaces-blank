# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['onward.py'],
    pathex=[],
    binaries=[],
    datas=[('fonts', 'fonts')],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Onward',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
)

# macOS: wrap the exe in a .app bundle
app = BUNDLE(
    exe,
    name='Onward.app',
    icon=None,
    bundle_identifier='com.onward.app',
    info_plist={
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Onward Project',
                'CFBundleTypeExtensions': ['onward'],
                'CFBundleTypeRole': 'Editor',
                'LSHandlerRank': 'Owner',
                'LSTypeIsPackage': True,
            }
        ],
    },
)
