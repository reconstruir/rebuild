#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild.recipe import recipe_section as section
from bes.key_value import key_value as KV, key_value_list as KVL

class test_recipe_section(unittest.TestCase):

  def test___init__values_empty_list(self):
    s = section(KV('name', 'foo'), [])
    self.assertEqual( 'name', s.header.key )
    self.assertEqual( 'foo', s.header.value )
    self.assertEqual( [], s.values )

  def test___init__values_none(self):
    s = section(KV('name', 'foo'), None)
    self.assertEqual( 'name', s.header.key )
    self.assertEqual( 'foo', s.header.value )
    self.assertEqual( [], s.values )
    
  def test___init__values_invalid_values(self):
    with self.assertRaises(TypeError) as context:
      section(KV('name', 'foo'), 666)
    with self.assertRaises(TypeError) as context:
      section(KV('name', 'foo'), 'foo')
    with self.assertRaises(TypeError) as context:
      section(KV('name', 'foo'), [ 'foo' ])
    
  def test___init__invalid_header(self):
    with self.assertRaises(TypeError) as context:
      section('foo', None)
    with self.assertRaises(TypeError) as context:
      section(KV('foo', 666), None)
    with self.assertRaises(TypeError) as context:
      section(KV('', 'x'), None)
    
  def test___str__(self):
    values = KVL([ KV('x', '5'), KV('y', 'hi') ])
    header = KV('name', 'foo')
    s = section(header, values)
    self.assertEqual( 'name: foo\nx: 5\ny: hi', str(s) )

if __name__ == "__main__":
  unittest.main()
