#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild.step import step, step_description

class test_step_description(unittest.TestCase):

  class sample_step_save_args1(step):
    def __init__(self):
      super(test_step_description.sample_step_save_args1, self).__init__()
    def execute(self, args):
      return step_result(True, None)
    def on_tag_changed(self):
      pass

  class sample_step_save_args2(step):
    def __init__(self):
      super(test_step_description.sample_step_save_args2, self).__init__()
    def execute(self, args):
      return step_result(True, None)
    def on_tag_changed(self):
      pass

  class sample_step_save_args3(step):
    def __init__(self):
      super(test_step_description.sample_step_save_args3, self).__init__()
    def execute(self, args):
      return step_result(True, None)
    def on_tag_changed(self):
      pass

  class test_step4(step):
    def __init__(self):
      super(test_step_description.test_step4, self).__init__()
    def execute(self, args):
      return step_result(True, None)
    def on_tag_changed(self):
      pass

  def test_parse_descriptions(self):
    items = [
      'sample_step_save_args1',
      'sample_step_save_args2', { 'num': 666, 's': 'foo' },
      'sample_step_save_args3',
      'test_step4', { 'num': 500, 's': 'hi' },
    ]

    descriptions = step_description.parse_descriptions(items)

    self.assertEqual( step_description(self.sample_step_save_args1, {}), descriptions[0] )
    self.assertEqual( step_description(self.sample_step_save_args2, { 'num': 666, 's': 'foo' }), descriptions[1] )
    self.assertEqual( step_description(self.sample_step_save_args3, {}), descriptions[2] )
    self.assertEqual( step_description(self.test_step4, { 'num': 500, 's': 'hi' }), descriptions[3] )

if __name__ == '__main__':
  unittest.main()
