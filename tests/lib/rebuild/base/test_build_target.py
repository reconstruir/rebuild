#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base.build_arch import build_arch as BA
from rebuild.base.build_level import build_level as BL
from rebuild.base.build_system import build_system as BS
from rebuild.base.build_target import build_target as BT

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
    self.assertEqual( 'linux/x86_64/release', BT('linux', 'none', '', None, 'x86_64', 'release').build_path )
    
  def test_parse_path(self):
    self.assertEqual( BT('macos', '', '10', '', 'x86_64', 'release'), BT.parse_path('macos-10/x86_64/release') )
    self.assertEqual( BT('macos', '', '10', '10', 'x86_64', 'release'), BT.parse_path('macos-10.10/x86_64/release') )
    self.assertEqual( BT('linux', 'ubuntu', '18', None, 'x86_64', 'release'), BT.parse_path('linux-ubuntu-18/x86_64/release') )
    self.assertEqual( BT('linux', '', '', None, 'x86_64', 'release'), BT.parse_path('linux/x86_64/release') )
    self.assertEqual( BT('ios', '', '12', None, 'armv7,arm64', 'release'), BT.parse_path('ios-12/arm64-armv7/release') )
    self.assertEqual( BT('ios', '', '12', None, 'armv7,arm64', 'debug'), BT.parse_path('ios-12/arm64-armv7/debug') )
    self.assertEqual( BT('macos', '', '10', '', 'x86_64', 'debug'), BT.parse_path('macos-10/x86_64/debug') )
    self.assertEqual( BT('macos', '', '10', '', 'x86_64', 'release'), BT.parse_path('macos-10/x86_64') )
    self.assertEqual( BT('linux', '', '', '', 'x86_64', 'release'), BT.parse_path('linux/x86_64') )
    self.assertEqual( BT('linux', '', '', '', 'x86_64', 'release'), BT.parse_path('linux/x86_64/release') )
    self.assertEqual( BT('linux', '', '', '', 'x86_64', 'debug'), BT.parse_path('linux/x86_64/debug') )
    
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

#  def test_wildcard(self):
#    # FIXME: wildcard doesnt work yet
#    self.assertEqual( 'macos-10.any/x86_64/any', BT('macos', '', '10', 'any', 'x86_64', 'any').build_path )
#    self.assertEqual( 'linux-any-any/x86_64/any', BT('linux', 'any', '', 'any', 'x86_64', 'any').build_path )

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

  def _match(self, a, b):
    return BT.parse_path(a).match(BT.parse_path(b))

  def test_match(self):
    self.assertTrue( self._match('macos-10.10/x86_64/release', 'macos-10.10/x86_64/release') )
    self.assertFalse( self._match('linux-ubuntu-18/x86_64/release', 'macos-10.10/x86_64/release') )
    self.assertTrue( self._match('linux-ubuntu-18/x86_64/release', 'linux-ubuntu-any/x86_64/release') )
    # FIXME: wildcard doesnt work yet
    #self.assertTrue( self._match('linux-ubuntu-18/x86_64/release', 'linux-any-any/x86_64/release') )
    #self.assertTrue( self._match('linux-fedora-29/x86_64/release', 'linux-any-any/x86_64/release') )
    #self.assertTrue( self._match('linux-fedora-29/x86_64/release', 'any-any-any/x86_64/release') )
    #self.assertTrue( self._match('macos-10/x86_64/release', 'any-any-any/x86_64/release') )
    
if __name__ == '__main__':
  unit_test.main()
