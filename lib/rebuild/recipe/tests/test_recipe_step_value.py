#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_step_value
from rebuild.step_manager import step_argspec

class test_recipe_step_value(unit_test):

  def test_key_only(self):
    self.assertEqual( ( None, 'foo', None ), recipe_step_value.parse('foo', step_argspec.STRING) )
    
  def test_key_and_value(self):
    self.assertEqual( ( None, 'foo', 'bar' ), recipe_step_value.parse('foo:bar', step_argspec.STRING) )
      
  def test_key_and_empty_value(self):
    self.assertEqual( ( None, 'foo', None ), recipe_step_value.parse('foo:', step_argspec.STRING) )
    
  def test_key_with_comment(self):
    self.assertEqual( ( None, 'foo', None ), recipe_step_value.parse('foo  # comment', step_argspec.STRING) )
    
  def test_key_and_value_with_comment(self):
    self.assertEqual( ( None, 'foo', 'bar' ), recipe_step_value.parse('foo:bar  # comment', step_argspec.STRING) )
    
  def test_key_and_empty_value_with_comment(self):
    self.assertEqual( ( None, 'foo', None ), recipe_step_value.parse('foo:# comment', step_argspec.STRING) )
    
  def test_value_string(self):
    self.assertEqual( ( None, 'foo', 'bar' ), recipe_step_value.parse('foo:bar', step_argspec.STRING) )

  def test_value_bool(self):
    self.assertEqual( ( None, 'foo', True ), recipe_step_value.parse('foo:True', step_argspec.BOOL) )
    self.assertEqual( ( None, 'foo', True ), recipe_step_value.parse('foo:true', step_argspec.BOOL) )
    self.assertEqual( ( None, 'foo', True ), recipe_step_value.parse('foo:1', step_argspec.BOOL) )
    self.assertEqual( ( None, 'foo', False ), recipe_step_value.parse('foo:False', step_argspec.BOOL) )
    self.assertEqual( ( None, 'foo', False ), recipe_step_value.parse('foo:false', step_argspec.BOOL) )
    self.assertEqual( ( None, 'foo', False ), recipe_step_value.parse('foo:0', step_argspec.BOOL) )
    
  def test_parse_key(self):
    self.assertEqual( '', recipe_step_value.parse_key('') )
    self.assertEqual( 'foo', recipe_step_value.parse_key('foo:True') )
    self.assertEqual( 'foo', recipe_step_value.parse_key('foo') )
    self.assertEqual( 'foo', recipe_step_value.parse_key('foo:') )
    self.assertEqual( 'f', recipe_step_value.parse_key('f:') )
    self.assertEqual( 'f', recipe_step_value.parse_key('f') )
    self.assertEqual( 'foo', recipe_step_value.parse_key('foo#') )
    
  def test_parse_system_mask(self):
    self.assertEqual( None, recipe_step_value.parse_system_mask('') )
    self.assertEqual( 'all', recipe_step_value.parse_system_mask('all:') )
    self.assertEqual( None, recipe_step_value.parse_system_mask('all') )
    self.assertEqual( 'linux', recipe_step_value.parse_system_mask('linux:foo') )
    self.assertEqual( 'linux', recipe_step_value.parse_system_mask('linux:#') )
    
if __name__ == '__main__':
  unit_test.main()
