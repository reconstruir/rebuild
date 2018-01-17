#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import script_unit_test
from bes.fs import file_find, temp_file
from bes.system import host
from bes.common import Shell

class test_rebuilder_script(script_unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/rebuilder'
  __script__ = __file__, '../../bin/rebuilder.py'

  DEBUG = False
#  DEBUG = True

  BUILD_LEVEL = 'release'

#  artifacts_dir = path.join(tmp_dir, 'artifacts', host.SYSTEM, 'x86_64', self.BUILD_LEVEL)
  
  def test_fructose(self):
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
    rv = self.run_script(cmd, cwd = self.data_dir())
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
    if True: #rv.exit_code != 0:
      print('FAILED stderr:')
      print((rv.stderr))
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
    rv = self.run_script(cmd, cwd = self.data_dir())
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
    rv = self.run_script(cmd, cwd = self.data_dir())
    if rv.exit_code != 0:
      print((rv.stdout))
    self.assertEqual( 0, rv.exit_code )
    artifacts_dir = path.join(tmp_dir, 'artifacts', host.SYSTEM, 'x86_64', self.BUILD_LEVEL)
    self.assertTrue( path.exists(path.join(artifacts_dir, 'fructose-3.4.5-6.tar.gz')) )
    self.assertTrue( path.exists(path.join(artifacts_dir, 'fiber-1.0.0.tar.gz')) )
    self.assertTrue( path.exists(path.join(artifacts_dir, 'fiber-orange-6.5.4-3.tar.gz')) )

  def _make_temp_dir(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print("tmp_dir: ", tmp_dir)
    return tmp_dir

if __name__ == '__main__':
  script_unit_test.main()
