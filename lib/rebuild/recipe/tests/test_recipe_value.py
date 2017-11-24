#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_value as V, masked_value as MV, masked_value_list as MVL
from bes.key_value import key_value as KV, key_value_list as KVL

class test_recipe_value(unit_test):

  def test__str__empty(self):
    self.assertEqual( 'key:', str(V('key', None)) )
    
  def test__str__one_line_bool(self):
    self.assertEqual( 'key: True', str(V('key', [ MV(None, True) ])) )
    
  def test__str__one_line_string(self):
    self.assertEqual( 'key: foo', str(V('key', [ MV(None, 'foo') ])) )
    
  def test__str__one_line_int(self):
    self.assertEqual( 'key: 666', str(V('key', [ MV(None, 666) ])) )
    
  def test__str__one_line_string_list(self):
    self.assertEqual( 'key: a b "c d"', str(V('key', [ MV(None, [ 'a', 'b', 'c d' ]) ])) )
    
  def test__str__one_line_key_values(self):
    self.assertEqual( 'key: a=5 b=6 c="x y"', str(V('key', [ MV(None, KVL([ ( 'a', 5 ), ( 'b', 6 ), ( 'c', 'x y' ) ])) ])) )
    
if __name__ == '__main__':
  unit_test.main()
