#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild import build_arch, build_target, System, build_type

class test_build_target(unittest.TestCase):

  def test_target_dir(self):
    self.assertEqual( 'BUILD/macos/release', build_target(System.MACOS).target_dir )
    self.assertEqual( 'BUILD/macos/debug', build_target(System.MACOS, build_type.DEBUG).target_dir )
    self.assertEqual( 'BUILD/macos/release', build_target(System.MACOS, build_target.DEFAULT).target_dir )
    self.assertEqual( 'BUILD/linux/release', build_target(System.LINUX).target_dir )
    self.assertEqual( 'BUILD/ios/release', build_target(System.IOS).target_dir )
    self.assertEqual( 'BUILD/ios/release', build_target(System.IOS, archs = [ build_arch.ARM64 ]).target_dir )

  def test_clone(self):
    bi = build_target(System.MACOS)
    self.assertEqual( bi, bi.clone() )

    bi = build_target(System.MACOS, build_type.DEBUG)
    self.assertEqual( bi, bi.clone() )
    
#    bi = build_target(System.MACOS, build_type.DEBUG, [ build_target.I386 ])
#    self.assertEqual( bi, bi.clone() )

  def test_clone_override(self):
    debug = build_target(System.MACOS, build_type.DEBUG)
    release = build_target(System.MACOS, build_type.RELEASE)
    self.assertEqual( release, debug.clone(build_type = build_type.RELEASE) )

if __name__ == '__main__':
  unittest.main()
