#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.key_value.key_value_list import key_value_list as KVL
from bes.text.tree_text_parser import tree_text_parser as TTP
from rebuild.recipe import recipe_parser_util as RPU
from rebuild.recipe.value import value_type as VT, value_origin as VO, value_key_values as VKV, value_string_list as VSL

class test_recipe_parser_util(unit_test):

  TEST_ORIGIN = VO(__file__, 1, '')
  
  def test_parse_key(self):
    self.assertEqual( '', RPU.parse_key(self.TEST_ORIGIN, '') )
    self.assertEqual( 'key', RPU.parse_key(self.TEST_ORIGIN, 'key:True') )
    self.assertEqual( 'key', RPU.parse_key(self.TEST_ORIGIN, 'key') )
    self.assertEqual( 'key', RPU.parse_key(self.TEST_ORIGIN, 'key:') )
    self.assertEqual( 'f', RPU.parse_key(self.TEST_ORIGIN, 'f:') )
    self.assertEqual( 'f', RPU.parse_key(self.TEST_ORIGIN, 'f') )
    self.assertEqual( 'key', RPU.parse_key(self.TEST_ORIGIN, 'key#') )

  def test_make_key_value_key_only(self):
    self.assertEqual( ( 'key', None ), RPU.make_key_value(self.TEST_ORIGIN, 'key', TTP.make_node('key', 1), 'string') )
    
  def test_make_key_value_key_and_value(self):
    self.assertEqual( ( 'key', 'bar' ), RPU.make_key_value(self.TEST_ORIGIN, 'key:bar', TTP.make_node('key:bar', 1), 'string') )
      
  def test_make_key_value_key_and_empty_value(self):
    self.assertEqual( ( 'key', None ), RPU.make_key_value(self.TEST_ORIGIN, 'key:', TTP.make_node('key:', 1), 'string') )
    
  def test_make_key_value_key_with_comment(self):
    self.assertEqual( ( 'key', None ), RPU.make_key_value(self.TEST_ORIGIN, 'key  # comment', TTP.make_node('key  # comment', 1), 'string') )
    
  def test_make_key_value_key_and_value_with_comment(self):
    self.assertEqual( ( 'key', 'bar' ), RPU.make_key_value(self.TEST_ORIGIN, 'key:bar  # comment', TTP.make_node('key:bar  # comment', 1), 'string') )
    
  def test_make_key_value_key_and_empty_value_with_comment(self):
    self.assertEqual( ( 'key', None ), RPU.make_key_value(self.TEST_ORIGIN, 'key:# comment', TTP.make_node('key:# comment', 1), 'string') )
    
  def test_make_key_value_value_string(self):
    self.assertEqual( ( 'key', None ), RPU.make_key_value(self.TEST_ORIGIN, 'key', TTP.make_node('key', 1), 'string') )
    self.assertEqual( ( 'key', None ), RPU.make_key_value(self.TEST_ORIGIN, 'key:', TTP.make_node('key:', 1), 'string') )
    self.assertEqual( ( 'key', 'bar' ), RPU.make_key_value(self.TEST_ORIGIN, 'key:bar', TTP.make_node('key:bar', 1), 'string') )

  def test_make_key_value_value_string_list(self):
    self.assertEqual( ( 'key', None ), RPU.make_key_value(self.TEST_ORIGIN, 'key', TTP.make_node('key', 1), 'string_list') )
    self.assertEqual( ( 'key', None ), RPU.make_key_value(self.TEST_ORIGIN, 'key:', TTP.make_node('key:', 1), 'string_list') )
    self.assertEqual( ( 'key', VSL(value = [ 'bar' ]) ), RPU.make_key_value(self.TEST_ORIGIN, 'key:bar', TTP.make_node('key:bar', 1), 'string_list') )
    self.assertEqual( ( 'key', VSL(value = [ 'foo', 'bar' ]) ), RPU.make_key_value(self.TEST_ORIGIN, 'key:foo bar', TTP.make_node('key:foo bar', 1), 'string_list') )

  def test_make_key_value_value_key_values(self):
    self.assertEqual( ( 'key', None ), RPU.make_key_value(self.TEST_ORIGIN, 'key', TTP.make_node('key', 1), 'key_values') )
    self.assertEqual( ( 'key', None ), RPU.make_key_value(self.TEST_ORIGIN, 'key:', TTP.make_node('key:', 1), 'key_values') )
    self.assertEqual( ( 'key', VKV(value = KVL([ ( 'foo', '5' ) ])) ),
                      RPU.make_key_value(self.TEST_ORIGIN, 'key:foo=5', TTP.make_node('key:foo=5', 1), 'key_values') )
    self.assertEqual( ( 'key', VKV(value = KVL([ ( 'foo', '5' ), ( 'bar', '7' ) ])) ),
                      RPU.make_key_value(self.TEST_ORIGIN, 'key:foo=5 bar=7', TTP.make_node('key:foo=5 bar=7', 1), 'key_values') )
    self.assertEqual( ( 'key', VKV(value = KVL([ ( 'foo', '"5 6"' ), ( 'bar', '"7 8"' ) ])) ),
                      RPU.make_key_value(self.TEST_ORIGIN, 'key:foo="5 6" bar="7 8"', TTP.make_node('key:foo="5 6" bar="7 8"', 1), 'key_values') )

  def test_make_key_value_value_bool(self):
    self.assertEqual( ( 'key', None ), RPU.make_key_value(self.TEST_ORIGIN, 'key', TTP.make_node('key', 1), 'bool') )
    self.assertEqual( ( 'key', None ), RPU.make_key_value(self.TEST_ORIGIN, 'key:', TTP.make_node('key:', 1), 'bool') )
    self.assertEqual( ( 'key', True ), RPU.make_key_value(self.TEST_ORIGIN, 'key:True', TTP.make_node('key:True', 1), 'bool') )
    self.assertEqual( ( 'key', True ), RPU.make_key_value(self.TEST_ORIGIN, 'key:true', TTP.make_node('key:true', 1), 'bool') )
    self.assertEqual( ( 'key', True ), RPU.make_key_value(self.TEST_ORIGIN, 'key:1', TTP.make_node('key:1', 1), 'bool') )
    self.assertEqual( ( 'key', False ), RPU.make_key_value(self.TEST_ORIGIN, 'key:False', TTP.make_node('key:False', 1), 'bool') )
    self.assertEqual( ( 'key', False ), RPU.make_key_value(self.TEST_ORIGIN, 'key:false', TTP.make_node('key:false', 1), 'bool') )
    self.assertEqual( ( 'key', False ), RPU.make_key_value(self.TEST_ORIGIN, 'key:0', TTP.make_node('key:0', 1), 'bool') )
    self.assertEqual( ( 'key', True ), RPU.make_key_value(self.TEST_ORIGIN, 'key: True', TTP.make_node('key: True', 1), 'bool') )
    self.assertEqual( ( 'key', False ), RPU.make_key_value(self.TEST_ORIGIN, 'key: False', TTP.make_node('key: False', 1), 'bool') )
    
  def test_make_key_value_value_int(self):
    self.assertEqual( ( 'key', None ), RPU.make_key_value(self.TEST_ORIGIN, 'key', TTP.make_node('key', 1), 'int') )
    self.assertEqual( ( 'key', None ), RPU.make_key_value(self.TEST_ORIGIN, 'key:', TTP.make_node('key:', 1), 'int') )
    self.assertEqual( ( 'key', 1 ), RPU.make_key_value(self.TEST_ORIGIN, 'key:1', TTP.make_node('key:1', 1), 'int') )
    self.assertEqual( ( 'key', 1 ), RPU.make_key_value(self.TEST_ORIGIN, 'key: 1', TTP.make_node('key: 1', 1), 'int') )
    self.assertEqual( ( 'key', 0 ), RPU.make_key_value(self.TEST_ORIGIN, 'key:0', TTP.make_node('key:0', 1), 'int') )
    self.assertEqual( ( 'key', 0 ), RPU.make_key_value(self.TEST_ORIGIN, 'key: 0', TTP.make_node('key: 0', 1), 'int') )
    self.assertEqual( ( 'key', 666 ), RPU.make_key_value(self.TEST_ORIGIN, 'key:666', TTP.make_node('key:666', 1), 'int') )

  def test_split_mask_and_value(self):
    self.assertEqual( ( 'all', 'foo' ), RPU.split_mask_and_value('all: foo') )
    self.assertEqual( ( 'all', 'foo' ), RPU.split_mask_and_value('all:foo') )
    self.assertEqual( ( 'all', 'foo' ), RPU.split_mask_and_value(' all:foo') )
    self.assertEqual( ( 'all', 'foo' ), RPU.split_mask_and_value(' all:foo ') )
    self.assertEqual( ( 'all', 'foo' ), RPU.split_mask_and_value(' all: foo ') )
    self.assertEqual( ( 'all', 'foo' ), RPU.split_mask_and_value(' all :foo ') )
    self.assertEqual( ( 'all', 'foo' ), RPU.split_mask_and_value(' all : foo ') )
    self.assertEqual( ( 'all', 'foo' ), RPU.split_mask_and_value('all : foo') )

  def test_strip_mask(self):
    self.assertEqual( 'foo', RPU.strip_mask('all: foo') )
    self.assertEqual( 'foo', RPU.strip_mask('all:foo') )
    self.assertEqual( 'foo', RPU.strip_mask(' all:foo') )
    self.assertEqual( 'foo', RPU.strip_mask(' all:foo ') )
    self.assertEqual( 'foo', RPU.strip_mask(' all: foo ') )
    self.assertEqual( 'foo', RPU.strip_mask(' all :foo ') )
    self.assertEqual( 'foo', RPU.strip_mask(' all : foo ') )
    self.assertEqual( 'foo', RPU.strip_mask('all : foo') )

if __name__ == '__main__':
  unit_test.main()
