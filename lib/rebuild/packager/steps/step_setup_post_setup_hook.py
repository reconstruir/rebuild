#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import Step

class step_setup_post_setup_hook(Step):
  'A step to run a hook right after the setup steps are done.'

  def __init__(self):
    super(step_setup_post_setup_hook, self).__init__()

  def execute(self, argument):
    return self.call_hooks(argument, 'post_setup_hooks')

  @classmethod
  def parse_step_args(clazz, script, args):
    return clazz.resolve_step_args_hooks(script, args, 'post_setup_hooks')
