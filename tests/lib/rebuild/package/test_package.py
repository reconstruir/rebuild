#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path, unittest
from bes.fs import temp_file, temp_item
from bes.archive import archiver, temp_archive
from rebuild.base import build_level, build_target, build_system, build_version, package_descriptor, requirement, requirement_list
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
    self.assertEqual( requirement_list.parse('fruit >= 1.0.0-0 citrus >= 1.0.0-0'), p.descriptor.requirements )
    self.assertEqual( {}, p.descriptor.properties )
    self.assertEqual( [ 'bin/orange_script.sh', 'docs/orange_bar.txt', 'docs/orange_foo.txt', 'lib/pkgconfig/orange.pc' ], p.files )
    self.assertEqual( [ 'lib/pkgconfig/orange.pc' ], p.pkg_config_files )

  def test_package_files(self):
    tmp_tarball = unit_test_packages.make_orange(debug = self.DEBUG)
    self.assertEqual( [ 'bin/orange_script.sh', 'docs/orange_bar.txt', 'docs/orange_foo.txt', 'lib/pkgconfig/orange.pc' ], package.package_files(tmp_tarball) )

  def test_package_descriptor_orange(self):
    tmp_tarball = unit_test_packages.make_orange(debug = self.DEBUG)
    expected_pi = package_descriptor('orange', '6.5.4-3',
                                     requirements = requirement_list.parse('fruit >= 1.0.0-0 citrus >= 1.0.0-0'),
                                     properties = {})
    self.assertEqual( expected_pi, package.package_descriptor(tmp_tarball) )

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

  def _make_package(self, dest_dir, name, version, system, build_level, items, env_items):
    pi = package_descriptor(name, version)
    tarball_path = path.join(dest_dir, pi.tarball_filename)
    bi = build_target(system, build_level)
    items = temp_archive.make_temp_item_list(items)
    tmp_stage_dir = temp_archive.write_temp_items(items)
    env_items = temp_archive.make_temp_item_list(env_items)
    tmp_env_dir = temp_archive.write_temp_items(env_items)
    package.create_tarball(tarball_path, pi, bi, tmp_stage_dir, tmp_env_dir)
    return tarball_path
    
if __name__ == '__main__':
  unittest.main()
