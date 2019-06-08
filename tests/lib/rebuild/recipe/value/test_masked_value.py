#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe.value.masked_value import masked_value as MV
from bes.key_value.key_value import key_value as KV
from bes.key_value.key_value_list import key_value_list as KVL

from rebuild.recipe.value.value_int import value_int
from rebuild.recipe.value.value_bool import value_bool
from rebuild.recipe.value.value_string import value_string
from rebuild.recipe.value.value_string_list import value_string_list
from rebuild.recipe.value.value_key_values import value_key_values

class test_masked_value(unit_test):

  def test__str__no_mask_int(self):
    self.assertEqual( '666', str(MV(None, value_int(value = 666))) )

  def test__str__no_mask_bool(self):
    self.assertEqual( 'True', str(MV(None, value_bool(value = True))) )

  def test__str__no_mask_string(self):
    self.assertEqual( 'foo', str(MV(None, value_string(value = 'foo'))) )

  def test__str__no_mask_string_list(self):
    self.assertEqual( 'foo bar "x y"', str(MV(None, value_string_list(value = [ 'foo', 'bar', 'x y' ]))) )

  def test__str__no_mask_key_values(self):
    self.assertEqual( 'foo=5 bar=6 baz="x y"', str(MV(None, value_key_values(value = KVL([KV('foo', 5), KV('bar', 6), KV('baz', 'x y')])))) )

  def test__str__with_mask_int(self):
    self.assertEqual( 'all: 666', str(MV('all', value_int(value = 666))) )

  def test__str__with_mask_bool(self):
    self.assertEqual( 'all: True', str(MV('all', value_bool(value = True))) )

  def test__str__with_mask_string(self):
    self.assertEqual( 'all: foo', str(MV('all', value_string(value = 'foo'))) )

  def test__str__with_mask_string_list(self):
    self.assertEqual( 'all: foo bar "x y"', str(MV('all', value_string_list(value = [ 'foo', 'bar', 'x y' ]))) )

  def test__str__with_mask_key_values(self):
    self.assertEqual( 'all: foo=5 bar=6 baz="x y"', str(MV('all', value_key_values(value = KVL([KV('foo', 5), KV('bar', 6), KV('baz', 'x y')])))) )
  
if __name__ == '__main__':
  unit_test.main()
