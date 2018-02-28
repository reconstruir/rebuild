#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.system import execute
from rebuild.step import step, step_result
from rebuild.binary_format import binary_detector
from rebuild.toolchain import library
from rebuild.base import build_level

class step_cleanup_macos_fix_rpath(step):
  'Check the rpath of binaries is relative to the executable_path.'

  def __init__(self):
    super(step_cleanup_macos_fix_rpath, self).__init__()

  def execute(self, script, env, args):
    if not script.build_target.is_darwin():
      return step_result(True, None)
    if not path.isdir(script.stage_dir):
      return step_result(True, None)
    binaries = binary_detector.find_strippable_binaries(script.stage_dir, format_name = 'macho')
    blurb_binaries = [ path.relpath(b) for b in binaries ]
    for b in binaries:
      deps = [ dep for dep in library.dependencies(b) if dep.startswith(script.stage_dir) ]
      for dep in deps:
        self.blurb('Fixing rpath: %s %s' % (path.relpath(b), path.relpath(dep)))
        rpath = library.relative_rpath(b, dep)
        new_dep = path.join('@executable_path', rpath)
        cmd = 'install_name_tool -change %s %s %s' % (dep, new_dep, b)
        execute.execute(cmd)
    return step_result(True, None)
