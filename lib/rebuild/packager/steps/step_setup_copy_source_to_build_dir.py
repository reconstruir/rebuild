#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.step_manager import Step, step_result
from bes.fs import tar_util

class step_setup_copy_source_to_build_dir(Step):
  'Some packages require extra setup in the build_dir.'

  def __init__(self):
    super(step_setup_copy_source_to_build_dir, self).__init__()

  def execute(self, argument):
    if argument.args.get('copy_source_to_build_dir', False):
      tar_util.copy_tree_with_tar(argument.script.source_unpacked_dir, argument.script.build_dir)
    return step_result(True, None)
