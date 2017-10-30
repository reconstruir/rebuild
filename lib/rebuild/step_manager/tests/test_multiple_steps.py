#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from test_steps import *
from rebuild.step_manager import multiple_steps, Step, step_argument

class test_multiple_steps(unittest.TestCase):

  def test_multi_step(self):

    class ThreeSteps(multiple_steps):
      step_classes = [ sample_step_save_args1, sample_step_save_args2, sample_step_save_args3 ]

    class TwoSteps(multiple_steps):
      step_classes = [ sample_step_save_args1, sample_step_save_args2 ]

    three_steps = ThreeSteps()

    script = { 'foo': 'hi', 'bar': 666 }
    global_args = { 'food': 'steak', 'drink': 'wine' }
    env = { 'fruit': 'kiwi' }
    result = three_steps.execute_caca(script, env, args = global_args)
    self.assertTrue( result.success )
    self.assertEqual( None, result.message )
    self.assertEqual( None, result.failed_step )

if __name__ == '__main__':
  unittest.main()
