#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import step, step_result
from bes.system import os_env

class step_setup_prepare_environment(step):
  'Prepare the environment.'

  def __init__(self):
    super(step_setup_prepare_environment, self).__init__()

  #@abstractmethod
  def execute(self, script, env, values, inputs):
    # We want a clean environment for tools to work
    os_env.path_reset()
    return step_result(True, None)
