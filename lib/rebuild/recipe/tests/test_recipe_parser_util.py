#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_parser_util as RPU
from rebuild.step import step_argspec

class test_recipe_parser_util(unit_test):

  def test_parse_key(self):
    self.assertEqual( '', RPU.parse_key('') )
    self.assertEqual( 'key', RPU.parse_key('key:True') )
    self.assertEqual( 'key', RPU.parse_key('key') )
    self.assertEqual( 'key', RPU.parse_key('key:') )
    self.assertEqual( 'f', RPU.parse_key('f:') )
    self.assertEqual( 'f', RPU.parse_key('f') )
    self.assertEqual( 'key', RPU.parse_key('key#') )

  def test_parse_key_and_value_key_only(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value('key', '<none>', step_argspec.STRING) )
    
  def test_parse_key_and_value_key_and_value(self):
    self.assertEqual( ( 'key', 'bar' ), RPU.parse_key_and_value('key:bar', '<none>', step_argspec.STRING) )
      
  def test_parse_key_and_value_key_and_empty_value(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value('key:', '<none>', step_argspec.STRING) )
    
  def test_parse_key_and_value_key_with_comment(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value('key  # comment', '<none>', step_argspec.STRING) )
    
  def test_parse_key_and_value_key_and_value_with_comment(self):
    self.assertEqual( ( 'key', 'bar' ), RPU.parse_key_and_value('key:bar  # comment', '<none>', step_argspec.STRING) )
    
  def test_parse_key_and_value_key_and_empty_value_with_comment(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value('key:# comment', '<none>', step_argspec.STRING) )
    
  def test_parse_key_and_value_value_string(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value('key', '<none>', step_argspec.STRING) )
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value('key:', '<none>', step_argspec.STRING) )
    self.assertEqual( ( 'key', 'bar' ), RPU.parse_key_and_value('key:bar', '<none>', step_argspec.STRING) )

  def test_parse_key_and_value_value_string_list(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value('key', '<none>', step_argspec.STRING_LIST) )
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value('key:', '<none>', step_argspec.STRING_LIST) )
    self.assertEqual( ( 'key', [ 'bar' ] ), RPU.parse_key_and_value('key:bar', '<none>', step_argspec.STRING_LIST) )
    self.assertEqual( ( 'key', [ 'foo', 'bar' ] ), RPU.parse_key_and_value('key:foo bar', '<none>', step_argspec.STRING_LIST) )

  def test_parse_key_and_value_value_key_values(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value('key', '<none>', step_argspec.KEY_VALUES) )
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value('key:', '<none>', step_argspec.KEY_VALUES) )
    self.assertEqual( ( 'key', [ ( 'foo', '5' ) ] ), RPU.parse_key_and_value('key:foo=5', '<none>', step_argspec.KEY_VALUES) )
    self.assertEqual( ( 'key', [ ( 'foo', '5' ), ( 'bar', '7' ) ] ),
                      RPU.parse_key_and_value('key:foo=5 bar=7', '<none>', step_argspec.KEY_VALUES) )
    self.assertEqual( ( 'key', [ ( 'foo', '"5 6"' ), ( 'bar', '"7 8"' ) ] ),
                      RPU.parse_key_and_value('key:foo="5 6" bar="7 8"', '<none>', step_argspec.KEY_VALUES) )

  def test_parse_key_and_value_value_bool(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value('key', '<none>', step_argspec.BOOL) )
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value('key:', '<none>', step_argspec.BOOL) )
    self.assertEqual( ( 'key', True ), RPU.parse_key_and_value('key:True', '<none>', step_argspec.BOOL) )
    self.assertEqual( ( 'key', True ), RPU.parse_key_and_value('key:true', '<none>', step_argspec.BOOL) )
    self.assertEqual( ( 'key', True ), RPU.parse_key_and_value('key:1', '<none>', step_argspec.BOOL) )
    self.assertEqual( ( 'key', False ), RPU.parse_key_and_value('key:False', '<none>', step_argspec.BOOL) )
    self.assertEqual( ( 'key', False ), RPU.parse_key_and_value('key:false', '<none>', step_argspec.BOOL) )
    self.assertEqual( ( 'key', False ), RPU.parse_key_and_value('key:0', '<none>', step_argspec.BOOL) )
    self.assertEqual( ( 'key', True ), RPU.parse_key_and_value('key: True', '<none>', step_argspec.BOOL) )
    self.assertEqual( ( 'key', False ), RPU.parse_key_and_value('key: False', '<none>', step_argspec.BOOL) )
    
  def test_parse_key_and_value_value_int(self):
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value('key', '<none>', step_argspec.INT) )
    self.assertEqual( ( 'key', None ), RPU.parse_key_and_value('key:', '<none>', step_argspec.INT) )
    self.assertEqual( ( 'key', 1 ), RPU.parse_key_and_value('key:1', '<none>', step_argspec.INT) )
    self.assertEqual( ( 'key', 1 ), RPU.parse_key_and_value('key: 1', '<none>', step_argspec.INT) )
    self.assertEqual( ( 'key', 0 ), RPU.parse_key_and_value('key:0', '<none>', step_argspec.INT) )
    self.assertEqual( ( 'key', 0 ), RPU.parse_key_and_value('key: 0', '<none>', step_argspec.INT) )
    self.assertEqual( ( 'key', 666 ), RPU.parse_key_and_value('key:666', '<none>', step_argspec.INT) )
    
if __name__ == '__main__':
  unit_test.main()
