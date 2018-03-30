#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import script_unit_test
from bes.fs import file_find, temp_file
from bes.archive import archiver
from bes.system import host
from collections import namedtuple

class test_rebuilder_script(script_unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/rebuilder'
  __script__ = __file__, '../../bin/rebuilder.py'

  DEBUG = script_unit_test.DEBUG
  #DEBUG = True

  BUILD_LEVEL = 'release'

  _test_context = namedtuple('_test_context', 'tmp_dir,command,result,artifacts_dir,artifacts,droppings')

  def test_basic_fructose(self):
    test = self._run_test('basic', 'fructose')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'fructose-3.4.5-6.tar.gz' ], test.artifacts )

  def test_one_project(self):
    test = self._run_test('one_project', 'fructose')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'fructose-3.4.5-6.tar.gz' ], test.artifacts )
    
  def test_fructose_and_fiber(self):
    test = self._run_test('basic', 'fructose', 'fiber')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'fiber-1.0.0.tar.gz', 'fructose-3.4.5-6.tar.gz' ], test.artifacts )
    
  def xxxtest_orange(self):
    test = self._run_test('basic', 'fructose', 'fiber')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'fiber-1.0.0.tar.gz', 'fiber-orange-6.5.4-3.tar.gz', 'fructose-3.4.5-6.tar.gz' ], test.artifacts )

  def test_tool_tfoo(self):
    test = self._run_test('basic', 'tfoo')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'tfoo-1.0.0.tar.gz' ], test.artifacts )
    
  def test_tool_tbar_depends_on_tfoo(self):
    test = self._run_test('basic', 'tbar')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'tbar-1.0.0.tar.gz', 'tfoo-1.0.0.tar.gz' ], test.artifacts )

  def test_tool_tbaz(self):
    test = self._run_test('basic', 'tbaz')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'tbaz-1.0.0.tar.gz' ], test.artifacts )
    
  def test_lib_libstarch(self):
    test = self._run_test('basic', 'libstarch')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'libstarch-1.0.0.tar.gz' ], test.artifacts )

  def test_lib_libpotato_depends_on_libstarch(self):
    test = self._run_test('basic', 'libpotato')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'libpotato-1.0.0.tar.gz', 'libstarch-1.0.0.tar.gz', 'tbar-1.0.0.tar.gz', 'tfoo-1.0.0.tar.gz' ], test.artifacts )

  def test_extra_tarballs(self):
    test = self._run_test('extra_tarballs', 'foo', '--source-dir', path.join(self.data_dir(), 'extra_tarballs/source'))
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'foo-1.0.0.tar.gz' ], test.artifacts )
    tgz = path.join(test.artifacts_dir, 'foo-1.0.0.tar.gz')
    self.assertEqual( [
      'files/foo-1.0.0/bin/bar.sh',
      'files/foo-1.0.0/usr/bin/foo.sh',
      'metadata/info.json',
    ], archiver.members(tgz) )
    
  def _make_temp_dir(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print("tmp_dir: ", tmp_dir)
    return tmp_dir

  def _make_command(self, tmp_dir, *args):
    cmd = [
      '--source-dir',
      path.join(self.data_dir(), '../packager'),
      '--no-network',
      '-v',
      '--root', tmp_dir,
      '--level', self.BUILD_LEVEL,
      '--timestamp', 'timestamp',
    ] + list(args)
    return cmd

  def _run_test(self, cwd_subdir, *args):
    tmp_dir = self._make_temp_dir()
    command = self._make_command(tmp_dir, *args)
    cwd = path.join(self.data_dir(), cwd_subdir)
    artifacts_dir = path.join(tmp_dir, 'artifacts', host.SYSTEM, 'x86_64', self.BUILD_LEVEL)
    result = self.run_script(command, cwd = cwd)
    artifacts = file_find.find(artifacts_dir)
    droppings = file_find.find(tmp_dir)
    if result.exit_code != 0 or self.DEBUG:
      print(result.stdout)
    return self._test_context(tmp_dir, command, result, artifacts_dir, artifacts, droppings)
  
if __name__ == '__main__':
  script_unit_test.main()
