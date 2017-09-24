#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild.instruction import instruction as I

class test_instruction(unittest.TestCase):

  def test___str__(self):
    i = I('foo', { 'x': '5', 'y': 'hi' }, set([ 'bar' ]))
    self.assertEqual( 'name: foo\nx: 5\ny: hi\nrequires: bar', str(i) )

if __name__ == "__main__":
  unittest.main()
