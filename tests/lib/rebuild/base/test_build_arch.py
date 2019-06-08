#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base.build_arch import build_arch as BA
from rebuild.base.build_system import build_system as BS

class test_build_arch(unit_test):

  def test_normalize(self):
    self.assertEqual( ( 'arm64', ), BA.normalize('arm64') )
    self.assertEqual( ( 'arm64', ), BA.normalize(( 'arm64', )) )
    self.assertEqual( ( 'arm64', 'armv7' ), BA.normalize([ 'arm64', 'armv7' ]) )
    self.assertEqual( ( 'arm64', 'armv7' ), BA.normalize(( 'arm64', 'armv7' )) )
    self.assertEqual( ( 'arm64', 'armv7' ), BA.normalize('arm64,armv7') )
    self.assertEqual( ( 'arm64', 'armv7', 'i386' ), BA.normalize(( 'arm64', 'armv7,i386' )) )
    self.assertEqual( ( 'arm64', 'armv7', 'i386' ), BA.normalize(( 'armv7,i386', 'arm64' )) )

  def test_split(self):
    self.assertEqual( ( 'arm64', ), BA.split('arm64') )
    self.assertEqual( ( 'arm64', 'i386' ), BA.split('arm64,i386') )
    self.assertEqual( ( 'arm64', 'i386' ), BA.split('arm64, i386') )
    self.assertEqual( ( 'arm64', 'i386' ), BA.split(' arm64, i386 ') )
    
  def test_join(self):
    self.assertEqual( 'arm64', BA.join(['arm64']) )
    self.assertEqual( 'arm64', BA.join(('arm64',)) )
    self.assertEqual( 'arm64,i386', BA.join(['arm64', 'i386']) )
    self.assertEqual( 'arm64,i386', BA.join(('arm64', 'i386')) )
    self.assertEqual( 'arm64,i386', BA.join([' arm64 ', 'i386 ']) )
    self.assertEqual( 'arm64,i386', BA.join((' arm64 ', 'i386 ')) )
    
  def test_default_arch(self):
    self.assertEqual( ( 'x86_64', ), BA.default_arch('linux', '') )
    self.assertEqual( ( 'x86_64', ), BA.default_arch('linux', 'ubuntu') )
    self.assertEqual( ( 'armv7', ), BA.default_arch('linux', 'raspbian') )
    self.assertEqual( ( 'x86_64', ), BA.default_arch('macos', '') )
    self.assertEqual( ( 'x86_64', ), BA.default_arch('macos', 'macos') )
    
  def xtest_arch_is_valid(self):
    self.assertTrue( BA.arch_is_valid(BA.ARMV7, BS.IOS) )
    self.assertTrue( BA.arch_is_valid(BA.ARM64, BS.IOS) )
    self.assertTrue( BA.arch_is_valid(BA.I386, BS.IOS_SIM) )
    self.assertTrue( BA.arch_is_valid(BA.X86_64, BS.IOS_SIM) )
    
  def xtest_determine_arch(self):
    self.assertEqual( [ BA.ARM64, BA.ARMV7 ], BA.determine_arch(BS.IOS, None, None) )
    self.assertEqual( [ BA.ARM64, BA.ARMV7 ], BA.determine_arch(BS.IOS, [], None) )
    self.assertEqual( [ BA.ARM64, BA.ARMV7 ], BA.determine_arch(BS.IOS, 'default', None) )
    self.assertEqual( [ BA.ARM64 ], BA.determine_arch(BS.IOS, BA.ARM64, None) )
    self.assertEqual( [ BA.ARM64 ], BA.determine_arch(BS.IOS, [ BA.ARM64 ], None) )
    self.assertEqual( [ BA.ARM64, BA.ARMV7 ], BA.determine_arch(BS.IOS, 'arm64,armv7', None) )
    self.assertEqual( [ BA.ARM64, BA.ARMV7 ], BA.determine_arch(BS.IOS, 'armv7,arm64', None) )

  def xtest_parse_arch(self):
    self.assertEqual( [ BA.ARM64, BA.ARMV7 ], BA.parse_arch(BS.IOS, 'arm64,armv7') )
    self.assertEqual( [ BA.ARM64 ], BA.parse_arch(BS.IOS, 'arm64') )
    self.assertEqual( [ BA.ARMV7 ], BA.parse_arch(BS.IOS, 'armv7') )
    
if __name__ == '__main__':
  unit_test.main()
