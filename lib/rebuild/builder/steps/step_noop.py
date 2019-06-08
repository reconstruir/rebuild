#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step.step import step
from rebuild.step.step_result import step_result

class step_noop(step):
  'step_noop'

  def __init__(self):
    super(step_noop, self).__init__()

  #@abstractmethod
  def execute(self, script, env, values, inputs):
    return step_result(True)
