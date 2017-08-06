#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild.recipe import recipe_section_parser as P
from rebuild.recipe import recipe_section as C
from bes.key_value import key_value as KV
from bes.key_value import key_value_list as KVL

class test_recipe_section_parser(unittest.TestCase):

  def test_empty(self):
    self.assertEqual( [], self._parse('', 'name') )
    
  def test_parse_simple(self):
    text = '''
name: foo
k1: v1
k2: v2 v2a v2b
v2c v2d
k3: v3
'''
    expected = [
      C(KV('name', 'foo'), KVL([KV('k1', 'v1'), KV('k2', 'v2 v2a v2b v2c v2d'), KV('k3', 'v3')]))
    ]
    self.assertEqual( expected, self._parse(text, 'name') )

  def test_parse_two(self):
    text = '''
name: foo
k1: v1
k2: v2 v2a v2b
v2c v2d
k3: v3
name: bar
k1: v1
k2: v2
k3: v3
'''
    expected = [
      C(KV('name', 'foo'), KVL([KV('k1', 'v1'), KV('k2', 'v2 v2a v2b v2c v2d'), KV('k3', 'v3')])),
      C(KV('name', 'bar'), KVL([KV('k1', 'v1'), KV('k2', 'v2'), KV('k3', 'v3')])),
    ]
    self.assertEqual( expected, self._parse(text, 'name') )

  @classmethod
  def _parse(self, text, header_key):
    return [ i for i in P.parse(text, header_key) ]
    
if __name__ == "__main__":
  unittest.main()
