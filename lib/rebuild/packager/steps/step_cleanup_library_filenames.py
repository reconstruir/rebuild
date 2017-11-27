#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs import file_util
from bes.common import string_util
from rebuild.toolchain import library
from rebuild.step import step, step_result
from rebuild.pkg_config import pkg_config, pkg_config_file

class step_cleanup_library_filenames(step):
  'Cleanups realted to the filenames of libraries.'

  def __init__(self):
    super(step_cleanup_library_filenames, self).__init__()

  def execute(self, script, env, args):
    if path.isdir(script.stage_lib_dir):
      libraries = library.list_libraries(script.stage_lib_dir, relative = True)
      for l in libraries:
        link_filename = library.name_add_prefix(l, env.config.third_party_prefix)
        link_path = path.join(script.stage_lib_dir, link_filename)
        file_util.symlink(l, link_path)

    pc_files = pkg_config.find_pc_files(script.stage_dir)
    for pc_file in pc_files:
      pc_file_basename = path.basename(pc_file)
      new_pc_file = self._pc_file_add_third_party_prefix(script, env, pc_file)
      file_util.symlink(pc_file_basename, new_pc_file)
    return step_result(True, None)

  @classmethod
  def _pc_file_add_third_party_prefix(clazz, script, env, filename):
    basename = path.basename(filename)
    if basename.startswith('lib'):
      new_base = 'lib%s%s' % (env.config.third_party_prefix, string_util.remove_head(basename, 'lib'))
    else:
      new_base = '%s%s' % (env.config.third_party_prefix, basename)
    return path.join(path.dirname(filename), new_base)
