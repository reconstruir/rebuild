#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import Step, step_result
from rebuild import SystemEnvironment

class step_setup_prepare_environment(Step):
  'Prepare the environment.'

  def __init__(self):
    super(step_setup_prepare_environment, self).__init__()

  def execute(self, argument):
    # We want a clean environment for tools to work
    SystemEnvironment.path_reset()
    return step_result(True, None)
