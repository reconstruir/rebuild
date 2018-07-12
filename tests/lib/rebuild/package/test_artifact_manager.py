#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_find, file_util, temp_file
from bes.git import git
from rebuild.base import build_arch, build_blurb, build_system, build_target, build_level, package_descriptor as PD
from rebuild.package import artifact_manager, package, artifact_descriptor as AD
from rebuild.package.unit_test_packages import unit_test_packages
from rebuild.package.db_error import *

class test_artifact_manager(unit_test):

  DEBUG = unit_test.DEBUG
  #DEBUG = True

  LINUX_BT = build_target(build_system.LINUX, build_level.RELEASE, archs = 'x86_64')
  MACOS_BT = build_target(build_system.MACOS, build_level.RELEASE)
  
  @classmethod
  def _make_test_artifact_manager(clazz, address = None, items = None):
    root_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    if clazz.DEBUG:
      print("root_dir:\n%s\n" % (root_dir))
    am = artifact_manager(root_dir, address = address)
    if items:
      clazz._make_test_artifacts(items, am.root_dir)
    unit_test_packages.publish_artifacts(am)
    return am

  def test_artifact_path(self):
    am = self._make_test_artifact_manager()
    pi = PD('foo', '1.2.34-1')
    bt = self.LINUX_BT
    self.assertEqual( path.join(am.root_dir, pi.artifact_path(bt)), am.artifact_path(pi, bt) )

  def test_publish(self):
    am = self._make_test_artifact_manager()
    bt = self.LINUX_BT
    tmp_tarball = unit_test_packages.make_apple()
    filename = am.publish(tmp_tarball, bt, False)
    self.assertTrue( path.exists(filename) )

  def test_publish_again_with_replace(self):
    am = self._make_test_artifact_manager()
    bt = self.LINUX_BT
    tmp_tarball = unit_test_packages.make_apple()
    filename = am.publish(tmp_tarball, bt, True)
    self.assertTrue( path.exists(filename) )
    filename = am.publish(tmp_tarball, bt, True)

  def test_publish_again_without_replace(self):
    am = self._make_test_artifact_manager()
    bt = self.LINUX_BT
    tmp_tarball = unit_test_packages.make_apple()
    filename = am.publish(tmp_tarball, bt, False)
    self.assertTrue( path.exists(filename) )
    with self.assertRaises(AlreadyInstalledError) as context:
      am.publish(tmp_tarball, bt, False)

  def _make_test_artifacts_git_repo(self):
    tmp_repo = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print("tmp_repo:\n%s\n" % (tmp_repo))
    self._make_test_artifacts(unit_test_packages.TEST_PACKAGES, tmp_repo)
    assert not git.is_repo(tmp_repo)
    git.init(tmp_repo)
    git.add(tmp_repo, '.')
    git.commit(tmp_repo, 'unittest', '.')
    return self._make_test_artifact_manager(address = tmp_repo)

  @classmethod
  def _make_test_artifacts(clazz, items, root_dir):
    unit_test_packages.make_test_packages(items, root_dir)
    
  def test_find_by_package_descriptor_linux(self):
    am = self._make_test_artifacts_git_repo()

    self.assertEqual( 'water-1.0.0', am.find_by_package_descriptor(PD('water', '1.0.0'), self.LINUX_BT).package_descriptor.full_name )
    self.assertEqual( 'water-1.0.0-1', am.find_by_package_descriptor(PD('water', '1.0.0-1'), self.LINUX_BT).package_descriptor.full_name )
    self.assertEqual( 'water-1.0.0-2', am.find_by_package_descriptor(PD('water', '1.0.0-2'), self.LINUX_BT).package_descriptor.full_name )
    self.assertEqual( 'fructose-3.4.5-6', am.find_by_package_descriptor(PD('fructose', '3.4.5-6'), self.LINUX_BT).package_descriptor.full_name )
    self.assertEqual( 'apple-1.2.3-1', am.find_by_package_descriptor(PD('apple', '1.2.3-1'), self.LINUX_BT).package_descriptor.full_name )
    self.assertEqual( 'orange-6.5.4-3', am.find_by_package_descriptor(PD('orange', '6.5.4-3'), self.LINUX_BT).package_descriptor.full_name )
    self.assertEqual( 'orange_juice-1.4.5', am.find_by_package_descriptor(PD('orange_juice', '1.4.5'), self.LINUX_BT).package_descriptor.full_name )
    self.assertEqual( 'pear_juice-6.6.6', am.find_by_package_descriptor(PD('pear_juice', '6.6.6'), self.LINUX_BT).package_descriptor.full_name )

  def test_find_by_package_descriptor_macos(self):
    am = self._make_test_artifacts_git_repo()

    self.assertEqual( 'water-1.0.0', am.find_by_package_descriptor(PD('water', '1.0.0'), self.MACOS_BT).package_descriptor.full_name )
    self.assertEqual( 'water-1.0.0-1', am.find_by_package_descriptor(PD('water', '1.0.0-1'), self.MACOS_BT).package_descriptor.full_name )
    self.assertEqual( 'water-1.0.0-2', am.find_by_package_descriptor(PD('water', '1.0.0-2'), self.MACOS_BT).package_descriptor.full_name )
    self.assertEqual( 'fructose-3.4.5-6', am.find_by_package_descriptor(PD('fructose', '3.4.5-6'), self.MACOS_BT).package_descriptor.full_name )
    self.assertEqual( 'apple-1.2.3-1', am.find_by_package_descriptor(PD('apple', '1.2.3-1'), self.MACOS_BT).package_descriptor.full_name )
    self.assertEqual( 'orange-6.5.4-3', am.find_by_package_descriptor(PD('orange', '6.5.4-3'), self.MACOS_BT).package_descriptor.full_name )
    self.assertEqual( 'orange_juice-1.4.5', am.find_by_package_descriptor(PD('orange_juice', '1.4.5'), self.MACOS_BT).package_descriptor.full_name )
    self.assertEqual( 'pear_juice-6.6.6', am.find_by_package_descriptor(PD('pear_juice', '6.6.6'), self.MACOS_BT).package_descriptor.full_name )

  def test_list_latest_versions(self):
    self.maxDiff = None
    am = self._make_test_artifacts_git_repo()
    self.assertEqual( [
      AD('apple', '1.2.3', 1, 0, 'linux', 'release', ['x86_64'], ''),
      AD('arsenic', '1.2.9', 1, 0, 'linux', 'release', ['x86_64'], ''),
      AD('citrus', '1.0.0', 2, 0, 'linux', 'release', ['x86_64'], ''),
      AD('fiber', '1.0.0', 0, 0, 'linux', 'release', ['x86_64'], ''),
      AD('fructose', '3.4.5', 6, 0, 'linux', 'release', ['x86_64'], ''),
      AD('fruit', '1.0.0', 0, 0, 'linux', 'release', ['x86_64'], ''),
      AD('mercury', '1.2.9', 0, 0, 'linux', 'release', ['x86_64'], ''),
      AD('mercury_conflict', '3.2.1', 0, 0, 'linux', 'release', ['x86_64'], ''),
      AD('orange', '6.5.4', 3, 0, 'linux', 'release', ['x86_64'], ''),
      AD('orange_juice', '1.4.5', 0, 0, 'linux', 'release', ['x86_64'], ''),
      AD('pear', '1.2.3', 1, 0, 'linux', 'release', ['x86_64'], ''),
      AD('pear_juice', '6.6.6', 0, 0, 'linux', 'release', ['x86_64'], ''),
      AD('smoothie', '1.0.0', 0, 0, 'linux', 'release', ['x86_64'], ''),
      AD('water', '1.0.0', 2, 0, 'linux', 'release', ['x86_64'], ''),
    ], am.list_latest_versions(self.LINUX_BT) )
    
    self.assertEqual( [
      AD('apple', '1.2.3', 1, 0, 'macos', 'release', ['x86_64'], ''),
      AD('arsenic', '1.2.9', 1, 0, 'macos', 'release', ['x86_64'], ''),
      AD('citrus', '1.0.0', 2, 0, 'macos', 'release', ['x86_64'], ''),
      AD('fiber', '1.0.0', 0, 0, 'macos', 'release', ['x86_64'], ''),
      AD('fructose', '3.4.5', 6, 0, 'macos', 'release', ['x86_64'], ''),
      AD('fruit', '1.0.0', 0, 0, 'macos', 'release', ['x86_64'], ''),
      AD('mercury', '1.2.9', 0, 0, 'macos', 'release', ['x86_64'], ''),
      AD('mercury_conflict', '3.2.1', 0, 0, 'macos', 'release', ['x86_64'], ''),
      AD('orange', '6.5.4', 3, 0, 'macos', 'release', ['x86_64'], ''),
      AD('orange_juice', '1.4.5', 0, 0, 'macos', 'release', ['x86_64'], ''),
      AD('pear', '1.2.3', 1, 0, 'macos', 'release', ['x86_64'], ''),
      AD('pear_juice', '6.6.6', 0, 0, 'macos', 'release', ['x86_64'], ''),
      AD('smoothie', '1.0.0', 0, 0, 'macos', 'release', ['x86_64'], ''),
      AD('water', '1.0.0', 2, 0, 'macos', 'release', ['x86_64'], ''),
    ], am.list_latest_versions(self.MACOS_BT) )
    
if __name__ == '__main__':
  unit_test.main()
