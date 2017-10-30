#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import Step, step_result
from rebuild import Install

from bes.fs import file_util
import os.path as path

class step_install_install_files(Step):
  'Install files to the stage dir.'

  def __init__(self):
    super(step_install_install_files, self).__init__()

  def execute(self, script, env, args):
    install_files = args.get('install_files', [])
    if not install_files:
      message = 'No install_files for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    separator = args.get('install_files_separator', 'install_files')
    
    for install_file in install_files:
      self.blurb('Installing extra file %s' % (install_file))
      parts = install_file.split(path.sep)
      sep_index = parts.index(separator)
      install_file_rel = path.sep.join(parts[sep_index + 1:])
      dest_filename = path.join(script.stage_dir, install_file_rel)
      if path.exists(dest_filename):
        return step_result(False, 'File already exists: %s' % (dest_filename))
      dest_dir = path.dirname(dest_filename)
      mode = file_util.mode(install_file)
      Install.install(install_file, dest_dir, mode)
      
    return step_result(True, None)

  def sources_keys(self):
    return [ 'install_files' ]

  @classmethod
  def parse_step_args(clazz, script, args):
    return clazz.resolve_step_args_files(script, args, 'install_files')
