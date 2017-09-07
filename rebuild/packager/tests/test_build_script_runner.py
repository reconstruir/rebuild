#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path
from bes.unit_test import unit_test
from bes.fs import file_util, temp_file
from rebuild import build_target, version as rebuild_version
from rebuild.packager import build_script_runner
from rebuild.package_manager import Package
from rebuild.packager.unit_test_packaging import unit_test_packaging

class test_build_script_runner(unit_test):

  __unit_test_data_dir__ = 'test_data/packager'
  
  def test_amhello(self):
    unit_test_packaging.build_script_runner_build_autoconf_package(self, 'amhello', '1.0', '1', self.data_dir())

  def test_water(self):
    unit_test_packaging.build_script_runner_build_autoconf_package(self, 'water', '1.0.0', '1', self.data_dir())

  def test_mercury(self):
    package = unit_test_packaging.build_script_runner_build_autoconf_package(self, 'mercury', '2.3.4', '0', self.data_dir())
    expected_files = [
      'bin/mercury_program1',
      'bin/mercury_program2',
      'bin/rebbe_mercury_program1',
      'bin/rebbe_mercury_program2',
      'include/mercury1/mercury1.h',
      'include/mercury2/mercury2.h',
      'lib/libmercury1.a',
      'lib/libmercury2.a',
      'lib/librebbe_mercury1.a',
      'lib/librebbe_mercury2.a',
      'lib/pkgconfig/mercury.pc',
      'lib/pkgconfig/rebbe_mercury.pc',
      'share/doc/mercury/README',
    ]
    self.assertEqual( expected_files, package.files )
    self.assertEqual( 'mercury', package.info.name )
    self.assertEqual( rebuild_version('2.3.4', 0, 0), package.info.version )
    self.assertEqual( 'lib', package.info.properties['category'] )

  def test_arsenic(self):
    package = unit_test_packaging.build_script_runner_build_autoconf_package(self, 'arsenic', '1.2.9', '0', self.data_dir())
    expected_files = [
      'bin/arsenic_program1',
      'bin/arsenic_program2',
      'bin/rebbe_arsenic_program1',
      'bin/rebbe_arsenic_program2',
      'include/arsenic1/arsenic1.h',
      'include/arsenic2/arsenic2.h',
      'lib/libarsenic1.a',
      'lib/libarsenic2.a',
      'lib/librebbe_arsenic1.a',
      'lib/librebbe_arsenic2.a',
      'lib/pkgconfig/arsenic.pc',
      'lib/pkgconfig/libarsenic1.pc',
      'lib/pkgconfig/libarsenic2.pc',
      'lib/pkgconfig/librebbe_arsenic1.pc',
      'lib/pkgconfig/librebbe_arsenic2.pc',
      'lib/pkgconfig/rebbe_arsenic.pc',
      'share/doc/arsenic/README',
    ]
    self.assertEqual( expected_files, package.files )
    self.assertEqual( 'arsenic', package.info.name )
    self.assertEqual( rebuild_version('1.2.9', 0, 0), package.info.version )
    self.assertEqual( 'lib', package.info.properties['category'] )

if __name__ == '__main__':
  unit_test.main()
