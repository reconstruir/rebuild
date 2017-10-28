#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_util
from rebuild.step_manager import Step, step_result

class step_cleanup_python_droppings(Step):
  'Cleanup python droppings.  The easy install crap.'

  def __init__(self):
    super(step_cleanup_python_droppings, self).__init__()

  def execute(self, argument):
    droppings = [
      'lib/python/easy-install.pth',
      'lib/python/site.py',
      'lib/python/site.pyc',
    ]
    droppings = [ path.join(argument.script.stage_dir, dropping) for dropping in droppings ]
    file_util.remove(droppings)
    return step_result(True, None)
