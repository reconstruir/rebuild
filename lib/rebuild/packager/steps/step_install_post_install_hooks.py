#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import Step

class step_install_post_install_hooks(Step):
  'A step to run a hook right after the setup steps are done.'

  def __init__(self):
    super(step_install_post_install_hooks, self).__init__()

  def execute_caca(self, script, env, args):
    return self.call_hooks(script, env, args, 'post_install_hooks')

  @classmethod
  def parse_step_args(clazz, script, args):
    return clazz.resolve_step_args_hooks(script, args, 'post_install_hooks')
