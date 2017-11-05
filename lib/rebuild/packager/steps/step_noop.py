#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import step, step_result

class step_noop(step):
  'step_noop'

  def __init__(self):
    super(step_noop, self).__init__()

  def execute(self, script, env, args):
    return step_result(True)
