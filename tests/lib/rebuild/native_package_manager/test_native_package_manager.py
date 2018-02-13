#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test
from rebuild.native_package_manager import native_package_manager
from bes.testing.unit_test.unit_test_skip import skip_if
from bes.system import host

class test_native_package_manager(unit_test):

  @skip_if(not host.is_macos(), 'not macos')
  def test_is_installed_macos(self):
    self.assertFalse( native_package_manager.is_installed('bash') )
    self.assertTrue( native_package_manager.is_installed('com.apple.pkg.Core') )
  
  @skip_if(not host.is_linux(), 'not linux')
  def test_is_installed_linux(self):
    self.assertTrue( native_package_manager.is_installed('bash') )
    self.assertFalse( native_package_manager.is_installed('com.apple.pkg.Core') )
  
  @skip_if(not host.is_linux(), 'not linux')
  def test_owner(self):
    self.assertEqual( 'coreutils', native_package_manager.owner('/bin/ls') )
    self.assertEqual( 'bash', native_package_manager.owner('/bin/bash') )
  
  def test_installed_packages(self):
    self.assertTrue( len(native_package_manager.installed_packages()) > 0 )
  
if __name__ == '__main__':
  unit_test.main()
