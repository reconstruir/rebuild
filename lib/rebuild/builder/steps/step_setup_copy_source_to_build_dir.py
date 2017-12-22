#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.step import step, step_result
from bes.fs import tar_util

class step_setup_copy_source_to_build_dir(step):
  'Some packages require extra setup in the build_dir.'

  def __init__(self):
    super(step_setup_copy_source_to_build_dir, self).__init__()

  @classmethod
  def define_args(clazz):
    return 'copy_source_to_build_dir bool False'
  
  def execute(self, script, env, args):
    if args.get('copy_source_to_build_dir', False):
      tar_util.copy_tree_with_tar(script.source_unpacked_dir, script.build_dir)
    return step_result(True, None)

