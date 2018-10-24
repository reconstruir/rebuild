#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from bes.fs import temp_file
from bes.system import execute
from rebuild.package import artifact_manager
from rebuild.base import package_descriptor
from rebuild.tools_manager import tools_package_manager
from rebuild.package.unit_test_packages import unit_test_packages

class test_tools_package_manager(unittest.TestCase):

  DEBUG = False
#  DEBUG = True

  def __make_test_tpm(self):
    root_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    pm_dir = path.join(root_dir, 'package_manager')
    if self.DEBUG:
      print("\nroot_dir:\n", root_dir)
    return tools_package_manager(pm_dir)

  @classmethod
  def __make_test_artifact_manager(clazz):
    root_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    if clazz.DEBUG:
      print("root_dir:\n%s\n" % (root_dir))
    am = artifact_manager(root_dir)
    unit_test_packages.make_test_packages(unit_test_packages.TEST_PACKAGES, am.root_dir)
    unit_test_packages.publish_artifacts(am)
    return am

  def test_install_package(self):
    tpm = self.__make_test_tpm()
    am = self.__make_test_artifact_manager()
    package_info = package_descriptor.parse('water-1.0.0-0')
    tpm.install_package(package_info, am)
    bin_dir = tpm.bin_dir(package_info)

  def test_tool_exe(self):
    tpm = self.__make_test_tpm()
    am = self.__make_test_artifact_manager()
    package_info = package_descriptor.parse('water-1.0.0-0')
    tpm.install_package(package_info, am)
    tool_name = package_info.name + '_script.sh'
    exe = tpm.tool_exe(package_info, tool_name)
    rv = execute.execute(exe)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( package_info.full_name, rv.stdout.strip() )

  def test_tool_exe_missing(self):
    tpm = self.__make_test_tpm()
    am = self.__make_test_artifact_manager()
    package_info = package_descriptor.parse('water-1.0.0-0')
    tpm.install_package(package_info, am)
    exe = tpm.tool_exe(package_info, 'notthere')
    self.assertEqual( None, exe )

  def test_uninstall_package(self):
    tpm = self.__make_test_tpm()
    am = self.__make_test_artifact_manager()
    package_info = package_descriptor.parse('water-1.0.0-0')
    tpm.install_package(package_info, am)
    tool_name = package_info.name + '_script.sh'
    exe = tpm.tool_exe(package_info, tool_name)
    self.assertTrue( exe != None )
    tpm.uninstall(package_info)

    with self.assertRaises(RuntimeError) as context:
      tpm.tool_exe(package_info, tool_name)

  def test_list_all(self):
    tpm = self.__make_test_tpm()
    am = self.__make_test_artifact_manager()
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
  unittest.main()

