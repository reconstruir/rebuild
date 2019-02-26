# -*- mode: python -*-

block_cipher = None

a = Analysis(['${REBUILD_BUILD_DIR}/bin/rebuilder.py'],
             pathex=['.'], #, 'lib/rebuild/builder/steps'],
             binaries=[],
             #datas=[ ( 'lib/rebuild/builder/steps/step_setup.py', 'rebuild.builder.steps' ) ],
             #datas=[ ( 'lib/rebuild/builder/steps/step_setup.py', 'rebuild' ) ],
             # this is annoying but required for pyinstaller to work with plugins such as steps
             #hiddenimports=['rebuild.builder.steps.step_setup'],
             hiddenimports=['step_setup'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='rebuilder',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
