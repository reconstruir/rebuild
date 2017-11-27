#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_find, file_util
from rebuild.step import step, step_result

class step_cleanup_droppings(step):
  'Cleanup libtool droppings.'

  def __init__(self):
    super(step_cleanup_droppings, self).__init__()

  def execute(self, script, env, args):
    droppings = file_find.find_fnmatch(script.stage_dir,
                                       [ '*.bak' ],
                                       relative = False)
    file_util.remove(droppings)
    return step_result(True, None)
