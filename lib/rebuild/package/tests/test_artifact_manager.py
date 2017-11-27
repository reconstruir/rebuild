#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path, unittest
from bes.fs import temp_file
from bes.git import git
from rebuild.base import build_arch, build_blurb, build_system, build_target, build_level, package_descriptor
from rebuild.package import artifact_manager
from rebuild.package.unit_test_packages import unit_test_packages

class test_artifact_manager(unittest.TestCase):

  DEBUG = False
  #DEBUG = True

  @classmethod
  def __make_test_artifact_manager(clazz, address = None, items = None):
    publish_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    if clazz.DEBUG:
      print("publish_dir:\n%s\n" % (publish_dir))
    am = artifact_manager(publish_dir, address = address)
    if items:
      unit_test_packages.make_test_packages(items, am.publish_dir)
    return am

  def test_artifact_path(self):
    manager = self.__make_test_artifact_manager()
    pi = package_descriptor('foo', '1.2.34-1')
    bt = build_target(build_system.LINUX, build_level.RELEASE)
    self.assertEqual( path.join(manager.publish_dir, pi.artifact_path(bt)), manager.artifact_path(pi, bt) )

  def test_publish(self):
    manager = self.__make_test_artifact_manager()
    bt = build_target(build_system.LINUX, build_level.RELEASE)
    tmp_tarball = unit_test_packages.make_apple()
    filename = manager.publish(tmp_tarball, bt)
    self.assertTrue( path.exists(filename) )

  def test_publish_again(self):
    manager = self.__make_test_artifact_manager()
    bt = build_target(build_system.LINUX, build_level.RELEASE)
    tmp_tarball = unit_test_packages.make_apple()
    filename = manager.publish(tmp_tarball, bt)
    self.assertTrue( path.exists(filename) )
    filename = manager.publish(tmp_tarball, bt)

  def __make_test_artifacts_git_repo(self):
    tmp_repo = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print("tmp_repo:\n%s\n" % (tmp_repo))
    unit_test_packages.make_test_packages(unit_test_packages.TEST_PACKAGES, tmp_repo)
    assert not git.is_repo(tmp_repo)
    git.init(tmp_repo)
    git.add(tmp_repo, '.')
    git.commit(tmp_repo, 'unittest', '.')
    return self.__make_test_artifact_manager(address = tmp_repo)

  def test_artifact_from_git(self):
    manager = self.__make_test_artifacts_git_repo()

    linux = build_target(build_system.LINUX, build_level.RELEASE)
    darwin = build_target(build_system.MACOS, build_level.RELEASE)

    self.assertEqual( 'water-1.0.0', manager.package(package_descriptor('water', '1.0.0'), darwin).info.full_name )
    self.assertEqual( 'water-1.0.0-1', manager.package(package_descriptor('water', '1.0.0-1'), darwin).info.full_name )
    self.assertEqual( 'water-1.0.0-2', manager.package(package_descriptor('water', '1.0.0-2'), darwin).info.full_name )
    self.assertEqual( 'fructose-3.4.5-6', manager.package(package_descriptor('fructose', '3.4.5-6'), darwin).info.full_name )
    self.assertEqual( 'apple-1.2.3-1', manager.package(package_descriptor('apple', '1.2.3-1'), darwin).info.full_name )
    self.assertEqual( 'orange-6.5.4-3', manager.package(package_descriptor('orange', '6.5.4-3'), darwin).info.full_name )
    self.assertEqual( 'orange_juice-1.4.5', manager.package(package_descriptor('orange_juice', '1.4.5'), darwin).info.full_name )
    self.assertEqual( 'pear_juice-6.6.6', manager.package(package_descriptor('pear_juice', '6.6.6'), darwin).info.full_name )

    self.assertEqual( 'water-1.0.0', manager.package(package_descriptor('water', '1.0.0'), linux).info.full_name )
    self.assertEqual( 'water-1.0.0-1', manager.package(package_descriptor('water', '1.0.0-1'), linux).info.full_name )
    self.assertEqual( 'water-1.0.0-2', manager.package(package_descriptor('water', '1.0.0-2'), linux).info.full_name )
    self.assertEqual( 'fructose-3.4.5-6', manager.package(package_descriptor('fructose', '3.4.5-6'), linux).info.full_name )
    self.assertEqual( 'apple-1.2.3-1', manager.package(package_descriptor('apple', '1.2.3-1'), linux).info.full_name )
    self.assertEqual( 'orange-6.5.4-3', manager.package(package_descriptor('orange', '6.5.4-3'), linux).info.full_name )
    self.assertEqual( 'orange_juice-1.4.5', manager.package(package_descriptor('orange_juice', '1.4.5'), linux).info.full_name )
    self.assertEqual( 'pear_juice-6.6.6', manager.package(package_descriptor('pear_juice', '6.6.6'), linux).info.full_name )

#  def test_parse_filename(self):
#    self.assertEqual( package_descriptor('foo', '1.2.3-1'), artifact_manager.parse_filename('foo-1.2.3-1.tar.gz') )

if __name__ == '__main__':
  unittest.main()
