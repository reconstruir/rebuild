#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from collections import namedtuple

from bes.testing.unit_test import unit_test
from bes.system import os_env, execute
from bes.fs import file_util, temp_file

from rebuild.base import build_target as BT
from rebuild.venv.venv_config import venv_config
from rebuild.venv.venv_manager import venv_manager
from rebuild.venv.venv_install_options import venv_install_options

from _rebuild_testing.fake_package_recipes import fake_package_recipes as RECIPES
from _rebuild_testing.venv_tester import venv_tester

class test_venv_manager(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/remanager'

  DEBUG = False
#  DEBUG = True

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
    test = venv_tester(config, recipes = RECIPES.FOODS)
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
    test = venv_tester(config, recipes = RECIPES.FOODS)
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
    test = venv_tester(config1, recipes = RECIPES.FOODS)
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
    test = venv_tester(config1, recipes = RECIPES.FOODS)
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
    test = venv_tester(config1, recipes = RECIPES.FOODS)
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
    test = venv_tester(config1, recipes = RECIPES.FOODS)
    test.update_from_config('test')
    self.assertEqual( [ 'arsenic', 'mercury', 'water' ], test.installed_packages('test') )
    test.clear_project_from_config('test')
    self.assertEqual( [], test.installed_packages('test') )
    
  def test_packages_update_upgrade(self):
    recipes1 = '''
fake_package aflatoxin 1.0.9 0 0 linux release x86_64 ubuntu 18 none
'''
    recipes2 = '''
fake_package aflatoxin 1.0.10 0 0 linux release x86_64 ubuntu 18 none
'''
    config = '''{head}
projects
  test
    packages
      aflatoxin
'''
    test = venv_tester(config)

    test.add_recipes(recipes1)
    test.publish_artifacts(recipes1)
    
    test.update_from_config('test')
    self.assertEqual( [ 'aflatoxin-1.0.9' ], test.installed_packages('test', include_version = True) )

    test.add_recipes(recipes2)
    test.publish_artifacts(recipes2)

    test.update_from_config('test')
    self.assertEqual( [ 'aflatoxin-1.0.10' ], test.installed_packages('test', include_version = True) )
    
  def test_packages_update_downgrade(self):
    recipes1 = '''
fake_package aflatoxin 1.0.10 0 0 linux release x86_64 ubuntu 18 none
'''
    recipes2 = '''
fake_package aflatoxin 1.0.9 0 0 linux release x86_64 ubuntu 18 none
'''
    config = '''{head}
projects
  test
    packages
      aflatoxin
'''
    test = venv_tester(config)
    test.add_recipes(recipes1)
    test.publish_artifacts(recipes1)
    
    test.update_from_config('test')
    self.assertEqual( [ 'aflatoxin-1.0.10' ], test.installed_packages('test', include_version = True) )

    test.clear_artifacts()
    
    test.add_recipes(recipes2)
    test.publish_artifacts(recipes2)

    test.update_from_config('test', options = venv_install_options(allow_downgrade = False))
    self.assertEqual( [ 'aflatoxin-1.0.10' ], test.installed_packages('test', include_version = True) )

    test.update_from_config('test', options = venv_install_options(allow_downgrade = True))
    self.assertEqual( [ 'aflatoxin-1.0.9' ], test.installed_packages('test', include_version = True) )
    
  def test_packages_update_specific_version(self):
    recipes1 = '''
fake_package aflatoxin 1.0.0 0 0 linux release x86_64 ubuntu 18 none
fake_package aflatoxin 1.0.1 0 0 linux release x86_64 ubuntu 18 none
fake_package aflatoxin 1.0.2 0 0 linux release x86_64 ubuntu 18 none
'''
    config = '''{head}
projects
  test
    packages
      aflatoxin == 1.0.1
'''
    test = venv_tester(config, recipes = recipes1)
    test.update_from_config('test')
    self.assertEqual( [ 'aflatoxin-1.0.1' ], test.installed_packages('test', include_version = True) )

  def test_packages_missing_version(self):
    recipes1 = '''
fake_package aflatoxin 1.0.0 0 0 linux release x86_64 ubuntu 18 none
fake_package aflatoxin 1.0.2 0 0 linux release x86_64 ubuntu 18 none
'''
    config = '''{head}
projects
  test
    packages
      aflatoxin == 1.0.1
'''
    test = venv_tester(config, recipes = recipes1)
    rv = test.update_from_config('test')
    self.assertEqual( False, rv )
    self.assertEqual( [], test.installed_packages('test', include_version = True) )
    
  def test_none_distro(self):
    recipes1 = '''
fake_package kiwi 1.2.3 0 0 linux release x86_64 none none none
  files
    bin/kiwi_script.sh
      #!/bin/bash
      echo kiwi
'''
    config = '''{head}
projects
  test
    packages
      aflatoxin == 1.0.1
'''
    test = venv_tester(config, recipes = recipes1)
    rv = test.update_from_config('test')
    self.assertEqual( False, rv )
    self.assertEqual( [], test.installed_packages('test', include_version = True) )
    
if __name__ == '__main__':
  unit_test.main()
