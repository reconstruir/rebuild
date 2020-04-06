#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.system.execute import execute
from bes.system.which import which
from bes.system.log import log
from rebuild.step.step import step
from rebuild.binary_format.binary_detector import binary_detector
from rebuild.toolchain.library import library

class step_cleanup_linux_fix_rpath(step):
  'Check the rpath of binaries is relative to the executable_path.'

  _PATCHELF_EXE = which.which('patchelf')
  
  def __init__(self):
    super(step_cleanup_linux_fix_rpath, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    rpath string $ORIGIN/../lib
    '''
  
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    if not self. _PATCHELF_EXE:
      if not self. _PATCHELF_EXE:
        log.console('WARNING: patchelf not found.  executables will be bad!')
      return self.result(True, None)
    if not script.build_target.is_linux():
      return self.result(True, None)
    if not path.isdir(script.staged_files_dir):
      return self.result(True, None)
    binaries = binary_detector.find_strippable_binaries(script.staged_files_dir, format_name = 'elf')
    rpath = values.get('rpath')
    for b in binaries:
      if not library.is_library(b):
        self.blurb('Setting rpath %s for %s' % (rpath, path.relpath(b)))
        cmd = '{} --set-rpath {} {}'.format(self. _PATCHELF_EXE, rpath, b)
        execute.execute(cmd)
    return self.result(True, None)
