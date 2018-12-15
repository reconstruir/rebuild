#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.step import step, step_result
from bes.fs import file_search, file_util, file_mime

class step_check_hard_coded_paths(step):
  'Check that no files in the stage directory have hard coded paths.'

  def __init__(self):
    super(step_check_hard_coded_paths, self).__init__()

  #@abstractmethod
  def execute(self, script, env, values, inputs):
    if not script.has_staged_files_dir():
      return step_result(True, 'No files to check in %s' % (path.relpath(script.staged_files_dir)))
    
    replacements = {
      script.staged_files_dir: '${REBUILD_PACKAGE_PREFIX}',
      script.requirements_manager.installation_dir: '${REBUILD_PACKAGE_PREFIX}',
    }
    from bes.debug import debug_timer
    result = file_search.search_replace(script.staged_files_dir,
                                        replacements,
                                        backup = False,
                                        test_func = file_mime.is_text)
    files_with_hardcoded_paths = [ file_util.remove_head(f, script.staged_files_dir) for f in result.replaced_filenames ]
    return step_result(True, None, outputs = { 'files_with_hardcoded_paths': files_with_hardcoded_paths })
