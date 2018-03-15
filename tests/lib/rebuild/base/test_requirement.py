#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base import requirement as R

class test_requirement(unit_test):

  def test___str__(self):
    self.assertEqual( 'foo >= 1.2.3', str(R('foo', '>=', '1.2.3')) )
    self.assertEqual( 'orange >= 6.6.6', str(R('orange', '>=', '6.6.6')) )

  def test___str__with_system(self):
    self.assertEqual( 'foo(linux) >= 1.2.3', str(R('foo', '>=', '1.2.3', 'linux')) )
    self.assertEqual( 'orange >= 6.6.6', str(R('orange', '>=', '6.6.6', 'all')) )

  def test_to_string_colon_format(self):
    self.assertEqual( 'all: foo >= 1.2.3', R('foo', '>=', '1.2.3', None).to_string_colon_format() )
    
  def clone_replace_hardness(self):
    r1 = R('foo', '>=', '1.2.3', 'linux', 'RUN')
    r2 = r1.clone_replace_hardness(self, 'BUILD')
    self.assertEqual( 'RUN', str(r1.hardness) )
    self.assertEqual( 'BUILD', str(r2.hardness) )
    
if __name__ == "__main__":
  unit_test.main()
