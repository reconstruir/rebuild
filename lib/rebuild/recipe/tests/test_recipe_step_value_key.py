#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_step_value_key

class test_recipe_step_value_key(unit_test):

  def test_left_only(self):
    self.assertTrue( ( 'foo', None ), recipe_step_value_key.parse('foo') )
      
  def test_left_and_right(self):
    self.assertTrue( ( 'foo', 'bar' ), recipe_step_value_key.parse('foo:bar') )
      
  def test_left_and_empty_right(self):
    self.assertTrue( ( 'foo', None ), recipe_step_value_key.parse('foo:') )
    
if __name__ == '__main__':
  unit_test.main()
