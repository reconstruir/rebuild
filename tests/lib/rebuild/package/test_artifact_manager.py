#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import temp_file
from bes.git import git
from rebuild.base import build_arch, build_blurb, build_system, build_target, build_level, package_descriptor
from rebuild.package import artifact_manager
from rebuild.package.unit_test_packages import unit_test_packages
from rebuild.package.db_error import *

class test_artifact_manager(unit_test):

  DEBUG = unit_test.DEBUG
  #DEBUG = True

  @classmethod
  def _make_test_artifact_manager(clazz, address = None, items = None):
    root_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    if clazz.DEBUG:
      print("root_dir:\n%s\n" % (root_dir))
    am = artifact_manager(root_dir, address = address)
    if items:
      unit_test_packages.make_test_packages(items, am.root_dir)
    return am

  def test_artifact_path(self):
    manager = self._make_test_artifact_manager()
    pi = package_descriptor('foo', '1.2.34-1')
    bt = build_target(build_system.LINUX, build_level.RELEASE)
    self.assertEqual( path.join(manager.root_dir, pi.artifact_path(bt)), manager.artifact_path(pi, bt) )

  def test_publish(self):
    manager = self._make_test_artifact_manager()
    bt = build_target(build_system.LINUX, build_level.RELEASE)
    tmp_tarball = unit_test_packages.make_apple()
    filename = manager.publish(tmp_tarball, bt, False)
    self.assertTrue( path.exists(filename) )

  def test_publish_again_with_replace(self):
    manager = self._make_test_artifact_manager()
    bt = build_target(build_system.LINUX, build_level.RELEASE)
    tmp_tarball = unit_test_packages.make_apple()
    filename = manager.publish(tmp_tarball, bt, True)
    self.assertTrue( path.exists(filename) )
    filename = manager.publish(tmp_tarball, bt, True)

  def test_publish_again_without_replace(self):
    manager = self._make_test_artifact_manager()
    bt = build_target(build_system.LINUX, build_level.RELEASE)
    tmp_tarball = unit_test_packages.make_apple()
    filename = manager.publish(tmp_tarball, bt, False)
    self.assertTrue( path.exists(filename) )
    with self.assertRaises(AlreadyInstalledError) as context:
      manager.publish(tmp_tarball, bt, False)

  def _make_test_artifacts_git_repo(self):
    tmp_repo = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print("tmp_repo:\n%s\n" % (tmp_repo))
    unit_test_packages.make_test_packages(unit_test_packages.TEST_PACKAGES, tmp_repo)
    assert not git.is_repo(tmp_repo)
    git.init(tmp_repo)
    git.add(tmp_repo, '.')
    git.commit(tmp_repo, 'unittest', '.')
    return self._make_test_artifact_manager(address = tmp_repo)

  def test_artifact_from_git(self):
    manager = self._make_test_artifacts_git_repo()

    linux = build_target(build_system.LINUX, build_level.RELEASE)
    darwin = build_target(build_system.MACOS, build_level.RELEASE)

    self.assertEqual( 'water-1.0.0', manager.package(package_descriptor('water', '1.0.0'), darwin).package_descriptor.full_name )
    self.assertEqual( 'water-1.0.0-1', manager.package(package_descriptor('water', '1.0.0-1'), darwin).package_descriptor.full_name )
    self.assertEqual( 'water-1.0.0-2', manager.package(package_descriptor('water', '1.0.0-2'), darwin).package_descriptor.full_name )
    self.assertEqual( 'fructose-3.4.5-6', manager.package(package_descriptor('fructose', '3.4.5-6'), darwin).package_descriptor.full_name )
    self.assertEqual( 'apple-1.2.3-1', manager.package(package_descriptor('apple', '1.2.3-1'), darwin).package_descriptor.full_name )
    self.assertEqual( 'orange-6.5.4-3', manager.package(package_descriptor('orange', '6.5.4-3'), darwin).package_descriptor.full_name )
    self.assertEqual( 'orange_juice-1.4.5', manager.package(package_descriptor('orange_juice', '1.4.5'), darwin).package_descriptor.full_name )
    self.assertEqual( 'pear_juice-6.6.6', manager.package(package_descriptor('pear_juice', '6.6.6'), darwin).package_descriptor.full_name )

    self.assertEqual( 'water-1.0.0', manager.package(package_descriptor('water', '1.0.0'), linux).package_descriptor.full_name )
    self.assertEqual( 'water-1.0.0-1', manager.package(package_descriptor('water', '1.0.0-1'), linux).package_descriptor.full_name )
    self.assertEqual( 'water-1.0.0-2', manager.package(package_descriptor('water', '1.0.0-2'), linux).package_descriptor.full_name )
    self.assertEqual( 'fructose-3.4.5-6', manager.package(package_descriptor('fructose', '3.4.5-6'), linux).package_descriptor.full_name )
    self.assertEqual( 'apple-1.2.3-1', manager.package(package_descriptor('apple', '1.2.3-1'), linux).package_descriptor.full_name )
    self.assertEqual( 'orange-6.5.4-3', manager.package(package_descriptor('orange', '6.5.4-3'), linux).package_descriptor.full_name )
    self.assertEqual( 'orange_juice-1.4.5', manager.package(package_descriptor('orange_juice', '1.4.5'), linux).package_descriptor.full_name )
    self.assertEqual( 'pear_juice-6.6.6', manager.package(package_descriptor('pear_juice', '6.6.6'), linux).package_descriptor.full_name )

if __name__ == '__main__':
  unit_test.main()
