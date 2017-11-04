#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base import build_type

class test_build_type(unit_test):

  def test_build_type_is_valid(self):
    self.assertTrue( build_type.build_type_is_valid('release') )
    self.assertTrue( build_type.build_type_is_valid('debug') )
    self.assertFalse( build_type.build_type_is_valid('optimized') )
    
  def test_parse_build_type(self):
    self.assertEqual( build_type.RELEASE, build_type.parse_build_type('release') )
    self.assertEqual( build_type.RELEASE, build_type.parse_build_type('default') )
    
if __name__ == '__main__':
  unit_test.main()
