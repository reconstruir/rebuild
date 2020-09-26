#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test
from rebuild.native_package.native_package import native_package
from bes.testing.unit_test_skip import skip_if
from bes.system.host import host

class test_native_package(unit_test):

  @skip_if(not host.is_macos(), 'not macos')
  def test_is_installed_macos(self):
    np = native_package()
    self.assertFalse( np.is_installed('bash') )
    self.assertTrue( np.is_installed('com.apple.pkg.Core') )
  
  @skip_if(not host.is_linux(), 'not linux')
  def test_is_installed_linux(self):
    np = native_package()
    self.assertTrue( np.is_installed('bash') )
    self.assertFalse( np.is_installed('com.apple.pkg.Core') )
  
  @skip_if(not host.is_linux(), 'not linux')
  def test_owner(self):
    np = native_package()
    self.assertEqual( 'coreutils', np.owner('/bin/ls') )
    self.assertEqual( 'bash', np.owner('/bin/bash') )
  
  def test_installed_packages(self):
    np = native_package()
    self.assertTrue( len(np.installed_packages()) > 0 )
  
if __name__ == '__main__':
  unit_test.main()
