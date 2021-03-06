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

if __name__ == '__main__':
  unittest.main()
