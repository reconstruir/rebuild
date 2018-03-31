#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import temp_file
from bes.system import execute
from rebuild.base import build_target, build_system, build_level, package_descriptor
from rebuild.package import artifact_manager
from rebuild.tools_manager import new_tools_manager as TM
from rebuild.package.unit_test_packages import unit_test_packages

class test_new_tools_manager(unit_test):

  DEBUG = False
#  DEBUG = True

  TEST_BUILD_TARGET = build_target(build_system.LINUX, build_level.RELEASE)

  def _make_test_tm(self):
    root_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    tools_dir = path.join(root_dir, 'tools')
    if self.DEBUG:
      print("\ntools_dir:\n", tools_dir)
    return TM(tools_dir)

  @classmethod
  def _make_test_artifact_manager(clazz):
    publish_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    if clazz.DEBUG:
      print("publish_dir:\n%s\n" % (publish_dir))
    am = artifact_manager(publish_dir, address = None, no_git = True)
    unit_test_packages.make_test_packages(unit_test_packages.TEST_PACKAGES, am.publish_dir)
    return am
  
  def test_update(self):
    tm = self._make_test_tm()
    am = self._make_test_artifact_manager()
    packages = [
      package_descriptor.parse('water-1.0.0-0'),
      package_descriptor.parse('mercury-1.2.8-0'),
      package_descriptor.parse('arsenic-1.2.9-0'),
    ]
    tm.update(packages, am)

  def test_install_and_use_a_tool(self):
    tm = self._make_test_tm()
    am = self._make_test_artifact_manager()
    water_desc = package_descriptor.parse('water-1.0.0-0')
    packages = [
      water_desc
    ]
    tm.update(packages, am)
    tool_name = water_desc.name + '_script.sh'
    exe = tm.tool_exe(water_desc, tool_name)
    rv = execute.execute(exe)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( water_desc.full_name, rv.stdout.strip() )

if __name__ == '__main__':
  unit_test.main()
