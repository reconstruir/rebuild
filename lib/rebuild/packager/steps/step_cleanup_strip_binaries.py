#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.step_manager import step, step_result
from rebuild.binary_format import binary_detector
from rebuild.base import build_level
from rebuild.toolchain import strip

class step_cleanup_strip_binaries(step):
  'Strip binaries.'

  def __init__(self):
    super(step_cleanup_strip_binaries, self).__init__()

  def execute(self, script, env, args):
    is_release = script.build_target.build_level == build_level.RELEASE
    if is_release:
      if args.get('dont_strip_binaries', False):
        return step_result(True, None)
    else:
      if not args.get('strip_binaries', False):
        return step_result(True, None)
    if not path.isdir(script.stage_dir):
      return step_result(True, None)
    binary_format = script.build_target.binary_format
    if not binary_format:
      return step_result(True, 'Unknown binary format: %s' % (binary_format))
    binaries = binary_detector.find_strippable_binaries(script.stage_dir, format_name = binary_format)
    for b in binaries:
      self.blurb('stripping binary: %s' % (path.relpath(b)))
      if not strip.strip(script.build_target, b):
        step_result(False, 'Failed to strip: %s' % (b))
    return step_result(True, None)
