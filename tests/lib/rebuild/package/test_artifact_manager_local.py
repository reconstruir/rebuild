#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.file_find import file_find
from bes.fs.temp_file import temp_file
from rebuild.base.artifact_descriptor import artifact_descriptor as AD
from rebuild.base.artifact_descriptor_list import artifact_descriptor_list as ADL
from rebuild.base.build_target import build_target as BT
from rebuild.base.package_descriptor import package_descriptor as PD
from rebuild.base.requirement_list import requirement_list as RL
from rebuild.package.db_error import *
from _rebuild_testing.fake_package_unit_test import fake_package_unit_test as FPUT
from _rebuild_testing.fake_package_recipes import fake_package_recipes as RECIPES
from _rebuild_testing.artifact_manager_tester import artifact_manager_tester as AMT

class test_artifact_manager_local(unit_test):

  DEBUG = unit_test.DEBUG
  #DEBUG = True

  LINUX_BT = BT('linux', 'ubuntu', '18', '', 'x86_64', 'release')
  MACOS_BT = BT('macos', '', '10', '14', 'x86_64', 'release')

  def __init__(self, *args, **kargs):
    super(test_artifact_manager_local, self).__init__(*args, **kargs)
    self.maxDiff = None
  
  def test_publish(self):
    t = AMT(recipes = RECIPES.APPLE)
    adesc = 'apple;1.2.3;1;0;linux;release;x86_64;ubuntu;18;'
    tmp_tarball = t.create_package(adesc)
    filename = t.am.publish(tmp_tarball.filename, False, tmp_tarball.metadata)
    self.assertTrue( path.exists(filename) )
    expected = [
      AD.parse('apple;1.2.3;1;0;linux;release;x86_64;ubuntu;18;'),
    ]
    self.assertEqual( expected, t.am.list_all_by_descriptor(None) )

  def test_publish_new_version(self):
    t = AMT(recipes = RECIPES.TWO_APPLES)
    tmp_tarball1 = t.create_package('apple;1.2.3;1;0;linux;release;x86_64;ubuntu;18;')
    t.am.publish(tmp_tarball1.filename, False, tmp_tarball1.metadata)
    self.assertEqual( [
      AD.parse('apple;1.2.3;1;0;linux;release;x86_64;ubuntu;18;'),
    ], t.am.list_all_by_descriptor(None) )

    tmp_tarball2 = t.create_package('apple;1.2.4;1;0;linux;release;x86_64;ubuntu;18;')
    t.am.publish(tmp_tarball2.filename, False, tmp_tarball2.metadata)
    self.assertEqual( [
      AD.parse('apple;1.2.3;1;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('apple;1.2.4;1;0;linux;release;x86_64;ubuntu;18;'),
    ], t.am.list_all_by_descriptor(None) )
    
  def test_artifact_path(self):
    t = AMT(recipes = RECIPES.APPLE)
    self.assertEqual( [], t.am.list_all_by_descriptor(None) )
    t.publish('apple;1.2.3;1;0;linux;release;x86_64;ubuntu;18;')
    self.assertEqual( 'linux-ubuntu-18/x86_64/release/apple-1.2.3-1.tar.gz',
                      t.am.artifact_path(PD('apple', '1.2.3-1'), self.LINUX_BT, True) )
    
  def test_publish_again_with_replace(self):
    am = FPUT.make_artifact_manager(debug = self.DEBUG)
    tmp_tarball = FPUT.create_one_package(RECIPES.APPLE)
    filename = am.publish(tmp_tarball.filename, False, tmp_tarball.metadata)
    self.assertTrue( path.exists(filename) )
    expected = [
      AD.parse('apple;1.2.3;1;0;linux;release;x86_64;ubuntu;18;'),
    ]
    self.assertEqual( expected, am.list_all_by_descriptor(None) )
    filename = am.publish(tmp_tarball.filename, True, tmp_tarball.metadata)
    self.assertEqual( expected, am.list_all_by_descriptor(None) )

  def test_publish_again_without_replace(self):
    am = FPUT.make_artifact_manager(debug = self.DEBUG)
    tmp_tarball = FPUT.create_one_package(RECIPES.APPLE)
    filename = am.publish(tmp_tarball.filename, False, tmp_tarball.metadata)
    self.assertTrue( path.exists(filename) )
    expected = [
      AD.parse('apple;1.2.3;1;0;linux;release;x86_64;ubuntu;18;'),
    ]
    self.assertEqual( expected, am.list_all_by_descriptor(None) )
    with self.assertRaises(AlreadyInstalledError) as context:
      am.publish(tmp_tarball.filename, False, tmp_tarball.metadata)
    
  def test_find_by_package_descriptor_linux(self):
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version_major': '18' }
    am = FPUT.make_artifact_manager(self.DEBUG, RECIPES.FOODS, mutations)
    self.assertEqual( 'water-1.0.0', am.find_by_package_descriptor(PD('water', '1.0.0'), self.LINUX_BT, False).package_descriptor.full_name )
    self.assertEqual( 'water-1.0.0-1', am.find_by_package_descriptor(PD('water', '1.0.0-1'), self.LINUX_BT, False).package_descriptor.full_name )
    self.assertEqual( 'water-1.0.0-2', am.find_by_package_descriptor(PD('water', '1.0.0-2'), self.LINUX_BT, False).package_descriptor.full_name )
    self.assertEqual( 'fructose-3.4.5-6', am.find_by_package_descriptor(PD('fructose', '3.4.5-6'), self.LINUX_BT, False).package_descriptor.full_name )
    self.assertEqual( 'apple-1.2.3-1', am.find_by_package_descriptor(PD('apple', '1.2.3-1'), self.LINUX_BT, False).package_descriptor.full_name )
    self.assertEqual( 'orange-6.5.4-3', am.find_by_package_descriptor(PD('orange', '6.5.4-3'), self.LINUX_BT, False).package_descriptor.full_name )
    self.assertEqual( 'orange_juice-1.4.5', am.find_by_package_descriptor(PD('orange_juice', '1.4.5'), self.LINUX_BT, False).package_descriptor.full_name )
    self.assertEqual( 'pear_juice-6.6.6', am.find_by_package_descriptor(PD('pear_juice', '6.6.6'), self.LINUX_BT, False).package_descriptor.full_name )

  def test_find_by_package_descriptor_macos(self):
    mutations = { 'system': 'macos', 'distro': '', 'distro_version_major': '10', 'distro_version_minor': '14' }
    am = FPUT.make_artifact_manager(self.DEBUG, RECIPES.FOODS, mutations)
    self.assertEqual( 'water-1.0.0', am.find_by_package_descriptor(PD('water', '1.0.0'), self.MACOS_BT, False).package_descriptor.full_name )
    self.assertEqual( 'water-1.0.0-1', am.find_by_package_descriptor(PD('water', '1.0.0-1'), self.MACOS_BT, False).package_descriptor.full_name )
    self.assertEqual( 'water-1.0.0-2', am.find_by_package_descriptor(PD('water', '1.0.0-2'), self.MACOS_BT, False).package_descriptor.full_name )
    self.assertEqual( 'fructose-3.4.5-6', am.find_by_package_descriptor(PD('fructose', '3.4.5-6'), self.MACOS_BT, False).package_descriptor.full_name )
    self.assertEqual( 'apple-1.2.3-1', am.find_by_package_descriptor(PD('apple', '1.2.3-1'), self.MACOS_BT, False).package_descriptor.full_name )
    self.assertEqual( 'orange-6.5.4-3', am.find_by_package_descriptor(PD('orange', '6.5.4-3'), self.MACOS_BT, False).package_descriptor.full_name )
    self.assertEqual( 'orange_juice-1.4.5', am.find_by_package_descriptor(PD('orange_juice', '1.4.5'), self.MACOS_BT, False).package_descriptor.full_name )
    self.assertEqual( 'pear_juice-6.6.6', am.find_by_package_descriptor(PD('pear_juice', '6.6.6'), self.MACOS_BT, False).package_descriptor.full_name )

  def test_list_latest_versions_linux(self):
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version_major': '18' }
    am = FPUT.make_artifact_manager(self.DEBUG, RECIPES.FOODS, mutations)
    expected = [
      AD.parse('apple;1.2.3;1;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('arsenic;1.2.10;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('citrus;1.0.0;2;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('fiber;1.0.0;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('fructose;3.4.5;6;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('fruit;1.0.0;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('knife;1.0.0;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('mercury;1.2.9;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('orange;6.5.4;3;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('orange_juice;1.4.5;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('pear;1.2.3;1;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('pear_juice;6.6.6;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('smoothie;1.0.0;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('water;1.0.0;2;0;linux;release;x86_64;ubuntu;18;'),
    ]
    self.assertEqual( expected, am.list_latest_versions(self.LINUX_BT) )

  def test_list_latest_versions_macos(self):
    mutations = { 'system': 'macos', 'distro': '', 'distro_version_major': '10', 'distro_version_minor': '14' }
    am = FPUT.make_artifact_manager(self.DEBUG, RECIPES.FOODS, mutations)
    expected = [
      AD.parse('apple;1.2.3;1;0;macos;release;x86_64;;10;14'),
      AD.parse('arsenic;1.2.10;0;0;macos;release;x86_64;;10;14'),
      AD.parse('citrus;1.0.0;2;0;macos;release;x86_64;;10;14'),
      AD.parse('fiber;1.0.0;0;0;macos;release;x86_64;;10;14'),
      AD.parse('fructose;3.4.5;6;0;macos;release;x86_64;;10;14'),
      AD.parse('fruit;1.0.0;0;0;macos;release;x86_64;;10;14'),
      AD.parse('knife;1.0.0;0;0;macos;release;x86_64;;10;14'),
      AD.parse('mercury;1.2.9;0;0;macos;release;x86_64;;10;14'),
      AD.parse('orange;6.5.4;3;0;macos;release;x86_64;;10;14'),
      AD.parse('orange_juice;1.4.5;0;0;macos;release;x86_64;;10;14'),
      AD.parse('pear;1.2.3;1;0;macos;release;x86_64;;10;14'),
      AD.parse('pear_juice;6.6.6;0;0;macos;release;x86_64;;10;14'),
      AD.parse('smoothie;1.0.0;0;0;macos;release;x86_64;;10;14'),
      AD.parse('water;1.0.0;2;0;macos;release;x86_64;;10;14'),
    ]
    self.assertEqual( expected, am.list_latest_versions(self.MACOS_BT) )

  def test_remove_artifact(self):
    mutations = { 'system': 'macos', 'distro': '', 'distro_version_major': '10', 'distro_version_minor': '14' }
    am = FPUT.make_artifact_manager(self.DEBUG, RECIPES.FOODS, mutations)
    expected = ADL([
      AD.parse('apple;1.2.3;1;0;macos;release;x86_64;;10;14'),
      AD.parse('arsenic;1.2.10;0;0;macos;release;x86_64;;10;14'),
      AD.parse('citrus;1.0.0;2;0;macos;release;x86_64;;10;14'),
      AD.parse('fiber;1.0.0;0;0;macos;release;x86_64;;10;14'),
      AD.parse('fructose;3.4.5;6;0;macos;release;x86_64;;10;14'),
      AD.parse('fruit;1.0.0;0;0;macos;release;x86_64;;10;14'),
      AD.parse('knife;1.0.0;0;0;macos;release;x86_64;;10;14'),
      AD.parse('mercury;1.2.9;0;0;macos;release;x86_64;;10;14'),
      AD.parse('orange;6.5.4;3;0;macos;release;x86_64;;10;14'),
      AD.parse('orange_juice;1.4.5;0;0;macos;release;x86_64;;10;14'),
      AD.parse('pear;1.2.3;1;0;macos;release;x86_64;;10;14'),
      AD.parse('pear_juice;6.6.6;0;0;macos;release;x86_64;;10;14'),
      AD.parse('smoothie;1.0.0;0;0;macos;release;x86_64;;10;14'),
      AD.parse('water;1.0.0;2;0;macos;release;x86_64;;10;14'),
    ])
    actual = am.list_latest_versions(self.MACOS_BT)
    self.assertMultiLineEqual( expected.to_string(), actual.to_string() )
    return
    self.assertEqual( [
      'artifacts.db',
      'macos-10.14/x86_64/release/apple-1.2.3-1.tar.gz',
      'macos-10.14/x86_64/release/arsenic-1.2.10.tar.gz',
      'macos-10.14/x86_64/release/arsenic-1.2.9-1.tar.gz',
      'macos-10.14/x86_64/release/arsenic-1.2.9.tar.gz',
      'macos-10.14/x86_64/release/citrus-1.0.0-2.tar.gz',
      'macos-10.14/x86_64/release/fiber-1.0.0.tar.gz',
      'macos-10.14/x86_64/release/fructose-3.4.5-6.tar.gz',
      'macos-10.14/x86_64/release/fruit-1.0.0.tar.gz',
      'macos-10.14/x86_64/release/knife-1.0.0.tar.gz',
      'macos-10.14/x86_64/release/mercury-1.2.8-1.tar.gz',
      'macos-10.14/x86_64/release/mercury-1.2.8.tar.gz',
      'macos-10.14/x86_64/release/mercury-1.2.9.tar.gz',
      'macos-10.14/x86_64/release/orange-6.5.4-3.tar.gz',
      'macos-10.14/x86_64/release/orange_juice-1.4.5.tar.gz',
      'macos-10.14/x86_64/release/pear-1.2.3-1.tar.gz',
      'macos-10.14/x86_64/release/pear_juice-6.6.6.tar.gz',
      'macos-10.14/x86_64/release/smoothie-1.0.0.tar.gz',
      'macos-10.14/x86_64/release/water-1.0.0-1.tar.gz',
      'macos-10.14/x86_64/release/water-1.0.0-2.tar.gz',
      'macos-10.14/x86_64/release/water-1.0.0.tar.gz',
      ], file_find.find(am.root_dir) )
    am.remove_artifact(AD.parse('apple;1.2.3;1;0;macos;release;x86_64;;10;14'))
    am.remove_artifact(AD.parse('smoothie;1.0.0;0;0;macos;release;x86_64;;10;14'))
    expected = [
      AD.parse('arsenic;1.2.10;0;0;macos;release;x86_64;;10;14'),
      AD.parse('citrus;1.0.0;2;0;macos;release;x86_64;;10;14'),
      AD.parse('fiber;1.0.0;0;0;macos;release;x86_64;;10;14'),
      AD.parse('fructose;3.4.5;6;0;macos;release;x86_64;;10;14'),
      AD.parse('fruit;1.0.0;0;0;macos;release;x86_64;;10;14'),
      AD.parse('knife;1.0.0;0;0;macos;release;x86_64;;10;14'),
      AD.parse('mercury;1.2.9;0;0;macos;release;x86_64;;10;14'),
      AD.parse('orange;6.5.4;3;0;macos;release;x86_64;;10;14'),
      AD.parse('orange_juice;1.4.5;0;0;macos;release;x86_64;;10;14'),
      AD.parse('pear;1.2.3;1;0;macos;release;x86_64;;10;14'),
      AD.parse('pear_juice;6.6.6;0;0;macos;release;x86_64;;10;14'),
      AD.parse('water;1.0.0;2;0;macos;release;x86_64;;10;14'),
    ]
    self.assertEqual( expected, am.list_latest_versions(self.MACOS_BT) )
    self.assertEqual( [
      'artifacts.db',
      'macos-10.14/x86_64/release/arsenic-1.2.10.tar.gz',
      'macos-10.14/x86_64/release/arsenic-1.2.9-1.tar.gz',
      'macos-10.14/x86_64/release/arsenic-1.2.9.tar.gz',
      'macos-10.14/x86_64/release/citrus-1.0.0-2.tar.gz',
      'macos-10.14/x86_64/release/fiber-1.0.0.tar.gz',
      'macos-10.14/x86_64/release/fructose-3.4.5-6.tar.gz',
      'macos-10.14/x86_64/release/fruit-1.0.0.tar.gz',
      'macos-10.14/x86_64/release/knife-1.0.0.tar.gz',
      'macos-10.14/x86_64/release/mercury-1.2.8-1.tar.gz',
      'macos-10.14/x86_64/release/mercury-1.2.8.tar.gz',
      'macos-10.14/x86_64/release/mercury-1.2.9.tar.gz',
      'macos-10.14/x86_64/release/orange-6.5.4-3.tar.gz',
      'macos-10.14/x86_64/release/orange_juice-1.4.5.tar.gz',
      'macos-10.14/x86_64/release/pear-1.2.3-1.tar.gz',
      'macos-10.14/x86_64/release/pear_juice-6.6.6.tar.gz',
      'macos-10.14/x86_64/release/water-1.0.0-1.tar.gz',
      'macos-10.14/x86_64/release/water-1.0.0-2.tar.gz',
      'macos-10.14/x86_64/release/water-1.0.0.tar.gz',
      ], file_find.find(am.root_dir) )

  def test_list_all_by_descriptor_many_versions(self):
    recipes = '''
fake_package water 1.0.0 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.1 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.2 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.3 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.8 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.9 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.10 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.11 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.13 0 0 linux release x86_64 ubuntu 18 none
'''
    t = AMT(recipes = recipes)
    t.publish('water;1.0.0;0;0;linux;release;x86_64;ubuntu;18;')
    t.publish('water;1.0.1;0;0;linux;release;x86_64;ubuntu;18;')
    t.publish('water;1.0.2;0;0;linux;release;x86_64;ubuntu;18;')
    t.publish('water;1.0.3;0;0;linux;release;x86_64;ubuntu;18;')
    t.publish('water;1.0.10;0;0;linux;release;x86_64;ubuntu;18;')
    t.publish('water;1.0.8;0;0;linux;release;x86_64;ubuntu;18;')
    t.publish('water;1.0.9;0;0;linux;release;x86_64;ubuntu;18;')
    t.publish('water;1.0.11;0;0;linux;release;x86_64;ubuntu;18;')
    t.publish('water;1.0.13;0;0;linux;release;x86_64;ubuntu;18;')
    expected = [
      AD.parse('water;1.0.0;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('water;1.0.1;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('water;1.0.2;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('water;1.0.3;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('water;1.0.8;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('water;1.0.9;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('water;1.0.10;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('water;1.0.11;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('water;1.0.13;0;0;linux;release;x86_64;ubuntu;18;'),
    ]
    self.assertEqual( expected, t.am.list_all_by_descriptor(None) )

  def test_packages_dict(self):
    water_recipes = '''
fake_package water 1.0.0 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.1 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.10 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.13 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.0 0 0 linux release x86_64 centos 7 none
fake_package water 1.0.1 0 0 linux release x86_64 centos 7 none
fake_package water 1.0.9 0 0 linux release x86_64 centos 7 none
fake_package water 1.0.11 0 0 linux release x86_64 centos 7 none
'''

    milk_recipes = '''
fake_package milk 1.0.0 0 0 linux release x86_64 ubuntu 18 none
fake_package milk 1.0.1 0 0 linux release x86_64 ubuntu 18 none
fake_package milk 1.0.10 0 0 linux release x86_64 ubuntu 18 none
fake_package milk 1.0.13 0 0 linux release x86_64 ubuntu 18 none
fake_package milk 1.0.0 0 0 linux release x86_64 centos 7 none
fake_package milk 1.0.1 0 0 linux release x86_64 centos 7 none
fake_package milk 1.0.9 0 0 linux release x86_64 centos 7 none
fake_package milk 1.0.11 0 0 linux release x86_64 centos 7 none
'''
    t = AMT()
    t.add_recipes(water_recipes)
    t.add_recipes(milk_recipes)
    
    t.publish(water_recipes)
    t.publish(milk_recipes)

    bt = BT.parse_path('linux-ubuntu-18/x86_64/release')

    actual = t.am.packages_dict(bt)
    self.assertEqual( [
      'water-1.0.0',
      'water-1.0.1',
      'water-1.0.10',
      'water-1.0.13'
    ], actual['water'].names(True) )
    self.assertEqual( [
      'milk-1.0.0',
      'milk-1.0.1',
      'milk-1.0.10',
      'milk-1.0.13'
    ], actual['milk'].names(True) )

  def test_list_all_filter_with_requirements(self):
    water_recipes = '''
fake_package water 1.0.0 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.1 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.10 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.13 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.0 0 0 linux release x86_64 centos 7 none
fake_package water 1.0.1 0 0 linux release x86_64 centos 7 none
fake_package water 1.0.9 0 0 linux release x86_64 centos 7 none
fake_package water 1.0.11 0 0 linux release x86_64 centos 7 none
'''

    milk_recipes = '''
fake_package milk 1.0.0 0 0 linux release x86_64 ubuntu 18 none
fake_package milk 1.0.1 0 0 linux release x86_64 ubuntu 18 none
fake_package milk 1.0.1 1 0 linux release x86_64 ubuntu 18 none
fake_package milk 1.0.10 0 0 linux release x86_64 ubuntu 18 none
fake_package milk 1.0.13 0 0 linux release x86_64 ubuntu 18 none
fake_package milk 1.0.0 0 0 linux release x86_64 centos 7 none
fake_package milk 1.0.1 0 0 linux release x86_64 centos 7 none
fake_package milk 1.0.9 0 0 linux release x86_64 centos 7 none
fake_package milk 1.0.11 0 0 linux release x86_64 centos 7 none
'''
    t = AMT()
    t.add_recipes(water_recipes)
    t.add_recipes(milk_recipes)
    
    t.publish(water_recipes)
    t.publish(milk_recipes)

    self.assertEqual( [
      PD.parse('milk-1.0.0'),
      PD.parse('milk-1.0.1'),
      PD.parse('milk-1.0.1-1'),
      PD.parse('water-1.0.10'),
      PD.parse('water-1.0.13'),
    ], t.am.list_all_filter_with_requirements(BT.parse_path('linux-ubuntu-18/x86_64/release'),
                                              RL.parse('water >= 1.0.9 milk < 1.0.10')) )

    self.assertEqual( [
      PD.parse('milk-1.0.0'),
      PD.parse('milk-1.0.1'),
      PD.parse('milk-1.0.9'),
      PD.parse('water-1.0.9'),
      PD.parse('water-1.0.11'),
    ], t.am.list_all_filter_with_requirements(BT.parse_path('linux-centos-7/x86_64/release'),
                                              RL.parse('water >= 1.0.9 milk < 1.0.10')) )

  def xtest_none_distro(self):
    recipe = '''
fake_package kiwi 1.2.3 0 0 linux release x86_64 none none none
  files
    bin/kiwi_script.sh
      #!/bin/bash
      echo kiwi
'''
    t = AMT()
    t.add_recipes(recipe)
    t.publish(recipe)
    self.assertEqual( [
      AD.parse('kiwi;1.2.3;0;0;linux;release;x86_64;;;'),
    ], t.am.list_all_by_descriptor(BT.parse_path('linux/x86_64/release')) )
    self.assertEqual( [
      AD.parse('kiwi;1.2.3;0;0;linux;release;x86_64;;;'),
    ], t.am.list_all_by_descriptor(BT.parse_path('linux-alpine-3/x86_64/release')) )
    
if __name__ == '__main__':
  unit_test.main()
