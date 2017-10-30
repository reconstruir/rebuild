#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_find, file_util
from rebuild.step_manager import Step, step_result

class step_cleanup_libtool_droppings(Step):
  'Cleanup libtool droppings.'

  def __init__(self):
    super(step_cleanup_libtool_droppings, self).__init__()

  def execute(self, script, env, args):
    stage_lib_dir = path.join(script.stage_dir, 'lib')
    if path.isdir(stage_lib_dir):
      droppings = file_find.find_fnmatch(path.join(script.stage_dir, 'lib'),
                                         [ '*.la' ],
                                         relative = False)
      file_util.remove(droppings)
    return step_result(True, None)
