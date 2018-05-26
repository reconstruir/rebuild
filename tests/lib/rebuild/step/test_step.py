#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.step import step, step_result

class test_step(unit_test):

  class TestStep(step):

    #@abstractmethod
    def execute(self, script, env, values, inputs):
      'Execute the step.'
      return self.result(True)

    def on_tag_changed(self):
      'Called when the tag changes.'
      pass

    @classmethod
    #@abstractmethod
    def define_args(clazz):
      'Return a list of arg specs.'
      return {}
    
  def test_test_step(self):
    s = self.TestStep()

  def test_test_arg_spec(self):
    s = self.TestStep()

if __name__ == '__main__':
  unit_test.main()
