#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.pcloud import metadata as M

class test_metadata(unit_test):

  def test_category(self):
    self.assertEqual( 'image', M('foo.jpg', False, 42, 'image', 'image/jpeg', 666, None).category )
    self.assertEqual( 'image', M('foo.jpg', False, 42, 1, 'image/jpeg', 666, None).category )

if __name__ == "__main__":
  unit_test.main()
