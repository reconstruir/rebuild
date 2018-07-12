#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.testing.unit_test import unit_test
from rebuild.base import build_arch as BA, build_system as BS, build_target as BT, build_level as BL

class test_build_target(unit_test):

  def test_build_path(self):
    self.assertEqual( 'macos/x86_64/release', BT(BS.MACOS).build_path )
    self.assertEqual( 'macos/x86_64/debug', BT(BS.MACOS, BL.DEBUG).build_path )
    self.assertEqual( 'macos/x86_64/release', BT(BS.MACOS, BT.DEFAULT).build_path )
    self.assertEqual( 'linux/x86_64/release', BT(BS.LINUX, archs = 'x86_64').build_path )
    self.assertEqual( 'ios/arm64-armv7/release', BT(BS.IOS).build_path )
    self.assertEqual( 'ios/arm64/release', BT(BS.IOS, archs = [ BA.ARM64 ]).build_path )

  def test_parse_expression(self):
    F = self._parse_exp
    self.assertTrue( F('macos/x86_64/release', '$system == MACOS and $level == RELEASE') )
    self.assertFalse( F('macos/x86_64/release', '$system == MACOS and $level != RELEASE') )
    self.assertTrue( F('linux.raspbian/x86_64/release', '$system == LINUX and $distro == RASPBIAN') )
    self.assertFalse( F('linux.raspbian/x86_64/release', '$system is MACOS or ($system is LINUX and $distro is not RASPBIAN)') )
    self.assertTrue( F('macos/x86_64/release', '$system is MACOS or ($system is LINUX and $distro is not RASPBIAN)') )
    self.assertTrue( F('macos/x86_64/debug', '$system is MACOS or ($system is LINUX and $distro is not RASPBIAN)') )
    self.assertTrue( F('linux/x86_64/release', '$system is MACOS or ($system is LINUX and $distro is not RASPBIAN)') )
    self.assertTrue( F('linux/x86_64/debug', '$system is MACOS or ($system is LINUX and $distro is not RASPBIAN)') )
    
  def _parse_exp(self, bt_path, exp):
    return BT.parse_path(bt_path).parse_expression(exp)

  def test_parse_path(self):
    self.assertEqual( BT(system = BS.MACOS, level = BL.RELEASE), BT.parse_path('macos/x86_64/release') )
    self.assertEqual( BT(system = BS.MACOS, level = BL.DEBUG), BT.parse_path('macos/x86_64/debug') )
    self.assertEqual( BT(system = BS.LINUX, level = BL.RELEASE, archs = 'x86_64'), BT.parse_path('linux/x86_64/release') )
    self.assertEqual( BT(system = BS.LINUX, level = BL.DEBUG, archs = 'x86_64'), BT.parse_path('linux/x86_64/debug') )
    self.assertEqual( BT(system = BS.LINUX, level = BL.DEBUG, archs = 'armv7', distro = BS.RASPBIAN), BT.parse_path('linux.raspbian/armv7/debug') )
    
if __name__ == '__main__':
  unit_test.main()
