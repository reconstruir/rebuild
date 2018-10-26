#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from collections import namedtuple

from bes.testing.unit_test import script_unit_test
from bes.system import os_env, execute
from bes.fs import file_util, temp_file
from rebuild.package import artifact_manager
from rebuild.package.fake_package_unit_test import fake_package_unit_test as FPUT
from rebuild.base import build_target as BT

class test_remanager(script_unit_test):

  TEST_BUILD_TARGET = BT.parse_path('linux-ubuntu-18/x86_64/release')

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/remanager'
  __script__ = __file__, '../../bin/remanager.py'

  DEBUG = False
#  DEBUG = True

  def test_simple_config(self):
    config = '''
[common]
artifacts_dir: /somewhere/not/there
[test1]
description: water only
packages: water
[test2]
description: fiber only
packages: fiber
'''
    test = self._setup_test(config)
    args = [
      'packages',
      'update',
      '--artifacts', test.artifact_manager.root_dir,
      '--root-dir', test.tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )

    args = [
      'packages',
      'print',
      '--root-dir', test.tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( [ 'water' ], rv.stdout.split('\n') )

  def test_update_first_time(self):
    config = '''
[common]
artifacts_dir: /somewhere/not/there
[test1]
description: test1
packages: orange_juice
[test2]
description: test2
packages: apple pear_juice
'''
    test = self._setup_test(config)
    args = [
      'packages',
      'update',
      '--artifacts', test.artifact_manager.root_dir,
      '--root-dir', test.tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )

    args = [
      'packages',
      'print',
      '--root-dir', test.tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( [ 'citrus', 'fiber', 'fructose', 'fruit', 'orange', 'orange_juice', 'water' ], rv.stdout.split('\n') )

  def test_update_two_times(self):
    config = '''
[common]
artifacts_dir: /somewhere/not/there
[test1]
description: test1
packages: orange_juice
'''
    test = self._setup_test(config)
    args = [
      'packages',
      'update',
      '--artifacts', test.artifact_manager.root_dir,
      '--root-dir', test.tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    args = [
      'packages',
      'print',
      '--root-dir', test.tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( [ 'citrus', 'fiber', 'fructose', 'fruit', 'orange', 'orange_juice', 'water' ], rv.stdout.split('\n') )
    config = '''
[common]
artifacts_dir: /somewhere/not/there
[test1]
description: test1
packages: orange_juice pear_juice
'''
    file_util.save(path.join(test.tmp_dir, 'config'), content = config)
    args = [
      'packages',
      'update',
      '--artifacts', test.artifact_manager.root_dir,
      '--root-dir', test.tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    args = [
      'packages',
      'print',
      '--root-dir', test.tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( [ 'citrus', 'fiber', 'fructose', 'fruit', 'orange', 'orange_juice', 'pear', 'pear_juice', 'water' ], rv.stdout.split('\n') )

  def test_update_script(self):
    config = '''
[common]
artifacts_dir: /somewhere/not/there
[test1]
description: test1
packages: orange_juice
'''
    test = self._setup_test(config)
    args = [
      'packages',
      'update',
      '--artifacts', test.artifact_manager.root_dir,
      '--root-dir', test.tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    args = [
      'packages',
      'print',
      '--root-dir', test.tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( [ 'citrus', 'fiber', 'fructose', 'fruit', 'orange', 'orange_juice', 'water' ], rv.stdout.split('\n') )
    config = '''
[common]
artifacts_dir: /somewhere/not/there
[test1]
description: test1
packages: orange_juice pear_juice
'''
    file_util.save(path.join(test.tmp_dir, 'config'), content = config)
    cmd = [
      path.join(test.tmp_dir, 'update.sh'),
      'test1'
    ]
    env = os_env.make_clean_env(keep_keys = [ 'PYTHONPATH' ],
                                update = { 'PATH': path.dirname(self.script) })
    rv = execute.execute(cmd, raise_error = False, env = env, stderr_to_stdout = True)
    if rv.exit_code != 0 or self.DEBUG:
      self.spew(rv.stdout)
    self.assertEqual( 0, rv.exit_code )
    args = [
      'packages',
      'print',
      '--root-dir', test.tmp_dir,
      '--system', 'linux',
      '--level', 'release',
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( [ 'citrus', 'fiber', 'fructose', 'fruit', 'orange', 'orange_juice', 'pear', 'pear_juice', 'water' ], rv.stdout.split('\n') )

  @classmethod
  def _make_temp_dir(clazz):
    tmp_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    if clazz.DEBUG:
      print("tmp_dir: ", tmp_dir)
    return tmp_dir

  @classmethod
  def _make_test_artifact_manager(clazz):
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    return FPUT.make_artifact_manager(debug = clazz.DEBUG,
                                      recipes = FPUT.TEST_RECIPES,
                                      build_target = clazz.TEST_BUILD_TARGET,
                                      mutations = mutations)

  _setup = namedtuple('_setup', 'tmp_dir, artifact_manager')
  @classmethod
  def _setup_test(clazz, config):
    tmp_dir = clazz._make_temp_dir()
    am = clazz._make_test_artifact_manager()
    file_util.save(path.join(tmp_dir, 'config'), content = config)
    return clazz._setup(tmp_dir, am)
    
if __name__ == '__main__':
  script_unit_test.main()
