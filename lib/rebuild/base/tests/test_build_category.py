#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base import build_category

class test_build_category(unit_test):

  def test_category_is_valid(self):
    self.assertTrue( build_category.is_valid('LIB') )
    self.assertTrue( build_category.is_valid('TOOL') )
    self.assertFalse( build_category.is_valid('XLIB') )
    self.assertTrue( build_category.is_valid(1) )
    self.assertTrue( build_category.is_valid(2) )
    self.assertFalse( build_category.is_valid(6) )

if __name__ == '__main__':
  unit_test.main()
