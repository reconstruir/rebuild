#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs import dir_util, file_util
from rebuild.step import step, step_result

class step_cleanup_binary_filenames(step):
  'Add a third party prefix to binaries.'

  def __init__(self):
    super(step_cleanup_binary_filenames, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    skip_binary_third_party_prefix   bool        False
    '''
    
  def execute(self, script, env, args):
    if not path.isdir(script.stage_bin_dir):
      return step_result(True, None)
    if args.get('skip_binary_third_party_prefix', False):
      return step_result(True, None)
      
    binaries = dir_util.list(script.stage_bin_dir)
    for b in binaries:
      link_src = path.basename(b)
      if not link_src.startswith(env.config.third_party_prefix):
        link_filename = '%s%s' % (env.config.third_party_prefix, link_src)
        link_dst = path.join(script.stage_bin_dir, link_filename)
        file_util.symlink(link_src, link_dst)
    return step_result(True, None)

  @classmethod
  def __pc_file_add_third_party_prefix(clazz, filename):
    basename = path.basename(filename)
    new_base = '%s%s' % (env.config.third_party_prefix, basename)
    return path.join(path.dirname(filename), new_base)
