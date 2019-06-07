#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common.check import check
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

  #@abstractmethod
  def execute(self, script, env, values, inputs):
    make_env = values.get('make_env')
    make_flags = values.get('make_flags') or []
    make_num_jobs = values.get('make_num_jobs')
    make_target = values.get('make_target')
    makefile = values.get('makefile')

    if make_num_jobs < 1:
      raise RuntimeError('make_num_jobs should be between 1 and %d instead of %s' % (self.MAX_NUM_JOBS, make_num_jobs))
    if make_num_jobs > 8:
      raise RuntimeError('make_num_jobs should be between 1 and %d instead of %s' % (self.MAX_NUM_JOBS, make_num_jobs))
    cmd = [ 'make', 'V=1', '-j', str(make_num_jobs) ]
    if makefile:
      cmd += [ '-f', path.basename(makefile.filename) ]

    cmd += make_flags
    cmd += self.extra_make_flags()
    if make_target:
      cmd += [ make_target ]
    
    return self.call_shell(cmd, script, env, shell_env = make_env)

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
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    makefile = values.get('makefile')
    install_target = values.get('install_target')
    make_install_flags = values.get('make_install_flags')
    make_install_env = values.get('make_install_env')

    if check.is_string_list(make_install_flags):
      make_install_flags = make_install_flags.to_list()
    else:
      assert isinstance(make_install_flags, list)
      
    if makefile:
      makefile_flags = '-f %s' % (path.basename(makefile.filename))
    else:
      makefile_flags = ''

    cmd = [
      'make',
      makefile_flags,
      install_target,
      'prefix=%s' % (script.staged_files_dir),
      'V=1',
    ] + make_install_flags
    return self.call_shell(cmd, script, env, shell_env = make_install_env)

class step_make_test(step):
  'make test phase of make.'

  def __init__(self):
    super(step_make_test, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    makefile         file
    make_test_flags  string_list
    make_test_env    key_values
    '''
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    make_test_flags = values.get('make_test_flags')
    make_test_env = values.get('make_test_env')
    makefile = values.get('makefile')

    if makefile:
      makefile_flags = '-f %s' % (path.basename(makefile.filename))
    else:
      makefile_flags = ''

    cmd = [
      'make',
      makefile_flags,
      'test',
      'V=1',
    ] + make_test_flags
    return self.call_shell(cmd, script, env, shell_env = make_test_env)

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
