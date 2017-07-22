#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, sys
from bes.common import Shell
from rebuild.step_manager import multiple_steps, Step, step_result
from rebuild.pkg_config import pkg_config
from step_make import step_make

class step_cmake_configure(Step):
  'Configure Setup.'

  def __init__(self):
    super(step_cmake_configure, self).__init__()

  def execute(self, argument):
    cmake_flags = argument.args.get('cmake_flags', [])
    assert isinstance(cmake_flags, list)

    cmake_env = argument.args.get('cmake_env', {})
    assert isinstance(cmake_env, dict)

    cmd = [ 'cmake' ]
    if argument.args.get('verbose', False):
      cmd.append('--debug-output')
    cmd.append('-DCMAKE_INSTALL_PREFIX=$REBUILD_STAGE_PREFIX_DIR')
    cmd.extend(cmake_flags)
    cmd.append(argument.env.source_unpacked_dir)
    return self.call_shell(cmd, argument.env, argument.args, extra_env = cmake_env,
                           save_logs = [ 'CMakeFiles/CMakeError.log', 'CMakeFiles/CMakeOutput.log' ])

  @classmethod
  def parse_step_args(clazz, packager_env, args):
    return clazz.resolve_step_args_env_and_flags(packager_env, args, 'cmake_env', 'cmake_flags')

class step_cmake_make(step_make):
  'step to build with cmake.  same as step_make with some extra flags'

  def __init__(self):
    super(step_cmake_make, self).__init__()

  def extra_make_flags(self):
    return [ 'VERBOSE=1' ]

class step_cmake_install(Step):
  'Configure Install.'

  def __init__(self):
    super(step_cmake_install, self).__init__()

  def execute(self, argument):
    cmd = 'make install prefix=$REBUILD_STAGE_PREFIX_DIR'
    return self.call_shell(cmd, argument.env, argument.args, None)

class step_cmake(multiple_steps):
  'A complete step to build cmake projects.'
  from step_make import step_make
  from step_setup import step_setup
  from step_post_install import step_post_install
  
  step_classes = [
    step_setup,
    step_cmake_configure,
    step_cmake_make,
    step_cmake_install,
    step_post_install,
  ]
  def __init__(self):
    super(step_cmake, self).__init__()
