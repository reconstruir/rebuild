#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs import temp_file
from rebuild.base import build_version, package_descriptor, requirement, requirement_list
from rebuild.package.package import package
from _rebuild_testing.fake_package_unit_test import fake_package_unit_test

class test_package(unit_test):

  _WATER = '''
fake_package water 1.0.0 0 0 macos release x86_64 none 10 15
  files
    bin/water_script.sh
      #!/bin/bash
      echo foo
    docs/water_bar.txt
      foo
    docs/water_foo.txt
      bar
    lib/pkgconfig/water.pc
      foo
'''

  _ORANGE = '''
fake_package orange 6.5.4 3 0 linux release x86_64 ubuntu 18 none
  files
    bin/orange_script.sh
      #!/bin/bash
      echo foo
    docs/orange_bar.txt
      foo
    docs/orange_foo.txt
      bar
    lib/pkgconfig/orange.pc
      foo
  requirements
    fruit >= 1.0.0-0
    citrus >= 1.0.0-0
'''
  
  def test_package_descriptor_water(self):
    tmp_tarball = fake_package_unit_test.create_one_package(self._WATER)
    p = package(tmp_tarball.filename)
    self.assertEqual( 'water', p.package_descriptor.name )
    self.assertEqual( build_version('1.0.0', '0', 0), p.package_descriptor.version )
    self.assertEqual( [], p.package_descriptor.requirements )
    self.assertEqual( {}, p.package_descriptor.properties )
    self.assertEqual( [ 'bin/water_script.sh', 'docs/water_bar.txt', 'docs/water_foo.txt', 'lib/pkgconfig/water.pc' ], p.files )
    self.assertEqual( [ 'lib/pkgconfig/water.pc' ], p.pkg_config_files )
    self.assertEqual( 'macos', p.system )
    
  def test_package_descriptor_with_requirements(self):
    tmp_tarball = fake_package_unit_test.create_one_package(self._ORANGE)
    p = package(tmp_tarball.filename)
    self.assertEqual( 'orange', p.package_descriptor.name )
    self.assertEqual( build_version('6.5.4', '3', 0), p.package_descriptor.version )
    self.assertEqual( requirement_list.parse('fruit >= 1.0.0-0 citrus >= 1.0.0-0'), p.package_descriptor.requirements )
    self.assertEqual( {}, p.package_descriptor.properties )
    self.assertEqual( [ 'bin/orange_script.sh', 'docs/orange_bar.txt', 'docs/orange_foo.txt', 'lib/pkgconfig/orange.pc' ],
                      p.files )
    self.assertEqual( [ 'lib/pkgconfig/orange.pc' ], p.pkg_config_files )

  def test_is_package(self):
    tmp_tarball = fake_package_unit_test.create_one_package(self._WATER)
    self.assertTrue( package.is_package(tmp_tarball.filename) )
    self.assertFalse( package.is_package(temp_file.make_temp_file(content = 'notpackage')) )

  def test_linux_no_distro(self):
    recipe = '''
fake_package kiwi 1.2.3 0 0 linux release x86_64 none none none
  files
    bin/kiwi_script.sh
      #!/bin/bash
      echo kiwi
'''
    tmp_tarball = fake_package_unit_test.create_one_package(recipe)
    md = package(tmp_tarball.filename).metadata
    self.assertEqual( '', md.distro )
    self.assertEqual( '', md.distro_version_major )
    self.assertEqual( '', md.distro_version_minor )
    
if __name__ == '__main__':
  unit_test.main()
