#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.step.compound_step import compound_step
from rebuild.step.step import step
from rebuild.step.step_result import step_result
from bes.python.setup_tools import setup_tools

class step_python_lib_build(step):
  'A step to do the "build" target of setuptools.'

  def __init__(self):
    super(step_python_lib_build, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    python_lib_build_flags   string_list
    python_lib_build_env     key_values
    setup_dir           string
    '''

  #@abstractmethod
  def execute(self, script, env, values, inputs):
    python_lib_build_env = values.get('python_lib_build_env')
    python_lib_build_flags = values.get('python_lib_build_flags')
    setup_dir = values.get('setup_dir')
    cmd = '${PYTHON} setup.py build %s' % (' '.join(python_lib_build_flags))
    return self.call_shell(cmd, script, env, shell_env = python_lib_build_env, execution_dir = setup_dir)

class step_python_lib_install(step):
  'Install the dist produced by setuptools install.'

  def __init__(self):
    super(step_python_lib_install, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    python_lib_install_flags   string_list
    python_lib_install_env     key_values
    setup_dir           string
    '''

  #@abstractmethod
  def execute(self, script, env, values, inputs):
    python_lib_install_env = values.get('python_lib_install_env')
    python_lib_install_flags = values.get('python_lib_install_flags')
    setup_dir = values.get('setup_dir')

    cmd = 'mkdir -p ${REBUILD_STAGE_PYTHON_LIB_DIR} && ${PYTHON} setup.py install --home=${REBUILD_STAGE_PREFIX_DIR} --install-lib=${REBUILD_STAGE_PYTHON_LIB_DIR} %s' % (' '.join(python_lib_install_flags))
    return self.call_shell(cmd, script, env, shell_env = python_lib_install_env, execution_dir = setup_dir)

class step_python_lib(compound_step):
  'A complete step to make python libs using the "build" target of setuptools.'
  from .step_setup import step_setup
  from .step_post_install import step_post_install

  __steps__ = [
    step_setup,
    step_python_lib_build,
    step_python_lib_install,
    step_post_install,
  ]
  def __init__(self):
    super(step_python_lib, self).__init__()
