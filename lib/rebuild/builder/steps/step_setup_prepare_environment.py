#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import step, step_result
from rebuild.base import build_os_env

class step_setup_prepare_environment(step):
  'Prepare the environment.'

  def __init__(self):
    super(step_setup_prepare_environment, self).__init__()

  def execute(self, script, env, args):
    # We want a clean environment for tools to work
    build_os_env.path_reset()
    return step_result(True, None)
