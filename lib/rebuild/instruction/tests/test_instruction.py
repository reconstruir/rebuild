#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.instruction import instruction as I

class test_instruction(unit_test):

  def test___str__(self):
    i = I('foo', { 'x': '5', 'y': 'hi' }, set([ 'bar' ]))
    self.assertEqual( 'name: foo\nx: 5\ny: hi\nrequires: bar', str(i) )

if __name__ == '__main__':
  unit_test.main()
