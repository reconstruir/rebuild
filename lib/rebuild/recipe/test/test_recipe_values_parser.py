#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild.recipe import recipe_values_parser as P
from bes.key_value import key_value as kv

class test_recipe_values_parser(unittest.TestCase):

  def test_empty(self):
    self.assertEqual( [ ], self._parse('') )
    
  def test_parse_simple(self):

    text = '''
name: foo
k1: v1
k2: v2 v2a v2b
    v2c v2d
k3: v3
'''
    self.assertEqual( [ kv('name', 'foo'), kv('k1', 'v1'), kv('k2', 'v2 v2a v2b v2c v2d'), kv('k3', 'v3') ],
                      self._parse(text) )

  def test_parse_two(self):
    text = '''
name: foo
k1: v1
k2: v2
k3: v3
name: bar
k4: v4
k5: v5
k6: v6
'''
    self.assertEqual( [ kv('name', 'foo'), kv('k1', 'v1'), kv('k2', 'v2'), kv('k3', 'v3'),
                        kv('name', 'bar'), kv('k4', 'v4'), kv('k5', 'v5'), kv('k6', 'v6') ],
                      self._parse(text) )

  def test_parse_with_quote(self):
    text = '''
name: foo
k1: v1
k2: v2="a b c"
k3: v3
'''
    self.assertEqual( [ kv('name', 'foo'), kv('k1', 'v1'), kv('k2', 'v2="a b c"'), kv('k3', 'v3') ],
                      self._parse(text) )


  def test_parse_with_parentesis(self):
    text = '''
name: foo
k1: v1 (p1)
k2: v2 (p2a,p2b)
k3: v3 (p3)
'''
    self.assertEqual( [ kv('name', 'foo'), kv('k1', 'v1 (p1)'), kv('k2', 'v2 (p2a,p2b)'), kv('k3', 'v3 (p3)') ],
                      self._parse(text) )


  @classmethod
  def _parse(self, text):
    return [ kv for kv in P.parse(text) ]
    
if __name__ == "__main__":
  unittest.main()
