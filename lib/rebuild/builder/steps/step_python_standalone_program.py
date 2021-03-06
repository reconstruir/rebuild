#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path

from bes.common import variable
from bes.fs import file_util
from bes.system import execute
from rebuild.step import compound_step, step, step_result
from rebuild.tools import install

class step_python_make_standalone_program(step):
  'A step to make standalone python programs using pyinstaller.'

  def __init__(self):
    super(step_python_make_standalone_program, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    standalone_programs   install_file
    '''
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    standalone_programs = values.get('standalone_programs', [])
      
    if not standalone_programs:
      return step_result(True)

    file_util.mkdir(script.staged_files_bin_dir)
    for program in standalone_programs:
      src_program = path.join(script.build_dir, program.filename)
      if src_program.lower().endswith('.py'):
        rv = self._make_standalone_python(program, script, env)
        if not rv.success:
          return rv
      elif src_program.lower().endswith('.sh'):
        rv = self._make_standalone_shell_script(program, script, env)
        if not rv.success:
          return rv
      else:
        raise RuntimeError('Unknown standalone program type: %s' % (src_program))
    return step_result(True, None)

  def _make_standalone_python(self, program, script, env):
    src_basename = path.basename(program.filename)
    dst_basename = path.basename(program.dst_filename)
    if dst_basename.endswith('.py'):
      return step_result(False, 'dst program should not end in .py: %s' % (dst_basename))
    src_program = variable.substitute(program.filename, script.substitutions)
    if not path.isabs(src_program):
      src_program = path.join(script.build_dir, src_program)
    if not path.isfile(src_program):
      return step_result(False, 'src program not found: %s' % (src_program))
    tmp_src_program = path.join(script.build_dir, dst_basename + '.py')
    file_util.copy(src_program, tmp_src_program)
    
    dst_program = path.join(script.build_dir, 'dist', dst_basename)
    cmd = 'pyinstaller --log INFO -F %s' % (tmp_src_program)
    rv = self.call_shell(cmd, script, env)
    if not rv.success:
      return rv
    if not path.isfile(dst_program):
      return step_result(False, 'dst program not found: %s' % (dst_program))
    installed_program = path.join(script.staged_files_dir, program.dst_filename)
    file_util.mkdir(path.dirname(installed_program))
    file_util.copy(dst_program, installed_program)
    os.chmod(installed_program, 0o755)
    return step_result(True, None)
  
  def _make_standalone_shell_script(self, program, script, env):
    src_basename = path.basename(program.filename)
    dst_basename = path.basename(program.dst_filename)
    if dst_basename.endswith('.sh'):
      return step_result(False, 'dst program should not end in .sh: %s' % (dst_basename))
    src_program = variable.substitute(program.filename, script.substitutions)
    if not path.isabs(src_program):
      src_program = path.join(script.build_dir, src_program)
    if not path.isfile(src_program):
      return step_result(False, 'src program not found: %s' % (src_program))
    installed_program = path.join(script.staged_files_dir, program.dst_filename)
    file_util.mkdir(path.dirname(installed_program))
    file_util.copy(src_program, installed_program)
    os.chmod(installed_program, 0o755)
    return step_result(True, None)

class step_python_standalone_program(compound_step):
  'A complete step to make python libs using the "build" target of setuptools.'
  from .step_setup import step_setup
  from .step_post_install import step_post_install

  __steps__ = [
    step_setup,
    step_python_make_standalone_program,
    step_post_install,
  ]
  def __init__(self):
    super(step_python_standalone_program, self).__init__()
