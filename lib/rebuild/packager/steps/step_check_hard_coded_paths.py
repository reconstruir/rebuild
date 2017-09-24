#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import Step, step_result
from bes.common import Shell
from bes.fs import file_search, file_util, file_mime

class step_check_hard_coded_paths(Step):
  'Check that no files in the stage directory have hard coded paths.'

  def __init__(self):
    super(step_check_hard_coded_paths, self).__init__()

  def execute(self, argument):
    replacements = {
      argument.env.stage_dir: '${REBUILD_PACKAGE_PREFIX}',
      argument.env.requirements_manager.installation_dir: '${REBUILD_PACKAGE_PREFIX}',
    }
    file_search.search_replace(argument.env.stage_dir,
                               replacements,
                               backup = False,
                               test_func = file_mime.is_text)
    return step_result(True, None)
