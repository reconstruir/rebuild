#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.system import execute
from rebuild.step import step
from rebuild.binary_format import binary_detector
from rebuild.toolchain import library

class step_cleanup_linux_fix_rpath(step):
  'Check the rpath of binaries is relative to the executable_path.'

  def __init__(self):
    super(step_cleanup_linux_fix_rpath, self).__init__()

  #@abstractmethod
  def execute(self, script, env, values, inputs):
    if not script.build_target.is_linux():
      return self.result(True, None)
    if not path.isdir(script.staged_files_dir):
      return self.result(True, None)
    binaries = binary_detector.find_strippable_binaries(script.staged_files_dir, format_name = 'elf')
    for b in binaries:
      if not library.is_library(b):
        self.blurb('Fixing rpath: %s' % (path.relpath(b)))
        cmd = 'patchelf --set-rpath $ORIGIN/../lib %s' % (b)
        execute.execute(cmd)
    return self.result(True, None)
