#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_find, file_util, temp_file
from bes.system import os_env
from bes.common import check, dict_util, object_util
from rebuild.base import build_target as BT, package_descriptor as PD
from rebuild.pkg_config import pkg_config
from rebuild.package import artifact_manager_local, package, package_manager
from rebuild.package import PackageFilesConflictError, PackageMissingRequirementsError
from rebuild.package.db_error import *
from bes.archive import archiver, temp_archive
from _rebuild_testing.fake_package_unit_test import fake_package_unit_test as FPUT
from _rebuild_testing.fake_package_recipes import fake_package_recipes as RECIPES
from _rebuild_testing.artifact_manager_tester import artifact_manager_tester as AMT

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
    am = artifact_manager_local(am_dir)
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
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    water_tarball = FPUT.create_one_package(RECIPES.WATER, mutations)
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
    tarball = FPUT.create_one_package(RECIPES.WATER, mutations)
    pm.install_tarball(tarball, ['BUILD', 'RUN'])
    with self.assertRaises(AlreadyInstalledError) as context:
      pm.install_tarball(tarball, ['BUILD', 'RUN'])
    self.assertEqual( 'package water already installed', context.exception.message )

  def test_install_tarball_missing_requirements(self):
    pm = self._make_test_pm_with_am()
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    apple_tarball = FPUT.create_one_package(RECIPES.APPLE, mutations)
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

    pm._artifact_manager.publish(foo_tarball, bt, False, None)
    pm._artifact_manager.publish(bar_tarball, bt, False, None)
    pm._artifact_manager.publish(baz_tarball, bt, False, None)
    
    pm.install_tarball(foo_tarball, ['BUILD', 'RUN'])
    pm.install_tarball(bar_tarball, ['BUILD', 'RUN'])
    pm.install_tarball(baz_tarball, ['BUILD', 'RUN'])

  def test_uninstall(self):
    pm = self._make_test_pm_with_am()
    pi = PD('water', '1.0.0')
    install_rv = pm.install_package(pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all(include_version = True) )
    pm.uninstall_package('water')
    self.assertEqual( [], pm.list_all(include_version = True) )
    
  def test_is_installed(self):
    pm = self._make_empty_pm()
    self.assertFalse( pm.is_installed('water') )
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    tarball = FPUT.create_one_package(RECIPES.WATER, mutations)
    pm.install_tarball(tarball, ['BUILD', 'RUN'])
    self.assertTrue( pm.is_installed('water') )
    self.assertFalse( pm.is_installed('notthere') )

  @classmethod
  def _make_test_artifact_manager(clazz):
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    return FPUT.make_artifact_manager(debug = clazz.DEBUG,
                                      recipes = RECIPES.FOODS,
                                      build_target = clazz.TEST_BUILD_TARGET,
                                      mutations = mutations)

  def test_install_package(self):
    pm = self._make_test_pm_with_am()
    pi = PD('water', '1.0.0')
    install_rv = pm.install_package(pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all(include_version = True) )

  def test_install_package_upgrade(self):
    pm = self._make_test_pm_with_am()

    old_pi = PD('water', '1.0.0')
    install_rv = pm.install_package(old_pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all(include_version = True) )

    new_pi = PD('water', '1.0.0-1')
    install_rv = pm.install_package(new_pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0-1' ], pm.list_all(include_version = True) )

  def test_install_package_same_version(self):
    pm = self._make_test_pm_with_am()

    old_pi = PD('water', '1.0.0')
    install_rv = pm.install_package(old_pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all(include_version = True) )

    new_pi = PD('water', '1.0.0')
    install_rv = pm.install_package(new_pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])
    self.assertFalse( install_rv )
    self.assertEqual( [ 'water-1.0.0' ], pm.list_all(include_version = True) )

  def test_install_package_unknown(self):
    pm = self._make_test_pm_with_am()
    pi = PD('notthere', '6.6.6-1')
    with self.assertRaises(NotInstalledError) as context:
      pm.install_package(pi, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])

  def test_install_packages(self):
    pm = self._make_test_pm_with_am()

    packages = [
      PD.parse('water-1.0.0'),
      PD.parse('mercury-1.2.8'),
      PD.parse('arsenic-1.2.9'),
    ]

    pm.install_packages(packages, self.TEST_BUILD_TARGET, ['BUILD', 'RUN'])

    self.assertEqual( [ 'arsenic-1.2.9', 'mercury-1.2.8', 'water-1.0.0' ], pm.list_all(include_version = True) )

  def test_dep_map(self):
    pm = self._make_test_pm_with_am()
    packages = [
      PD.parse('water-1.0.0'),
      PD.parse('fiber-1.0.0'),
      PD.parse('fructose-3.4.5-6'),
      PD.parse('fruit-1.0.0'),
      PD.parse('apple-1.2.3-1'),
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

  def _make_cabbage_pm(self):
    t = AMT(recipes = self.VEGGIES)
    t.publish('cabbage;1.0.0;0;0;linux;release;x86_64;ubuntu;18')
    t.publish('unset;1.0.0;0;0;linux;release;x86_64;ubuntu;18')
    pm = self._make_caca_test_pm(t.am)
    cabbage = PD.parse('cabbage-1.0.0')
    bt = BT.parse_path('linux-ubuntu-18/x86_64/release')
    pm.install_package(cabbage, bt, [ 'RUN' ])
    pm.install_package(PD.parse('unset-1.0.0'), bt, [ 'RUN' ])
    return pm, cabbage

  def _make_one_env_file_pm(self, code):
    recipe = self.ONE_ENV_FILE_RECIPE % (code)
    t = AMT(recipes = recipe)
    t.publish('one_env_file;1.0.0;0;0;linux;release;x86_64;ubuntu;18')
    pm = self._make_caca_test_pm(t.am)
    pdesc = PD.parse('one_env_file-1.0.0')
    bt = BT.parse_path('linux-ubuntu-18/x86_64/release')
    pm.install_package(pdesc, bt, [ 'RUN' ])
    return pm

  def _make_two_env_files_pm(self, code1, code2):
    recipe = self.TWO_ENV_FILES_RECIPE % (code1, code2)
    t = AMT(recipes = recipe)
    t.publish('two_env_files;1.0.0;0;0;linux;release;x86_64;ubuntu;18')
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
    code = '''
      rebuild_env_path_append PATH /zzzz/bin
      rebuild_env_path_append PYTHONPATH /zzzz/lib/python
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
    code = '''
      rebuild_env_path_prepend PATH /zzzz/bin
      rebuild_env_path_prepend PYTHONPATH /zzzz/lib/python
#      rebuild_LD_LIBRARY_PATH_prepend /zzzz/lib
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
    code1 = '''
      export FOO=foo
      export BAR=bar
      export BAZ=baz
'''
    code2 = '''
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
    recipe = '''
fake_package files 1.0.0 0 0 linux release x86_64 ubuntu 18
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
    amt = self._make_test_amt(recipe, 'files;1.0.0;0;0;linux;release;x86_64;ubuntu;18')
    pm = self._make_caca_test_pm(amt.am)
    self._install_package(pm, 'files-1.0.0', 'linux-ubuntu-18/x86_64/release')
    self.assertEqual( [ 'files-1.0.0' ], pm.list_all(include_version = True) )
    expected = [
      'db/packages.db',
      'env/bar.sh',
      'env/foo.sh',
      'env/framework/rebuild_framework.sh',
      'stuff/bin/apple.sh',
      'stuff/bin/orange.sh',
    ]
    self.assertEqual( expected, file_find.find(pm.root_dir, relative = True) )

  def test_installed_files_only_files(self):
    recipe = '''
fake_package files 1.0.0 0 0 linux release x86_64 ubuntu 18
  files
    bin/apple.sh
      \#!/bin/bash
      echo apple ; exit 0
    bin/orange.sh
      \#!/bin/bash
      echo orange ; exit 0
  '''
    amt = self._make_test_amt(recipe, 'files;1.0.0;0;0;linux;release;x86_64;ubuntu;18')
    pm = self._make_caca_test_pm(amt.am)
    self._install_package(pm, 'files-1.0.0', 'linux-ubuntu-18/x86_64/release')
    self.assertEqual( [ 'files-1.0.0' ], pm.list_all(include_version = True) )
    expected = [
      'db/packages.db',
      'env/framework/rebuild_framework.sh',
      'stuff/bin/apple.sh',
      'stuff/bin/orange.sh',
    ]
    self.assertEqual( expected, file_find.find(pm.root_dir, relative = True) )

  def test_installed_files_only_env_files(self):
    recipe = '''
fake_package files 1.0.0 0 0 linux release x86_64 ubuntu 18
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
    amt = self._make_test_amt(recipe, 'files;1.0.0;0;0;linux;release;x86_64;ubuntu;18')
    pm = self._make_caca_test_pm(amt.am)
    self._install_package(pm, 'files-1.0.0', 'linux-ubuntu-18/x86_64/release')
    self.assertEqual( [ 'files-1.0.0' ], pm.list_all(include_version = True) )
    expected = [
      'db/packages.db',
      'env/bar.sh',
      'env/foo.sh',
      'env/framework/rebuild_framework.sh',
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
    
  ONE_ENV_FILE_RECIPE = '''
fake_package one_env_file 1.0.0 0 0 linux release x86_64 ubuntu 18
  env_files
    file1.sh
      \#@REBUILD_HEAD@
      %s
      \#@REBUILD_TAIL@
  '''

  TWO_ENV_FILES_RECIPE = '''
fake_package two_env_files 1.0.0 0 0 linux release x86_64 ubuntu 18
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
  
  VEGGIES = '''fake_package cabbage 1.0.0 0 0 linux release x86_64 ubuntu 18
  files
    bin/cut.sh
      \#!/bin/bash
      echo cabbage ; exit 0
  env_files
    cabbage_env.sh
      \#@REBUILD_HEAD@
      rebuild_env_path_append PATH ${REBUILD_STUFF_DIR}/bin
      #rebuild_env_path_append PYTHONPATH ${REBUILD_STUFF_DIR}/lib/python
      #rebuild_LD_LIBRARY_PATH_append ${REBUILD_STUFF_DIR}/lib
      \#@REBUILD_TAIL@

fake_package unset 1.0.0 0 0 linux release x86_64 ubuntu 18
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
  
if __name__ == '__main__':
  unit_test.main()
