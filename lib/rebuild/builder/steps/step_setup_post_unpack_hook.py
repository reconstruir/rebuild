#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import step

class step_setup_post_unpack_hook(step):
  'A step to run a hook right after the unpack step is done.'

  def __init__(self):
    super(step_setup_post_unpack_hook, self).__init__()

  def execute(self, script, env, args):
    return self.call_hooks(script, env, args, 'post_unpack_hooks')

  @classmethod
  def parse_step_args(clazz, script, env, args):
    return clazz.resolve_step_args_hooks(script, args, 'post_unpack_hooks')