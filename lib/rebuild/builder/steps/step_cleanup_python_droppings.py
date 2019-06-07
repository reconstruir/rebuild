#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs.file_util import file_util
from rebuild.step import step, step_result

class step_cleanup_python_droppings(step):
  'Cleanup python droppings.  The easy install crap.'

  def __init__(self):
    super(step_cleanup_python_droppings, self).__init__()

  #@abstractmethod
  @classmethod
  def define_args(clazz):
    return ''
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    droppings = [
      'lib/python/easy-install.pth',
      'lib/python/site.py',
      'lib/python/site.pyc',
    ]
    droppings = [ path.join(script.staged_files_dir, dropping) for dropping in droppings ]
    file_util.remove(droppings)
    return step_result(True, None)
