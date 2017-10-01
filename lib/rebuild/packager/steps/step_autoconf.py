#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import Shell
from rebuild.step_manager import multiple_steps, Step, step_call_hooks, step_result

class step_autoconf_configure(Step):
  'Configure Setup.'

  def __init__(self):
    super(step_autoconf_configure, self).__init__()

  def execute(self, argument):

    configure_flags = argument.args.get('configure_flags', [])
    assert isinstance(configure_flags, list)

    configure_env = argument.args.get('configure_env', {})
    assert isinstance(configure_env, dict)

    configure_script = argument.args.get('configure_script', 'configure')

    need_autoreconf = argument.args.get('need_autoreconf', False)
    if need_autoreconf:
      autoreconf_cmd = [ 'autoreconf', '-i' ]
    else:
      autoreconf_cmd = None
      
    configure_script_path = path.join(argument.env.source_unpacked_dir, configure_script)
    configure_cmd = [
      configure_script_path,
      '--prefix=%s' % (argument.env.stage_dir),
    ] + configure_flags

    if autoreconf_cmd:
      cmd = autoreconf_cmd + [ '&&' ] + configure_cmd
    else:
      cmd = configure_cmd

    return self.call_shell(cmd, argument.env, argument.args, configure_env,
                           save_logs = [ 'config.log', 'config.status' ])

  @classmethod
  def parse_step_args(clazz, packager_env, args):
    return clazz.resolve_step_args_env_and_flags(packager_env, args, 'configure_env', 'configure_flags')

class step_autoconf_pre_configure_hooks(step_call_hooks):
  'Run hooks before configure.'
  HOOKS_NAMES = 'pre_configure_hooks'
  def __init__(self):
    super(step_autoconf_pre_configure_hooks, self).__init__()

class step_autoconf_post_configure_hooks(step_call_hooks):
  'Run hooks before configure.'
  HOOKS_NAMES = 'post_configure_hooks'
  def __init__(self):
    super(step_autoconf_post_configure_hooks, self).__init__()

class step_autoconf(multiple_steps):
  'A simple uber step for autoconf projects.'
  from .step_make import step_make, step_make_install
  from .step_setup import step_setup
  from .step_post_install import step_post_install
  
  step_classes = [
    step_setup,
    step_autoconf_pre_configure_hooks,
    step_autoconf_configure,
    step_autoconf_post_configure_hooks,
    step_make,
    step_make_install,
    step_post_install,
  ]
  def __init__(self):
    super(step_autoconf, self).__init__()
