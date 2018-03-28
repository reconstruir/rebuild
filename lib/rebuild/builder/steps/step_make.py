#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import compound_step, step, step_result

class step_make(step):
  'step to make something with make on unix (gnu or bsd).'

  DEFAULT_NUM_JOBS = 4
  MAX_NUM_JOBS = 8

  def __init__(self):
    super(step_make, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    makefile       file
    make_flags     string_list
    make_env       key_values
    make_target    string
    make_num_jobs  int           4
    '''
    
  def extra_make_flags(self):
    return []

  def execute(self, script, env, args):
    if self._recipe:
      values = self.recipe.resolve_values(env.config.build_target.system)
      makefile = values.get('makefile')
      make_flags = values.get('make_flags')
      make_env = values.get('make_env')
      make_target = values.get('make_target')
      make_flags = values.get('make_flags')
      make_env = values.get('make_env')
      make_num_jobs = values.get('make_num_jobs')
    else:
      makefile = args.get('makefile', None)
      make_flags = args.get('make_flags', [])
      make_num_jobs = int(args.get('make_num_jobs', self.DEFAULT_NUM_JOBS))
      make_target = args.get('make_target', None)
      make_flags = self.args_get_string_list(args, 'make_flags')
      make_env = self.args_get_key_value_list(args, 'make_env')
      
    if make_num_jobs < 1:
      raise RuntimeError('make_num_jobs should be between 1 and %d instead of %s' % (self.MAX_NUM_JOBS, make_num_jobs))
    if make_num_jobs > 8:
      raise RuntimeError('make_num_jobs should be between 1 and %d instead of %s' % (self.MAX_NUM_JOBS, make_num_jobs))
    cmd = [ 'make', 'V=1', '-j', str(make_num_jobs) ]
    if makefile:
      cmd += [ '-f', makefile ]

    cmd += make_flags
    cmd += self.extra_make_flags()
    if make_target:
      cmd += [ make_target ]
    
    return self.call_shell(cmd, script, env, args, extra_env = make_env)

  @classmethod
  def parse_step_args(clazz, script, env, args):
    return clazz.resolve_step_args_env_and_flags(script, args, 'make_env', 'make_flags')

class step_make_install(step):
  'make install phase of make.'

  def __init__(self):
    super(step_make_install, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    makefile             file
    make_install_flags   string_list
    make_install_env     key_values
    install_target       string       install
    '''
    
  def execute(self, script, env, args):
    if self._recipe:
      values = self.recipe.resolve_values(env.config.build_target.system)
      makefile = values.get('makefile')
      install_target = values.get('install_target')
      make_install_flags = values.get('make_install_flags').to_list()
      make_install_env = values.get('make_install_env')
    else:
      makefile = args.get('makefile', None)
      install_target = args.get('install_target', 'install')
      make_install_flags = self.args_get_string_list(args, 'make_install_flags').to_list()
      make_install_env = self.args_get_key_value_list(args, 'make_install_env')
    
    makefile = args.get('makefile', None)
    if makefile:
      makefile_flags = '-f %s' % (makefile)
    else:
      makefile_flags = ''

    cmd = [
      'make',
      makefile_flags,
      install_target,
      'prefix=%s' % (script.stage_dir),
      'V=1',
    ] + make_install_flags
    return self.call_shell(cmd, script, env, args, extra_env = self.args_get_key_value_list(args, 'make_install_env'))

  @classmethod
  def parse_step_args(clazz, script, env, args):
    return clazz.resolve_step_args_env_and_flags(script, args, 'make_install_env', 'make_install_flags')

class step_make_test(step):
  'make test phase of make.'

  def __init__(self):
    super(step_make_test, self).__init__()

  def execute(self, script, env, args):
    make_test_flags = args.get('make_test_flags', [])

    makefile = args.get('makefile', None)
    if makefile:
      makefile_flags = '-f %s' % (makefile)
    else:
      makefile_flags = ''

    cmd = [
      'make',
      makefile_flags,
      'test',
      'V=1',
    ] + make_test_flags
    return self.call_shell(cmd, script, env, args, extra_env = self.args_get_key_value_list(args, 'make_test_env'))

  @classmethod
  def parse_step_args(clazz, script, env, args):
    return clazz.resolve_step_args_env_and_flags(script, args, 'make_test_env', 'make_test_flags')

class step_make_caca(compound_step):
  'A simple uber step for autoconf projects.'
  from .step_setup import step_setup
  from .step_post_install import step_post_install
  
  __steps__ = [
    step_setup,
    step_make,
    step_make_install,
    step_post_install,
  ]
  def __init__(self):
    super(step_make_caca, self).__init__()
