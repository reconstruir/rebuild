#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from rebuild.step import step, step_result

class step_cleanup_droppings(step):
  'Cleanup libtool droppings.'

  def __init__(self):
    super(step_cleanup_droppings, self).__init__()

  #@abstractmethod
  @classmethod
  def define_args(clazz):
    return ''
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    if not script.has_staged_files_dir():
      return step_result(True, script.format_message('No droppings to cleanup in {staged_files_dir}'))
    
    droppings = file_find.find_fnmatch(script.staged_files_dir,
                                       [ '*.bak' ],
                                       relative = False)
    file_util.remove(droppings)
    return step_result(True, None)
