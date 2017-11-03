#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.testing.unit_test import unit_test
from rebuild.base import build_arch, build_system, build_target, build_type

class test_build_target(unit_test):

  def test_target_dir(self):
    self.assertEqual( 'BUILD/macos/release', build_target(build_system.MACOS).target_dir )
    self.assertEqual( 'BUILD/macos/debug', build_target(build_system.MACOS, build_type.DEBUG).target_dir )
    self.assertEqual( 'BUILD/macos/release', build_target(build_system.MACOS, build_target.DEFAULT).target_dir )
    self.assertEqual( 'BUILD/linux/release', build_target(build_system.LINUX).target_dir )
    self.assertEqual( 'BUILD/ios/release', build_target(build_system.IOS).target_dir )
    self.assertEqual( 'BUILD/ios/release', build_target(build_system.IOS, archs = [ build_arch.ARM64 ]).target_dir )

  def test_clone(self):
    bi = build_target(build_system.MACOS)
    self.assertEqual( bi, bi.clone() )

    bi = build_target(build_system.MACOS, build_type.DEBUG)
    self.assertEqual( bi, bi.clone() )
    
#    bi = build_target(build_system.MACOS, build_type.DEBUG, [ build_target.I386 ])
#    self.assertEqual( bi, bi.clone() )

  def test_clone_override(self):
    debug = build_target(build_system.MACOS, build_type.DEBUG)
    release = build_target(build_system.MACOS, build_type.RELEASE)
    self.assertEqual( release, debug.clone(build_type = build_type.RELEASE) )

if __name__ == '__main__':
  unit_test.main()
