#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from test_steps import *
from rebuild.step.compound_step import compound_step
from bes.debug.debug_timer import debug_timer

class test_compound_step(unittest.TestCase):

  def xtest_multi_step(self):

    class ThreeSteps(compound_step):
      __steps__ = [ sample_step_save_args1, sample_step_save_args2, sample_step_save_args3 ]

    class TwoSteps(compound_step):
      __steps__ = [ sample_step_save_args1, sample_step_save_args2 ]

    three_steps = ThreeSteps()

    class script(object):
      def __init__(self):
        self.timer = debug_timer('test_compound_step', 'info')
    
    common_args = { 'food': 'steak', 'drink': 'wine' }
    env = { 'fruit': 'kiwi' }
    result = three_steps.execute(script(), env, args = common_args)
    self.assertTrue( result.success )
    self.assertEqual( None, result.message )
    self.assertEqual( None, result.failed_step )

if __name__ == '__main__':
  unittest.main()
