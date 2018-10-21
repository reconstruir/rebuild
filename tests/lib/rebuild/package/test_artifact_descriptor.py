#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.package import artifact_descriptor as AD

class test_artifact_descriptor(unit_test):

  def test_full_name(self):
    self.assertEqual( 'foo-1.2.3', AD('foo', '1.2.3', 0, 0, 'linux', 'debug', ( 'x86_64', ), '', '').full_name )
    self.assertEqual( 'foo-1.2.3-1', AD('foo', '1.2.3', 1, 0, 'linux', 'debug', ( 'x86_64', ), '', '').full_name )
    self.assertEqual( 'foo-1:1.2.3-1', AD('foo', '1.2.3', 1, 1, 'linux', 'debug', ( 'x86_64', ), '', '').full_name )

  def test_clone_with_mutation(self):
    a = AD('foo', '1.2.3', 0, 0, 'linux', 'debug', 'x86_64', '', '')
    b = a.clone_with_mutation('name', 'bar')

    self.assertEqual( 'foo', a.name )
    self.assertEqual( 'bar', b.name )
    la = list(a)
    la.pop(a._fields.index('name'))
    lb = list(b)
    lb.pop(b._fields.index('name'))
    self.assertEqual( la, lb )
    
if __name__ == '__main__':
  unit_test.main()
