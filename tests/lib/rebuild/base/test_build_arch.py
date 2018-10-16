#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base import build_arch as BA, build_system as BS

class test_build_arch(unit_test):

  def test_arch_is_valid(self):
    self.assertTrue( BA.arch_is_valid(BA.ARMV7, BS.IOS) )
    self.assertTrue( BA.arch_is_valid(BA.ARM64, BS.IOS) )
    self.assertTrue( BA.arch_is_valid(BA.I386, BS.IOS_SIM) )
    self.assertTrue( BA.arch_is_valid(BA.X86_64, BS.IOS_SIM) )
    
  def test_determine_archs(self):
    self.assertEqual( [ BA.ARM64, BA.ARMV7 ], BA.determine_archs(BS.IOS, None) )
    self.assertEqual( [ BA.ARM64, BA.ARMV7 ], BA.determine_archs(BS.IOS, []) )
    self.assertEqual( [ BA.ARM64, BA.ARMV7 ], BA.determine_archs(BS.IOS, 'default') )
    self.assertEqual( [ BA.ARM64 ], BA.determine_archs(BS.IOS, BA.ARM64) )
    self.assertEqual( [ BA.ARM64 ], BA.determine_archs(BS.IOS, [ BA.ARM64 ]) )
    self.assertEqual( [ BA.ARM64, BA.ARMV7 ], BA.determine_archs(BS.IOS, 'arm64,armv7') )
    self.assertEqual( [ BA.ARM64, BA.ARMV7 ], BA.determine_archs(BS.IOS, 'armv7,arm64') )

  def test_archs_to_string(self):
    self.assertEqual( 'i386,x86_64', BA.archs_to_string( [ BA.I386, BA.X86_64 ] ) )

  def test_parse_archs(self):
    self.assertEqual( [ BA.ARM64, BA.ARMV7 ], BA.parse_archs(BS.IOS, 'arm64,armv7') )
    self.assertEqual( [ BA.ARM64 ], BA.parse_archs(BS.IOS, 'arm64') )
    self.assertEqual( [ BA.ARMV7 ], BA.parse_archs(BS.IOS, 'armv7') )
    
if __name__ == '__main__':
  unit_test.main()
