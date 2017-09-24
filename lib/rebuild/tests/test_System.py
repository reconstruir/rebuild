#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild import System

class test_system(unittest.TestCase):

  def test_resolve_mask(self):
    self.assertEqual( 'android', System.resolve_mask('android') )
    self.assertEqual( 'macos', System.resolve_mask('macos') )
    self.assertEqual( 'ios', System.resolve_mask('ios') )
    self.assertEqual( 'linux', System.resolve_mask('linux') )
    self.assertEqual( 'android|ios', System.resolve_mask('android|ios') )
    self.assertEqual( 'linux|macos', System.resolve_mask('macos|linux') )
    self.assertEqual( 'android|ios|ios_sim|linux|macos', System.resolve_mask('all') )
    self.assertEqual( 'none', System.resolve_mask('') )
    self.assertEqual( 'none', System.resolve_mask('none') )
    self.assertEqual( 'android|ios', System.resolve_mask('mobile') )
    self.assertEqual( 'linux|macos', System.resolve_mask('desktop') )
    self.assertEqual( 'ios|ios_sim|macos', System.resolve_mask('darwin') )

  def test_resolve_mask_recursive(self):
    self.assertEqual( 'android|ios|ios_sim|linux|macos', System.resolve_mask('darwin|desktop|mobile') )

  def test_parse_system(self):
    self.assertEqual( 'android', System.parse_system('android') )
    self.assertEqual( 'ios', System.parse_system('ios') )
    self.assertEqual( 'macos', System.parse_system('macos') )
    self.assertEqual( 'linux', System.parse_system('linux') )
    self.assertEqual( 'android', System.parse_system('ANDROID') )
    self.assertEqual( 'ios', System.parse_system('IOS') )
    self.assertEqual( 'macos', System.parse_system('MACOS') )
    self.assertEqual( 'linux', System.parse_system('LINUX') )

  def test_parse_system_invalid(self):
    with self.assertRaises(RuntimeError) as context:
      System.parse_system('darwin')
    with self.assertRaises(RuntimeError) as context:
      System.parse_system('DESKTOP')
    with self.assertRaises(RuntimeError) as context:
      System.parse_system('MOBILE')
    with self.assertRaises(RuntimeError) as context:
      System.parse_system('DARWIN')
    with self.assertRaises(RuntimeError) as context:
      System.parse_system('ALL')
    with self.assertRaises(RuntimeError) as context:
      System.parse_system('desktop')
    with self.assertRaises(RuntimeError) as context:
      System.parse_system('mobile')
    with self.assertRaises(RuntimeError) as context:
      System.parse_system('all')
    with self.assertRaises(RuntimeError) as context:
      System.parse_system('linux|macos')
    with self.assertRaises(RuntimeError) as context:
      System.parse_system('macos|linux')
    with self.assertRaises(RuntimeError) as context:
      System.parse_system('LINUX|MACOS')
    with self.assertRaises(RuntimeError) as context:
      System.parse_system('MACOS|LINUX')
    
  def test_system_is_valid(self):
    self.assertEqual( True, System.system_is_valid('linux') )
    self.assertEqual( True, System.system_is_valid('macos') )
    self.assertEqual( True, System.system_is_valid('ios') )
    self.assertEqual( True, System.system_is_valid('ios_sim') )
    self.assertEqual( True, System.system_is_valid('android') )
    self.assertEqual( False , System.system_is_valid('mobile') )
    self.assertEqual( False , System.system_is_valid('desktop') )
    self.assertEqual( False , System.system_is_valid('darwin') )

  def test_match(self):
    self.assertEqual( True, System.mask_matches('all', 'linux') )
    self.assertEqual( False, System.mask_matches('macos', 'linux') )
    self.assertEqual( True, System.mask_matches('linux|macos', 'macos') )
    self.assertEqual( True, System.mask_matches('desktop', 'macos') )
    self.assertEqual( False, System.mask_matches('mobile', 'macos') )

if __name__ == '__main__':
  unittest.main()
