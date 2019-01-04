#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from collections import namedtuple

from bes.testing.unit_test import unit_test
from bes.system import os_env, execute
from bes.fs import file_util, temp_file
from _rebuild_testing.fake_package_unit_test import fake_package_unit_test as FPUT
from _rebuild_testing.fake_package_recipes import fake_package_recipes as RECIPES
from rebuild.base import build_target as BT

from rebuild.venv.venv_config import venv_config
from rebuild.venv.venv_manager import venv_manager
from rebuild.venv.venv_install_options import venv_install_options
  
class test_manager(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/remanager'

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
    self.assertEqual( [], test.installed_packages('test1') )

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
    test.update_from_config('test1')
    self.assertEqual( [ 'water' ], test.installed_packages('test1') )

  def test_packages_update_add_packages(self):
    config1 = '''{head}
projects
  test
    packages
      water
'''
    config2 = '''{head}
projects
  test
    packages
      water fiber
'''
    config3 = '''{head}
projects
  test
    packages
      water fiber orange_juice
'''
    test = self._setup_test(config1)
    test.update_from_config('test')
    self.assertEqual( [ 'water' ], test.installed_packages('test') )

    test.rewrite_config(config2)
    test.update_from_config('test')
    self.assertEqual( [ 'fiber', 'water' ], test.installed_packages('test') )

    test.rewrite_config(config3)
    test.update_from_config('test')
    self.assertEqual( [ 'citrus', 'fiber', 'fructose', 'fruit', 'orange', 'orange_juice', 'water' ], test.installed_packages('test') )
    
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
    test.update_from_config('test')
    self.assertEqual( [ 'citrus', 'fiber', 'fructose', 'fruit', 'orange', 'orange_juice', 'water' ], test.installed_packages('test') )

    test.rewrite_config(config2)
    test.update_from_config('test')
    self.assertEqual( [ 'fiber', 'fructose', 'fruit', 'pear', 'pear_juice', 'water' ], test.installed_packages('test') )

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
    test.update_from_config('test')
    self.assertEqual( [ 'arsenic', 'mercury', 'water' ], test.installed_packages('test') )

    test.rewrite_config(config2)
    test.update_from_config('test')
    self.assertEqual( [ 'arsenic', 'mercury' ], test.installed_packages('test') )
    
    test.rewrite_config(config3)
    test.update_from_config('test')
    self.assertEqual( [ 'arsenic' ], test.installed_packages('test') )

    test.rewrite_config(config4)
    test.update_from_config('test')
    self.assertEqual( [], test.installed_packages('test') )

  def test_packages_clear(self):
    config1 = '''{head}
projects
  test
    packages
      arsenic mercury water
'''
    test = self._setup_test(config1)
    test.update_from_config('test')
    self.assertEqual( [ 'arsenic', 'mercury', 'water' ], test.installed_packages('test') )
    test.clear_project_from_config('test')
    self.assertEqual( [], test.installed_packages('test') )
    
  def test_packages_update_upgrade(self):
    recipes1 = '''
fake_package aflatoxin 1.0.9 0 0 linux release x86_64 ubuntu 18
'''
    recipes2 = '''
fake_package aflatoxin 1.0.10 0 0 linux release x86_64 ubuntu 18
'''
    config = '''{head}
projects
  test
    packages
      aflatoxin
'''
    test = self._setup_test(config, recipes = recipes1)
    test.update_from_config('test')
    self.assertEqual( [ 'aflatoxin-1.0.9' ], test.installed_packages('test', include_version = True) )

    test.publish_artifacts(recipes2)

    test.update_from_config('test')
    self.assertEqual( [ 'aflatoxin-1.0.10' ], test.installed_packages('test', include_version = True) )

  def test_packages_update_downgrade(self):
    recipes1 = '''
fake_package aflatoxin 1.0.10 0 0 linux release x86_64 ubuntu 18
'''
    recipes2 = '''
fake_package aflatoxin 1.0.9 0 0 linux release x86_64 ubuntu 18
'''
    config = '''{head}
projects
  test
    packages
      aflatoxin
'''
    test = self._setup_test(config, recipes = recipes1)
    test.update_from_config('test')
    self.assertEqual( [ 'aflatoxin-1.0.10' ], test.installed_packages('test', include_version = True) )

    test.clear_artifacts()
    test.publish_artifacts(recipes2)

    test.update_from_config('test', options = venv_install_options(allow_downgrade = False))
    self.assertEqual( [ 'aflatoxin-1.0.10' ], test.installed_packages('test', include_version = True) )

    test.update_from_config('test', options = venv_install_options(allow_downgrade = True))
    self.assertEqual( [ 'aflatoxin-1.0.9' ], test.installed_packages('test', include_version = True) )

    
  def xtest_packages_update_specific_version(self):
    recipes1 = '''
fake_package aflatoxin 1.0.0 0 0 linux release x86_64 ubuntu 18
fake_package aflatoxin 1.0.1 0 0 linux release x86_64 ubuntu 18
fake_package aflatoxin 1.0.2 0 0 linux release x86_64 ubuntu 18
'''
    config = '''{head}
projects
  test
    packages
      aflatoxin == 1.0.1
'''
    test = self._setup_test(config, recipes = recipes1)
    test.update_from_config('test')
    self.assertEqual( [ 'aflatoxin-1.0.1' ], test.installed_packages('test', include_version = True) )
    
  @classmethod
  def _make_temp_dir(clazz):
    tmp_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    if clazz.DEBUG:
      print("tmp_dir: ", tmp_dir)
    return tmp_dir

  @classmethod
  def _make_test_artifact_manager(clazz, recipes = None):
    recipes = recipes or RECIPES.FOODS
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    return FPUT.make_artifact_manager(debug = clazz.DEBUG,
                                      recipes = recipes,
                                      mutations = mutations)

  @classmethod
  def _setup_test(clazz, config, recipes = None):
    root_dir = clazz._make_temp_dir()
    am = clazz._make_test_artifact_manager(recipes = recipes)
    config_filename = path.join(root_dir, 'config.revenv')
    clazz._write_config_file(config_filename, config, am)

    bt = BT.parse_path('linux-ubuntu-18/x86_64/release')
    config_obj = venv_config.load(config_filename, bt)
    vm = venv_manager(config_obj, am, bt, root_dir)
    return _test_context(root_dir, config_filename, am, vm, bt)
    
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
      '--system', 'linux',
      '--distro', 'ubuntu',
      '--distro-version', '18',
      '--level', 'release',
      'unit_test_storage',
    ] + list(args)
  
  @classmethod
  def _parse_stdout_list(clazz, s):
    return [ x.strip() for x in s.split('\n') if x.strip() ]


class _test_context(namedtuple('_test_context', 'tmp_dir, config_filename, artifact_manager, manager, build_target')):

  def __new__(clazz, tmp_dir, config_filename, artifact_manager, manager, build_target):
    return clazz.__bases__[0].__new__(clazz, tmp_dir, config_filename, artifact_manager, manager, build_target)

  def installed_packages(self, project_name, include_version = False):
    return self.manager.installed_packages_names(project_name, self.build_target, include_version = include_version)

  def update_from_config(self, project_name, options = None):
    return self.manager.update_from_config(project_name, self.build_target, options = options)

  def clear_project_from_config(self, project_name):
    return self.manager.clear_project_from_config(project_name, self.build_target)
  
  def rewrite_config(self, config):
    config_head = test_manager._HEAD_TEMPLATE.format(artifacts_dir = self.artifact_manager._root_dir)
    content = config.format(head = config_head)
    file_util.save(self.config_filename, content = content)
    config_obj = venv_config.load(self.config_filename, self.build_target)
    self.manager._config = config_obj

  def publish_artifacts(self, recipes):
    FPUT.artifact_manager_publish(self.artifact_manager, recipes = recipes)
    
  def clear_artifacts(self):
    FPUT.artifact_manager_clear(self.artifact_manager)
    
if __name__ == '__main__':
  unit_test.main()
