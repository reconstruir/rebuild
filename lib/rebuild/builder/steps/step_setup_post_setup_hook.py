#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step.step import step

class step_setup_post_setup_hook(step):
  'A step to run a hook right after the setup steps are done.'

  def __init__(self):
    super(step_setup_post_setup_hook, self).__init__()

  @classmethod
  def define_args(clazz):
    return 'post_setup_hooks hook'
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    return self.call_hooks(values.get('post_setup_hooks'), script, env)
  
