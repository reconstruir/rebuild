#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import script_unit_test
from bes.fs import file_find, temp_file
from bes.system import host

class test_rebuilder_script(script_unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/rebuilder'
  __script__ = __file__, '../../bin/rebuilder.py'

  DEBUG = False
#  DEBUG = True

  BUILD_LEVEL = 'release'

  def test_basic_fructose(self):
    tmp_dir = self._make_temp_dir()
    cmd = [
      '--source-dir',
      path.join(self.data_dir(), '../packager'),
      '--no-network',
      '-v',
      '--root', tmp_dir,
      '--level', self.BUILD_LEVEL,
      'fructose',
    ]
    rv = self.run_script(cmd, cwd = path.join(self.data_dir(), 'basic'))
    if rv.exit_code != 0:
      print((rv.stdout))
    self.assertEqual( 0, rv.exit_code )
    artifacts_dir = path.join(tmp_dir, 'artifacts', host.SYSTEM, 'x86_64', self.BUILD_LEVEL)
    self.assertTrue( path.exists(path.join(artifacts_dir, 'fructose-3.4.5-6.tar.gz')) )
    self.assertFalse( path.exists(path.join(artifacts_dir, 'fiber-1.0.0.tar.gz')) )

  def test_fructose_recipe_v2(self):
    tmp_dir = self._make_temp_dir()
    cmd = [
      '--source-dir',
      path.join(self.data_dir(), '../packager'),
      '--no-network',
      '-v',
      '--root', tmp_dir,
      '--level', self.BUILD_LEVEL,
      'fructose',
    ]
    rv = self.run_script(cmd, cwd = path.join(self.data_dir(), 'recipe_v2'))
    if rv.exit_code != 0:
      print('FAILED stdout:')
      print((rv.stdout))
    self.assertEqual( 0, rv.exit_code )
    artifacts_dir = path.join(tmp_dir, 'artifacts', host.SYSTEM, 'x86_64', self.BUILD_LEVEL)
    self.assertTrue( path.exists(path.join(artifacts_dir, 'fructose-3.4.5-6.tar.gz')) )
    self.assertFalse( path.exists(path.join(artifacts_dir, 'fiber-1.0.0.tar.gz')) )
    
  def test_fructose_fiber(self):
    tmp_dir = self._make_temp_dir()
    cmd = [
      '--source-dir',
      path.join(self.data_dir(), '../packager'),
      '--no-network',
      '-v',
      '--root', tmp_dir,
      '--level', self.BUILD_LEVEL,
      'fructose',
      'fiber',
    ]
    rv = self.run_script(cmd, cwd = path.join(self.data_dir(), 'basic'))
    if rv.exit_code != 0:
      print((rv.stdout))
    self.assertEqual( 0, rv.exit_code )
    artifacts_dir = path.join(tmp_dir, 'artifacts', host.SYSTEM, 'x86_64', self.BUILD_LEVEL)
    self.assertTrue( path.exists(path.join(artifacts_dir, 'fructose-3.4.5-6.tar.gz')) )
    self.assertTrue( path.exists(path.join(artifacts_dir, 'fiber-1.0.0.tar.gz')) )
    
  def xxxtest_orange(self):
    tmp_dir = self._make_temp_dir()
    cmd = [
      '--source-dir',
      path.join(self.data_dir(), '../packager'),
      '--no-network',
      '-v',
      '--root', tmp_dir,
      '--level', self.BUILD_LEVEL,
      'orange',
    ]
    rv = self.run_script(cmd, cwd = path.join(self.data_dir(), 'basic'))
    if rv.exit_code != 0:
      print((rv.stdout))
    self.assertEqual( 0, rv.exit_code )
    artifacts_dir = path.join(tmp_dir, 'artifacts', host.SYSTEM, 'x86_64', self.BUILD_LEVEL)
    self.assertTrue( path.exists(path.join(artifacts_dir, 'fructose-3.4.5-6.tar.gz')) )
    self.assertTrue( path.exists(path.join(artifacts_dir, 'fiber-1.0.0.tar.gz')) )
    self.assertTrue( path.exists(path.join(artifacts_dir, 'fiber-orange-6.5.4-3.tar.gz')) )

  def test_tool_tfoo(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_dir()
    cmd = [
      '--source-dir',
      path.join(self.data_dir(), '../packager'),
      '--no-network',
      '-v',
      '--root', tmp_dir,
      '--level', self.BUILD_LEVEL,
      '--timestamp', 'timestamp',
      'tfoo',
    ]
    rv = self.run_script(cmd, cwd = path.join(self.data_dir(), 'basic'))
    if rv.exit_code != 0:
      print((rv.stdout))
    self.assertEqual( 0, rv.exit_code )
    artifacts_dir = path.join(tmp_dir, 'artifacts', host.SYSTEM, 'x86_64', self.BUILD_LEVEL)
    self.assertEqual( [
      'artifacts/macos/x86_64/release/tfoo-1.0.0.tar.gz',
      'builds/macos/x86_64/release/tfoo-1.0.0_timestamp/artifact/tfoo-1.0.0.tar.gz',
      'builds/macos/x86_64/release/tfoo-1.0.0_timestamp/check/unpacked/files/bin/tfoo.py',
      'builds/macos/x86_64/release/tfoo-1.0.0_timestamp/check/unpacked/metadata/info.json',
      'builds/macos/x86_64/release/tfoo-1.0.0_timestamp/stage/bin/tfoo.py',
      'builds/macos/x86_64/release/tfoo-1.0.0_timestamp/test/test-tfoo/requirements/database/packages.json',
      'builds/macos/x86_64/release/tfoo-1.0.0_timestamp/test/test-tfoo/requirements/installation/bin/tfoo.py',
      'builds/macos/x86_64/release/tfoo-1.0.0_timestamp/test/test-tfoo/test-tfoo.sh',
      'checksums/macos/x86_64/release/tfoo-1.0.0/sources.checksums',
      'checksums/macos/x86_64/release/tfoo-1.0.0/targets.checksums',
    ], file_find.find(tmp_dir) )
    
  def test_tool_tbar_depends_on_tool_tfoo(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_dir()
    cmd = [
      '--source-dir',
      path.join(self.data_dir(), '../packager'),
      '--no-network',
      '-v',
      '--root', tmp_dir,
      '--level', self.BUILD_LEVEL,
      '--timestamp', 'timestamp',
      'tbar',
    ]
    rv = self.run_script(cmd, cwd = path.join(self.data_dir(), 'basic'))
    if rv.exit_code != 0:
      print((rv.stdout))
    self.assertEqual( 0, rv.exit_code )
    artifacts_dir = path.join(tmp_dir, 'artifacts', host.SYSTEM, 'x86_64', self.BUILD_LEVEL)
    #self.assertTrue( path.exists(path.join(artifacts_dir, 'tbar-1.0.0.tar.gz')) )
    self.assertEqual( [
      'artifacts/macos/x86_64/release/tbar-1.0.0.tar.gz',
      'artifacts/macos/x86_64/release/tfoo-1.0.0.tar.gz',
      'builds/macos/x86_64/release/tbar-1.0.0_timestamp/artifact/tbar-1.0.0.tar.gz',
      'builds/macos/x86_64/release/tbar-1.0.0_timestamp/check/unpacked/files/bin/tbar.py',
      'builds/macos/x86_64/release/tbar-1.0.0_timestamp/check/unpacked/metadata/info.json',
      'builds/macos/x86_64/release/tbar-1.0.0_timestamp/stage/bin/tbar.py',
      'builds/macos/x86_64/release/tbar-1.0.0_timestamp/test/test-tbar/requirements/database/packages.json',
      'builds/macos/x86_64/release/tbar-1.0.0_timestamp/test/test-tbar/requirements/installation/bin/tbar.py',
      'builds/macos/x86_64/release/tbar-1.0.0_timestamp/test/test-tbar/test-tbar.sh',
      'builds/macos/x86_64/release/tfoo-1.0.0_timestamp/artifact/tfoo-1.0.0.tar.gz',
      'builds/macos/x86_64/release/tfoo-1.0.0_timestamp/check/unpacked/files/bin/tfoo.py',
      'builds/macos/x86_64/release/tfoo-1.0.0_timestamp/check/unpacked/metadata/info.json',
      'builds/macos/x86_64/release/tfoo-1.0.0_timestamp/stage/bin/tfoo.py',
      'builds/macos/x86_64/release/tfoo-1.0.0_timestamp/test/test-tfoo/requirements/database/packages.json',
      'builds/macos/x86_64/release/tfoo-1.0.0_timestamp/test/test-tfoo/requirements/installation/bin/tfoo.py',
      'builds/macos/x86_64/release/tfoo-1.0.0_timestamp/test/test-tfoo/test-tfoo.sh',
      'checksums/macos/x86_64/release/tbar-1.0.0/sources.checksums',
      'checksums/macos/x86_64/release/tbar-1.0.0/targets.checksums',
      'checksums/macos/x86_64/release/tfoo-1.0.0/sources.checksums',
      'checksums/macos/x86_64/release/tfoo-1.0.0/targets.checksums',
      'tools/macos/tfoo-1.0.0/bin/tfoo.py',
    ], file_find.find(tmp_dir) )

  def test_lib_libstarch(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_dir()
    cmd = [
      '--source-dir',
      path.join(self.data_dir(), '../packager'),
      '--no-network',
      '-v',
      '--root', tmp_dir,
      '--level', self.BUILD_LEVEL,
      '--timestamp', 'timestamp',
      'libstarch',
    ]
    rv = self.run_script(cmd, cwd = path.join(self.data_dir(), 'basic'))
    if rv.exit_code != 0:
      print((rv.stdout))
    self.assertEqual( 0, rv.exit_code )
    artifacts_dir = path.join(tmp_dir, 'artifacts', host.SYSTEM, 'x86_64', self.BUILD_LEVEL)
    self.assertEqual( [
      'artifacts/macos/x86_64/release/libstarch-1.0.0.tar.gz',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/artifact/libstarch-1.0.0.tar.gz',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/.gitignore',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/Makefile',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/libstarch.a',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/libstarch/amylopectin.c',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/libstarch/amylopectin.h',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/libstarch/amylopectin.o',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/libstarch/amylose.c',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/libstarch/amylose.h',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/libstarch/amylose.o',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/libstarch/common.c',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/libstarch/common.h',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/libstarch/common.o',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/programs/starch_prog1/starch_prog1_main.c',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/programs/starch_prog1/starch_prog1_main.c~',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/programs/starch_prog1/starch_prog1_main.o',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/rebbe_retry.sh',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/build/starch_prog1_main',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/check/unpacked/files/bin/starch_prog1_main',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/check/unpacked/files/include/libstarch/amylopectin.h',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/check/unpacked/files/include/libstarch/amylose.h',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/check/unpacked/files/include/libstarch/common.h',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/check/unpacked/files/lib/libstarch.a',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/check/unpacked/files/lib/pkgconfig/libstarch.pc',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/check/unpacked/metadata/info.json',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/libstarch-1.0.0.tar.gz',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/source/.gitignore',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/source/Makefile',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/source/libstarch/amylopectin.c',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/source/libstarch/amylopectin.h',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/source/libstarch/amylose.c',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/source/libstarch/amylose.h',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/source/libstarch/common.c',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/source/libstarch/common.h',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/source/programs/starch_prog1/starch_prog1_main.c',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/source/programs/starch_prog1/starch_prog1_main.c~',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/stage/bin/starch_prog1_main',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/stage/include/libstarch/amylopectin.h',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/stage/include/libstarch/amylose.h',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/stage/include/libstarch/common.h',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/stage/lib/libstarch.a',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/stage/lib/pkgconfig/libstarch.pc',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/stage/lib/pkgconfig/libstarch.pc.bak',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/test/test-libstarch/requirements/database/packages.json',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/test/test-libstarch/requirements/installation/bin/starch_prog1_main',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/test/test-libstarch/requirements/installation/include/libstarch/amylopectin.h',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/test/test-libstarch/requirements/installation/include/libstarch/amylose.h',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/test/test-libstarch/requirements/installation/include/libstarch/common.h',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/test/test-libstarch/requirements/installation/lib/libstarch.a',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/test/test-libstarch/requirements/installation/lib/pkgconfig/libstarch.pc',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/test/test-libstarch/test-libstarch.c',
      'builds/macos/x86_64/release/libstarch-1.0.0_timestamp/test/test-libstarch/test-libstarch.exe',
      'checksums/macos/x86_64/release/libstarch-1.0.0/sources.checksums',
      'checksums/macos/x86_64/release/libstarch-1.0.0/targets.checksums',
    ], file_find.find(tmp_dir) )

  def test_lib_libpotato(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_dir()
    cmd = [
      '--source-dir',
      path.join(self.data_dir(), '../packager'),
      '--no-network',
      '-v',
      '--root', tmp_dir,
      '--level', self.BUILD_LEVEL,
      '--timestamp', 'timestamp',
      'libpotato',
    ]
    rv = self.run_script(cmd, cwd = path.join(self.data_dir(), 'basic'))
    if rv.exit_code != 0:
      print((rv.stdout))
    self.assertEqual( 0, rv.exit_code )
    artifacts_dir = path.join(tmp_dir, 'artifacts', host.SYSTEM, 'x86_64', self.BUILD_LEVEL)
    self.assertTrue( path.exists(path.join(artifacts_dir, 'libpotato-1.0.0.tar.gz')) )
    
  def _make_temp_dir(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print("tmp_dir: ", tmp_dir)
    return tmp_dir

if __name__ == '__main__':
  script_unit_test.main()
