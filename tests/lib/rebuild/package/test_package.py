#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path, unittest
from bes.fs import temp_file, temp_item
from rebuild.base import build_target, build_version, package_descriptor, requirement, requirement_list
from rebuild.package.package import package
from rebuild.package.unit_test_packages import unit_test_packages

class test_package(unittest.TestCase):

  DEBUG = False
  #DEBUG = True

  def test_package_descriptor_water(self):
    tmp_tarball = unit_test_packages.make_water(debug = self.DEBUG)
    p = package(tmp_tarball)
    self.assertEqual( 'water', p.descriptor.name )
    self.assertEqual( build_version('1.0.0', '0', 0), p.descriptor.version )
    self.assertEqual( [], p.descriptor.requirements )
    self.assertEqual( {}, p.descriptor.properties )
    self.assertEqual( [ 'bin/water_script.sh', 'docs/water_bar.txt', 'docs/water_foo.txt', 'lib/pkgconfig/water.pc' ], p.files )
    self.assertEqual( [ 'lib/pkgconfig/water.pc' ], p.pkg_config_files )
    self.assertEqual( 'macos', p.system )

  def test_package_descriptor_with_requirements(self):
    tmp_tarball = unit_test_packages.make_orange(debug = self.DEBUG)
    p = package(tmp_tarball)
    self.assertEqual( 'orange', p.descriptor.name )
    self.assertEqual( build_version('6.5.4', '3', 0), p.descriptor.version )
    self.assertEqual( requirement_list.parse('fruit(all) >= 1.0.0-0 citrus(all) >= 1.0.0-0'), p.descriptor.requirements )
    self.assertEqual( {}, p.descriptor.properties )
    self.assertEqual( [ 'bin/orange_script.sh', 'docs/orange_bar.txt', 'docs/orange_foo.txt', 'lib/pkgconfig/orange.pc' ], p.files )
    self.assertEqual( [ 'lib/pkgconfig/orange.pc' ], p.pkg_config_files )

  def test_package_files(self):
    tmp_tarball = unit_test_packages.make_orange(debug = self.DEBUG)
    self.assertEqual( [ 'bin/orange_script.sh', 'docs/orange_bar.txt', 'docs/orange_foo.txt', 'lib/pkgconfig/orange.pc' ], package.package_files(tmp_tarball) )

  def test_package_descriptor_orange(self):
    tmp_tarball = unit_test_packages.make_orange(debug = self.DEBUG)
    expected_pi = package_descriptor('orange', '6.5.4-3',
                                     requirements = requirement_list.parse('fruit(all) >= 1.0.0-0 citrus(all) >= 1.0.0-0'),
                                     properties = {})
    self.assertEqual( expected_pi, package.package_descriptor(tmp_tarball) )

if __name__ == '__main__':
  unittest.main()
