#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, sys
from bes.common import check
from rebuild.step import compound_step, step, step_result
from .step_make import step_make

class step_cmake_configure(step):
  'Configure Setup.'

  def __init__(self):
    super(step_cmake_configure, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    cmake_flags   string_list
    cmake_env     key_values
    '''
    
  def execute(self, script, env, args):
    values = self.recipe.resolve_values(env.config.build_target.system)
    cmake_env = values.get('cmake_env')
    cmake_flags = values.get('cmake_flags')

    if check.is_string_list(cmake_flags):
      cmake_flags = cmake_flags.to_list()
    else:
      assert isinstance(cmake_flags, list)

    cmd = [ 'cmake' ]
    if env.config.verbose:
      cmd.append('--debug-output')
    cmd.append('-DCMAKE_INSTALL_PREFIX=$REBUILD_STAGE_PREFIX_DIR')
    cmd.extend(cmake_flags)
    cmd.append(script.source_unpacked_dir)
    return self.call_shell(cmd, script, env, args, extra_env = cmake_env,
                           save_logs = [ 'CMakeFiles/CMakeError.log', 'CMakeFiles/CMakeOutput.log' ])

class step_cmake_make(step_make):
  'step to build with cmake.  same as step_make with some extra flags'

  def __init__(self):
    super(step_cmake_make, self).__init__()

  def extra_make_flags(self):
    return [ 'VERBOSE=1' ]

class step_cmake_install(step):
  'Configure Install.'

  def __init__(self):
    super(step_cmake_install, self).__init__()

  def execute(self, script, env, args):
    cmd = 'make install prefix=$REBUILD_STAGE_PREFIX_DIR'
    return self.call_shell(cmd, script, env, args)

class step_cmake(compound_step):
  'A complete step to build cmake projects.'
  from .step_make import step_make
  from .step_setup import step_setup
  from .step_post_install import step_post_install
  
  __steps__ = [
    step_setup,
    step_cmake_configure,
    step_cmake_make,
    step_cmake_install,
    step_post_install,
  ]
  def __init__(self):
    super(step_cmake, self).__init__()
