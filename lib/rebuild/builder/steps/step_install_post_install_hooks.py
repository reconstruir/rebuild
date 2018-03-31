#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from rebuild.step import step

class step_install_post_install_hooks(step):
  'A step to run a hook right after the setup steps are done.'

  def __init__(self):
    super(step_install_post_install_hooks, self).__init__()

  @classmethod
  def define_args(clazz):
    return 'post_install_hooks hook_list'
    
  def execute(self, script, env, args):
    values = self.recipe.resolve_values(script.build_target.system)
    return self.call_hooks(values.get('post_install_hooks'), script, env, args)
