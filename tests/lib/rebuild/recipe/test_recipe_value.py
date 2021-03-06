#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_value as V, masked_value as MV, masked_value_list as MVL
from bes.key_value import key_value as KV, key_value_list as KVL
from rebuild.recipe.value import value_key_values as VKV
from rebuild.recipe.value import value_type as VT

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
    self.assertEqual( 'key: a=5 b=6 c="x y"', str(V('key', [ MV(None, VKV(values = KVL([ ( 'a', 5 ), ( 'b', 6 ), ( 'c', 'x y' ) ]))) ])) )

  def test__str__multi_line_bool(self):
    self.assertEqual( 'key\n  all: True', str(V('key', [ MV('all', True) ])) )
    
  def test__str__multi_line_many(self):
    values = [
      MV('all', [ 'all' ]),
      MV('linux', [ 'linux' ]),
      MV('macos', [ 'macos' ]),
    ]
    self.assertEqual( 'key\n  all: all\n  linux: linux\n  macos: macos', str(V('key', values)) )
    
  def test_resolve(self):
    values = [
      MV('all', [ 'forall' ]),
      MV('linux', [ 'forlinux' ]),
      MV('macos', [ 'formacos' ]),
    ]

    self.assertEqual( [ 'forall', 'forlinux' ], V('key', values).resolve('linux', VT.STRING_LIST) )
    self.assertEqual( [ 'forall', 'formacos' ], V('key', values).resolve('macos', VT.STRING_LIST) )
    self.assertEqual( [ 'forall' ], V('key', values).resolve('android', VT.STRING_LIST) )
    
if __name__ == '__main__':
  unit_test.main()
