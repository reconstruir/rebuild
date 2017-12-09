#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from rebuild.step import step, step_result
from bes.common import Shell, string_util

class step_shell(step):
  'A build step that is a shell command.'

  def __init__(self):
    super(step_shell, self).__init__()

  def execute(self, script, env, args):
    cmd = args.get('cmd', None)
    assert string_util.is_string(cmd)
    shell_env = self.args_get_key_value_list(args, 'shell_env')
    self.log_d('step_shell.execute() cmd=%s; shell_env=%s' % (cmd, shell_env))
    return self.call_shell(cmd, script, env, args, extra_env = shell_env)

  @classmethod
  def parse_step_args(clazz, script, env, args):
    result = clazz.resolve_step_args_env_and_flags(script, args, 'shell_env', None)
    assert 'cmd' in args
    result['cmd'] = args['cmd']
    return result
