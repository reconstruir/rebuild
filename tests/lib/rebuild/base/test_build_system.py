#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.testing.unit_test import unit_test
from rebuild.base import build_system as BT
  
class test_build_system(unit_test):

  def test_resolve_mask(self):
    self.assertEqual( 'android', BT.resolve_mask('android') )
    self.assertEqual( 'macos', BT.resolve_mask('macos') )
    self.assertEqual( 'ios', BT.resolve_mask('ios') )
    self.assertEqual( 'linux', BT.resolve_mask('linux') )
    self.assertEqual( 'android|ios', BT.resolve_mask('android|ios') )
    self.assertEqual( 'linux|macos', BT.resolve_mask('macos|linux') )
    self.assertEqual( 'android|ios|ios_sim|linux|macos', BT.resolve_mask('all') )
    self.assertEqual( 'none', BT.resolve_mask('') )
    self.assertEqual( 'none', BT.resolve_mask('none') )
    self.assertEqual( 'android|ios', BT.resolve_mask('mobile') )
    self.assertEqual( 'linux|macos', BT.resolve_mask('desktop') )
    self.assertEqual( 'ios|ios_sim|macos', BT.resolve_mask('darwin') )

  def test_resolve_mask_recursive(self):
    self.assertEqual( 'android|ios|ios_sim|linux|macos', BT.resolve_mask('darwin|desktop|mobile') )

  def test_parse_system(self):
    self.assertEqual( 'android', BT.parse_system('android') )
    self.assertEqual( 'ios', BT.parse_system('ios') )
    self.assertEqual( 'macos', BT.parse_system('macos') )
    self.assertEqual( 'linux', BT.parse_system('linux') )
    self.assertEqual( 'android', BT.parse_system('ANDROID') )
    self.assertEqual( 'ios', BT.parse_system('IOS') )
    self.assertEqual( 'macos', BT.parse_system('MACOS') )
    self.assertEqual( 'linux', BT.parse_system('LINUX') )

  def test_parse_system_invalid(self):
    with self.assertRaises(ValueError) as context:
      BT.parse_system('darwin')
    with self.assertRaises(ValueError) as context:
      BT.parse_system('DESKTOP')
    with self.assertRaises(ValueError) as context:
      BT.parse_system('MOBILE')
    with self.assertRaises(ValueError) as context:
      BT.parse_system('DARWIN')
    with self.assertRaises(ValueError) as context:
      BT.parse_system('ALL')
    with self.assertRaises(ValueError) as context:
      BT.parse_system('desktop')
    with self.assertRaises(ValueError) as context:
      BT.parse_system('mobile')
    with self.assertRaises(ValueError) as context:
      BT.parse_system('all')
    with self.assertRaises(ValueError) as context:
      BT.parse_system('linux|macos')
    with self.assertRaises(ValueError) as context:
      BT.parse_system('macos|linux')
    with self.assertRaises(ValueError) as context:
      BT.parse_system('LINUX|MACOS')
    with self.assertRaises(ValueError ) as context:
      BT.parse_system('MACOS|LINUX')
    
  def test_system_is_valid(self):
    self.assertEqual( True, BT.system_is_valid('linux') )
    self.assertEqual( True, BT.system_is_valid('macos') )
    self.assertEqual( True, BT.system_is_valid('ios') )
    self.assertEqual( True, BT.system_is_valid('ios_sim') )
    self.assertEqual( True, BT.system_is_valid('android') )
    self.assertEqual( False , BT.system_is_valid('mobile') )
    self.assertEqual( False , BT.system_is_valid('desktop') )
    self.assertEqual( False , BT.system_is_valid('darwin') )

  def test_match(self):
    self.assertEqual( True, BT.mask_matches('all', 'linux') )
    self.assertEqual( False, BT.mask_matches('macos', 'linux') )
    self.assertEqual( True, BT.mask_matches('linux|macos', 'macos') )
    self.assertEqual( True, BT.mask_matches('desktop', 'macos') )
    self.assertEqual( False, BT.mask_matches('mobile', 'macos') )

if __name__ == '__main__':
  unit_test.main()
