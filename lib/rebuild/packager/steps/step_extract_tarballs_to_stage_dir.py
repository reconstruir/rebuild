#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import step, step_result
from bes.archive import archiver

class step_extract_tarballs_to_stage_dir(step):
  'repackage.'
  
  def __init__(self):
    super(self.__class__, self).__init__()
  
  def execute(self, script, env, args):
    tarballs = args.get('tarballs', [])
    strip_common_base = args.get('tarballs_strip_common_base', False)
    for tarball in tarballs:
      archiver.extract(tarball, script.stage_dir,
                       base_dir = script.descriptor.full_name,
                       strip_common_base = strip_common_base)
    return step_result(True)
