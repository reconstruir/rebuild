#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild.step import step, step_result

class test_step(unittest.TestCase):

  class TestStep(step):
    def execute(self, argument):
      'Execute the step.'
      return step_result(True, '')

    def on_tag_changed(self):
      'Called when the tag changes.'
      pass

  def test_test_step(self):
    s = self.TestStep()

if __name__ == '__main__':
  unittest.main()
