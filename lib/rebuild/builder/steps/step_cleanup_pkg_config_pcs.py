#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from rebuild.step import step, step_result
from rebuild.pkg_config import pkg_config, pkg_config_file

class step_cleanup_pkg_config_pcs(step):
  'Fix duplicate flags in pc files.'

  def __init__(self):
    super(step_cleanup_pkg_config_pcs, self).__init__()

  #@abstractmethod
  @classmethod
  def define_args(clazz):
    return ''
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    pc_files = pkg_config.find_pc_files(script.staged_files_dir)
    for pc_file in pc_files:
      if pkg_config_file.rewrite_cleanup(pc_file, pc_file, backup = False):
        self.blurb('Cleaned %s' % (path.relpath(pc_file)))

    return step_result(True, None)
