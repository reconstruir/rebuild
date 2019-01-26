#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base import build_arch as BA, build_system as BS, build_target as BT, build_level as BL

class test_build_target(unit_test):

  def test_build_path(self):
    self.assertEqual( 'macos-10.10/x86_64/release', BT('macos', '', '10', '10', 'x86_64', 'release').build_path )
    self.assertEqual( 'macos-10/x86_64/release', BT('macos', '', '10', None, 'x86_64', 'release').build_path )
    self.assertEqual( 'linux-ubuntu-18/x86_64/release', BT('linux', 'ubuntu', '18', None, 'x86_64', 'release').build_path )
    self.assertEqual( 'ios-12/arm64-armv7/release', BT('ios', '', '12', None,  'armv7,arm64', 'release').build_path )
    self.assertEqual( 'ios-12/arm64-armv7/debug', BT('ios', '', '12', None, 'armv7,arm64', 'debug').build_path )
    self.assertEqual( 'ios-12/arm64/release', BT('ios', '', '12', None, 'arm64', 'release').build_path )
    self.assertEqual( 'ios-12/arm64/debug', BT('ios', '', '12', None, 'arm64', 'debug').build_path )
    self.assertEqual( 'macos/x86_64/release', BT('macos', '', '', None, 'x86_64', 'release').build_path )
    self.assertEqual( 'linux-ubuntu/x86_64/release', BT('linux', 'ubuntu', '', None, 'x86_64', 'release').build_path )
    
  def test_parse_path(self):
    self.assertEqual( BT('macos', '', '10', '', 'x86_64', 'release'), BT.parse_path('macos-10/x86_64/release') )
    self.assertEqual( BT('macos', '', '10', '10', 'x86_64', 'release'), BT.parse_path('macos-10.10/x86_64/release') )
    self.assertEqual( BT('linux', 'ubuntu', '18', None, 'x86_64', 'release'), BT.parse_path('linux-ubuntu-18/x86_64/release') )
    self.assertEqual( BT('linux', '', '', None, 'x86_64', 'release'), BT.parse_path('linux/x86_64/release') )
    self.assertEqual( BT('ios', '', '12', None, 'armv7,arm64', 'release'), BT.parse_path('ios-12/arm64-armv7/release') )
    self.assertEqual( BT('ios', '', '12', None, 'armv7,arm64', 'debug'), BT.parse_path('ios-12/arm64-armv7/debug') )
    self.assertEqual( BT('macos', '', '10', '', 'x86_64', 'debug'), BT.parse_path('macos-10/x86_64/debug') )
    self.assertEqual( BT('macos', '', '10', '', 'x86_64', 'release'), BT.parse_path('macos-10/x86_64') )
    
  def test_parse_expression(self):
    F = self._parse_exp
    self.assertTrue( F('macos-10.10/x86_64/release', '${system} == MACOS and ${level} == RELEASE') )
    self.assertFalse( F('macos-10.10/x86_64/release', '${system} == MACOS and ${level} != RELEASE') )
    self.assertTrue( F('linux-raspbian-9/x86_64/release', '${system} == LINUX and ${distro} == RASPBIAN') )
    self.assertFalse( F('linux-raspbian-9/x86_64/release', '${system} is MACOS or (${system} is LINUX and ${distro} is not RASPBIAN)') )
    self.assertTrue( F('macos-10.10/x86_64/release', '${system} is MACOS or (${system} is LINUX and ${distro} is not RASPBIAN)') )
    self.assertTrue( F('macos-10.10/x86_64/debug', '${system} is MACOS or (${system} is LINUX and ${distro} is not RASPBIAN)') )
    self.assertTrue( F('linux-ubuntu-18/x86_64/release', '${system} is MACOS or (${system} is LINUX and ${distro} is not RASPBIAN)') )
    self.assertTrue( F('linux-ubuntu-18/x86_64/debug', '${system} is MACOS or (${system} is LINUX and ${distro} is not RASPBIAN)') )

  def test_wildcard(self):
    self.assertEqual( 'macos-10.any/x86_64/any', BT('macos', '', '10', 'any', 'x86_64', 'any').build_path )

  def test_clone(self):
    p = BT.parse_path
    self.assertEqual( 'macos-10.10/x86_64/release',
                      p('macos-10.10/x86_64/release').clone().build_path )
    self.assertEqual( 'macos-10.10/x86_64/debug',
                      p('macos-10.10/x86_64/release').clone({ 'level': 'debug' }).build_path )
    self.assertEqual( 'macos-10.10/i386/release',
                      p('macos-10.10/x86_64/release').clone({ 'arch': 'i386' }).build_path )
    self.assertEqual( 'macos-10.10/i386/debug',
                      p('macos-10.10/x86_64/release').clone({ 'level': 'debug', 'arch': 'i386' }).build_path )

  def _parse_exp(self, bt_path, exp):
    return BT.parse_path(bt_path).parse_expression(exp)

if __name__ == '__main__':
  unit_test.main()
