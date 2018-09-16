#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.pcloud import metadata as M

class test_metadata(unit_test):

  def test__init__(self):
    pass
    #self.assertEqual( 'foo >= 1.2.3', str(R('foo', '>=', '1.2.3')) )

if __name__ == "__main__":
  unit_test.main()
