#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild.step_manager import Step

class test_step(unittest.TestCase):

  def test_blurb(self):
    s = Step()
    #s.blurb('foo')

if __name__ == '__main__':
  unittest.main()
