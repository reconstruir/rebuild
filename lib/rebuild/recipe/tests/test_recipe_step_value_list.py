#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_step_value, recipe_step_value_list

class test_recipe_step_value_list(unit_test):

  def test_foo(self):
    r = recipe_step_value_list()
    r.add(recipe_step_value(None, 'foo', 666))
    
if __name__ == '__main__':
  unit_test.main()
