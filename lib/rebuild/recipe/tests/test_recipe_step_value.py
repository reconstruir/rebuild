#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_step_value
from rebuild.step_manager import step_argspec
from bes.key_value import key_value as KV, key_value_list as KVL

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
    self.assertEqual( ( None, 'key', [ ( 'foo', '5' ), ( 'bar', '7' ) ] ),
                      recipe_step_value.parse('key:foo=5 bar=7', step_argspec.KEY_VALUES) )
    self.assertEqual( ( None, 'key', [ ( 'foo', '"5 6"' ), ( 'bar', '"7 8"' ) ] ),
                      recipe_step_value.parse('key:foo="5 6" bar="7 8"', step_argspec.KEY_VALUES) )

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
    
  def test_parse_mask(self):
    self.assertEqual( None, recipe_step_value.parse_mask('') )
    self.assertEqual( 'all', recipe_step_value.parse_mask('all:') )
    self.assertEqual( None, recipe_step_value.parse_mask('all') )
    self.assertEqual( 'linux', recipe_step_value.parse_mask('linux:key') )
    self.assertEqual( 'linux', recipe_step_value.parse_mask('linux:#') )
    
  def test__str__no_mask_int(self):
    self.assertEqual( 'key: 666', str(recipe_step_value(None, 'key', 666)) )

  def test__str__no_mask_bool(self):
    self.assertEqual( 'key: True', str(recipe_step_value(None, 'key', True)) )

  def test__str__no_mask_string(self):
    self.assertEqual( 'key: foo', str(recipe_step_value(None, 'key', 'foo')) )

  def test__str__no_mask_string_list(self):
    self.assertEqual( 'key: foo bar "x y"', str(recipe_step_value(None, 'key', [ 'foo', 'bar', 'x y' ])) )

  def test__str__no_mask_key_values(self):
    self.assertEqual( 'key: foo=5 bar=6 baz="x y"', str(recipe_step_value(None, 'key', KVL([KV('foo', 5), KV('bar', 6), KV('baz', 'x y')]))) )

  def test__str__with_mask_int(self):
    self.assertEqual( 'key\n  all: 666', str(recipe_step_value('all', 'key', 666)) )

  def test__str__with_mask_bool(self):
    self.assertEqual( 'key\n  all: True', str(recipe_step_value('all', 'key', True)) )

  def test__str__with_mask_string(self):
    self.assertEqual( 'key\n  all: foo', str(recipe_step_value('all', 'key', 'foo')) )

  def test__str__with_mask_string_list(self):
    self.assertEqual( 'key\n  all: foo bar "x y"', str(recipe_step_value('all', 'key', [ 'foo', 'bar', 'x y' ])) )

  def test__str__with_mask_key_values(self):
    self.assertEqual( 'key\n  all: foo=5 bar=6 baz="x y"', str(recipe_step_value('all', 'key', KVL([KV('foo', 5), KV('bar', 6), KV('baz', 'x y')]))) )
  
if __name__ == '__main__':
  unit_test.main()
