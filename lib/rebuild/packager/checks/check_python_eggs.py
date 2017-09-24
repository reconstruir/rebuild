#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.packager import Check, check_result
from bes.fs import file_find

class check_python_eggs(Check):
  'Check that only 1 egg is present.'

  def __init__(self):
    super(check_python_eggs, self).__init__()

  def check(self, files_dir, env):
    eggs = file_find.find_fnmatch(files_dir, [ '*.egg', '*.egg-info' ], relative = False, file_type = file_find.ANY)
    num_eggs = len(eggs)
    if num_eggs != 1:
      return check_result(False, 'found %d eggs instead of 1: %s' % (num_eggs, ' '.join(eggs)))
    return check_result(True)
