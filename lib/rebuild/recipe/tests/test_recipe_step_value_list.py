#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_step_value as V, recipe_step_value_list as VL
from rebuild.base import build_system

class test_recipe_step_value_list(unit_test):

  def test_append(self):
    r = VL()
    r.append(V(None, 'foo', 666))
    r.append(V(None, 'bar', 667))
    self.assertEqual( 2, len(r) )
    
  def test_resolve_int(self):
    r = VL()
    r.append(V(None, 'foo', 666))
    r.append(V(None, 'bar', 667))
    self.assertEqual( 667, r.resolve(build_system.LINUX) )
    
if __name__ == '__main__':
  unit_test.main()
