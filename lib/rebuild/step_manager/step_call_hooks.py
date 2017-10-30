#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .Step import Step
from .Step import step_result

class step_call_hooks(Step):
  'A superclass for steps that call hooks.'

  def __init__(self):
    super(step_call_hooks, self).__init__()

  def execute(self, script, env, args):
    return self.call_hooks(script, env, args, self.HOOKS_NAMES)

  @classmethod
  def parse_step_args(clazz, packager_env, args):
    return clazz.resolve_step_args_list(packager_env, args, clazz.HOOKS_NAMES)
