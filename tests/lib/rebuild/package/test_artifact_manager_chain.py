#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_find, temp_file
from rebuild.base import artifact_descriptor as AD, build_target, package_descriptor as PD
from rebuild.package import artifact_manager_chain as AMC
from rebuild.package.db_error import *
from _rebuild_testing.fake_package_unit_test import fake_package_unit_test as FPUT
from _rebuild_testing.fake_package_recipes import fake_package_recipes as RECIPES
from _rebuild_testing.artifact_manager_tester import artifact_manager_tester as AMT

class test_artifact_manager_chain(unit_test):

  DEBUG = unit_test.DEBUG
  #DEBUG = True

  LINUX_BT = build_target('linux', 'ubuntu', '18', 'x86_64', 'release')
  MACOS_BT = build_target('macos', '', '10.14', 'x86_64', 'release')

  def test_publish(self):
    t1 = AMT(recipes = RECIPES.APPLE)
    t2 = AMT(recipes = RECIPES.WATER)

    adesc1 = 'apple;1.2.3;1;0;linux;release;x86_64;ubuntu;18'
    adesc2 = 'water;1.0.0;0;0;linux;release;x86_64;ubuntu;18'

    t1.publish(adesc1)
    t2.publish(adesc2)
    
    self.assertEqual( [ AD.parse(adesc1) ], t1.am.list_all_by_descriptor(None) )
    self.assertEqual( [ AD.parse(adesc2) ], t2.am.list_all_by_descriptor(None) )

    c = AMC()
    c.add_artifact_manager(t1.am)
    c.add_artifact_manager(t2.am)

    self.assertEqual( [ AD.parse(adesc1), AD.parse(adesc2) ], c.list_all_by_descriptor(None) )

    rm = c.get_requirement_manager(self.LINUX_BT)
    dm = rm.dependency_map( [ 'RUN' ], 'linux')
    print(dm)
    
if __name__ == '__main__':
  unit_test.main()
