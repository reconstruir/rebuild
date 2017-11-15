#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.testing.unit_test import unit_test
from rebuild.base import build_arch, build_system, build_target, build_level

class test_build_target(unit_test):

  def test_build_path(self):
    self.assertEqual( 'macos/x86_64/release', build_target(build_system.MACOS).build_path )
    self.assertEqual( 'macos/x86_64/debug', build_target(build_system.MACOS, build_level.DEBUG).build_path )
    self.assertEqual( 'macos/x86_64/release', build_target(build_system.MACOS, build_target.DEFAULT).build_path )
    self.assertEqual( 'linux/x86_64/release', build_target(build_system.LINUX).build_path )
    self.assertEqual( 'ios/arm64-armv7/release', build_target(build_system.IOS).build_path )
    self.assertEqual( 'ios/arm64/release', build_target(build_system.IOS, archs = [ build_arch.ARM64 ]).build_path )

if __name__ == '__main__':
  unit_test.main()
