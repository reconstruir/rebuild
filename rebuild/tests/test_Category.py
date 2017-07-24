#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild import Category

class TestCategory(unittest.TestCase):

  def test_category_is_valid(self):
    self.assertTrue( Category.category_is_valid('lib') )
    self.assertFalse( Category.category_is_valid('xlib') )

if __name__ == '__main__':
  unittest.main()
