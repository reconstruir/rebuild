#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import Shell
from rebuild.step_manager import multiple_steps, Step, step_result

class step_make(Step):
  'step to make something with make on unix (gnu or bsd).'

  DEFAULT_NUM_JOBS = 4
  MAX_NUM_JOBS = 8

  def __init__(self):
    super(step_make, self).__init__()

  def extra_make_flags(self):
    return []

  def execute(self, argument):
    makefile = argument.args.get('makefile', None)
    make_flags = argument.args.get('make_flags', [])
    make_num_jobs = int(argument.args.get('make_num_jobs', self.DEFAULT_NUM_JOBS))
    if make_num_jobs < 1:
      raise RuntimeError('make_num_jobs should be between 1 and %d instead of %s' % (self.MAX_NUM_JOBS, make_num_jobs))
    if make_num_jobs > 8:
      raise RuntimeError('make_num_jobs should be between 1 and %d instead of %s' % (self.MAX_NUM_JOBS, make_num_jobs))
    cmd = [ 'make', 'V=1', '-j', str(make_num_jobs) ]
    if makefile:
      cmd += [ '-f', makefile ]

    cmd += make_flags
    cmd += self.extra_make_flags()
      
    return self.call_shell(cmd, argument.script, argument.args, extra_env = argument.args.get('make_env', {}))

  @classmethod
  def parse_step_args(clazz, script, args):
    return clazz.resolve_step_args_env_and_flags(script, args, 'make_env', 'make_flags')

class step_make_install(Step):
  'make install phase of make.'

  def __init__(self):
    super(step_make_install, self).__init__()

  def execute(self, argument):
    install_target = argument.args.get('install_target', 'install')
    make_install_flags = argument.args.get('make_install_flags', [])

    makefile = argument.args.get('makefile', None)
    if makefile:
      makefile_flags = '-f %s' % (makefile)
    else:
      makefile_flags = ''

    cmd = [
      'make',
      makefile_flags,
      install_target,
      'prefix=%s' % (argument.script.stage_dir),
      'V=1',
    ] + make_install_flags
    return self.call_shell(cmd, argument.script, argument.args, extra_env = argument.args.get('make_install_env', {}))

  @classmethod
  def parse_step_args(clazz, script, args):
    return clazz.resolve_step_args_env_and_flags(script, args, 'make_install_env', 'make_install_flags')

class step_make_test(Step):
  'make test phase of make.'

  def __init__(self):
    super(step_make_test, self).__init__()

  def execute(self, argument):
    make_test_flags = argument.args.get('make_test_flags', [])

    makefile = argument.args.get('makefile', None)
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
    return self.call_shell(cmd, argument.script, argument.args, extra_env = argument.args.get('make_test_env', {}))

  @classmethod
  def parse_step_args(clazz, script, args):
    return clazz.resolve_step_args_env_and_flags(script, args, 'make_test_env', 'make_test_flags')

class step_make_caca(multiple_steps):
  'A simple uber step for autoconf projects.'
  from .step_setup import step_setup
  from .step_post_install import step_post_install
  
  step_classes = [
    step_setup,
    step_make,
    step_make_install,
    step_post_install,
  ]
  def __init__(self):
    super(step_make_caca, self).__init__()
