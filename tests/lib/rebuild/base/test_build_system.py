#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.testing.unit_test import unit_test
from rebuild.base.build_system import build_system as BS
  
class test_build_system(unit_test):

  def test_resolve_mask(self):
    self.assertEqual( 'android', BS.resolve_mask('android') )
    self.assertEqual( 'macos', BS.resolve_mask('macos') )
    self.assertEqual( 'windows', BS.resolve_mask('windows') )
    self.assertEqual( 'ios', BS.resolve_mask('ios') )
    self.assertEqual( 'linux', BS.resolve_mask('linux') )
    self.assertEqual( 'android|ios', BS.resolve_mask('android|ios') )
    self.assertEqual( 'linux|macos', BS.resolve_mask('macos|linux') )
    self.assertEqual( 'linux|macos|windows', BS.resolve_mask('macos|linux|windows') )
    self.assertEqual( 'android|ios|ios_sim|linux|macos|windows', BS.resolve_mask('all') )
    self.assertEqual( 'none', BS.resolve_mask('') )
    self.assertEqual( 'none', BS.resolve_mask('none') )
    self.assertEqual( 'android|ios', BS.resolve_mask('mobile') )
    self.assertEqual( 'linux|macos|windows', BS.resolve_mask('desktop') )
    self.assertEqual( 'ios|ios_sim|macos', BS.resolve_mask('darwin') )

  def test_resolve_mask_recursive(self):
    self.assertEqual( 'android|ios|ios_sim|linux|macos|windows', BS.resolve_mask('darwin|desktop|mobile') )

  def test_parse_system(self):
    self.assertEqual( 'android', BS.parse_system('android') )
    self.assertEqual( 'ios', BS.parse_system('ios') )
    self.assertEqual( 'macos', BS.parse_system('macos') )
    self.assertEqual( 'windows', BS.parse_system('windows') )
    self.assertEqual( 'linux', BS.parse_system('linux') )

  def test_parse_system_case(self):
    self.assertEqual( 'android', BS.parse_system('ANDROID') )
    self.assertEqual( 'ios', BS.parse_system('IOS') )
    self.assertEqual( 'macos', BS.parse_system('MACOS') )
    self.assertEqual( 'linux', BS.parse_system('LINUX') )
    self.assertEqual( 'windows', BS.parse_system('WINDOWS') )

  def test_parse_system_invalid(self):
    with self.assertRaises(ValueError) as context:
      BS.parse_system('darwin')
    with self.assertRaises(ValueError) as context:
      BS.parse_system('DESKTOP')
    with self.assertRaises(ValueError) as context:
      BS.parse_system('MOBILE')
    with self.assertRaises(ValueError) as context:
      BS.parse_system('DARWIN')
    with self.assertRaises(ValueError) as context:
      BS.parse_system('ALL')
    with self.assertRaises(ValueError) as context:
      BS.parse_system('desktop')
    with self.assertRaises(ValueError) as context:
      BS.parse_system('mobile')
    with self.assertRaises(ValueError) as context:
      BS.parse_system('all')
    with self.assertRaises(ValueError) as context:
      BS.parse_system('linux|macos')
    with self.assertRaises(ValueError) as context:
      BS.parse_system('macos|linux')
    with self.assertRaises(ValueError) as context:
      BS.parse_system('LINUX|MACOS')
    with self.assertRaises(ValueError) as context:
      BS.parse_system('MACOS|LINUX')
    with self.assertRaises(ValueError) as context:
      BS.parse_system('windows10')
    
  def test_system_is_valid(self):
    self.assertEqual( True, BS.system_is_valid('linux') )
    self.assertEqual( True, BS.system_is_valid('macos') )
    self.assertEqual( True, BS.system_is_valid('ios') )
    self.assertEqual( True, BS.system_is_valid('ios_sim') )
    self.assertEqual( True, BS.system_is_valid('android') )
    self.assertEqual( True, BS.system_is_valid('windows') )
    self.assertEqual( False , BS.system_is_valid('mobile') )
    self.assertEqual( False , BS.system_is_valid('desktop') )
    self.assertEqual( False , BS.system_is_valid('darwin') )

  def test_match(self):
    self.assertEqual( True, BS.mask_matches('all', 'linux') )
    self.assertEqual( False, BS.mask_matches('macos', 'linux') )
    self.assertEqual( True, BS.mask_matches('linux|macos', 'macos') )
    self.assertEqual( True, BS.mask_matches('linux|windows', 'windows') )
    self.assertEqual( True, BS.mask_matches('desktop', 'macos') )
    self.assertEqual( False, BS.mask_matches('mobile', 'macos') )
    self.assertEqual( False, BS.mask_matches('mobile', 'windows') )

  def test_is_desktop(self):
    self.assertEqual( True, BS.is_desktop('linux') )
    self.assertEqual( True, BS.is_desktop('macos') )
    self.assertEqual( False, BS.is_desktop('ios') )
    self.assertEqual( False, BS.is_desktop('android') )
    self.assertEqual( True, BS.is_desktop('windows') )
    
  def test_is_mobile(self):
    self.assertEqual( False, BS.is_mobile('linux') )
    self.assertEqual( False, BS.is_mobile('macos') )
    self.assertEqual( False, BS.is_mobile('windows') )
    self.assertEqual( True, BS.is_mobile('ios') )
    self.assertEqual( True, BS.is_mobile('android') )
    
  def test_mask_is_valid(self):
    self.assertEqual( True, BS.mask_is_valid('linux') )
    self.assertEqual( True, BS.mask_is_valid('macos') )
    self.assertEqual( True, BS.mask_is_valid('windows') )
    self.assertEqual( True, BS.mask_is_valid('linux|macos') )
    self.assertEqual( True, BS.mask_is_valid('linux|macos|windows') )
    self.assertEqual( True, BS.mask_is_valid('desktop') )
    self.assertEqual( True, BS.mask_is_valid('all') )
    self.assertEqual( False, BS.mask_is_valid('foo') )
    self.assertEqual( False, BS.mask_is_valid('something') )
    self.assertEqual( False, BS.mask_is_valid('solaris') )
    self.assertEqual( False, BS.mask_is_valid('linux|solaris') )
    self.assertEqual( False, BS.mask_is_valid('windows|solaris') )
    
if __name__ == '__main__':
  unit_test.main()
