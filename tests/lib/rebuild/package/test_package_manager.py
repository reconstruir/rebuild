#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_find, file_util, temp_file
from bes.system import host
from rebuild.base import build_target as BT, package_descriptor
from rebuild.pkg_config import pkg_config
from rebuild.package import artifact_manager, package, package_manager
from rebuild.package import PackageFilesConflictError, PackageMissingRequirementsError
from rebuild.package.db_error import *
from bes.archive import archiver, temp_archive
from _rebuild_testing.fake_package_unit_test import fake_package_unit_test as FPUT

class test_package_manager(unit_test):

  DEBUG = unit_test.DEBUG
  DEBUG = True

  TEST_BUILD_TARGET = BT.parse_path('linux-ubuntu-18/x86_64/release')

  ZLIB_CONTENTS = [
    'include/zconf.h',
    'include/zlib.h',
    'lib/librebbe_z.a',
    'lib/libz.a',
    'lib/pkgconfig/rebbe_zlib.pc',
    'lib/pkgconfig/zlib.pc',
    'share/man/man3/zlib.3',
  ]

  @classmethod
  def _make_test_pm_with_am(clazz):
    root_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    pm_dir = path.join(root_dir, 'package_manager')
    if clazz.DEBUG:
      print("\nroot_dir:\n", root_dir)
    am = clazz._make_test_artifact_manager()
    return package_manager(pm_dir, am)

  @classmethod
  def _make_empty_pm(clazz):
    root_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    pm_dir = path.join(root_dir, 'package_manager')
    am_dir = path.join(root_dir, 'artifact_manager')
    if clazz.DEBUG:
      print("root_dir:\n%s\n" % (root_dir))
    am = artifact_manager(am_dir)
    return package_manager(pm_dir, am)
  
  def test_install_tarball_simple(self):
    pm = self._make_empty_pm()
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    water_tarball = FPUT.create_one_package(FPUT.WATER_RECIPE, mutations)
    pm.install_tarball(water_tarball, ['BUILD', 'RUN'])
    
  def test_install_tarball_pkg_config(self):
    recipe = '''
fake_package libfoo 1.0.0 0 0 linux release x86_64 ubuntu 18
  files
    lib/pkgconfig/libfoo.pc
      prefix=${REBUILD_PACKAGE_PREFIX}
      exec_prefix=${prefix}
      libdir=${exec_prefix}/lib
      includedir=${prefix}/include
      
      Name: libfoo
      Description: libfoo
      Version: 1.0.0
      Libs: -L${libdir} -lfoo
      Libs.private: -lfoo-private
      Cflags: -I${includedir}
'''

    self.maxDiff = None
    pm = self._make_test_pm_with_am()
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    tarball = FPUT.create_one_package(recipe, metadata_mutations = mutations, debug = self.DEBUG)
    pm.install_tarball(tarball, ['BUILD', 'RUN'])
    self.assertEqual( [ 'libfoo-1.0.0' ], pm.list_all(include_version = True) )
    
    PKG_CONFIG_PATH = pm.pkg_config_path
    print('PKG_CONFIG_PATH: %s' % (PKG_CONFIG_PATH))
    
    # list_all
    packages = pkg_config.list_all(PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    # 2 because of the rebbe_ links
    self.assertEqual( 1, len(packages) )
    self.assertEqual( set(['libfoo']), set([ p[0] for p in packages ]) )

    # cflags
    modules = [ 'libfoo' ]
    cflags = pkg_config.cflags(modules, PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    expected_cflags = [
      '-I%s' % (path.join(pm.installation_dir, 'include')),
    ]
    self.assertEqual( expected_cflags, cflags )

    # libs
    modules = [ 'libfoo' ]
    libs = pkg_config.libs(modules, PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    expected_libs = [
      '-L%s' % (path.join(pm.installation_dir, 'lib')),
      '-lfoo',
    ]
    self.assertEqual( expected_libs, libs )

  def test_install_tarball_conflicts(self):
    foo_recipe = '''
fake_package foo 1.0.0 0 0 linux release x86_64 ubuntu 18
  files
    foo/cellulose.txt
      cellulose
    foo/inulin.txt
      inulin
'''

    bar_recipe = '''
fake_package bar 1.0.0 0 0 linux release x86_64 ubuntu 18
  files
    foo/cellulose.txt
      cellulose
    foo/inulin.txt
      inulin
'''

    pm = self._make_empty_pm()
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    foo_tarball = FPUT.create_one_package(foo_recipe, mutations)
    bar_tarball = FPUT.create_one_package(bar_recipe, mutations)
    pm.install_tarball(foo_tarball, ['BUILD', 'RUN'])
    with self.assertRaises(PackageFilesConflictError) as context:
      pm.install_tarball(bar_tarball, ['BUILD', 'RUN'])

  def test_install_tarball_already_installed(self):
    pm = self._make_empty_pm()
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    tarball = FPUT.create_one_package(FPUT.WATER_RECIPE, mutations)
    pm.install_tarball(tarball, ['BUILD', 'RUN'])
    with self.assertRaises(AlreadyInstalledError) as context:
      pm.install_tarball(tarball, ['BUILD', 'RUN'])
    self.assertEqual( 'package water already installed', context.exception.message )

  def test_install_tarball_missing_requirements(self):
    pm = self._make_test_pm_with_am()
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    apple_tarball = FPUT.create_one_package(FPUT.APPLE_RECIPE, mutations)
    with self.assertRaises(PackageMissingRequirementsError) as context:
      pm.install_tarball(apple_tarball, ['BUILD', 'RUN'])
    self.assertEqual( 'package apple missing requirements: fiber, fructose, water', context.exception.message )

  def test_install_tarball_with_manual_requirements(self):
    foo_recipe = '''
fake_package foo 1.0.0 0 0 linux release x86_64 ubuntu 18
'''
    bar_recipe = '''
fake_package bar 1.0.0 0 0 linux release x86_64 ubuntu 18
  requirements
    foo >= 1.0.0
'''

    baz_recipe = '''
fake_package baz 1.0.0 0 0 linux release x86_64 ubuntu 18
  requirements
    bar >= 1.0.0
'''
    
    pm = self._make_test_pm_with_am()
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    bt = BT.parse_path('linux-ubuntu-18/x86_64/release')
    foo_tarball = FPUT.create_one_package(foo_recipe, mutations)
    bar_tarball = FPUT.create_one_package(bar_recipe, mutations)
    baz_tarball = FPUT.create_one_package(baz_recipe, mutations)

    pm._artifact_manager.publish(foo_tarball, bt, False)
    pm._artifact_manager.publish(bar_tarball, bt, False)
    pm._artifact_manager.publish(baz_tarball, bt, False)
    
    pm.install_tarball(foo_tarball, ['BUILD', 'RUN'])
    pm.install_tarball(bar_tarball, ['BUILD', 'RUN'])
    pm.install_tarball(baz_tarball, ['BUILD', 'RUN'])

  def test_uninstall(self):
    pm = self._make_test_pm_with_am()
    pi = package_descriptor('water', '1.0.0')
    install_rv = pm.install_package(pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all(include_version = True) )
    pm.uninstall_package('water')
    self.assertEqual( [], pm.list_all(include_version = True) )
    
  def test_is_installed(self):
    pm = self._make_empty_pm()
    self.assertFalse( pm.is_installed('water') )
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    tarball = FPUT.create_one_package(FPUT.WATER_RECIPE, mutations)
    pm.install_tarball(tarball, ['BUILD', 'RUN'])
    self.assertTrue( pm.is_installed('water') )
    self.assertFalse( pm.is_installed('notthere') )

  @classmethod
  def _make_test_artifact_manager(clazz):
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    return FPUT.make_artifact_manager(debug = clazz.DEBUG,
                                      recipes = FPUT.TEST_RECIPES,
                                      build_target = clazz.TEST_BUILD_TARGET,
                                      mutations = mutations)

  def test_install_package(self):
    pm = self._make_test_pm_with_am()
    pi = package_descriptor('water', '1.0.0')
    install_rv = pm.install_package(pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all(include_version = True) )

  def test_install_package_upgrade(self):
    pm = self._make_test_pm_with_am()

    old_pi = package_descriptor('water', '1.0.0')
    install_rv = pm.install_package(old_pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all(include_version = True) )

    new_pi = package_descriptor('water', '1.0.0-1')
    install_rv = pm.install_package(new_pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0-1' ], pm.list_all(include_version = True) )

  def test_install_package_same_version(self):
    pm = self._make_test_pm_with_am()

    old_pi = package_descriptor('water', '1.0.0')
    install_rv = pm.install_package(old_pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all(include_version = True) )

    new_pi = package_descriptor('water', '1.0.0')
    install_rv = pm.install_package(new_pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertFalse( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all(include_version = True) )

  def test_install_package_unknown(self):
    pm = self._make_test_pm_with_am()
    pi = package_descriptor('notthere', '6.6.6-1')
    with self.assertRaises(NotInstalledError) as context:
      pm.install_package(pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])

  def test_install_packages(self):
    pm = self._make_test_pm_with_am()

    packages = [
      package_descriptor.parse('water-1.0.0'),
      package_descriptor.parse('mercury-1.2.8'),
      package_descriptor.parse('arsenic-1.2.9'),
    ]

    pm.install_packages(packages, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])

    self.assertEqual( [ 'arsenic-1.2.9', 'mercury-1.2.8', 'water-1.0.0' ], pm.list_all(include_version = True) )

  def test_dep_map(self):
    pm = self._make_test_pm_with_am()
    packages = [
      package_descriptor.parse('water-1.0.0'),
      package_descriptor.parse('fiber-1.0.0'),
      package_descriptor.parse('fructose-3.4.5-6'),
      package_descriptor.parse('fruit-1.0.0'),
      package_descriptor.parse('apple-1.2.3-1'),
    ]
    pm.install_packages(packages, self.TEST_BUILD_TARGET, [ 'RUN' ])
    self.assertEqual( [ 'apple-1.2.3-1', 'fiber-1.0.0', 'fructose-3.4.5-6', 'fruit-1.0.0', 'water-1.0.0' ],
                      pm.list_all(include_version = True) )
    self.assertEqual( {
      'apple': set(['fruit']),
      'fiber': set([]),
      'fructose': set([]),
      'fruit': set(['fiber', 'fructose', 'water']),
      'water': set([]),
    }, pm.dep_map() )

if __name__ == '__main__':
  unit_test.main()
