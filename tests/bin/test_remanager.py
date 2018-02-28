#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import script_unit_test
from bes.system import os_env, execute
from bes.fs import file_util, temp_file
from rebuild.package import artifact_manager
from rebuild.package.unit_test_packages import unit_test_packages

class test_remanager(script_unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/remanager'
  __script__ = __file__, '../../bin/remanager.py'

  DEBUG = False
#g  DEBUG = True
  
  def test_update_first_time(self):
    tmp_dir = self._make_temp_dir()
    am = self._make_test_artifact_manager()
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
    file_util.save(path.join(tmp_dir, 'config'), content = config)
    args = [
      'packages',
      'update',
      '--artifacts', am.publish_dir,
      '--root-dir', tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )

    args = [
      'packages',
      'print',
      '--root-dir', tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( [ 'citrus', 'fiber', 'fructose', 'fruit', 'orange', 'orange_juice', 'water' ], rv.stdout.split('\n') )

  def test_update_two_times(self):
    tmp_dir = self._make_temp_dir()
    am = self._make_test_artifact_manager()
    config = '''
[common]
artifacts_dir: /somewhere/not/there
[test1]
description: test1
packages: orange_juice
'''
    file_util.save(path.join(tmp_dir, 'config'), content = config)
    args = [
      'packages',
      'update',
      '--artifacts', am.publish_dir,
      '--root-dir', tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    args = [
      'packages',
      'print',
      '--root-dir', tmp_dir,
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
    file_util.save(path.join(tmp_dir, 'config'), content = config)
    args = [
      'packages',
      'update',
      '--artifacts', am.publish_dir,
      '--root-dir', tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    args = [
      'packages',
      'print',
      '--root-dir', tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( [ 'citrus', 'fiber', 'fructose', 'fruit', 'orange', 'orange_juice', 'pear', 'pear_juice', 'water' ], rv.stdout.split('\n') )

  def test_update_script(self):
    tmp_dir = self._make_temp_dir()
    am = self._make_test_artifact_manager()
    config = '''
[common]
artifacts_dir: /somewhere/not/there
[test1]
description: test1
packages: orange_juice
'''
    file_util.save(path.join(tmp_dir, 'config'), content = config)
    args = [
      'packages',
      'update',
      '--artifacts', am.publish_dir,
      '--root-dir', tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    args = [
      'packages',
      'print',
      '--root-dir', tmp_dir,
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
    file_util.save(path.join(tmp_dir, 'config'), content = config)
    cmd = [
      path.join(tmp_dir, 'update.sh'),
      'test1'
    ]
    env = os_env.make_clean_env(keep_keys = [ 'PYTHONPATH' ],
                                update = { 'PATH': path.dirname(self.script) })
    rv = execute.execute(cmd, raise_error = False, env = env)
    self.assertEqual( 0, rv.exit_code )
    args = [
      'packages',
      'print',
      '--root-dir', tmp_dir,
      'test1'
    ]
    rv = self.run_script(args)
    self.assertEqual( [ 'citrus', 'fiber', 'fructose', 'fruit', 'orange', 'orange_juice', 'pear', 'pear_juice', 'water' ], rv.stdout.split('\n') )

  def _make_temp_dir(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print("tmp_dir: ", tmp_dir)
    return tmp_dir

  @classmethod
  def _make_test_artifact_manager(clazz):
    publish_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    if clazz.DEBUG:
      print("publish_dir:\n%s\n" % (publish_dir))
    am = artifact_manager(publish_dir, address = None, no_git = True)
    unit_test_packages.make_test_packages(unit_test_packages.TEST_PACKAGES, am.publish_dir)
    return am
  
if __name__ == '__main__':
  script_unit_test.main()
