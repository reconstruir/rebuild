#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.system.os_env import os_env
from bes.system.which import which
from bes.system.command_line import command_line
from bes.system.execute import execute

from rebuild.native_package_manager.native_package_manager_error import native_package_manager_error

class pkgutil(object):
  'Class to deal with the pkgutil executable.'
  
  @classmethod
  def call_pkgutil(clazz, args, cwd = None):
    exe = which.which('pkgutil')
    if not exe:
      raise native_package_manager_error('pkgutil not found')
    cmd = [ exe ] + command_line.parse_args(args)
    env = os_env.clone_current_env(d = {})
    rv = execute.execute(cmd,
                         env = env,
                         cwd = cwd,
                         stderr_to_stdout = True,
                         raise_error = False)
    if rv.exit_code != 0:
      cmd_flag = ' '.join(cmd)
      msg = 'pkgutil command failed: {}\n{}'.format(cmd_flag, rv.stdout)
      raise native_package_manager_error(msg)
    return rv
