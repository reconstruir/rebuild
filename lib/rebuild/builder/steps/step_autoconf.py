#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check_type, Shell
from rebuild.step import compound_step, step, step_call_hooks, step_result
from rebuild.toolchain import toolchain

class step_autoconf_configure(step):

  def __init__(self):
    super(step_autoconf_configure, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    configure_flags   string_list
    configure_env     key_values
    configure_script  string      configure
    need_autoreconf   bool        False
    '''
    
  def execute(self, script, env, args):
    '''
    if False and script.recipe.format_version == 2:
      print('CACA: RECIPE VERSION: %s' % (script.recipe.format_version))
      print('CACA: build_target: %s' % (str(script.build_target)))
      print('CACA: step recipe: %s' % (str(self.recipe.name)))
      caca_values = self.recipe.resolve_values(script.build_target.system)
      print('CACA: values: %s' % (str(caca_values)))
      #caca_configure_env = self.recipe.resolve_values(script.build_target)
    '''
    configure_flags = self.args_get_list(args, 'configure_flags')
    configure_env = self.args_get_key_value_list(args, 'configure_env')

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
                           extra_env = configure_env,
                           save_logs = [ 'config.log', 'config.status' ])

  @classmethod
  def parse_step_args(clazz, script, env, args):
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
