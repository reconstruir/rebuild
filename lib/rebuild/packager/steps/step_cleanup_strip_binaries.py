#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.step_manager import Step, step_result
from rebuild import build_type, binary_detector
from rebuild.toolchain import strip

class step_cleanup_strip_binaries(Step):
  'Strip binaries.'

  def __init__(self):
    super(step_cleanup_strip_binaries, self).__init__()

  def execute(self, argument):
    is_release = argument.env.rebuild_env.config.build_target.build_type == build_type.RELEASE
    if is_release:
      if argument.args.get('dont_strip_binaries', False):
        return step_result(True, None)
    else:
      if not argument.args.get('strip_binaries', False):
        return step_result(True, None)
    if not path.isdir(argument.env.stage_dir):
      return step_result(True, None)
    binary_format = argument.env.rebuild_env.config.build_target.binary_format
    if not binary_format:
      return step_result(True, 'Unknown binary format: %s' % (binary_format))
    binaries = binary_detector.find_strippable_binaries(argument.env.stage_dir, format_name = binary_format)
    for b in binaries:
      self.blurb('stripping binary: %s' % (path.relpath(b)))
      if not strip.strip(argument.env.rebuild_env.config.build_target, b):
        step_result(False, 'Failed to strip: %s' % (b))
    return step_result(True, None)
