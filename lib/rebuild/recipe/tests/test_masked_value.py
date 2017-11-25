#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import masked_value as RSV
from rebuild.step_manager import step_argspec
from bes.key_value import key_value as KV, key_value_list as KVL

class test_masked_value(unit_test):

  def test__str__no_mask_int(self):
    self.assertEqual( '666', str(RSV(None, 666)) )

  def test__str__no_mask_bool(self):
    self.assertEqual( 'True', str(RSV(None, True)) )

  def test__str__no_mask_string(self):
    self.assertEqual( 'foo', str(RSV(None, 'foo')) )

  def test__str__no_mask_string_list(self):
    self.assertEqual( 'foo bar "x y"', str(RSV(None, [ 'foo', 'bar', 'x y' ])) )

  def test__str__no_mask_key_values(self):
    self.assertEqual( 'foo=5 bar=6 baz="x y"', str(RSV(None, KVL([KV('foo', 5), KV('bar', 6), KV('baz', 'x y')]))) )

  def test__str__with_mask_int(self):
    self.assertEqual( 'all: 666', str(RSV('all', 666)) )

  def test__str__with_mask_bool(self):
    self.assertEqual( 'all: True', str(RSV('all', True)) )

  def test__str__with_mask_string(self):
    self.assertEqual( 'all: foo', str(RSV('all', 'foo')) )

  def test__str__with_mask_string_list(self):
    self.assertEqual( 'all: foo bar "x y"', str(RSV('all', [ 'foo', 'bar', 'x y' ])) )

  def test__str__with_mask_key_values(self):
    self.assertEqual( 'all: foo=5 bar=6 baz="x y"', str(RSV('all', KVL([KV('foo', 5), KV('bar', 6), KV('baz', 'x y')]))) )
  
if __name__ == '__main__':
  unit_test.main()
