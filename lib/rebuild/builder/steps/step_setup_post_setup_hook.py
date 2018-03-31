#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import step

class step_setup_post_setup_hook(step):
  'A step to run a hook right after the setup steps are done.'

  def __init__(self):
    super(step_setup_post_setup_hook, self).__init__()

  @classmethod
  def define_args(clazz):
    return 'post_setup_hooks hook_list'
    
  def execute(self, script, env, args):
    values = self.recipe.resolve_values(script.build_target.system)
    return self.call_hooks(values.get('post_setup_hooks'), script, env, args)
  
