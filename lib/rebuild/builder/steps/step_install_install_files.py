#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import step, step_result
from rebuild.tools import install

from bes.common import object_util
from bes.fs import file_util
import os, os.path as path, shutil

class step_install_install_files(step):
  'Install files to the stage dir.'

  def __init__(self):
    super(step_install_install_files, self).__init__()

  def execute(self, script, env, args):
    install_files = args.get('install_files', [])
    if not install_files:
      message = 'No install_files for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    if (len(install_files) % 2) != 0:
      return step_result(False, 'Invalid file list: %s' % (install_files))
      
    for install_file in object_util.chunks(install_files, 2):
      src = path.join(script.source_dir, install_file[0])
      if not path.isfile(src):
        return step_result(False, 'File not found: %s' % (src))
      dst = path.join(script.stage_dir, install_file[1])
      if path.exists(dst):
        return step_result(False, 'File already exists: %s' % (dst))
      dst_dir = path.dirname(dst)
      mode = file_util.mode(src)
      self.blurb('Installing file %s in %s (%s)' % (src, dst_dir, mode))
      file_util.mkdir(path.dirname(dst))
      shutil.copy(src, dst)
      os.chmod(dst, mode)
      
    return step_result(True, None)

#  def sources_keys(self):
#    return [ 'install_files' ]

  @classmethod
  def parse_step_args(clazz, script, env, args):
    return clazz.resolve_step_args_list(script, args, 'install_files')
