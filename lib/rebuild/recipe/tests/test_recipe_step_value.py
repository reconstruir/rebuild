#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_step_value
from rebuild.step_manager import step_argspec

class test_recipe_step_value(unit_test):

  def test_key_only(self):
    self.assertEqual( ( None, 'key', None ), recipe_step_value.parse('key', step_argspec.STRING) )
    
  def test_key_and_value(self):
    self.assertEqual( ( None, 'key', 'bar' ), recipe_step_value.parse('key:bar', step_argspec.STRING) )
      
  def test_key_and_empty_value(self):
    self.assertEqual( ( None, 'key', None ), recipe_step_value.parse('key:', step_argspec.STRING) )
    
  def test_key_with_comment(self):
    self.assertEqual( ( None, 'key', None ), recipe_step_value.parse('key  # comment', step_argspec.STRING) )
    
  def test_key_and_value_with_comment(self):
    self.assertEqual( ( None, 'key', 'bar' ), recipe_step_value.parse('key:bar  # comment', step_argspec.STRING) )
    
  def test_key_and_empty_value_with_comment(self):
    self.assertEqual( ( None, 'key', None ), recipe_step_value.parse('key:# comment', step_argspec.STRING) )
    
  def test_value_string(self):
    self.assertEqual( ( None, 'key', None ), recipe_step_value.parse('key', step_argspec.STRING) )
    self.assertEqual( ( None, 'key', None ), recipe_step_value.parse('key:', step_argspec.STRING) )
    self.assertEqual( ( None, 'key', 'bar' ), recipe_step_value.parse('key:bar', step_argspec.STRING) )

  def test_value_string_list(self):
    self.assertEqual( ( None, 'key', None ), recipe_step_value.parse('key', step_argspec.STRING_LIST) )
    self.assertEqual( ( None, 'key', None ), recipe_step_value.parse('key:', step_argspec.STRING_LIST) )
    self.assertEqual( ( None, 'key', [ 'bar' ] ), recipe_step_value.parse('key:bar', step_argspec.STRING_LIST) )
    self.assertEqual( ( None, 'key', [ 'foo', 'bar' ] ), recipe_step_value.parse('key:foo bar', step_argspec.STRING_LIST) )

  def test_value_key_values(self):
    self.assertEqual( ( None, 'key', None ), recipe_step_value.parse('key', step_argspec.KEY_VALUES) )
    self.assertEqual( ( None, 'key', None ), recipe_step_value.parse('key:', step_argspec.KEY_VALUES) )
    self.assertEqual( ( None, 'key', [ ( 'foo', '5' ) ] ), recipe_step_value.parse('key:foo=5', step_argspec.KEY_VALUES) )

  def test_value_bool(self):
    self.assertEqual( ( None, 'key', None ), recipe_step_value.parse('key', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', None ), recipe_step_value.parse('key:', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', True ), recipe_step_value.parse('key:True', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', True ), recipe_step_value.parse('key:true', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', True ), recipe_step_value.parse('key:1', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', False ), recipe_step_value.parse('key:False', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', False ), recipe_step_value.parse('key:false', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', False ), recipe_step_value.parse('key:0', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', True ), recipe_step_value.parse('key: True', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', False ), recipe_step_value.parse('key: False', step_argspec.BOOL) )
    
  def test_value_int(self):
    self.assertEqual( ( None, 'key', None ), recipe_step_value.parse('key', step_argspec.INT) )
    self.assertEqual( ( None, 'key', None ), recipe_step_value.parse('key:', step_argspec.INT) )
    self.assertEqual( ( None, 'key', 1 ), recipe_step_value.parse('key:1', step_argspec.INT) )
    self.assertEqual( ( None, 'key', 1 ), recipe_step_value.parse('key: 1', step_argspec.INT) )
    self.assertEqual( ( None, 'key', 0 ), recipe_step_value.parse('key:0', step_argspec.INT) )
    self.assertEqual( ( None, 'key', 0 ), recipe_step_value.parse('key: 0', step_argspec.INT) )
    self.assertEqual( ( None, 'key', 666 ), recipe_step_value.parse('key:666', step_argspec.INT) )
    
  def test_parse_key(self):
    self.assertEqual( '', recipe_step_value.parse_key('') )
    self.assertEqual( 'key', recipe_step_value.parse_key('key:True') )
    self.assertEqual( 'key', recipe_step_value.parse_key('key') )
    self.assertEqual( 'key', recipe_step_value.parse_key('key:') )
    self.assertEqual( 'f', recipe_step_value.parse_key('f:') )
    self.assertEqual( 'f', recipe_step_value.parse_key('f') )
    self.assertEqual( 'key', recipe_step_value.parse_key('key#') )
    
  def test_parse_system_mask(self):
    self.assertEqual( None, recipe_step_value.parse_system_mask('') )
    self.assertEqual( 'all', recipe_step_value.parse_system_mask('all:') )
    self.assertEqual( None, recipe_step_value.parse_system_mask('all') )
    self.assertEqual( 'linux', recipe_step_value.parse_system_mask('linux:key') )
    self.assertEqual( 'linux', recipe_step_value.parse_system_mask('linux:#') )
    
if __name__ == '__main__':
  unit_test.main()
