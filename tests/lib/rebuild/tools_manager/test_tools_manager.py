#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, unittest
from bes.fs import temp_file
from bes.testing.unit_test import unit_test
from bes.system import execute
from rebuild.base import build_target, build_system, build_level, package_descriptor
from rebuild.tools_manager import tools_manager
from _rebuild_testing.fake_package_unit_test import fake_package_unit_test as FPUT
from _rebuild_testing.fake_package_recipes import fake_package_recipes as RECIPES

class test_tools_manager(unit_test):

  DEBUG = unit_test.DEBUG
  #DEBUG = True

  TEST_BUILD_TARGET = build_target.parse_path('linux-ubuntu-18/x86_64/release')

  def _make_test_tm(self):
    root_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    tools_dir = path.join(root_dir, 'tools')
    if self.DEBUG:
      print("\ntools_dir:\n", tools_dir)
    return tools_manager(tools_dir, self.TEST_BUILD_TARGET)

  def test_update(self):
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    am = FPUT.make_artifact_manager(self.DEBUG, RECIPES.FOODS, self.TEST_BUILD_TARGET, mutations)
    tm = self._make_test_tm()
    packages = [
      package_descriptor.parse('water-1.0.0-0'),
      package_descriptor.parse('mercury-1.2.8-0'),
      package_descriptor.parse('arsenic-1.2.9-0'),
    ]
    tm.update(packages, am)

  def test_install_and_use_a_tool(self):
    recipe = '''
fake_package mytool 1.2.3 1 0 linux release x86_64 ubuntu 18
  files
    bin/mytool.sh
      \#!/bin/bash
      echo mytool.sh
      exit 0
'''
    tm = self._make_test_tm()
    bt = build_target.parse_path('linux-ubuntu-18/x86_64/release')
    am = FPUT.make_artifact_manager()
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    tmp_tarball = FPUT.create_one_package(recipe, mutations)
    am.publish(tmp_tarball, bt, False, None)
    desc = package_descriptor.parse('mytool-1.2.3-1')
    packages = [
      desc
    ]
    tm.update(packages, am)
    tool_name = 'mytool.sh'
    exe = tm.tool_exe(desc, 'mytool.sh')
    rv = execute.execute(exe)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'mytool.sh', rv.stdout.strip() )

if __name__ == '__main__':
  unit_test.main()
