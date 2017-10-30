#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import Step, step_result

from bes.fs import file_util
import os.path as path

class step_install_delete_files(Step):
  'Delete files in the stage dir.'

  def __init__(self):
    super(step_install_delete_files, self).__init__()

  def execute(self, script, env, args):
    delete_files = args.get('delete_files', [])
    if not delete_files:
      message = 'No delete_files for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)
    delete_files_in_stage_dir = [ path.join(script.stage_dir, f) for f in delete_files ]
    missing_files = [ f for f in delete_files_in_stage_dir if not path.exists(f) ]
    ignore_missing = args.get('delete_files_ignore_missing', False)
    if missing_files and not ignore_missing:
      return step_result(False, 'File(s) to delete not found: %s' % (' '.join(missing_files)))
    file_util.remove(delete_files_in_stage_dir)
    return step_result(True, None)

  @classmethod
  def parse_step_args(clazz, script, args):
    return clazz.resolve_step_args_list(script, args, 'delete_files')
