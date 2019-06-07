#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import step, step_result
from bes.common.check import check

class step_shell(step):
  'A build step that is a shell command.'

  def __init__(self):
    super(step_shell, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    cmd   string
    shell_env     key_values
    '''
  
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    shell_env = values.get('shell_env')
    cmd = values.get('cmd')
    check.check_string(cmd)
    self.log_d('step_shell.execute() cmd=%s; shell_env=%s' % (cmd, shell_env))
    return self.call_shell(cmd, script, env, shell_env = shell_env)
