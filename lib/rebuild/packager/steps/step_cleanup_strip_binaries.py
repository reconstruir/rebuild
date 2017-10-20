#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.step_manager import Step, step_result
from rebuild import build_type, binary_detector, strip

class step_cleanup_strip_binaries(Step):
  'Strip binaries.'

  def __init__(self):
    super(step_cleanup_strip_binaries, self).__init__()

  def execute(self, argument):
    is_release = argument.env.build_target.build_type == build_type.RELEASE
    if is_release:
      if argument.args.get('dont_strip_binaries', False):
        return step_result(True, None)
    else:
      if not argument.args.get('strip_binaries', False):
        return step_result(True, None)
    if not path.isdir(argument.env.stage_dir):
      return step_result(True, None)
    binaries = binary_detector.find_strippable_binaries(argument.env.stage_dir)
    blurb_binaries = [ path.relpath(b) for b in binaries ]
    for b in blurb_binaries:
      self.blurb('stripping binary: %s' % (b))
    strip.strip(argument.env.build_target, binaries)
    return step_result(True, None)
