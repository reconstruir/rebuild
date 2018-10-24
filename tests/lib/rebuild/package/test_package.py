#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.testing.unit_test import unit_test
from bes.fs import temp_file, temp_item
from bes.archive import archiver, temp_archive
from rebuild.base import build_level, build_target, build_system, build_version, package_descriptor, requirement, requirement_list
from rebuild.package.package import package
from rebuild.package.unit_test_packages import unit_test_packages
from rebuild.package.fake_package_unit_test import fake_package_unit_test

class test_package(unit_test):

  DEBUG = False
  #DEBUG = True

  def test_package_descriptor_water(self):
    content='''
fake_package water 1.0.0 0 0 macos release x86_64 none 10.15
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
    tmp_tarball, _ = fake_package_unit_test.create_one_package(content)
    p = package(tmp_tarball)
    self.assertEqual( 'water', p.package_descriptor.name )
    self.assertEqual( build_version('1.0.0', '0', 0), p.package_descriptor.version )
    self.assertEqual( [], p.package_descriptor.requirements )
    self.assertEqual( {}, p.package_descriptor.properties )
    self.assertEqual( [ 'bin/water_script.sh', 'docs/water_bar.txt', 'docs/water_foo.txt', 'lib/pkgconfig/water.pc' ], p.files )
    self.assertEqual( [ 'lib/pkgconfig/water.pc' ], p.pkg_config_files )
    self.assertEqual( 'macos', p.system )
    
  def test_package_descriptor_with_requirements(self):
    tmp_tarball = unit_test_packages.make_orange(debug = self.DEBUG)
    p = package(tmp_tarball)
    self.assertEqual( 'orange', p.package_descriptor.name )
    self.assertEqual( build_version('6.5.4', '3', 0), p.package_descriptor.version )
    self.assertEqual( requirement_list.parse('fruit >= 1.0.0-0 citrus >= 1.0.0-0'), p.package_descriptor.requirements )
    self.assertEqual( {}, p.package_descriptor.properties )
    self.assertEqual( [ 'bin/orange_script.sh', 'docs/orange_bar.txt', 'docs/orange_foo.txt', 'lib/pkgconfig/orange.pc' ],
                      p.files )
    self.assertEqual( [ 'lib/pkgconfig/orange.pc' ], p.pkg_config_files )

  def test_package_files(self):
    tmp_tarball = unit_test_packages.make_orange(debug = self.DEBUG)
    pkg = package(tmp_tarball)
    self.assertEqual( [ 'bin/orange_script.sh', 'docs/orange_bar.txt', 'docs/orange_foo.txt', 'lib/pkgconfig/orange.pc' ],
                      pkg.files )

  def test_package_descriptor_orange(self):
    tmp_tarball = unit_test_packages.make_orange(debug = self.DEBUG)
    expected = package_descriptor('orange', '6.5.4-3',
                                  requirements = requirement_list.parse('fruit >= 1.0.0-0 citrus >= 1.0.0-0'),
                                  properties = {})
    self.assertEqual( expected, package(tmp_tarball).package_descriptor )

  def test_create_package(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    tarball_path = self._make_package(tmp_dir,
                                      'foo', '1.2.3-1',
                                      build_system.LINUX, build_level.RELEASE,
                                      [
                                        ( 'foo.txt', 'foo.txt\n' ),
                                        ( 'bar.txt', 'bar.txt\n' ),
                                      ],
                                      [
                                        ( 'foo.sh', 'echo foo.sh\n' ),
                                        ( 'bar.sh', 'echo bar.sh\n' ),
                                      ])
    assert path.exists(tarball_path)
    expected_members = [
      'env/bar.sh',
      'env/foo.sh',
      'files/bar.txt',
      'files/foo.txt',
      'metadata/metadata.json',
    ]
    self.assertEqual( expected_members, archiver.members(tarball_path) )

  def test_is_package(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    tarball_path = self._make_package(tmp_dir,
                                      'foo', '1.2.3-1',
                                      build_system.LINUX, build_level.RELEASE,
                                      [
                                        ( 'foo.txt', 'foo.txt\n' ),
                                        ( 'bar.txt', 'bar.txt\n' ),
                                      ],
                                      [
                                        ( 'foo.sh', 'echo foo.sh\n' ),
                                        ( 'bar.sh', 'echo bar.sh\n' ),
                                      ])
    self.assertTrue( package.is_package(tarball_path) )
    self.assertFalse( package.is_package(temp_file.make_temp_file(content = 'notpackage')) )

  def _make_package(self, dest_dir, name, version, system, build_level, items, env_items):
    pi = package_descriptor(name, version)
    tarball_path = path.join(dest_dir, pi.tarball_filename)
    bi = build_target(system, '', '', ( 'x86_64' ), build_level)
    items = temp_archive.make_temp_item_list(items)
    env_items = temp_archive.make_temp_item_list(env_items)
    tmp_stage_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    tmp_staged_files_dir = path.join(tmp_stage_dir, 'files')
    tmp_staged_env_dir = path.join(tmp_stage_dir, 'env')
    temp_archive.write_items(tmp_staged_files_dir, items)
    temp_archive.write_items(tmp_staged_env_dir, env_items)
    package.create_package(tarball_path, pi, bi, tmp_stage_dir)
    return tarball_path

if __name__ == '__main__':
  unit_test.main()
