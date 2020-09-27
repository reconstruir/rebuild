#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.system.os_env import os_env
from bes.system.which import which
from bes.system.command_line import command_line
from bes.system.execute import execute

from .sudo_error import sudo_error

class sudo_exe(object):
  'Class to deal with the sudo_exe executable.'
  
  @classmethod
  def call_sudo(clazz, args, cwd = None, msg = None, prompt = None):
    exe = which.which('sudo')
    if not exe:
      raise sudo_error('sudo not found')
    cmd = [ exe ]
    if prompt:
      cmd.extend( ['--prompt', prompt] )
    cmd.extend(command_line.parse_args(args))
    env = os_env.clone_current_env(d = {})
    rv = execute.execute(cmd,
                         env = env,
                         cwd = cwd,
                         stderr_to_stdout = True,
                         raise_error = False)
    if rv.exit_code != 0:
      if not msg:
        cmd_flag = ' '.join(cmd)
        msg = 'sudo_exe command failed: {}\n{}'.format(cmd_flag, rv.stdout)
      raise sudo_error(msg)
    return rv

  @classmethod
  def validate(clazz, cwd = None, msg = None, prompt = 'sudo password: '):
    clazz.call_sudo('--validate', cwd = cwd, msg = msg, prompt = prompt)
