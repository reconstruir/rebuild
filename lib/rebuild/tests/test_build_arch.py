#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild import build_arch, System

class test_build_arch(unittest.TestCase):

  def test_arch_is_valid(self):
    self.assertTrue( build_arch.arch_is_valid(build_arch.ARMV7, System.IOS) )
    self.assertTrue( build_arch.arch_is_valid(build_arch.ARM64, System.IOS) )
    self.assertTrue( build_arch.arch_is_valid(build_arch.I386, System.IOS_SIM) )
    self.assertTrue( build_arch.arch_is_valid(build_arch.X86_64, System.IOS_SIM) )
    
  def test_determine_archs(self):
    self.assertEqual( [ build_arch.ARM64, build_arch.ARMV7 ], build_arch.determine_archs(System.IOS, None) )
    self.assertEqual( [ build_arch.ARM64, build_arch.ARMV7 ], build_arch.determine_archs(System.IOS, []) )
    self.assertEqual( [ build_arch.ARM64, build_arch.ARMV7 ], build_arch.determine_archs(System.IOS, 'default') )
    self.assertEqual( [ build_arch.ARM64 ], build_arch.determine_archs(System.IOS, build_arch.ARM64) )
    self.assertEqual( [ build_arch.ARM64 ], build_arch.determine_archs(System.IOS, [ build_arch.ARM64 ]) )
    self.assertEqual( [ build_arch.ARM64, build_arch.ARMV7 ], build_arch.determine_archs(System.IOS, 'arm64,armv7') )
    self.assertEqual( [ build_arch.ARM64, build_arch.ARMV7 ], build_arch.determine_archs(System.IOS, 'armv7,arm64') )

  def test_archs_to_string(self):
    self.assertEqual( 'i386,x86_64', build_arch.archs_to_string( [ build_arch.I386, build_arch.X86_64 ] ) )

  def test_parse_archs(self):
    self.assertEqual( [ build_arch.ARM64, build_arch.ARMV7 ], build_arch.parse_archs(System.IOS, 'arm64,armv7') )
    self.assertEqual( [ build_arch.ARM64 ], build_arch.parse_archs(System.IOS, 'arm64') )
    self.assertEqual( [ build_arch.ARMV7 ], build_arch.parse_archs(System.IOS, 'armv7') )
    
if __name__ == '__main__':
  unittest.main()
