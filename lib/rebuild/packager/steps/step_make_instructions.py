#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path

from bes.common import variable
from bes.fs import file_util
from rebuild.step_manager import step, step_result

class step_make_instructions(step):
  'Make and save build instructions for packages.'

  def __init__(self):
    super(step_make_instructions, self).__init__()

  def execute(self, script, env, args):
    if not script.instructions:
      message = 'No build instructions for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)
    success, message = script.instructions.save(script.stage_compile_instructions_dir)
    if not success:
      self.log_d(message)
      return step_result(False, message)
    return step_result(True, None)
