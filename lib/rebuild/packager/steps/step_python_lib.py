#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.step_manager import multiple_steps, Step, step_result
from bes.python import setup_tools

class step_python_lib_build(Step):
  'A step to do the "build" target of setuptools.'

  def __init__(self):
    super(step_python_lib_build, self).__init__()

  def execute(self, script, env, args):
    cmd = '${PYTHON} setup.py build %s' % (args.get('python_lib_build_flags', ''))
    return self.call_shell(cmd, script, args, args.get('python_lib_build_env', {}))

  @classmethod
  def parse_step_args(clazz, script, args):
    return clazz.resolve_step_args_env_and_flags(script, args, 'python_lib_build_env', 'python_lib_build_flags')

class step_python_lib_install(Step):
  'Install the dist produced by setuptools install.'

  def __init__(self):
    super(step_python_lib_install, self).__init__()

  def execute(self, script, env, args):
    cmd = 'mkdir -p ${REBUILD_STAGE_PYTHON_LIB_DIR} && ${PYTHON} setup.py install --home=${REBUILD_STAGE_PREFIX_DIR} --install-lib=${REBUILD_STAGE_PYTHON_LIB_DIR} %s' % (args.get('python_lib_install_flags', ''))
    return self.call_shell(cmd, script, args, args.get('python_lib_install_env', {}))

  @classmethod
  def parse_step_args(clazz, script, args):
    return clazz.resolve_step_args_env_and_flags(script, args, 'python_lib_install_env', 'python_lib_install_flags')

class step_python_lib(multiple_steps):
  'A complete step to make python libs using the "build" target of setuptools.'
  from .step_setup import step_setup
  from .step_post_install import step_post_install

  __step_global_args__ = {
    'copy_source_to_build_dir': True,
  }

  step_classes = [
    step_setup,
    step_python_lib_build,
    step_python_lib_install,
    step_post_install,
  ]
  def __init__(self):
    super(step_python_lib, self).__init__()
