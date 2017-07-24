#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild import build_type

class test_build_type(unittest.TestCase):

  def test_build_type_is_valid(self):
    self.assertTrue( build_type.build_type_is_valid('release') )
    self.assertTrue( build_type.build_type_is_valid('debug') )
    self.assertFalse( build_type.build_type_is_valid('optimized') )
    
  def test_parse_build_type(self):
    self.assertEqual( build_type.RELEASE, build_type.parse_build_type('release') )
    self.assertEqual( build_type.RELEASE, build_type.parse_build_type('default') )
    
if __name__ == '__main__':
  unittest.main()
