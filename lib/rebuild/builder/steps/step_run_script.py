#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.step import step, step_result
from rebuild.tools import patch

class step_run_script(step):
  'Run a script.'

  def __init__(self):
    super(step_run_script, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    script file
    script_env key_values
    '''
    
  def execute(self, script, env, args):
    values = self.recipe.resolve_values(env.config.build_target.system)
    script_file = values.get('script')
    script_env = values.get('script_env')
      
    if not script_file:
      message = 'No script for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    return self.call_shell(path.abspath(script_file.filename), script, env, shell_env = script_env)
