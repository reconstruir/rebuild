#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.step_manager import multiple_steps, Step, step_result
from rebuild import System
from bes.python import setup_tools
from bes.common import Shell

class step_perl_module_setup(Step):
  'Setup a perl module for compilation.'

  def __init__(self):
    super(step_perl_module_setup, self).__init__()

  def execute(self, script, env, args):
    makefile = args.get('makefile', 'Makefile.PL')
    mkdir_cmd = 'mkdir -p ${REBUILD_STAGE_PYTHON_LIB_DIR}'
    perl_cmd = '${PERL} %s PREFIX=${REBUILD_STAGE_PREFIX_DIR} INSTALLDIRS=perl' % (makefile)
    perl_env_args = args.get('perl_module_setup_flags', '')
    assert isinstance(perl_env_args, list)
    cmd = '%s && %s %s' % (mkdir_cmd, perl_cmd, ' '.join(perl_env_args))
    return self.call_shell(cmd, script, args, extra_env = args.get('perl_module_setup_env'))

  @classmethod
  def parse_step_args(clazz, script, args):
    return clazz.resolve_step_args_env_and_flags(script, args, 'perl_module_setup_env', 'perl_module_setup_flags')

class step_perl_module_post_install_cleanup(Step):
  'Cleanup some stuff about the perl module.'

  def __init__(self):
    super(step_perl_module_post_install_cleanup, self).__init__()

  def execute(self, script, env, args):
    bi = script.env.config.build_target
    if not bi.system == System.LINUX:
      return step_result(True)
    return step_result(True)
    new_path = path.join(script.stage_lib_dir, 'x86_64-linux-gnu')
    if not path.exists(new_path):
      cmd = 'mkdir x86_64-linux-gnu && mv perl x86_64-linux-gnu'
      Shell.execute(cmd, cwd = script.stage_lib_dir, shell = True)
    return step_result(True)

class step_perl_module(multiple_steps):
  'A complete step to make python libs using the "build" target of setuptools.'
  from .step_setup import step_setup
  from .step_post_install import step_post_install
  from .step_make import step_make_install

  step_classes = [
    step_setup,
    step_perl_module_setup,
    step_make_install,
    step_perl_module_post_install_cleanup,
    step_post_install,
  ]
  def __init__(self):
    super(step_perl_module, self).__init__()
