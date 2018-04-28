#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from rebuild.step import compound_step, step, step_result
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
    values = self.recipe.resolve_values(env.recipe_load_env)
    configure_env = values.get('configure_env')
    configure_flags = values.get('configure_flags') or []
    configure_script = values.get('configure_script')
    need_autoreconf = values.get('need_autoreconf')

    if check.is_string_list(configure_flags):
      configure_flags = configure_flags.to_list()
    else:
      assert isinstance(configure_flags, list)

    if need_autoreconf:
      autoreconf_cmd = [ 'autoreconf', '-i' ]
    else:
      autoreconf_cmd = None

    tc = toolchain.get_toolchain(script.build_target)
      
    configure_script_path = path.join(script.source_unpacked_dir, configure_script)
    configure_cmd = [
      configure_script_path,
      '--prefix=%s' % (script.staged_files_dir),
    ] + configure_flags + tc.autoconf_flags()

    if autoreconf_cmd:
      cmd = autoreconf_cmd + [ '&&' ] + configure_cmd
    else:
      cmd = configure_cmd

    return self.call_shell(cmd, script, env,
                           shell_env = configure_env,
                           save_logs = [ 'config.log', 'config.status' ])

class step_autoconf_pre_configure_hooks(step):
  'Run hooks before configure.'

  def __init__(self):
    super(step_autoconf_pre_configure_hooks, self).__init__()

  @classmethod
  def define_args(clazz):
    return 'pre_configure_hooks hook_list'
    
  def execute(self, script, env, args):
    values = self.recipe.resolve_values(env.recipe_load_env)
    return self.call_hooks(values.get('pre_configure_hooks'), script, env)

class step_autoconf_post_configure_hooks(step):
  'Run hooks before configure.'

  def __init__(self):
    super(step_autoconf_post_configure_hooks, self).__init__()

  @classmethod
  def define_args(clazz):
    return 'post_configure_hooks hook_list'
    
  def execute(self, script, env, args):
    values = self.recipe.resolve_values(env.recipe_load_env)
    return self.call_hooks(values.get('post_configure_hooks'), script, env)

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
