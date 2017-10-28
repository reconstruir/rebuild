#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import dir_util, file_util
from .packager import packager
from rebuild import build_blurb
from rebuild.step_manager import step_aborted
from collections import namedtuple

class build_script_runner(object):

  SUCCESS = 'success'
  FAILED = 'failed'
  CURRENT = 'current'
  ABORTED = 'aborted'

  RunResult = namedtuple('RunResult', 'status,packager_result')

  def __init__(self, filenames, build_target):
    pass
  
  def run_build_script(self, script, env):
    try:
      pkg = packager(script, env)
      checksum_ignored = env.checksum_manager.is_ignored(script.descriptor.full_name)
      needs_rebuilding = checksum_ignored or script.needs_rebuilding(pkg.packager_env)
      if not needs_rebuilding:
        # If the working directory is empty, it means no work happened and its useless
        if dir_util.is_empty(pkg.packager_env.working_dir):
          file_util.remove(pkg.packager_env.working_dir)
        return self.RunResult(self.CURRENT, None)
      build_blurb.blurb('build', '%s - building' % (script.descriptor.name))
      packager_result = pkg.execute()
      #print("CACA: packager_result: %s" % (str(packager_result)))
      if packager_result.success:
        return self.RunResult(self.SUCCESS, packager_result)
      else:
        return self.RunResult(self.FAILED, packager_result)

    except step_aborted as ex:
      return self.RunResult(self.ABORTED, None)

    assert False, 'Not Reached'
    return self.RunResult(self.FAILED, None)
