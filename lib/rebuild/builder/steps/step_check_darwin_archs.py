#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs import dir_util, file_util
from rebuild.toolchain import library
from rebuild.toolchain.darwin import lipo
from rebuild.step import step, step_result

class step_check_darwin_archs(step):
  'Cleanups realted to the filenames of libraries.'

  def __init__(self):
    super(step_check_darwin_archs, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return '''
    ignore_check_darwin_archs   bool        False
    '''

  def __matches(self, expected, actual):
    for arch in actual:
      if not arch in expected:
        return False
    return True

  def execute(self, script, env, args):
    if not script.build_target.is_darwin():
      return step_result(True, None)
    if path.isdir(script.stage_lib_dir):
      expected_archs = script.build_target.archs
      for lib in library.list_libraries(script.stage_lib_dir, relative = False):
        actual_archs = lipo.archs(lib)
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
