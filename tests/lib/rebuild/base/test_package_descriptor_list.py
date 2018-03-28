#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base import package_descriptor as PD, package_descriptor_list as PDL

class test_package_descriptor_list(unit_test):

  def test___str__(self):

    l = PDL([
      PD('foo', '1.2.3-1'),
      PD('bar', '4.5.6'),
      PD('baz', '7.8.9'),
    ])
    self.assertEqual( 'foo-1.2.3-1\nbar-4.5.6\nbaz-7.8.9', str(l) )
            
            
if __name__ == "__main__":
  unit_test.main()
