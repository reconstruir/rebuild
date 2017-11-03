#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs import dir_util, file_util
from rebuild import library
from rebuild.base import build_category
from rebuild.darwin import Lipo
from rebuild.step_manager import Step, step_result
from rebuild.pkg_config import pkg_config, pkg_config_file

class step_check_darwin_archs(Step):
  'Cleanups realted to the filenames of libraries.'

  def __init__(self):
    super(step_check_darwin_archs, self).__init__()

  def __matches(self, expected, actual):
    for arch in actual:
      if not arch in expected:
        return False
    return True

  def execute(self, script, env, args):
    if not env.config.build_target.is_darwin():
      return step_result(True, None)
    if script.descriptor.category != build_category.LIB:
      return step_result(True, None)
    if path.isdir(script.stage_lib_dir):
      expected_archs = env.config.build_target.archs
      for lib in library.list_libraries(script.stage_lib_dir, relative = False):
        actual_archs = Lipo.archs(lib)
        if not self.__matches(expected_archs, actual_archs):
          expected_label = ','.join(expected_archs)
          if actual_archs:
            actual_label = ','.join(actual_archs)
          else:
            actual_label = 'None'
          msg = 'Expected archs for %s dont match.  Should be \"%s\" instead if \"%s\"' % (lib, expected_label, actual_label)
          if args.get('ignore_check_darwin_archs', False):
            return step_result(True, None)
          else:
            return step_result(False, msg)

    return step_result(True, None)
