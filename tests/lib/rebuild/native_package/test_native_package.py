#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test
from rebuild.native_package.native_package import native_package
from bes.testing.unit_test_skip import skip_if
from bes.system.host import host

class test_native_package(unit_test):

  _MACOS_EXAMPLE_PKG = 'com.apple.pkg.Core'
  
  def test_installed_packages(self):
    np = native_package()
    self.assertTrue( len(np.installed_packages()) > 0 )

  @skip_if(not host.is_macos(), 'not macos')
  def test_package_manifest_macos(self):
    np = native_package()
    manifest = np.package_files(self._MACOS_EXAMPLE_PKG)
    self.assertTrue( '/bin/bash' in manifest )
    self.assertTrue( '/usr/bin/awk' in manifest )

  @skip_if(not host.is_macos(), 'not macos')
  def test_package_info_macos(self):
    np = native_package()
    info = np.package_info(self._MACOS_EXAMPLE_PKG)
    self.assertEqual( '/', info['volume'] )
    self.assertEqual( '/', info['install_location'] )
    self.assertEqual( 'com.apple.pkg.Core', info['package_id'] )
    
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

  @skip_if(not host.is_macos(), 'not macos')
  def test_owner_macos(self):
    np = native_package()
    self.assertTrue( np.owner('/bin/bash').startswith('com.apple.pkg.') )
    
  @skip_if(not host.is_linux(), 'not linux')
  def test_owner_linux(self):
    np = native_package()
    self.assertEqual( 'coreutils', np.owner('/bin/ls') )
    self.assertEqual( 'bash', np.owner('/bin/bash') )
  
  def test_installed_packages(self):
    np = native_package()
    self.assertTrue( len(np.installed_packages()) > 0 )
  
if __name__ == '__main__':
  unit_test.main()
