#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.testing.unit_test import unit_test
from rebuild.base import build_system
  
class test_build_system(unit_test):

  def test_resolve_mask(self):
    self.assertEqual( 'android', build_system.resolve_mask('android') )
    self.assertEqual( 'macos', build_system.resolve_mask('macos') )
    self.assertEqual( 'ios', build_system.resolve_mask('ios') )
    self.assertEqual( 'linux', build_system.resolve_mask('linux') )
    self.assertEqual( 'android|ios', build_system.resolve_mask('android|ios') )
    self.assertEqual( 'linux|macos', build_system.resolve_mask('macos|linux') )
    self.assertEqual( 'android|ios|ios_sim|linux|macos', build_system.resolve_mask('all') )
    self.assertEqual( 'none', build_system.resolve_mask('') )
    self.assertEqual( 'none', build_system.resolve_mask('none') )
    self.assertEqual( 'android|ios', build_system.resolve_mask('mobile') )
    self.assertEqual( 'linux|macos', build_system.resolve_mask('desktop') )
    self.assertEqual( 'ios|ios_sim|macos', build_system.resolve_mask('darwin') )

  def test_resolve_mask_recursive(self):
    self.assertEqual( 'android|ios|ios_sim|linux|macos', build_system.resolve_mask('darwin|desktop|mobile') )

  def test_parse_system(self):
    self.assertEqual( 'android', build_system.parse_system('android') )
    self.assertEqual( 'ios', build_system.parse_system('ios') )
    self.assertEqual( 'macos', build_system.parse_system('macos') )
    self.assertEqual( 'linux', build_system.parse_system('linux') )
    self.assertEqual( 'android', build_system.parse_system('ANDROID') )
    self.assertEqual( 'ios', build_system.parse_system('IOS') )
    self.assertEqual( 'macos', build_system.parse_system('MACOS') )
    self.assertEqual( 'linux', build_system.parse_system('LINUX') )

  def test_parse_system_invalid(self):
    with self.assertRaises(RuntimeError) as context:
      build_system.parse_system('darwin')
    with self.assertRaises(RuntimeError) as context:
      build_system.parse_system('DESKTOP')
    with self.assertRaises(RuntimeError) as context:
      build_system.parse_system('MOBILE')
    with self.assertRaises(RuntimeError) as context:
      build_system.parse_system('DARWIN')
    with self.assertRaises(RuntimeError) as context:
      build_system.parse_system('ALL')
    with self.assertRaises(RuntimeError) as context:
      build_system.parse_system('desktop')
    with self.assertRaises(RuntimeError) as context:
      build_system.parse_system('mobile')
    with self.assertRaises(RuntimeError) as context:
      build_system.parse_system('all')
    with self.assertRaises(RuntimeError) as context:
      build_system.parse_system('linux|macos')
    with self.assertRaises(RuntimeError) as context:
      build_system.parse_system('macos|linux')
    with self.assertRaises(RuntimeError) as context:
      build_system.parse_system('LINUX|MACOS')
    with self.assertRaises(RuntimeError) as context:
      build_system.parse_system('MACOS|LINUX')
    
  def test_system_is_valid(self):
    self.assertEqual( True, build_system.system_is_valid('linux') )
    self.assertEqual( True, build_system.system_is_valid('macos') )
    self.assertEqual( True, build_system.system_is_valid('ios') )
    self.assertEqual( True, build_system.system_is_valid('ios_sim') )
    self.assertEqual( True, build_system.system_is_valid('android') )
    self.assertEqual( False , build_system.system_is_valid('mobile') )
    self.assertEqual( False , build_system.system_is_valid('desktop') )
    self.assertEqual( False , build_system.system_is_valid('darwin') )

  def test_match(self):
    self.assertEqual( True, build_system.mask_matches('all', 'linux') )
    self.assertEqual( False, build_system.mask_matches('macos', 'linux') )
    self.assertEqual( True, build_system.mask_matches('linux|macos', 'macos') )
    self.assertEqual( True, build_system.mask_matches('desktop', 'macos') )
    self.assertEqual( False, build_system.mask_matches('mobile', 'macos') )

if __name__ == '__main__':
  unit_test.main()
