#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import Shell
from rebuild.step_manager import Step, step_result
from rebuild import build_type, binary_detector, library

class step_cleanup_macos_fix_rpath(Step):
  'Check the rpath of binaries is relative to the executable_path.'

  def __init__(self):
    super(step_cleanup_macos_fix_rpath, self).__init__()

  def execute(self, argument):
    if not argument.env.rebuild_env.config.build_target.is_darwin():
      return step_result(True, None)
    if not path.isdir(argument.env.stage_dir):
      return step_result(True, None)
    binaries = binary_detector.find_strippable_binaries(argument.env.stage_dir, format_name = 'macho')
    blurb_binaries = [ path.relpath(b) for b in binaries ]
    for b in binaries:
      deps = [ dep for dep in library.dependencies(b) if dep.startswith(argument.env.stage_dir) ]
      for dep in deps:
        self.blurb('Fixing rpath: %s %s' % (path.relpath(b), path.relpath(dep)))
        rpath = library.relative_rpath(b, dep)
        new_dep = path.join('@executable_path', rpath)
        cmd = 'install_name_tool -change %s %s %s' % (dep, new_dep, b)
        Shell.execute(cmd)
    return step_result(True, None)
