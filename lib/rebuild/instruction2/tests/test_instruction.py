#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.instruction2 import instruction2 as I

class test_instruction(unit_test):

  def test___str__(self):
    i = I('orange', { 'x': '5', 'y': 'hi' }, set([ 'fructose', 'fiber' ]))
    expected = '''\
orange
  x
    5
  y
    hi
  requires
    fiber
    fructose\
'''
    self.assertMultiLineEqual( expected, str(i) )

if __name__ == '__main__':
  unit_test.main()
