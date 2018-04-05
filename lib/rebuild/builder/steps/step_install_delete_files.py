#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import step, step_result

from bes.fs import file_util
import os.path as path

class step_install_delete_files(step):
  'Delete files in the stage dir.'

  def __init__(self):
    super(step_install_delete_files, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    delete_files                 string_list
    delete_files_ignore_missing  bool         False
    '''
  
  def execute(self, script, env, args):
    values = self.recipe.resolve_values(env.config.build_target.system)
    delete_files = values.get('delete_files')
    ignore_missing = values.get('delete_files_ignore_missing')

    if not delete_files:
      message = 'No delete_files for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)
    delete_files_in_staged_files_dir = [ path.join(script.staged_files_dir, f) for f in delete_files ]
    missing_files = [ f for f in delete_files_in_staged_files_dir if not path.exists(f) ]
    if missing_files and not ignore_missing:
      return step_result(False, 'File(s) to delete not found: %s' % (' '.join(missing_files)))
    file_util.remove(delete_files_in_staged_files_dir)
    return step_result(True, None)
