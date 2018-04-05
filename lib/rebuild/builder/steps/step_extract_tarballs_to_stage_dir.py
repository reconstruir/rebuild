#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.step import step, step_result
from bes.archive import archiver

class step_extract_tarballs_to_stage_dir(step):
  'repackage.'
  
  def __init__(self):
    super(self.__class__, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    tarballs_strip_common_base bool False
    tarballs_no_base_dir bool False
    skip_unpack                  bool         False
    '''
    
  def execute(self, script, env, args):
    values = self.recipe.resolve_values(env.config.build_target.system)
    skip_unpack = values.get('skip_unpack')
    tarballs_no_base_dir = values.get('tarballs_no_base_dir')
    tarballs_strip_common_base = values.get('tarballs_strip_common_base')
    
    if skip_unpack:
      return step_result(True, None)

    tarballs = args.get('tarballs', [])
    if tarballs_no_base_dir:
      base_dir = None
    else:
      base_dir = script.descriptor.full_name

    for tarball in tarballs:
      self.blurb('Extracting extra tarball %s' % (path.relpath(tarball)))
      archiver.extract(tarball, script.stage_dir,
                       base_dir = base_dir,
                       strip_common_base = tarballs_strip_common_base)
    return step_result(True)
