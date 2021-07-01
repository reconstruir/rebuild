#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path

from bes.archive.archiver import archiver
from bes.archive.temp_archive import temp_archive
from bes.common.check import check
from bes.common.dict_util import dict_util
from bes.common.object_util import object_util
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.execute import execute
from bes.system.os_env import os_env
from bes.testing.unit_test import unit_test

from bes.build.build_target import build_target as BT
from bes.build.package_descriptor import package_descriptor as PD
from bes.build.package_descriptor_list import package_descriptor_list as PDL
from rebuild.package.artifact_manager_local import artifact_manager_local
from rebuild.package.db_error import *
from rebuild.package.package import package
from rebuild.package.package_install_options import package_install_options
from rebuild.package.package_manager import PackageFilesConflictError
from rebuild.package.package_manager import PackageMissingRequirementsError
from rebuild.package.package_manager import package_manager
from rebuild.pkg_config.pkg_config import pkg_config

from rebuild._testing.fake_package_unit_test import fake_package_unit_test as FPUT
from rebuild._testing.fake_package_recipes import fake_package_recipes as RECIPES
from rebuild._testing.artifact_manager_tester import artifact_manager_tester as AMT
from rebuild._testing.artifact_manager_helper import artifact_manager_helper

from bes.build.build_system import build_system
from bes.testing.unit_test_skip import skip_if

class test_package_manager(unit_test):

  DEBUG = unit_test.DEBUG
  #DEBUG = True

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
    am = artifact_manager_helper.make_local_artifact_manager(am_dir)
    return package_manager(pm_dir, am)

  @classmethod
  def _make_caca_test_pm(clazz, am):
    root_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    pm_dir = path.join(root_dir, 'package_manager')
    if clazz.DEBUG:
      print("\nroot_dir:\n", root_dir)
    return package_manager(pm_dir, am)
  
  def test_install_tarball_simple(self):
    pm = self._make_empty_pm()
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version_major': '18' }
    water_tarball = FPUT.create_one_package(RECIPES.WATER, mutations)
    pm.install_tarball(water_tarball.filename, water_tarball.metadata, ['BUILD', 'RUN'])
    
  def test_install_tarball_pkg_config(self):
    recipe = r'''
fake_package libfoo 1.0.0 0 0 linux release x86_64 ubuntu 18 none
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
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version_major': '18' }
    pkg = FPUT.create_one_package(recipe, metadata_mutations = mutations, debug = self.DEBUG)
    pm.install_tarball(pkg.filename, pkg.metadata, ['BUILD', 'RUN'])
    self.assertEqual( [ 'libfoo-1.0.0' ], pm.list_all_names(include_version = True) )
    
    PKG_CONFIG_PATH = pm.pkg_config_path
    
    # list_all_names
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

  def test_install_tarball_conflicts_same_checksum(self):
    foo_recipe = r'''
fake_package foo 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  files
    foo/cellulose.txt
      cellulose
    foo/inulin.txt
      inulin
'''

    bar_recipe = r'''
fake_package bar 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  files
    foo/cellulose.txt
      cellulose
    foo/inulin.txt
      inulin
'''

    pm = self._make_empty_pm()
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version_major': '18' }
    foo_tarball = FPUT.create_one_package(foo_recipe, mutations)
    bar_tarball = FPUT.create_one_package(bar_recipe, mutations)
    pm.install_tarball(foo_tarball.filename, foo_tarball.metadata, ['BUILD', 'RUN'])
    pm.install_tarball(bar_tarball.filename, bar_tarball.metadata, ['BUILD', 'RUN'])
    self.assertEqual( [ 'bar-1.0.0', 'foo-1.0.0' ], pm.list_all_names(include_version = True) )

  def test_install_tarball_conflicts_different_checksum(self):
    foo_recipe = r'''
fake_package foo 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  files
    foo/cellulose.txt
      cellulose1
    foo/inulin.txt
      inulin
'''

    bar_recipe = r'''
fake_package bar 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  files
    foo/cellulose.txt
      cellulose2
    foo/inulin.txt
      inulin
'''

    pm = self._make_empty_pm()
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version_major': '18' }
    foo_tarball = FPUT.create_one_package(foo_recipe, mutations)
    bar_tarball = FPUT.create_one_package(bar_recipe, mutations)
    pm.install_tarball(foo_tarball.filename, foo_tarball.metadata, ['BUILD', 'RUN'])
    with self.assertRaises(PackageFilesConflictError) as context:
      pm.install_tarball(bar_tarball.filename, bar_tarball.metadata, ['BUILD', 'RUN'])
    self.assertEqual( [ 'foo-1.0.0' ], pm.list_all_names(include_version = True) )
      
  def test_install_tarball_already_installed(self):
    pm = self._make_empty_pm()
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version_major': '18' }
    water = FPUT.create_one_package(RECIPES.WATER, mutations)
    pm.install_tarball(water.filename, water.metadata, ['BUILD', 'RUN'])
    with self.assertRaises(AlreadyInstalledError) as context:
      pm.install_tarball(water.filename, water.metadata, ['BUILD', 'RUN'])
    self.assertEqual( 'package water already installed', context.exception.message )

  def test_install_tarball_missing_requirements(self):
    pm = self._make_test_pm_with_am()
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version_major': '18' }
    apple_package = FPUT.create_one_package(RECIPES.APPLE, mutations)
    with self.assertRaises(PackageMissingRequirementsError) as context:
      pm.install_tarball(apple_package.filename, apple_package.metadata, ['BUILD', 'RUN'])
    self.assertEqual( 'package apple missing requirements: fiber, fructose, water', context.exception.message )

  def test_install_tarball_with_manual_requirements(self):
    foo_recipe = r'''
fake_package foo 1.0.0 0 0 linux release x86_64 ubuntu 18 none
'''
    bar_recipe = r'''
fake_package bar 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  requirements
    foo >= 1.0.0
'''

    baz_recipe = r'''
fake_package baz 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  requirements
    bar >= 1.0.0
'''
    
    pm = self._make_test_pm_with_am()
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version_major': '18' }
    foo_tarball = FPUT.create_one_package(foo_recipe, mutations)
    bar_tarball = FPUT.create_one_package(bar_recipe, mutations)
    baz_tarball = FPUT.create_one_package(baz_recipe, mutations)

    pm._artifact_manager.publish(foo_tarball.filename, False, foo_tarball.metadata)
    pm._artifact_manager.publish(bar_tarball.filename, False, bar_tarball.metadata)
    pm._artifact_manager.publish(baz_tarball.filename, False, baz_tarball.metadata)
    
    pm.install_tarball(foo_tarball.filename, foo_tarball.metadata, ['BUILD', 'RUN'])
    pm.install_tarball(bar_tarball.filename, bar_tarball.metadata, ['BUILD', 'RUN'])
    pm.install_tarball(baz_tarball.filename, baz_tarball.metadata, ['BUILD', 'RUN'])

  def test_uninstall(self):
    pm = self._make_test_pm_with_am()
    pi = PD('water', '1.0.0')
    install_rv = pm.install_package(pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all_names(include_version = True) )
    pm.uninstall_package(pi)
    self.assertEqual( [], pm.list_all_names(include_version = True) )
    
  def test_is_installed(self):
    pm = self._make_empty_pm()
    self.assertFalse( pm.is_installed('water') )
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version_major': '18' }
    pkg = FPUT.create_one_package(RECIPES.WATER, mutations)
    pm.install_tarball(pkg.filename, pkg.metadata, ['BUILD', 'RUN'])
    self.assertTrue( pm.is_installed('water') )
    self.assertFalse( pm.is_installed('notthere') )

  @classmethod
  def _make_test_artifact_manager(clazz):
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version_major': '18' }
    return FPUT.make_artifact_manager(debug = clazz.DEBUG,
                                      recipes = RECIPES.FOODS,
                                      mutations = mutations)

  def test_install_package(self):
    pm = self._make_test_pm_with_am()
    pi = PD('water', '1.0.0')
    install_rv = pm.install_package(pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all_names(include_version = True) )

  def test_install_package_upgrade(self):
    pm = self._make_test_pm_with_am()

    old_pkg_desc = PD('water', '1.0.0')
    install_rv = pm.install_package(old_pkg_desc, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all_names(include_version = True) )

    new_pkg_desc = PD('water', '1.0.0-1')
    install_rv = pm.install_package(new_pkg_desc, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0-1' ], pm.list_all_names(include_version = True) )

  def test_install_package_same_version(self):
    pm = self._make_test_pm_with_am()

    old_pkg_desc = PD('water', '1.0.0')
    install_rv = pm.install_package(old_pkg_desc, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all_names(include_version = True) )

    new_pkg_desc = PD('water', '1.0.0')
    install_rv = pm.install_package(new_pkg_desc, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertFalse( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all_names(include_version = True) )

  def test_install_package_unknown(self):
    pm = self._make_test_pm_with_am()
    pi = PD('notthere', '6.6.6-1')
    with self.assertRaises(NotInstalledError) as context:
      pm.install_package(pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])

  def test_install_packages(self):
    pm = self._make_test_pm_with_am()
    packages = PDL([
      PD.parse('arsenic-1.2.9'),
      PD.parse('mercury-1.2.8'),
      PD.parse('water-1.0.0'),
    ])
    pm.install_packages(packages, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertEqual( [ 'arsenic-1.2.9', 'mercury-1.2.8', 'water-1.0.0' ], pm.list_all_names(include_version = True) )

  def test_list_all_descriptors(self):
    pm = self._make_test_pm_with_am()
    packages = PDL([
      PD.parse('arsenic-1.2.9'),
      PD.parse('mercury-1.2.8'),
      PD.parse('water-1.0.0'),
    ])
    pm.install_packages(packages, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    actual = pm.list_all_descriptors()
    self.assertEqual( packages, pm.list_all_descriptors() )

  def test_dep_map(self):
    pm = self._make_test_pm_with_am()
    packages = PDL([
      PD.parse('water-1.0.0'),
      PD.parse('fiber-1.0.0'),
      PD.parse('fructose-3.4.5-6'),
      PD.parse('fruit-1.0.0'),
      PD.parse('apple-1.2.3-1'),
    ])
    pm.install_packages(packages, self.TEST_BUILD_TARGET, [ 'RUN' ])
    self.assertEqual( [ 'apple-1.2.3-1', 'fiber-1.0.0', 'fructose-3.4.5-6', 'fruit-1.0.0', 'water-1.0.0' ],
                      pm.list_all_names(include_version = True) )
    self.assertEqual( {
      'apple': set(['fruit']),
      'fiber': set([]),
      'fructose': set([]),
      'fruit': set(['fiber', 'fructose', 'water']),
      'water': set([]),
    }, pm.dep_map() )

  def test_descriptors_for_names(self):
    pm = self._make_test_pm_with_am()
    packages = PDL([
      PD.parse('water-1.0.0'),
      PD.parse('fiber-1.0.0'),
      PD.parse('fructose-3.4.5-6'),
      PD.parse('fruit-1.0.0'),
      PD.parse('apple-1.2.3-1'),
    ])
    pm.install_packages(packages, self.TEST_BUILD_TARGET, [ 'RUN' ])
    self.assertEqual( PDL([ PD.parse('water-1.0.0') ]), pm.descriptors_for_names([ 'water' ]) )
    self.assertEqual( PDL([ PD.parse('fiber-1.0.0'), PD.parse('water-1.0.0') ]), pm.descriptors_for_names([ 'water', 'fiber' ]) )

  def _make_cabbage_pm(self):
    t = AMT(recipes = self.VEGGIES)
    t.publish('cabbage;1.0.0;0;0;linux;release;x86_64;ubuntu;18;')
    t.publish('unset;1.0.0;0;0;linux;release;x86_64;ubuntu;18;')
    pm = self._make_caca_test_pm(t.am)
    cabbage = PD.parse('cabbage-1.0.0')
    bt = BT.parse_path('linux-ubuntu-18/x86_64/release')
    pm.install_package(cabbage, bt, [ 'RUN' ])
    pm.install_package(PD.parse('unset-1.0.0'), bt, [ 'RUN' ])
    return pm, cabbage

  def _make_one_env_file_pm(self, code):
    recipe = self.ONE_ENV_FILE_RECIPE % (code)
    t = AMT(recipes = recipe)
    t.publish('one_env_file;1.0.0;0;0;linux;release;x86_64;ubuntu;18;')
    pm = self._make_caca_test_pm(t.am)
    pdesc = PD.parse('one_env_file-1.0.0')
    bt = BT.parse_path('linux-ubuntu-18/x86_64/release')
    pm.install_package(pdesc, bt, [ 'RUN' ])
    return pm

  def _make_two_env_files_pm(self, code1, code2):
    recipe = self.TWO_ENV_FILES_RECIPE % (code1, code2)
    t = AMT(recipes = recipe)
    t.publish('two_env_files;1.0.0;0;0;linux;release;x86_64;ubuntu;18;')
    pm = self._make_caca_test_pm(t.am)
    pdesc = PD.parse('two_env_files-1.0.0')
    bt = BT.parse_path('linux-ubuntu-18/x86_64/release')
    pm.install_package(pdesc, bt, [ 'RUN' ])
    return pm
  
  def test_transform_env_input_not_mutated(self):
    'Check that the environment passed into transform_env() is not mutated.'
    pm, cabbage = self._make_cabbage_pm()
    env1 = { 'FOO': 'foo', 'BAR': 'bar' }
    env1_save = copy.deepcopy(env1)
    env2 = pm.transform_env(env1, [ 'cabbage' ])
    self.assert_dict_as_text_equal( env1_save, env1 )
  
  @skip_if(not build_system.HOST == build_system.MACOS, 'FIXME: broken on linux')
  def test_transform_env_defaults(self):
    'Check the defaults of transform_env() when the input env is empty.'
    pm, cabbage = self._make_cabbage_pm()
    env1 = {}
    env2 = self._transform_env(pm, env1, [ 'cabbage' ])
    self.assertEqual( {
      'PKG_CONFIG_PATH': '$ROOT_DIR/stuff/lib/pkgconfig:$ROOT_DIR/stuff/share/pkgconfig',
      'PATH': '$DEFAULT_PATH:$ROOT_DIR/stuff/bin:$ROOT_DIR/stuff/bin',
      'PYTHONPATH': '$ROOT_DIR/stuff/lib/python',
      '$LD_LIBRARY_PATH': '$ROOT_DIR/stuff/lib',
    }, env2 )

  def test_transform_env_append(self):
    code = r'''
      bes_env_path_append PATH /zzzz/bin
      bes_env_path_append PYTHONPATH /zzzz/lib/python
'''
    pm = self._make_one_env_file_pm(code)
    env1 = {
      'PATH': '$DEFAULT_PATH:/p/bin',
      'PYTHONPATH': '/p/lib/python',
    }
    env2 = self._transform_env(pm, env1, [ 'one_env_file' ])
    expected = {
      'PATH': '$DEFAULT_PATH:/p/bin:$ROOT_DIR/stuff/bin:/zzzz/bin',
      'PYTHONPATH': '/p/lib/python:$ROOT_DIR/stuff/lib/python:/zzzz/lib/python',
      '$LD_LIBRARY_PATH':  '$ROOT_DIR/stuff/lib',
      'PKG_CONFIG_PATH': '$ROOT_DIR/stuff/lib/pkgconfig:$ROOT_DIR/stuff/share/pkgconfig',
    }
    self.assert_dict_as_text_equal( expected, env2 )

  def test_transform_env_prepend(self):
    code = r'''
      bes_env_path_prepend PATH /zzzz/bin
      bes_env_path_prepend PYTHONPATH /zzzz/lib/python
#      bes_env_path_prepend LD_LIBRARY_PATH /zzzz/lib
'''
    pm = self._make_one_env_file_pm(code)
    env1 = {
      'PATH': '$DEFAULT_PATH:/p/bin',
      'PYTHONPATH': '/p/lib/python',
#      '$LD_LIBRARY_PATH': '/p/lib',
    }
    env2 = self._transform_env(pm, env1, [ 'one_env_file' ])
    expected = {
      'PATH': '/zzzz/bin:$DEFAULT_PATH:/p/bin:$ROOT_DIR/stuff/bin',
      'PYTHONPATH': '/zzzz/lib/python:/p/lib/python:$ROOT_DIR/stuff/lib/python',
      '$LD_LIBRARY_PATH':  '$ROOT_DIR/stuff/lib',
      'PKG_CONFIG_PATH': '$ROOT_DIR/stuff/lib/pkgconfig:$ROOT_DIR/stuff/share/pkgconfig',
    }
    self.assert_dict_as_text_equal( expected, env2 )

  def test_transform_env_unset(self):
    code1 = r'''
      export FOO=foo
      export BAR=bar
      export BAZ=baz
'''
    code2 = r'''
      unset BAR
'''
    pm = self._make_two_env_files_pm(code1, code2)
    env1 = {}
    env2 = self._transform_env(pm, env1, [ 'two_env_files' ])
    expected = {
      '$LD_LIBRARY_PATH': '$ROOT_DIR/stuff/lib',
      'PKG_CONFIG_PATH': '$ROOT_DIR/stuff/lib/pkgconfig:$ROOT_DIR/stuff/share/pkgconfig',
      'PATH': '$DEFAULT_PATH:$ROOT_DIR/stuff/bin',
      'PYTHONPATH': '$ROOT_DIR/stuff/lib/python',
      'FOO': 'foo',
      'BAZ': 'baz',
    }
    self.assert_dict_as_text_equal( expected, env2 )

  def test_installed_files(self):
    recipe = r'''
fake_package files 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  files
    bin/apple.sh
      \#!/bin/bash
      echo apple ; exit 0
    bin/orange.sh
      \#!/bin/bash
      echo orange ; exit 0
  env_files
    foo.sh
      \#@REBUILD_HEAD@
      export FOO=foo
      \#@REBUILD_TAIL@
    bar.sh
      \#@REBUILD_HEAD@
      export BAR=bar
      \#@REBUILD_TAIL@
  '''
    amt = self._make_test_amt(recipe, 'files;1.0.0;0;0;linux;release;x86_64;ubuntu;18;')
    pm = self._make_caca_test_pm(amt.am)
    self._install_package(pm, 'files-1.0.0', 'linux-ubuntu-18/x86_64/release')
    self.assertEqual( [ 'files-1.0.0' ], pm.list_all_names(include_version = True) )
    expected = [
      'db/packages.db',
      'env/bar.sh',
      'env/foo.sh',
      'env/framework/bes_shell.bash',
      'stuff/bin/apple.sh',
      'stuff/bin/orange.sh',
    ]
    self.assertEqual( expected, file_find.find(pm.root_dir, relative = True) )

  def test_installed_files_only_files(self):
    recipe = r'''
fake_package files 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  files
    bin/apple.sh
      \#!/bin/bash
      echo apple ; exit 0
    bin/orange.sh
      \#!/bin/bash
      echo orange ; exit 0
  '''
    amt = self._make_test_amt(recipe, 'files;1.0.0;0;0;linux;release;x86_64;ubuntu;18;')
    pm = self._make_caca_test_pm(amt.am)
    self._install_package(pm, 'files-1.0.0', 'linux-ubuntu-18/x86_64/release')
    self.assertEqual( [ 'files-1.0.0' ], pm.list_all_names(include_version = True) )
    expected = [
      'db/packages.db',
      'env/framework/bes_shell.bash',
      'stuff/bin/apple.sh',
      'stuff/bin/orange.sh',
    ]
    self.assertEqual( expected, file_find.find(pm.root_dir, relative = True) )

  def test_installed_files_only_env_files(self):
    recipe = r'''
fake_package files 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  env_files
    foo.sh
      \#@REBUILD_HEAD@
      export FOO=foo
      \#@REBUILD_TAIL@
    bar.sh
      \#@REBUILD_HEAD@
      export BAR=bar
      \#@REBUILD_TAIL@
  '''
    amt = self._make_test_amt(recipe, 'files;1.0.0;0;0;linux;release;x86_64;ubuntu;18;')
    pm = self._make_caca_test_pm(amt.am)
    self._install_package(pm, 'files-1.0.0', 'linux-ubuntu-18/x86_64/release')
    self.assertEqual( [ 'files-1.0.0' ], pm.list_all_names(include_version = True) )
    expected = [
      'db/packages.db',
      'env/bar.sh',
      'env/foo.sh',
      'env/framework/bes_shell.bash',
    ]
    self.assertEqual( expected, file_find.find(pm.root_dir, relative = True) )
    
  def _make_test_amt(self, recipes, publish):
    amt = AMT(recipes = recipes)
    publish = object_util.listify(publish)
    check.check_string_seq(publish)
    for p in publish:
      amt.publish(p)
    return amt

  def _install_package(self, pm, desc, bt):
    if check.is_string(desc):
      desc = PD.parse(desc)
    check.check_package_descriptor(desc)
    if check.is_string(bt):
      bt = BT.parse_path(bt)
    check.check_build_target(bt)
    pm.install_package(desc, bt, [ 'RUN' ])
    
  ONE_ENV_FILE_RECIPE = r'''
fake_package one_env_file 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  env_files
    file1.sh
      \#@REBUILD_HEAD@
      %s
      \#@REBUILD_TAIL@
  '''

  TWO_ENV_FILES_RECIPE = r'''
fake_package two_env_files 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  files
    bin/cut.sh
      \#!/bin/bash
      echo cabbage ; exit 0
  env_files
    file1.sh
      \#@REBUILD_HEAD@
      %s
      \#@REBUILD_TAIL@
    file2.sh
      \#@REBUILD_HEAD@
      %s
      \#@REBUILD_TAIL@
  '''
  
  VEGGIES = r'''
fake_package cabbage 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  files
    bin/cut.sh
      \#!/bin/bash
      echo cabbage ; exit 0
  env_files
    cabbage_env.sh
      \#@REBUILD_HEAD@
      bes_env_path_append PATH ${REBUILD_STUFF_DIR}/bin
      #bes_env_path_append PYTHONPATH ${REBUILD_STUFF_DIR}/lib/python
      #bes_env_path_append LD_LIBRARY_PATH ${REBUILD_STUFF_DIR}/lib
      \#@REBUILD_TAIL@

fake_package unset 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  files
    bin/unsetcut.sh
      \#!/bin/bash
      echo cabbage ; exit 0
  env_files
    unset1.sh
      \#@REBUILD_HEAD@
      export FOO=foo
      \#@REBUILD_TAIL@
    unset2.sh
      \#@REBUILD_HEAD@
      export BAR=bar
      \#@REBUILD_TAIL@
    unset3.sh
      \#@REBUILD_HEAD@
      unset FOO
      \#@REBUILD_TAIL@
'''

  @classmethod
  def _replace_input_env(clazz, env):
    result = copy.deepcopy(env)
    if '$LD_LIBRARY_PATH' in result:
      result['LD_LIBRARY_PATH'] = result['$LD_LIBRARY_PATH']
      del result['$LD_LIBRARY_PATH']
    replacements = {
      '$DEFAULT_PATH': os_env.DEFAULT_SYSTEM_PATH,
    }
    dict_util.replace_values(result, replacements)
    return result
  
  @classmethod
  def _replace_output_env(clazz, pm, env):
    result = copy.deepcopy(env)
    if os_env.LD_LIBRARY_PATH_VAR_NAME in result:
      result['$LD_LIBRARY_PATH'] = result[os_env.LD_LIBRARY_PATH_VAR_NAME]
      del result[os_env.LD_LIBRARY_PATH_VAR_NAME]
    replacements = {
      '/private': '',
      pm.root_dir: '$ROOT_DIR',
      os_env.DEFAULT_SYSTEM_PATH: '$DEFAULT_PATH',
    }
    dict_util.replace_values(result, replacements)
    return result
  
  @classmethod
  def _transform_env(clazz, pm, env, package_names):
    env = clazz._replace_input_env(env)
    result = pm.transform_env(env, package_names)
    return clazz._replace_output_env(pm, result)

  def test_install_package_same_version_files(self):
    '''
    A test that proves package manager will reinstall a package if the version is the
    same and contents changed and same_version is given
    '''

    recipe1 = r'''
fake_package cabbage 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  files
    bin/cabbage.sh
      \#!/bin/bash
      echo cabbage1 ; exit 0
'''

    recipe2 = r'''
fake_package cabbage 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  files
    bin/cabbage.sh
      \#!/bin/bash
      echo cabbage2 ; exit 0
'''

    cabbage = PD.parse('cabbage-1.0.0')
    bt = BT.parse_path('linux-ubuntu-18/x86_64/release')
    
    t = AMT()
    pm = self._make_caca_test_pm(t.am)
    t.add_recipes(recipe1)
    t.publish('cabbage;1.0.0;0;0;linux;release;x86_64;ubuntu;18;')
    pm.install_package(cabbage, bt, [ 'RUN' ])
    exe = pm.tool_exe('cabbage.sh')
    self.assertEqual( 'cabbage1', execute.execute(exe).stdout.strip() )
    
    t.retire('cabbage;1.0.0;0;0;linux;release;x86_64;ubuntu;18;')
    t.clear_recipes()
    t.add_recipes(recipe2)
    t.publish('cabbage;1.0.0;0;0;linux;release;x86_64;ubuntu;18;')
    pm.install_package(cabbage, bt, [ 'RUN' ], package_install_options(allow_same_version = False))
    self.assertEqual( 'cabbage1', execute.execute(exe).stdout.strip() )
    pm.install_package(cabbage, bt, [ 'RUN' ], package_install_options(allow_same_version = True))
    self.assertEqual( 'cabbage2', execute.execute(exe).stdout.strip() )
  
  def test_install_package_same_version_env_files(self):
    '''
    A test that proves package manager will reinstall a package if the version is the
    same and env_files contents changed and same_version is given
    '''

    recipe1 = r'''
fake_package cabbage 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  files
    bin/unsetcut.sh
      \#!/bin/bash
      echo cabbage ; exit 0
  env_files
    cabbage_env.sh
      \#@REBUILD_HEAD@
      export FOO=cabbage1
      \#@REBUILD_TAIL@
'''

    recipe2 = r'''
fake_package cabbage 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  files
    bin/unsetcut.sh
      \#!/bin/bash
      echo cabbage ; exit 0
  env_files
    cabbage_env.sh
      \#@REBUILD_HEAD@
      export FOO=cabbage2
      \#@REBUILD_TAIL@
'''

    cabbage = PD.parse('cabbage-1.0.0')
    bt = BT.parse_path('linux-ubuntu-18/x86_64/release')
    
    t = AMT()
    pm = self._make_caca_test_pm(t.am)
    t.add_recipes(recipe1)
    t.publish('cabbage;1.0.0;0;0;linux;release;x86_64;ubuntu;18;')
    pm.install_package(cabbage, bt, [ 'RUN' ])
    result = pm.transform_env({}, [ 'cabbage' ])
    self.assertEqual( 'cabbage1', result['FOO'] )

    t.retire('cabbage;1.0.0;0;0;linux;release;x86_64;ubuntu;18;')
    t.clear_recipes()
    t.add_recipes(recipe2)
    t.publish('cabbage;1.0.0;0;0;linux;release;x86_64;ubuntu;18;')
    pm.install_package(cabbage, bt, [ 'RUN' ], package_install_options(allow_same_version = False))
    result = pm.transform_env({}, [ 'cabbage' ])
    self.assertEqual( 'cabbage1', result['FOO'] )
    pm.install_package(cabbage, bt, [ 'RUN' ], package_install_options(allow_same_version = True))
    result = pm.transform_env({}, [ 'cabbage' ])
    self.assertEqual( 'cabbage2', result['FOO'] )
  
  def test_install_package_hardcoded_paths(self):
    '''
    A test that proves package manager will properly install test files that
    have the variables ${REBUILD_PACKAGE_PREFIX} in them.
    '''

    recipe = r'''
fake_package cabbage 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  files
    bin/cabbage.sh
      \#!/bin/bash
      echo prefix=${REBUILD_PACKAGE_PREFIX}
      exit 0
'''
    cabbage = PD.parse('cabbage-1.0.0')
    bt = BT.parse_path('linux-ubuntu-18/x86_64/release')
    t = AMT(recipes = recipe)
    pm = self._make_caca_test_pm(t.am)
    t.publish('cabbage;1.0.0;0;0;linux;release;x86_64;ubuntu;18;')
    pm.install_package(cabbage, bt, [ 'RUN' ])
    exe = pm.tool_exe('cabbage.sh')
    expected='prefix=%s' % (pm.installation_dir)
    self.assertEqual( expected, execute.execute(exe).stdout.strip() )

  def test_install_package_hardcoded_paths_env_files(self):
    '''
    A test that proves package manager will properly install env files that
    have the variables ${REBUILD_PACKAGE_PREFIX} in them (which is bad practice
    for env files since things should generally be relative and not hardcoded
    but it needs to work nontheless)
    '''

    recipe = r'''
fake_package cabbage 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  env_files
    foo.sh
      \#@REBUILD_HEAD@
      export FOO=${REBUILD_PACKAGE_PREFIX}/foo
      \#@REBUILD_TAIL@
    bar.sh
      \#@REBUILD_HEAD@
      export BAR=${REBUILD_PACKAGE_PREFIX}/bar
      \#@REBUILD_TAIL@
'''
    cabbage = PD.parse('cabbage-1.0.0')
    bt = BT.parse_path('linux-ubuntu-18/x86_64/release')
    t = AMT(recipes = recipe)
    pm = self._make_caca_test_pm(t.am)
    t.publish('cabbage;1.0.0;0;0;linux;release;x86_64;ubuntu;18;')
    pm.install_package(cabbage, bt, [ 'RUN' ])
    env1 = {}
    env2 = self._transform_env(pm, env1, [ 'cabbage' ])
    self.assertEqual( '$ROOT_DIR/stuff/foo', env2['FOO'] )
    self.assertEqual( '$ROOT_DIR/stuff/bar', env2['BAR'] )
    
  def test_install_tarball_no_distro(self):
    recipes = r'''
fake_package foo 1.0.0 0 0 linux release x86_64 any any none

fake_package bar 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  requirements
    foo >= 1.0.0

fake_package baz 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  requirements
    bar >= 1.0.0
'''

    t = AMT(recipes = recipes)
    t.publish([
      'foo;1.0.0;0;0;linux;release;x86_64;any;any;',
      'bar;1.0.0;0;0;linux;release;x86_64;ubuntu;18;',
      'baz;1.0.0;0;0;linux;release;x86_64;ubuntu;18;',
    ])
    linux_bt = BT.parse_path('linux-ubuntu-18/x86_64/release')
    
    p = t.am.list_all_by_descriptor(linux_bt)
    pm = self._make_caca_test_pm(t.am)
    pm.install_packages(PDL([
      PD.parse('foo-1.0.0'),
      PD.parse('bar-1.0.0'),
      PD.parse('baz-1.0.0'),
    ]), linux_bt, ['BUILD', 'RUN'])
    self.assertEqual( [ 'bar-1.0.0', 'baz-1.0.0', 'foo-1.0.0' ], pm.list_all_names(include_version = True) )
    
if __name__ == '__main__':
  unit_test.main()
