#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.base.artifact_descriptor import artifact_descriptor as AD
from rebuild.base.build_target import build_target as BT
from rebuild.base.package_descriptor import package_descriptor as PD
from rebuild.base.requirement_list import requirement_list as RL
from _rebuild_testing.fake_package_recipes import fake_package_recipes as RECIPES
from _rebuild_testing.artifact_manager_tester import artifact_manager_tester as AMT

class test_artifact_manager_tester(unit_test):

  #DEBUG = True

  def test_publish_new_version_manual(self):
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

  def test_publish_new_version_easier(self):
    recipes1 = '''
fake_package aflatoxin 1.0.9 0 0 linux release x86_64 ubuntu 18 none
'''
    recipes2 = '''
fake_package aflatoxin 1.0.10 0 0 linux release x86_64 ubuntu 18 none
'''

    t = AMT()
    x = t.add_recipes(recipes1)
    self.assertEqual( [
    ], t.am.list_all_by_descriptor(None) )
    
    x = t.publish(recipes1)
    self.assertEqual( [
      AD.parse('aflatoxin;1.0.9;0;0;linux;release;x86_64;ubuntu;18;'),
    ], t.am.list_all_by_descriptor(None) )

    t.add_recipes(recipes2)
    self.assertEqual( [
      AD.parse('aflatoxin;1.0.9;0;0;linux;release;x86_64;ubuntu;18;'),
    ], t.am.list_all_by_descriptor(None) )

    t.publish(recipes2)
    self.assertEqual( [
      AD.parse('aflatoxin;1.0.9;0;0;linux;release;x86_64;ubuntu;18;'),
      AD.parse('aflatoxin;1.0.10;0;0;linux;release;x86_64;ubuntu;18;'),
    ], t.am.list_all_by_descriptor(None) )

if __name__ == '__main__':
  unit_test.main()
