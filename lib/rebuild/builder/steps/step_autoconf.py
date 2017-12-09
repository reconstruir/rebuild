#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check_type, Shell
from bes.key_value import key_value_list
from rebuild.step import compound_step, step, step_call_hooks, step_result
from rebuild.toolchain import toolchain

class step_autoconf_configure(step):
  'Configure Setup.'

  def __init__(self):
    super(step_autoconf_configure, self).__init__()

  @classmethod
  def argspec(clazz):
    return {
      'configure_flags': clazz.STRING_LIST,
      'configure_env': clazz.KEY_VALUES,
      'configure_script': clazz.STRING,
      'need_autoreconf': clazz.BOOL,
    }
    
  def execute(self, script, env, args):
    configure_flags = args.get('configure_flags', [])
    check_type.check_list(configure_flags, 'configure_flags')

    configure_env = args.get('configure_env', key_value_list())
    check_type.check_key_value_list(configure_env, 'configure_env')

    configure_script = args.get('configure_script', 'configure')

    need_autoreconf = args.get('need_autoreconf', False)
    if need_autoreconf:
      autoreconf_cmd = [ 'autoreconf', '-i' ]
    else:
      autoreconf_cmd = None

      tc = toolchain.get_toolchain(script.build_target)
      
    configure_script_path = path.join(script.source_unpacked_dir, configure_script)
    configure_cmd = [
      configure_script_path,
      '--prefix=%s' % (script.stage_dir),
    ] + configure_flags + tc.autoconf_flags()

    if autoreconf_cmd:
      cmd = autoreconf_cmd + [ '&&' ] + configure_cmd
    else:
      cmd = configure_cmd

    return self.call_shell(cmd, script, env, args,
                           extra_env = configure_env.to_dict(),
                           save_logs = [ 'config.log', 'config.status' ])

  @classmethod
  def parse_step_args(clazz, script, env, args):
    x =  clazz.resolve_step_args_env_and_flags(script, args, 'configure_env', 'configure_flags')
    print("clazz=%s; POOOOTOT: x=%s" % (clazz, str(x)))
    return clazz.resolve_step_args_env_and_flags(script, args, 'configure_env', 'configure_flags')

class step_autoconf_pre_configure_hooks(step_call_hooks):
  'Run hooks before configure.'
  __hook_names__ = 'pre_configure_hooks'
  def __init__(self):
    super(step_autoconf_pre_configure_hooks, self).__init__()

class step_autoconf_post_configure_hooks(step_call_hooks):
  'Run hooks before configure.'
  __hook_names__ = 'post_configure_hooks'
  def __init__(self):
    super(step_autoconf_post_configure_hooks, self).__init__()

class step_autoconf(compound_step):
  'A compound step for autoconf projects.'
  from .step_make import step_make, step_make_install
  from .step_setup import step_setup
  from .step_post_install import step_post_install
  
  __steps__ = [
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
