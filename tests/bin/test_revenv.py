#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from collections import namedtuple

from bes.testing.script_unit_test import script_unit_test
from bes.system.os_env import os_env
from bes.system.execute import execute
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from _rebuild_testing.fake_package_unit_test import fake_package_unit_test as FPUT
from _rebuild_testing.fake_package_recipes import fake_package_recipes as RECIPES
from rebuild.base.build_target import build_target as BT

class test_revenv(script_unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/remanager'
  __script__ = __file__, '../../bin/revenv.py'

  DEBUG = False
#  DEBUG = True

  _HEAD_TEMPLATE = '''\
!rebuild.revenv!
config
  storage
    name: unit_test_storage
    provider: local
    location: {artifacts_dir}
'''

  def test_packages_print_empty(self):
    config = '''{head}
projects
  test1
    packages
      water
  test2
    packages
      fiber
'''
    test = self._setup_test(config)
    args = self._make_packages_cmd('print', test.tmp_dir, 'test1')
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [], self._parse_stdout_list(rv.output) )

  def test_packages_update(self):
    config = '''{head}
projects
  test1
    packages
      water
  test2
    packages
      fiber
'''
    test = self._setup_test(config)
    args = self._make_packages_cmd('update', test.tmp_dir, 'test1')
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    args = self._make_packages_cmd('print', test.tmp_dir, 'test1')
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'water' ], self._parse_stdout_list(rv.output) )

  def test_packages_update_add_packages(self):
    config1 = '''{head}
projects
  test
    packages
      orange_juice
'''
    config2 = '''{head}
projects
  test
    packages
      orange_juice pear_juice
'''
    test = self._setup_test(config1)
    update_args = self._make_packages_cmd('update', test.tmp_dir, 'test')
    rv = self.run_script(update_args)
    self.assertEqual( 0, rv.exit_code )
    print_args = self._make_packages_cmd('print', test.tmp_dir, 'test')
    rv = self.run_script(print_args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'citrus', 'fiber', 'fructose', 'fruit', 'orange', 'orange_juice', 'water' ], self._parse_stdout_list(rv.output) )

    self._write_config_file(test.config_filename, config2, test.artifact_manager)

    rv = self.run_script(update_args)
    self.assertEqual( 0, rv.exit_code )
    rv = self.run_script(print_args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'citrus', 'fiber', 'fructose', 'fruit', 'orange', 'orange_juice', 'pear', 'pear_juice', 'water' ], self._parse_stdout_list(rv.output) )

  def test_packages_update_change_packages(self):
    config1 = '''{head}
projects
  test
    packages
      orange_juice
'''
    config2 = '''{head}
projects
  test
    packages
      pear_juice
'''
    test = self._setup_test(config1)
    update_args = self._make_packages_cmd('update', test.tmp_dir, 'test')
    rv = self.run_script(update_args)
    self.assertEqual( 0, rv.exit_code )
    print_args = self._make_packages_cmd('print', test.tmp_dir, 'test')
    rv = self.run_script(print_args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'citrus', 'fiber', 'fructose', 'fruit', 'orange', 'orange_juice', 'water' ], self._parse_stdout_list(rv.output) )

    self._write_config_file(test.config_filename, config2, test.artifact_manager)

    rv = self.run_script(update_args)
    self.assertEqual( 0, rv.exit_code )
    rv = self.run_script(print_args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'fiber', 'fructose', 'fruit', 'pear', 'pear_juice', 'water' ], self._parse_stdout_list(rv.output) )

  def test_packages_update_remove_packages(self):
    config1 = '''{head}
projects
  test
    packages
      arsenic mercury water
'''
    config2 = '''{head}
projects
  test
    packages
      arsenic mercury
'''
    config3 = '''{head}
projects
  test
    packages
      arsenic
'''
    config4 = '''{head}
projects
  test
    packages
'''
    test = self._setup_test(config1)
    update_args = self._make_packages_cmd('update', test.tmp_dir, 'test')
    rv = self.run_script(update_args)
    self.assertEqual( 0, rv.exit_code )
    print_args = self._make_packages_cmd('print', test.tmp_dir, 'test')
    rv = self.run_script(print_args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'arsenic', 'mercury', 'water' ], self._parse_stdout_list(rv.output) )

    self._write_config_file(test.config_filename, config2, test.artifact_manager)
    rv = self.run_script(update_args)
    self.assertEqual( 0, rv.exit_code )
    rv = self.run_script(print_args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'arsenic', 'mercury' ], self._parse_stdout_list(rv.output) )
    
    self._write_config_file(test.config_filename, config3, test.artifact_manager)
    rv = self.run_script(update_args)
    self.assertEqual( 0, rv.exit_code )
    rv = self.run_script(print_args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'arsenic' ], self._parse_stdout_list(rv.output) )

    self._write_config_file(test.config_filename, config4, test.artifact_manager)
    rv = self.run_script(update_args)
    self.assertEqual( 0, rv.exit_code )
    rv = self.run_script(print_args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [], self._parse_stdout_list(rv.output) )

  def test_packages_update_with_update_dot_sh(self):
    config1 = '''{head}
projects
  test
    packages
      orange_juice
'''
    config2 = '''{head}
projects
  test
    packages
      orange_juice pear_juice
'''
    test = self._setup_test(config1)
    update_args = self._make_packages_cmd('update', test.tmp_dir, 'test')
    rv = self.run_script(update_args)
    self.assertEqual( 0, rv.exit_code )
    print_args = self._make_packages_cmd('print', test.tmp_dir, 'test')
    rv = self.run_script(print_args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'citrus', 'fiber', 'fructose', 'fruit', 'orange', 'orange_juice', 'water' ], self._parse_stdout_list(rv.output) )
    self._write_config_file(test.config_filename, config2, test.artifact_manager)
    update_dot_sh = path.join(test.tmp_dir, 'update.sh')
    cmd = [
      update_dot_sh,
      'test',
      '--build-target', 'linux-ubuntu-18/x86_64/release',
    ]
    env = os_env.make_clean_env(keep_keys = [ 'PYTHONPATH' ],
                                update = { 'PATH': path.dirname(self.script) })
    rv = execute.execute(cmd, raise_error = False, env = env, stderr_to_stdout = True)
    if rv.exit_code != 0 or self.DEBUG:
      self.spew('update.sh command: %s' % (' '.join(cmd)))
      self.spew('update.sh script:\n----------\n%s\n----------\n' % (file_util.read(update_dot_sh)))
      self.spew(rv.output)
    self.assertEqual( 0, rv.exit_code )
    rv = self.run_script(print_args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'citrus', 'fiber', 'fructose', 'fruit', 'orange', 'orange_juice', 'pear', 'pear_juice', 'water' ], self._parse_stdout_list(rv.output) )
    
  def test_packages_clear(self):
    config1 = '''{head}
projects
  test
    packages
      arsenic mercury water
'''
    test = self._setup_test(config1)
    update_args = self._make_packages_cmd('update', test.tmp_dir, 'test')
    rv = self.run_script(update_args)
    self.assertEqual( 0, rv.exit_code )
    print_args = self._make_packages_cmd('print', test.tmp_dir, 'test')
    rv = self.run_script(print_args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'arsenic', 'mercury', 'water' ], self._parse_stdout_list(rv.output) )

    clear_args = self._make_packages_cmd('clear', test.tmp_dir, 'test')
    rv = self.run_script(clear_args)
    self.assertEqual( 0, rv.exit_code )
    rv = self.run_script(print_args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [], self._parse_stdout_list(rv.output) )
    
  def test_config_projects(self):
    config = '''{head}
projects
  test1
    packages
  test2
    packages
  test3
    packages
'''
    test = self._setup_test(config)
    args = self._make_config_cmd('projects', test.tmp_dir)
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'test1', 'test2', 'test3' ], self._parse_stdout_list(rv.output) )
    
  def test_config_packages(self):
    config = '''{head}
projects
  test1
    packages
      orange_juice
  test2
    packages
      pear_juice
      arsenic
'''
    test = self._setup_test(config)
    args = self._make_config_cmd('packages', test.tmp_dir, 'test1')
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'orange_juice' ], self._parse_stdout_list(rv.output) )

    args = self._make_config_cmd('packages', test.tmp_dir, 'test2')
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'arsenic', 'pear_juice' ], self._parse_stdout_list(rv.output) )

  def test_packages_update_upgrade(self):
    recipes1 = '''
fake_package aflatoxin 1.0.0 0 0 linux release x86_64 ubuntu 18 none
'''
    recipes2 = '''
fake_package aflatoxin 1.0.1 0 0 linux release x86_64 ubuntu 18 none
'''
    config = '''{head}
projects
  test
    packages
      aflatoxin
'''
    test = self._setup_test(config, recipes = recipes1)
    args = self._make_packages_cmd('update', test.tmp_dir, 'test')
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    args = self._make_packages_cmd('print', test.tmp_dir, 'test', '--versions')
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'aflatoxin-1.0.0' ], self._parse_stdout_list(rv.output) )

    FPUT.artifact_manager_publish(test.artifact_manager, recipes = recipes2)

    args = self._make_packages_cmd('update', test.tmp_dir, 'test')
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    args = self._make_packages_cmd('print', test.tmp_dir, 'test', '--versions')
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'aflatoxin-1.0.1' ], self._parse_stdout_list(rv.output) )

  def test_packages_update_specific_version(self):
    recipes1 = '''
fake_package aflatoxin 1.0.1 0 0 linux release x86_64 ubuntu 18 none
fake_package aflatoxin 1.0.11 0 0 linux release x86_64 ubuntu 18 none
fake_package aflatoxin 1.0.11 1 0 linux release x86_64 ubuntu 18 none
fake_package aflatoxin 1.0.2 0 0 linux release x86_64 ubuntu 18 none
fake_package aflatoxin 1.0.0 0 0 linux release x86_64 ubuntu 18 none
fake_package aflatoxin 1.0.9 0 0 linux release x86_64 ubuntu 18 none
fake_package aflatoxin 1.0.11 2 0 linux release x86_64 ubuntu 18 none
'''
    config = '''{head}
projects
  test
    packages
      aflatoxin == 1.0.11-1
'''
    test = self._setup_test(config, recipes = recipes1)
    args = self._make_packages_cmd('update', test.tmp_dir, 'test')
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    args = self._make_packages_cmd('print', test.tmp_dir, 'test', '--versions')
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'aflatoxin-1.0.11-1' ], self._parse_stdout_list(rv.output) )

  def test_packages_update_use_properties_file(self):
    recipes1 = '''
fake_package aflatoxin 1.0.10 0 0 linux release x86_64 ubuntu 18 none
fake_package aflatoxin 1.0.11 0 0 linux release x86_64 ubuntu 18 none
fake_package aflatoxin 1.0.12 1 0 linux release x86_64 ubuntu 18 none
'''
    config = '''{head}
projects
  test
    packages
      aflatoxin == ${{AFLATOXIN_VERSION}}
'''
    test = self._setup_test(config, recipes = recipes1)

    properties_content = '''\
AFLATOXIN_VERSION: 1.0.11
'''
    tmp_props = temp_file.make_temp_file(content = properties_content)
    
    args = self._make_packages_cmd('update', test.tmp_dir, 'test', '--properties-file', tmp_props)
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    args = self._make_packages_cmd('print', test.tmp_dir, 'test', '--versions')
    rv = self.run_script(args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'aflatoxin-1.0.11' ], self._parse_stdout_list(rv.output) )

  def test_version(self):
    rv = self.run_script(['version'])
    self.assertEqual( 0, rv.exit_code )
    version = rv.output.strip()
    self.assertTrue( len(version) > 0 )
    
  @classmethod
  def _make_temp_dir(clazz):
    tmp_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    if clazz.DEBUG:
      print("tmp_dir: ", tmp_dir)
    return tmp_dir

  @classmethod
  def _make_test_artifact_manager(clazz, recipes = None):
    recipes = recipes or RECIPES.FOODS
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version_major': '18', 'distro_version_minor': '' }
    return FPUT.make_artifact_manager(debug = clazz.DEBUG,
                                      recipes = recipes,
                                      mutations = mutations)

  _setup = namedtuple('_setup', 'tmp_dir, config_filename, artifact_manager')
  @classmethod
  def _setup_test(clazz, config, recipes = None):
    tmp_dir = clazz._make_temp_dir()
    am = clazz._make_test_artifact_manager(recipes = recipes)
    config_filename = path.join(tmp_dir, 'config.revenv')
    clazz._write_config_file(config_filename, config, am)
    return clazz._setup(tmp_dir, config_filename, am)
    
  @classmethod
  def _write_config_file(clazz, filename, config, artifact_manager):
    config_head = clazz._HEAD_TEMPLATE.format(artifacts_dir = artifact_manager._root_dir)
    content = config.format(head = config_head)
    file_util.save(filename, content = content)

  @classmethod
  def _make_packages_cmd(clazz, sub_command, root_dir, *args):
    return clazz._make_cmd('packages', sub_command, root_dir, *args)
  
  @classmethod
  def _make_config_cmd(clazz, sub_command, root_dir, *args):
    return clazz._make_cmd('config', sub_command, root_dir, *args)

  @classmethod
  def _make_cmd(clazz, command, sub_command, root_dir, *args):
    return [
      command,
      sub_command,
      root_dir,
      '--config', 'config.revenv',
      '--build-target', 'linux-ubuntu-18/x86_64/release',
      'unit_test_storage',
    ] + list(args)
  
  @classmethod
  def _parse_stdout_list(clazz, s):
    return [ x.strip() for x in s.split('\n') if x.strip() ]
  
if __name__ == '__main__':
  script_unit_test.main()
