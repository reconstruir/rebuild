#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.testing.unit_test import unit_test
from bes.fs import temp_file
from bes.system import execute
from rebuild.package import artifact_manager
from rebuild.base import build_target, package_descriptor
from rebuild.tools_manager import tools_package_manager
from _rebuild_testing.fake_package_unit_test import fake_package_unit_test as FPUT
from rebuild.base import build_target as BT

class test_tools_package_manager(unit_test):

  DEBUG = unit_test.DEBUG
  #DEBUG = True

  TEST_BUILD_TARGET = BT.parse_path('linux-ubuntu-18/x86_64/release')

  @classmethod
  def _make_test_tpm(clazz):
    root_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    pm_dir = path.join(root_dir, 'package_manager')
    if clazz.DEBUG:
      print("\nroot_dir:\n", root_dir)
    return tools_package_manager(pm_dir, clazz.TEST_BUILD_TARGET)

  @classmethod
  def _make_test_artifact_manager(clazz):
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    return FPUT.make_artifact_manager(debug = clazz.DEBUG,
                                      recipes = FPUT.TEST_RECIPES,
                                      build_target = clazz.TEST_BUILD_TARGET,
                                      mutations = mutations)

  def test_install_package(self):
    tpm = self._make_test_tpm()
    am = self._make_test_artifact_manager()
    package_info = package_descriptor.parse('water-1.0.0-0')
    tpm.install_package(package_info, am)
    bin_dir = tpm.bin_dir(package_info)

  def test_tool_exe(self):
    tpm = self._make_test_tpm()
    am = self._make_test_artifact_manager()
    package_info = package_descriptor.parse('knife-1.0.0-0')
    tpm.install_package(package_info, am)
    tool_name = 'cut.sh'
    exe = tpm.tool_exe(package_info, tool_name)
    rv = execute.execute(exe)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'cut', rv.stdout.strip() )

  def test_tool_exe_missing(self):
    tpm = self._make_test_tpm()
    am = self._make_test_artifact_manager()
    package_info = package_descriptor.parse('water-1.0.0-0')
    tpm.install_package(package_info, am)
    exe = tpm.tool_exe(package_info, 'notthere')
    self.assertEqual( None, exe )

  def test_uninstall_package(self):
    tpm = self._make_test_tpm()
    am = self._make_test_artifact_manager()
    package_info = package_descriptor.parse('knife-1.0.0-0')
    tpm.install_package(package_info, am)
    tool_name = 'cut.sh'
    exe = tpm.tool_exe(package_info, tool_name)
    self.assertTrue( exe != None )
    tpm.uninstall(package_info)

    with self.assertRaises(RuntimeError) as context:
      tpm.tool_exe(package_info, tool_name)

  def test_list_all(self):
    tpm = self._make_test_tpm()
    am = self._make_test_artifact_manager()
    packages = [
      package_descriptor.parse('water-1.0.0-0'),
      package_descriptor.parse('water-1.0.0-1'),
      package_descriptor.parse('water-1.0.0-2'),
      package_descriptor.parse('mercury-1.2.8-0'),
      package_descriptor.parse('mercury-1.2.8-1'),
      package_descriptor.parse('mercury-1.2.9-0'),
      package_descriptor.parse('arsenic-1.2.9-0'),
      package_descriptor.parse('arsenic-1.2.9-1'),
      package_descriptor.parse('arsenic-1.2.10-0'),
    ]
    tpm.install_packages(packages, am)

    self.assertTrue( packages, tpm.list_all() )
    
if __name__ == '__main__':
  unit_test.main()
