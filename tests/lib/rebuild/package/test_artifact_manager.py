#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import temp_file
from rebuild.base import build_target, package_descriptor as PD
from rebuild.package import artifact_manager, artifact_descriptor as AD
from rebuild.package.db_error import *
from _rebuild_testing.fake_package_unit_test import fake_package_unit_test as FPUT
from rebuild.package import artifact_descriptor as AD

class test_artifact_manager(unit_test):

  DEBUG = unit_test.DEBUG
  #DEBUG = True

  LINUX_BT = build_target('linux', 'ubuntu', '18', 'x86_64', 'release')
  MACOS_BT = build_target('macos', '', '10.14', 'x86_64', 'release')

  def test_artifact_path(self):
    am = FPUT.make_artifact_manager()
    pi = PD('foo', '1.2.34-1')
    self.assertEqual( path.join(am.root_dir, pi.artifact_path(self.LINUX_BT)), am.artifact_path(pi, self.LINUX_BT) )

  _APPLE = '''
fake_package apple 1.2.3 1 0 linux release x86_64 ubuntu 18
  requirements
    fruit >= 1.0.0
'''
    
  def test_publish(self):
    am = FPUT.make_artifact_manager()
    tmp_tarball = FPUT.create_one_package(self._APPLE)
    self.assertEqual( [], am.list_all_by_descriptor() )
    filename = am.publish(tmp_tarball, self.LINUX_BT, False)
    self.assertTrue( path.exists(filename) )
    expected = [
      AD('apple', '1.2.3', 1, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
    ]
    self.assertEqual( expected, am.list_all_by_descriptor() )

  def test_publish_again_with_replace(self):
    am = FPUT.make_artifact_manager()
    tmp_tarball = FPUT.create_one_package(self._APPLE)
    filename = am.publish(tmp_tarball, self.LINUX_BT, False)
    self.assertTrue( path.exists(filename) )
    expected = [
      AD('apple', '1.2.3', 1, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
    ]
    self.assertEqual( expected, am.list_all_by_descriptor() )
    filename = am.publish(tmp_tarball, self.LINUX_BT, True)
    self.assertEqual( expected, am.list_all_by_descriptor() )

  def test_publish_again_without_replace(self):
    am = FPUT.make_artifact_manager()
    tmp_tarball = FPUT.create_one_package(self._APPLE)
    filename = am.publish(tmp_tarball, self.LINUX_BT, False)
    self.assertTrue( path.exists(filename) )
    expected = [
      AD('apple', '1.2.3', 1, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
    ]
    self.assertEqual( expected, am.list_all_by_descriptor() )
    with self.assertRaises(AlreadyInstalledError) as context:
      am.publish(tmp_tarball, self.LINUX_BT, False)
    
  def test_find_by_package_descriptor_linux(self):
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    am = FPUT.make_artifact_manager(self.DEBUG, FPUT.TEST_RECIPES, self.LINUX_BT, mutations)
    self.assertEqual( 'water-1.0.0', am.find_by_package_descriptor(PD('water', '1.0.0'), self.LINUX_BT).package_descriptor.full_name )
    self.assertEqual( 'water-1.0.0-1', am.find_by_package_descriptor(PD('water', '1.0.0-1'), self.LINUX_BT).package_descriptor.full_name )
    self.assertEqual( 'water-1.0.0-2', am.find_by_package_descriptor(PD('water', '1.0.0-2'), self.LINUX_BT).package_descriptor.full_name )
    self.assertEqual( 'fructose-3.4.5-6', am.find_by_package_descriptor(PD('fructose', '3.4.5-6'), self.LINUX_BT).package_descriptor.full_name )
    self.assertEqual( 'apple-1.2.3-1', am.find_by_package_descriptor(PD('apple', '1.2.3-1'), self.LINUX_BT).package_descriptor.full_name )
    self.assertEqual( 'orange-6.5.4-3', am.find_by_package_descriptor(PD('orange', '6.5.4-3'), self.LINUX_BT).package_descriptor.full_name )
    self.assertEqual( 'orange_juice-1.4.5', am.find_by_package_descriptor(PD('orange_juice', '1.4.5'), self.LINUX_BT).package_descriptor.full_name )
    self.assertEqual( 'pear_juice-6.6.6', am.find_by_package_descriptor(PD('pear_juice', '6.6.6'), self.LINUX_BT).package_descriptor.full_name )

  def test_find_by_package_descriptor_macos(self):
    mutations = { 'system': 'macos', 'distro': '', 'distro_version': '10.14' }
    am = FPUT.make_artifact_manager(self.DEBUG, FPUT.TEST_RECIPES, self.MACOS_BT, mutations)
    self.assertEqual( 'water-1.0.0', am.find_by_package_descriptor(PD('water', '1.0.0'), self.MACOS_BT).package_descriptor.full_name )
    self.assertEqual( 'water-1.0.0-1', am.find_by_package_descriptor(PD('water', '1.0.0-1'), self.MACOS_BT).package_descriptor.full_name )
    self.assertEqual( 'water-1.0.0-2', am.find_by_package_descriptor(PD('water', '1.0.0-2'), self.MACOS_BT).package_descriptor.full_name )
    self.assertEqual( 'fructose-3.4.5-6', am.find_by_package_descriptor(PD('fructose', '3.4.5-6'), self.MACOS_BT).package_descriptor.full_name )
    self.assertEqual( 'apple-1.2.3-1', am.find_by_package_descriptor(PD('apple', '1.2.3-1'), self.MACOS_BT).package_descriptor.full_name )
    self.assertEqual( 'orange-6.5.4-3', am.find_by_package_descriptor(PD('orange', '6.5.4-3'), self.MACOS_BT).package_descriptor.full_name )
    self.assertEqual( 'orange_juice-1.4.5', am.find_by_package_descriptor(PD('orange_juice', '1.4.5'), self.MACOS_BT).package_descriptor.full_name )
    self.assertEqual( 'pear_juice-6.6.6', am.find_by_package_descriptor(PD('pear_juice', '6.6.6'), self.MACOS_BT).package_descriptor.full_name )

  def test_list_latest_versions_linux(self):
    self.maxDiff = None
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    am = FPUT.make_artifact_manager(self.DEBUG, FPUT.TEST_RECIPES, self.LINUX_BT, mutations)
    expected = [
      AD('apple', '1.2.3', 1, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
      AD('arsenic', '1.2.9', 1, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
      AD('citrus', '1.0.0', 2, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
      AD('fiber', '1.0.0', 0, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
      AD('fructose', '3.4.5', 6, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
      AD('fruit', '1.0.0', 0, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
      AD('knife', '1.0.0', 0, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
      AD('mercury', '1.2.9', 0, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
      AD('orange', '6.5.4', 3, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
      AD('orange_juice', '1.4.5', 0, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
      AD('pear', '1.2.3', 1, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
      AD('pear_juice', '6.6.6', 0, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
      AD('smoothie', '1.0.0', 0, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
      AD('water', '1.0.0', 2, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
    ]
    self.assertEqual( expected, am.list_latest_versions(self.LINUX_BT) )

  def test_list_latest_versions_macos(self):
    self.maxDiff = None
    mutations = { 'system': 'macos', 'distro': '', 'distro_version': '10.14' }
    am = FPUT.make_artifact_manager(self.DEBUG, FPUT.TEST_RECIPES, self.MACOS_BT, mutations)
    expected = [
      AD('apple', '1.2.3', 1, 0, 'macos', 'release', 'x86_64', '', '10.14'),
      AD('arsenic', '1.2.9', 1, 0, 'macos', 'release', 'x86_64', '', '10.14'),
      AD('citrus', '1.0.0', 2, 0, 'macos', 'release', 'x86_64', '', '10.14'),
      AD('fiber', '1.0.0', 0, 0, 'macos', 'release', 'x86_64', '', '10.14'),
      AD('fructose', '3.4.5', 6, 0, 'macos', 'release', 'x86_64', '', '10.14'),
      AD('fruit', '1.0.0', 0, 0, 'macos', 'release', 'x86_64', '', '10.14'),
      AD('knife', '1.0.0', 0, 0, 'macos', 'release', 'x86_64', '', '10.14'),
      AD('mercury', '1.2.9', 0, 0, 'macos', 'release', 'x86_64', '', '10.14'),
      AD('orange', '6.5.4', 3, 0, 'macos', 'release', 'x86_64', '', '10.14'),
      AD('orange_juice', '1.4.5', 0, 0, 'macos', 'release', 'x86_64', '', '10.14'),
      AD('pear', '1.2.3', 1, 0, 'macos', 'release', 'x86_64', '', '10.14'),
      AD('pear_juice', '6.6.6', 0, 0, 'macos', 'release', 'x86_64', '', '10.14'),
      AD('smoothie', '1.0.0', 0, 0, 'macos', 'release', 'x86_64', '', '10.14'),
      AD('water', '1.0.0', 2, 0, 'macos', 'release', 'x86_64', '', '10.14'),
    ]
    self.assertEqual( expected, am.list_latest_versions(self.MACOS_BT) )

if __name__ == '__main__':
  unit_test.main()
