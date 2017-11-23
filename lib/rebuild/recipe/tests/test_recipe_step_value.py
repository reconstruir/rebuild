#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_step_value as RSV
from rebuild.step_manager import step_argspec
from bes.key_value import key_value as KV, key_value_list as KVL

class test_recipe_step_value(unit_test):

  def test_key_only(self):
    self.assertEqual( ( None, 'key', None ), RSV.parse_key_and_value('key', step_argspec.STRING) )
    
  def test_key_and_value(self):
    self.assertEqual( ( None, 'key', 'bar' ), RSV.parse_key_and_value('key:bar', step_argspec.STRING) )
      
  def test_key_and_empty_value(self):
    self.assertEqual( ( None, 'key', None ), RSV.parse_key_and_value('key:', step_argspec.STRING) )
    
  def test_key_with_comment(self):
    self.assertEqual( ( None, 'key', None ), RSV.parse_key_and_value('key  # comment', step_argspec.STRING) )
    
  def test_key_and_value_with_comment(self):
    self.assertEqual( ( None, 'key', 'bar' ), RSV.parse_key_and_value('key:bar  # comment', step_argspec.STRING) )
    
  def test_key_and_empty_value_with_comment(self):
    self.assertEqual( ( None, 'key', None ), RSV.parse_key_and_value('key:# comment', step_argspec.STRING) )
    
  def test_value_string(self):
    self.assertEqual( ( None, 'key', None ), RSV.parse_key_and_value('key', step_argspec.STRING) )
    self.assertEqual( ( None, 'key', None ), RSV.parse_key_and_value('key:', step_argspec.STRING) )
    self.assertEqual( ( None, 'key', 'bar' ), RSV.parse_key_and_value('key:bar', step_argspec.STRING) )

  def test_value_string_list(self):
    self.assertEqual( ( None, 'key', None ), RSV.parse_key_and_value('key', step_argspec.STRING_LIST) )
    self.assertEqual( ( None, 'key', None ), RSV.parse_key_and_value('key:', step_argspec.STRING_LIST) )
    self.assertEqual( ( None, 'key', [ 'bar' ] ), RSV.parse_key_and_value('key:bar', step_argspec.STRING_LIST) )
    self.assertEqual( ( None, 'key', [ 'foo', 'bar' ] ), RSV.parse_key_and_value('key:foo bar', step_argspec.STRING_LIST) )

  def test_value_key_values(self):
    self.assertEqual( ( None, 'key', None ), RSV.parse_key_and_value('key', step_argspec.KEY_VALUES) )
    self.assertEqual( ( None, 'key', None ), RSV.parse_key_and_value('key:', step_argspec.KEY_VALUES) )
    self.assertEqual( ( None, 'key', [ ( 'foo', '5' ) ] ), RSV.parse_key_and_value('key:foo=5', step_argspec.KEY_VALUES) )
    self.assertEqual( ( None, 'key', [ ( 'foo', '5' ), ( 'bar', '7' ) ] ),
                      RSV.parse_key_and_value('key:foo=5 bar=7', step_argspec.KEY_VALUES) )
    self.assertEqual( ( None, 'key', [ ( 'foo', '"5 6"' ), ( 'bar', '"7 8"' ) ] ),
                      RSV.parse_key_and_value('key:foo="5 6" bar="7 8"', step_argspec.KEY_VALUES) )

  def test_value_bool(self):
    self.assertEqual( ( None, 'key', None ), RSV.parse_key_and_value('key', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', None ), RSV.parse_key_and_value('key:', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', True ), RSV.parse_key_and_value('key:True', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', True ), RSV.parse_key_and_value('key:true', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', True ), RSV.parse_key_and_value('key:1', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', False ), RSV.parse_key_and_value('key:False', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', False ), RSV.parse_key_and_value('key:false', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', False ), RSV.parse_key_and_value('key:0', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', True ), RSV.parse_key_and_value('key: True', step_argspec.BOOL) )
    self.assertEqual( ( None, 'key', False ), RSV.parse_key_and_value('key: False', step_argspec.BOOL) )
    
  def test_value_int(self):
    self.assertEqual( ( None, 'key', None ), RSV.parse_key_and_value('key', step_argspec.INT) )
    self.assertEqual( ( None, 'key', None ), RSV.parse_key_and_value('key:', step_argspec.INT) )
    self.assertEqual( ( None, 'key', 1 ), RSV.parse_key_and_value('key:1', step_argspec.INT) )
    self.assertEqual( ( None, 'key', 1 ), RSV.parse_key_and_value('key: 1', step_argspec.INT) )
    self.assertEqual( ( None, 'key', 0 ), RSV.parse_key_and_value('key:0', step_argspec.INT) )
    self.assertEqual( ( None, 'key', 0 ), RSV.parse_key_and_value('key: 0', step_argspec.INT) )
    self.assertEqual( ( None, 'key', 666 ), RSV.parse_key_and_value('key:666', step_argspec.INT) )
    
  def test__str__no_mask_int(self):
    self.assertEqual( 'key: 666', str(RSV(None, 'key', 666)) )

  def test__str__no_mask_bool(self):
    self.assertEqual( 'key: True', str(RSV(None, 'key', True)) )

  def test__str__no_mask_string(self):
    self.assertEqual( 'key: foo', str(RSV(None, 'key', 'foo')) )

  def test__str__no_mask_string_list(self):
    self.assertEqual( 'key: foo bar "x y"', str(RSV(None, 'key', [ 'foo', 'bar', 'x y' ])) )

  def test__str__no_mask_key_values(self):
    self.assertEqual( 'key: foo=5 bar=6 baz="x y"', str(RSV(None, 'key', KVL([KV('foo', 5), KV('bar', 6), KV('baz', 'x y')]))) )

  def test__str__with_mask_int(self):
    self.assertEqual( 'key\n  all: 666', str(RSV('all', 'key', 666)) )

  def test__str__with_mask_bool(self):
    self.assertEqual( 'key\n  all: True', str(RSV('all', 'key', True)) )

  def test__str__with_mask_string(self):
    self.assertEqual( 'key\n  all: foo', str(RSV('all', 'key', 'foo')) )

  def test__str__with_mask_string_list(self):
    self.assertEqual( 'key\n  all: foo bar "x y"', str(RSV('all', 'key', [ 'foo', 'bar', 'x y' ])) )

  def test__str__with_mask_key_values(self):
    self.assertEqual( 'key\n  all: foo=5 bar=6 baz="x y"', str(RSV('all', 'key', KVL([KV('foo', 5), KV('bar', 6), KV('baz', 'x y')]))) )
  
if __name__ == '__main__':
  unit_test.main()
