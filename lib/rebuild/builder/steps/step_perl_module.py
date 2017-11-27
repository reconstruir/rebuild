#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.step import compound_step, step, step_result
from rebuild.base import build_system
from bes.python import setup_tools
from bes.common import Shell

class step_perl_module_setup(step):
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
    return self.call_shell(cmd, script, env, args, extra_env = args.get('perl_module_setup_env'))

  @classmethod
  def parse_step_args(clazz, script, env, args):
    return clazz.resolve_step_args_env_and_flags(script, args, 'perl_module_setup_env', 'perl_module_setup_flags')

class step_perl_module_post_install_cleanup(step):
  'Cleanup some stuff about the perl module.'

  def __init__(self):
    super(step_perl_module_post_install_cleanup, self).__init__()

  def execute(self, script, env, args):
    bt = script.build_target
    if not bt.system == build_system.LINUX:
      return step_result(True)
    return step_result(True)
    new_path = path.join(script.stage_lib_dir, 'x86_64-linux-gnu')
    if not path.exists(new_path):
      cmd = 'mkdir x86_64-linux-gnu && mv perl x86_64-linux-gnu'
      Shell.execute(cmd, cwd = script.stage_lib_dir, shell = True)
    return step_result(True)

class step_perl_module(compound_step):
  'A complete step to make python libs using the "build" target of setuptools.'
  from .step_setup import step_setup
  from .step_post_install import step_post_install
  from .step_make import step_make_install

  __steps__ = [
    step_setup,
    step_perl_module_setup,
    step_make_install,
    step_perl_module_post_install_cleanup,
    step_post_install,
  ]
  def __init__(self):
    super(step_perl_module, self).__init__()
