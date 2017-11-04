#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base import build_category

class test_build_category(unit_test):

  def test_category_is_valid(self):
    self.assertTrue( build_category.category_is_valid('lib') )
    self.assertFalse( build_category.category_is_valid('xlib') )

if __name__ == '__main__':
  unit_test.main()
