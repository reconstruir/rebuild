#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import temp_file
from bes.system import host
from bes.common import Shell

class test_rebuilder_script(unit_test):

  __unit_test_data_dir__ = '../../lib/rebuild/test_data/rebuilder'

  DEBUG = False
  DEBUG = True

  REBUILDER_SCRIPT = path.abspath(path.join(path.dirname(__file__), '../rebuilder.py'))
  BUILD_LEVEL = 'release'

#  artifacts_dir = path.join(tmp_dir, 'artifacts', host.SYSTEM, 'x86_64', self.BUILD_LEVEL)
  
  def test_fructose(self):
    tmp_dir = self._make_temp_dir()
    cmd = [
      self.REBUILDER_SCRIPT,
      '--source-dir',
      path.join(self.data_dir(), '../packager'),
      '--no-network',
      '-v',
      '--root', tmp_dir,
      '--level', self.BUILD_LEVEL,
      'fructose',
    ]
    rv = self._call_shell(cmd)
    if rv.exit_code != 0:
      print((rv.stdout))
    self.assertEqual( 0, rv.exit_code )
    artifacts_dir = path.join(tmp_dir, 'artifacts', host.SYSTEM, 'x86_64', self.BUILD_LEVEL)
    self.assertTrue( path.exists(path.join(artifacts_dir, 'fructose-3.4.5-6.tar.gz')) )
    self.assertFalse( path.exists(path.join(artifacts_dir, 'fiber-1.0.0.tar.gz')) )
    
  def test_fructose_fiber(self):
    tmp_dir = self._make_temp_dir()
    cmd = [
      self.REBUILDER_SCRIPT,
      '--source-dir',
      path.join(self.data_dir(), '../packager'),
      '--no-network',
      '-v',
      '--root', tmp_dir,
      '--level', self.BUILD_LEVEL,
      'fructose',
      'fiber',
    ]
    rv = self._call_shell(cmd)
    if rv.exit_code != 0:
      print((rv.stdout))
    self.assertEqual( 0, rv.exit_code )
    artifacts_dir = path.join(tmp_dir, 'artifacts', host.SYSTEM, 'x86_64', self.BUILD_LEVEL)
    self.assertTrue( path.exists(path.join(artifacts_dir, 'fructose-3.4.5-6.tar.gz')) )
    self.assertTrue( path.exists(path.join(artifacts_dir, 'fiber-1.0.0.tar.gz')) )
    
  def xxxtest_orange(self):
    tmp_dir = self._make_temp_dir()
    cmd = [
      self.REBUILDER_SCRIPT,
      '--source-dir',
      path.join(self.data_dir(), '../packager'),
      '--no-network',
      '-v',
      '--root', tmp_dir,
      '--level', self.BUILD_LEVEL,
      'orange',
    ]
    rv = self._call_shell(cmd)
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

  def _call_shell(self, cmd):
    return Shell.execute(cmd, non_blocking = True, raise_error = False,
                         cwd = self.data_dir(), stderr_to_stdout = True)
    
if __name__ == '__main__':
  unit_test.main()
