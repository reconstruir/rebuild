#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_util
from rebuild.step import step, step_result

class step_cleanup_gnu_info(step):
  'Cleanup gnu info droppings which tend to clash between packages.'

  def __init__(self):
    super(step_cleanup_gnu_info, self).__init__()

  def execute(self, script, env, args):
    info_dir = path.join(script.stage_dir, 'share/info')
    file_util.remove(info_dir)
    return step_result(True, None)
