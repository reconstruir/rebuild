#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import Step, step_result
from bes.archive import archiver

class step_extract_tarballs_to_stage_dir(Step):
  'repackage.'
  
  def __init__(self):
    super(self.__class__, self).__init__()
  
  def execute(self, script, env, args):
    tarballs = args.get('tarballs', [])
    for tarball in tarballs:
      archiver.extract(tarball, script.stage_dir)
    return step_result(True)
