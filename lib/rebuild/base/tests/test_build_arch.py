#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.testing.unit_test import unit_test
from rebuild.base import build_arch, build_system

class test_build_arch(unit_test):

  def test_arch_is_valid(self):
    self.assertTrue( build_arch.arch_is_valid(build_arch.ARMV7, build_system.IOS) )
    self.assertTrue( build_arch.arch_is_valid(build_arch.ARM64, build_system.IOS) )
    self.assertTrue( build_arch.arch_is_valid(build_arch.I386, build_system.IOS_SIM) )
    self.assertTrue( build_arch.arch_is_valid(build_arch.X86_64, build_system.IOS_SIM) )
    
  def test_determine_archs(self):
    self.assertEqual( [ build_arch.ARM64, build_arch.ARMV7 ], build_arch.determine_archs(build_system.IOS, None) )
    self.assertEqual( [ build_arch.ARM64, build_arch.ARMV7 ], build_arch.determine_archs(build_system.IOS, []) )
    self.assertEqual( [ build_arch.ARM64, build_arch.ARMV7 ], build_arch.determine_archs(build_system.IOS, 'default') )
    self.assertEqual( [ build_arch.ARM64 ], build_arch.determine_archs(build_system.IOS, build_arch.ARM64) )
    self.assertEqual( [ build_arch.ARM64 ], build_arch.determine_archs(build_system.IOS, [ build_arch.ARM64 ]) )
    self.assertEqual( [ build_arch.ARM64, build_arch.ARMV7 ], build_arch.determine_archs(build_system.IOS, 'arm64,armv7') )
    self.assertEqual( [ build_arch.ARM64, build_arch.ARMV7 ], build_arch.determine_archs(build_system.IOS, 'armv7,arm64') )

  def test_archs_to_string(self):
    self.assertEqual( 'i386,x86_64', build_arch.archs_to_string( [ build_arch.I386, build_arch.X86_64 ] ) )

  def test_parse_archs(self):
    self.assertEqual( [ build_arch.ARM64, build_arch.ARMV7 ], build_arch.parse_archs(build_system.IOS, 'arm64,armv7') )
    self.assertEqual( [ build_arch.ARM64 ], build_arch.parse_archs(build_system.IOS, 'arm64') )
    self.assertEqual( [ build_arch.ARMV7 ], build_arch.parse_archs(build_system.IOS, 'armv7') )
    
if __name__ == '__main__':
  unit_test.main()
