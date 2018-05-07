#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.key_value import key_value_list as KVL
from rebuild.recipe import recipe_parser_util as RPU, recipe_load_env
from rebuild.recipe.value import value_type as VT, value_key_values as VKV

class test_recipe_parser_util(unit_test):

  TEST_ENV = recipe_load_env(None, None)
  
  def test_parse_key(self):
    self.assertEqual( '', RPU.parse_key('') )
    self.assertEqual( 'key', RPU.parse_key('key:True') )
    self.assertEqual( 'key', RPU.parse_key('key') )
    self.assertEqual( 'key', RPU.parse_key('key:') )
    self.assertEqual( 'f', RPU.parse_key('f:') )
    self.assertEqual( 'f', RPU.parse_key('f') )
    self.assertEqual( 'key', RPU.parse_key('key#') )

  def test_parse_key_and_value_key_only(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key', VT.STRING) )
    
  def test_parse_key_and_value_key_and_value(self):
    self.assertEqual( ( 'key', 'bar' ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:bar', VT.STRING) )
      
  def test_parse_key_and_value_key_and_empty_value(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:', VT.STRING) )
    
  def test_parse_key_and_value_key_with_comment(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key  # comment', VT.STRING) )
    
  def test_parse_key_and_value_key_and_value_with_comment(self):
    self.assertEqual( ( 'key', 'bar' ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:bar  # comment', VT.STRING) )
    
  def test_parse_key_and_value_key_and_empty_value_with_comment(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:# comment', VT.STRING) )
    
  def test_parse_key_and_value_value_string(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV,       '<none>', 'key', VT.STRING) )
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV,       '<none>', 'key:', VT.STRING) )
    self.assertEqual( ( 'key', 'bar' ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:bar', VT.STRING) )

  def test_parse_key_and_value_value_string_list(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key', VT.STRING_LIST) )
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:', VT.STRING_LIST) )
    self.assertEqual( ( 'key', [ 'bar' ] ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:bar', VT.STRING_LIST) )
    self.assertEqual( ( 'key', [ 'foo', 'bar' ] ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:foo bar', VT.STRING_LIST) )

  def test_parse_key_and_value_value_key_values(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key', VT.KEY_VALUES) )
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:', VT.KEY_VALUES) )
    self.assertEqual( ( 'key', VKV(values = KVL([ ( 'foo', '5' ) ])) ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:foo=5', VT.KEY_VALUES) )
    self.assertEqual( ( 'key', VKV(values = KVL([ ( 'foo', '5' ), ( 'bar', '7' ) ])) ),
                      RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:foo=5 bar=7', VT.KEY_VALUES) )
    self.assertEqual( ( 'key', VKV(values = KVL([ ( 'foo', '"5 6"' ), ( 'bar', '"7 8"' ) ])) ),
                      RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:foo="5 6" bar="7 8"', VT.KEY_VALUES) )

  def test_parse_key_and_value_value_bool(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key', VT.BOOL) )
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:', VT.BOOL) )
    self.assertEqual( ( 'key', True ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:True', VT.BOOL) )
    self.assertEqual( ( 'key', True ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:true', VT.BOOL) )
    self.assertEqual( ( 'key', True ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:1', VT.BOOL) )
    self.assertEqual( ( 'key', False ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:False', VT.BOOL) )
    self.assertEqual( ( 'key', False ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:false', VT.BOOL) )
    self.assertEqual( ( 'key', False ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:0', VT.BOOL) )
    self.assertEqual( ( 'key', True ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key: True', VT.BOOL) )
    self.assertEqual( ( 'key', False ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key: False', VT.BOOL) )
    
  def test_parse_key_and_value_value_int(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key', VT.INT) )
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:', VT.INT) )
    self.assertEqual( ( 'key', 1 ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:1', VT.INT) )
    self.assertEqual( ( 'key', 1 ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key: 1', VT.INT) )
    self.assertEqual( ( 'key', 0 ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:0', VT.INT) )
    self.assertEqual( ( 'key', 0 ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key: 0', VT.INT) )
    self.assertEqual( ( 'key', 666 ), RPU.parse_key_and_value(self.TEST_ENV, '<none>', 'key:666', VT.INT) )

if __name__ == '__main__':
  unit_test.main()
