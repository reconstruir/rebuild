#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import dir_util, file_util
from rebuild import build_blurb
from rebuild.step_manager import step_aborted
from collections import namedtuple

class build_script_runner(object):

  SUCCESS = 'success'
  FAILED = 'failed'
  CURRENT = 'current'
  ABORTED = 'aborted'

  _run_result = namedtuple('_run_result', 'status,packager_result')

  def __init__(self, filenames, build_target):
    pass
  
  def run_build_script(self, script, env):
    try:
      checksum_ignored = env.checksum_manager.is_ignored(script.descriptor.full_name)
      needs_rebuilding = checksum_ignored or script.needs_rebuilding()
      if not needs_rebuilding:
        # If the working directory is empty, it means no work happened and its useless
        if path.exists(script.working_dir) and dir_util.is_empty(script.working_dir):
          file_util.remove(script.working_dir)
        return self._run_result(self.CURRENT, None)
      build_blurb.blurb('build', '%s - building' % (script.descriptor.name))
      packager_result = script.execute({})
      if packager_result.success:
        return self._run_result(self.SUCCESS, packager_result)
      else:
        return self._run_result(self.FAILED, packager_result)

    except step_aborted as ex:
      return self._run_result(self.ABORTED, None)

    assert False, 'Not Reached'
    return self._run_result(self.FAILED, None)
