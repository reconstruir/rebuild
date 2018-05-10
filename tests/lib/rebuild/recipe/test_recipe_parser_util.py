#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.key_value import key_value_list as KVL
from rebuild.recipe import recipe_parser_util as RPU, recipe_load_env
from rebuild.recipe.value import value_type as VT, value_origin as VO, value_key_values as VKV

class test_recipe_parser_util(unit_test):

  TEST_ENV = recipe_load_env(None, None)
  TEST_ORIGIN = VO(__file__, 1, '')
  
  def test_parse_key(self):
    self.assertEqual( '', RPU.parse_key(self.TEST_ORIGIN, '') )
    self.assertEqual( 'key', RPU.parse_key(self.TEST_ORIGIN, 'key:True') )
    self.assertEqual( 'key', RPU.parse_key(self.TEST_ORIGIN, 'key') )
    self.assertEqual( 'key', RPU.parse_key(self.TEST_ORIGIN, 'key:') )
    self.assertEqual( 'f', RPU.parse_key(self.TEST_ORIGIN, 'f:') )
    self.assertEqual( 'f', RPU.parse_key(self.TEST_ORIGIN, 'f') )
    self.assertEqual( 'key', RPU.parse_key(self.TEST_ORIGIN, 'key#') )

  def test_parse_key_and_value_key_only(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key', 'string') )
    
  def test_parse_key_and_value_key_and_value(self):
    self.assertEqual( ( 'key', 'bar' ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:bar', 'string') )
      
  def test_parse_key_and_value_key_and_empty_value(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:', 'string') )
    
  def test_parse_key_and_value_key_with_comment(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key  # comment', 'string') )
    
  def test_parse_key_and_value_key_and_value_with_comment(self):
    self.assertEqual( ( 'key', 'bar' ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:bar  # comment', 'string') )
    
  def test_parse_key_and_value_key_and_empty_value_with_comment(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:# comment', 'string') )
    
  def test_parse_key_and_value_value_string(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV,       self.TEST_ORIGIN, 'key', 'string') )
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV,       self.TEST_ORIGIN, 'key:', 'string') )
    self.assertEqual( ( 'key', 'bar' ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:bar', 'string') )

  def test_parse_key_and_value_value_string_list(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key', 'string_list') )
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:', 'string_list') )
    self.assertEqual( ( 'key', [ 'bar' ] ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:bar', 'string_list') )
    self.assertEqual( ( 'key', [ 'foo', 'bar' ] ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:foo bar', 'string_list') )

  def test_parse_key_and_value_value_key_values(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key', 'key_values') )
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:', 'key_values') )
    self.assertEqual( ( 'key', VKV(values = KVL([ ( 'foo', '5' ) ])) ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:foo=5', 'key_values') )
    self.assertEqual( ( 'key', VKV(values = KVL([ ( 'foo', '5' ), ( 'bar', '7' ) ])) ),
                      RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:foo=5 bar=7', 'key_values') )
    self.assertEqual( ( 'key', VKV(values = KVL([ ( 'foo', '"5 6"' ), ( 'bar', '"7 8"' ) ])) ),
                      RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:foo="5 6" bar="7 8"', 'key_values') )

  def test_parse_key_and_value_value_bool(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key', 'bool') )
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:', 'bool') )
    self.assertEqual( ( 'key', True ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:True', 'bool') )
    self.assertEqual( ( 'key', True ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:true', 'bool') )
    self.assertEqual( ( 'key', True ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:1', 'bool') )
    self.assertEqual( ( 'key', False ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:False', 'bool') )
    self.assertEqual( ( 'key', False ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:false', 'bool') )
    self.assertEqual( ( 'key', False ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:0', 'bool') )
    self.assertEqual( ( 'key', True ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key: True', 'bool') )
    self.assertEqual( ( 'key', False ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key: False', 'bool') )
    
  def test_parse_key_and_value_value_int(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key', 'int') )
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:', 'int') )
    self.assertEqual( ( 'key', 1 ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:1', 'int') )
    self.assertEqual( ( 'key', 1 ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key: 1', 'int') )
    self.assertEqual( ( 'key', 0 ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:0', 'int') )
    self.assertEqual( ( 'key', 0 ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key: 0', 'int') )
    self.assertEqual( ( 'key', 666 ), RPU.parse_key_and_value(self.TEST_ENV, self.TEST_ORIGIN, 'key:666', 'int') )

if __name__ == '__main__':
  unit_test.main()
