#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path

from bes.common import variable
from bes.fs import file_util
from rebuild.step_manager import Step, step_result

class step_make_instructions(Step):
  'Make and save build instructions for packages.'

  def __init__(self):
    super(step_make_instructions, self).__init__()

  def execute(self, argument):
    if not argument.env.script.instruction_list:
      message = 'No build instructions for %s' % (argument.env.script.package_descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)
    success, message = argument.env.script.instruction_list.save(argument.env.stage_compile_instructions_dir)
    if not success:
      self.log_d(message)
      return step_result(False, message)
    return step_result(True, None)
