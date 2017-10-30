#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from rebuild.step_manager import Step, step_result
from bes.common import Shell, string_util

class step_shell(Step):
  'A build step that is a shell command.'

  def __init__(self):
    super(step_shell, self).__init__()

  def execute(self, script, env, args):
    cmd = args.get('cmd', None)
    assert string_util.is_string(cmd)
    shell_env = args.get('shell_env', {})
    self.log_d('step_shell.execute() cmd=%s; shell_env=%s' % (cmd, shell_env))
    return self.call_shell(cmd, script, args, shell_env)

  @classmethod
  def parse_step_args(clazz, script, args):
    result = clazz.resolve_step_args_env_and_flags(script, args, 'shell_env', None)
    assert 'cmd' in args
    result['cmd'] = args['cmd']
    return result
