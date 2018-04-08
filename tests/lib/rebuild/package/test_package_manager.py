#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from bes.fs import temp_file
from bes.system import host
from rebuild.base import build_system, build_target, build_level, package_descriptor
from rebuild.pkg_config import pkg_config
from rebuild.package import artifact_manager, package_manager
from rebuild.package import PackageFilesConflictError, PackageMissingRequirementsError
from rebuild.package.db_error import *
from bes.archive import archiver, temp_archive
from rebuild.package.unit_test_packages import unit_test_packages

class test_package_manager(unittest.TestCase):

  TEST_BUILD_TARGET = build_target(build_system.LINUX, build_level.RELEASE)

  ZLIB_CONTENTS = [
    'include/zconf.h',
    'include/zlib.h',
    'lib/librebbe_z.a',
    'lib/libz.a',
    'lib/pkgconfig/rebbe_zlib.pc',
    'lib/pkgconfig/zlib.pc',
    'share/man/man3/zlib.3',
  ]

  DEBUG = False
  #DEBUG = True

  @classmethod
  def _make_test_pm(clazz):
    root_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    pm_dir = path.join(root_dir, 'package_manager')
    if clazz.DEBUG:
      print("\nroot_dir:\n", root_dir)
    am = clazz._make_test_artifact_manager()
    return package_manager(pm_dir, am)

  def test_install_tarball_simple(self):
    pm = self._make_test_pm()
    water_tarball = unit_test_packages.make_water()
    pm.install_tarball(water_tarball, ['BUILD', 'RUN'])

  def test_install_tarball_pkg_config(self):
    self.maxDiff = None
    pm = self._make_test_pm()

    water_tarball = unit_test_packages.make_water()
    pm.install_tarball(water_tarball, ['BUILD', 'RUN'])

    PKG_CONFIG_PATH = pm.pkg_config_path

    # list_all
    packages = pkg_config.list_all(PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    # 2 because of the rebbe_ links
    self.assertEqual( 1, len(packages) )
    self.assertEqual( set(['water']), set([ p[0] for p in packages ]) )

    # cflags
    modules = [ 'water' ]
    cflags = pkg_config.cflags(modules, PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    expected_cflags = [
      '-I%s' % (path.join(pm.installation_dir, 'include')),
    ]
    self.assertEqual( expected_cflags, cflags )

    # libs
    modules = [ 'water' ]
    libs = pkg_config.libs(modules, PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    expected_libs = [
      '-L%s' % (path.join(pm.installation_dir, 'lib')),
      '-lwater',
    ]
    self.assertEqual( expected_libs, libs )

  def test_install_tarball_conflicts(self):
    pm = self._make_test_pm()
    mercury_tarball = unit_test_packages.make_mercury(debug = self.DEBUG)
    mercury_confict_tarball = unit_test_packages.make_mercury_conflict(debug = self.DEBUG)
    pm.install_tarball(mercury_tarball, ['BUILD', 'RUN'])
    with self.assertRaises(PackageFilesConflictError) as context:
      pm.install_tarball(mercury_confict_tarball, ['BUILD', 'RUN'])

  def test_install_tarball_already_installed(self):
    pm = self._make_test_pm()
    water_tarball = unit_test_packages.make_water(debug = self.DEBUG)
    pm.install_tarball(water_tarball, ['BUILD', 'RUN'])
    with self.assertRaises(AlreadyInstalledError) as context:
      pm.install_tarball(water_tarball, ['BUILD', 'RUN'])
    self.assertEqual( 'package water already installed', context.exception.message )

  def test_install_tarball_missing_requirements(self):
    pm = self._make_test_pm()
    apple_tarball = unit_test_packages.make_apple(debug = self.DEBUG)
    with self.assertRaises(PackageMissingRequirementsError) as context:
      pm.install_tarball(apple_tarball, ['BUILD', 'RUN'])
    self.assertEqual( 'package apple missing requirements: fiber, fructose, water', context.exception.message )

  def test_install_tarball_with_manual_requirements(self):
    pm = self._make_test_pm()
    water_tarball = unit_test_packages.make_water(debug = self.DEBUG)
    apple_tarball = unit_test_packages.make_apple(debug = self.DEBUG)
    fructose_tarball = unit_test_packages.make_fructose(debug = self.DEBUG)
    fiber_tarball = unit_test_packages.make_fiber(debug = self.DEBUG)
    fruit_tarball = unit_test_packages.make_fruit(debug = self.DEBUG)
    pm.install_tarball(water_tarball, ['BUILD', 'RUN'])
    pm.install_tarball(fiber_tarball, ['BUILD', 'RUN'])
    pm.install_tarball(fructose_tarball, ['BUILD', 'RUN'])
    pm.install_tarball(fruit_tarball, ['BUILD', 'RUN'])
    pm.install_tarball(apple_tarball, ['BUILD', 'RUN'])

  def test_uninstall(self):
    pm = self._make_test_pm()
    pi = package_descriptor('water', '1.0.0')
    install_rv = pm.install_package(pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all(include_version = True) )
    pm.uninstall_package('water')
    self.assertEqual( [], pm.list_all(include_version = True) )
    
  def test_is_installed(self):
    pm = self._make_test_pm()
    water_tarball = unit_test_packages.make_water(debug = self.DEBUG)
    pm.install_tarball(water_tarball, ['BUILD', 'RUN'])
    self.assertTrue( pm.is_installed('water') )
    self.assertFalse( pm.is_installed('notthere') )

  @classmethod
  def _make_test_artifact_manager(clazz):
    root_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    if clazz.DEBUG:
      print("root_dir:\n%s\n" % (root_dir))
    am = artifact_manager(root_dir, address = None, no_git = True)
    unit_test_packages.make_test_packages(unit_test_packages.TEST_PACKAGES, am.root_dir)
    return am

  def test_install_package(self):
    pm = self._make_test_pm()
    pi = package_descriptor('water', '1.0.0')
    install_rv = pm.install_package(pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all(include_version = True) )

  def test_install_package_upgrade(self):
    pm = self._make_test_pm()

    old_pi = package_descriptor('water', '1.0.0')
    install_rv = pm.install_package(old_pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all(include_version = True) )

    new_pi = package_descriptor('water', '1.0.0-1')
    install_rv = pm.install_package(new_pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0-1' ], pm.list_all(include_version = True) )

  def test_install_package_same_version(self):
    pm = self._make_test_pm()

    old_pi = package_descriptor('water', '1.0.0')
    install_rv = pm.install_package(old_pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all(include_version = True) )

    new_pi = package_descriptor('water', '1.0.0')
    install_rv = pm.install_package(new_pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertFalse( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all(include_version = True) )

  def test_install_package_unknown(self):
    pm = self._make_test_pm()
    pi = package_descriptor('notthere', '6.6.6-1')
    with self.assertRaises(NotInstalledError) as context:
      pm.install_package(pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])

  def test_install_packages(self):
    pm = self._make_test_pm()

    packages = [
      package_descriptor.parse('water-1.0.0'),
      package_descriptor.parse('mercury-1.2.8'),
      package_descriptor.parse('arsenic-1.2.9'),
    ]

    pm.install_packages(packages, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])

    self.assertEqual( [ 'arsenic-1.2.9', 'mercury-1.2.8', 'water-1.0.0' ], pm.list_all(include_version = True) )

if __name__ == '__main__':
  unittest.main()
