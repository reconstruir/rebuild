#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base import build_level

class test_build_level(unit_test):

  def test_build_level_is_valid(self):
    self.assertTrue( build_level.build_level_is_valid('release') )
    self.assertTrue( build_level.build_level_is_valid('debug') )
    self.assertFalse( build_level.build_level_is_valid('optimized') )
    
  def test_parse_build_level(self):
    self.assertEqual( build_level.RELEASE, build_level.parse_build_level('release') )
    self.assertEqual( build_level.RELEASE, build_level.parse_build_level('default') )
    
if __name__ == '__main__':
  unit_test.main()
