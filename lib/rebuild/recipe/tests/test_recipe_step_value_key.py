#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_step_value_key
from rebuild.step_manager import step_argspec

class test_recipe_step_value_key(unit_test):

  def test_key_only(self):
    self.assertEqual( ( 'foo', None ), recipe_step_value_key.parse('foo', step_argspec.STRING) )
    
  def test_key_and_value(self):
    self.assertEqual( ( 'foo', 'bar' ), recipe_step_value_key.parse('foo:bar', step_argspec.STRING) )
      
  def test_key_and_empty_value(self):
    self.assertEqual( ( 'foo', None ), recipe_step_value_key.parse('foo:', step_argspec.STRING) )
    
  def test_key_with_comment(self):
    self.assertEqual( ( 'foo', None ), recipe_step_value_key.parse('foo  # comment', step_argspec.STRING) )
    
  def test_key_and_value_with_comment(self):
    self.assertEqual( ( 'foo', 'bar' ), recipe_step_value_key.parse('foo:bar  # comment', step_argspec.STRING) )
    
  def test_key_and_empty_value_with_comment(self):
    self.assertEqual( ( 'foo', None ), recipe_step_value_key.parse('foo:# comment', step_argspec.STRING) )
    
  def test_value_string(self):
    self.assertEqual( ( 'foo', 'bar' ), recipe_step_value_key.parse('foo:bar', step_argspec.STRING) )

  def test_value_bool(self):
    self.assertEqual( ( 'foo', True ), recipe_step_value_key.parse('foo:True', step_argspec.BOOL) )
    self.assertEqual( ( 'foo', True ), recipe_step_value_key.parse('foo:true', step_argspec.BOOL) )
    self.assertEqual( ( 'foo', True ), recipe_step_value_key.parse('foo:1', step_argspec.BOOL) )
    self.assertEqual( ( 'foo', False ), recipe_step_value_key.parse('foo:False', step_argspec.BOOL) )
    self.assertEqual( ( 'foo', False ), recipe_step_value_key.parse('foo:false', step_argspec.BOOL) )
    self.assertEqual( ( 'foo', False ), recipe_step_value_key.parse('foo:0', step_argspec.BOOL) )
    
if __name__ == '__main__':
  unit_test.main()
