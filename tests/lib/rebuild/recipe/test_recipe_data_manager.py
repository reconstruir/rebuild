#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe.recipe_data_manager import recipe_data_manager as DM

class test_recipe_data_manager(unit_test):

  def test_get_empty(self):
    dm = DM()
    with self.assertRaises(KeyError) as ctx:
      dm.get('@DATA:foo:1.2.3')
    
  def test_set_get(self):
    dm = DM()
    dm.set('@DATA:foo:1.2.3', 'hi')
    self.assertEqual( 'hi', dm.get('@DATA:foo:1.2.3') )
    dm.set('@DATA:foo:1.2.3', 'bye')
    self.assertEqual( 'bye', dm.get('@DATA:foo:1.2.3') )
    
if __name__ == '__main__':
  unit_test.main()
