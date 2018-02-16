#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_util
from bes.common import Shell
from rebuild.step import compound_step, step, step_result
from rebuild.tools import install

class step_python_make_standalone_program(step):
  'A step to make standalone python programs using pyinstaller.'

  def __init__(self):
    super(step_python_make_standalone_program, self).__init__()

  def execute(self, script, env, args):
    standalone_programs = args.get('standalone_programs', [])
    if not standalone_programs:
      return step_result(True)

    for program in standalone_programs:
      rv = Shell.execute('pyinstaller', raise_error = False)
      src_program = path.join(script.build_dir, program[0])
      dst_program = path.join(script.build_dir, 'dist', path.basename(program[1]))
      cmd = 'pyinstaller -F %s' % (src_program)
      rv = self.call_shell(cmd, script, env, args)
      if not rv.success:
        return rv
      file_util.mkdir(script.stage_bin_dir)
      install.install(dst_program, script.stage_bin_dir, mode = 0o755)
    return step_result(True)

class step_python_standalone_program(compound_step):
  'A complete step to make python libs using the "build" target of setuptools.'
  from .step_setup import step_setup
  from .step_post_install import step_post_install

  __step_global_args__ = {
    'copy_source_to_build_dir': True,
  }

  __steps__ = [
    step_setup,
    step_python_make_standalone_program,
    step_post_install,
  ]
  def __init__(self):
    super(step_python_standalone_program, self).__init__()
