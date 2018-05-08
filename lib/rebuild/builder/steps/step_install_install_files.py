#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import step, step_result
from rebuild.tools import install

from rebuild.recipe import recipe_parser_util

from bes.common import check, object_util, variable
from bes.fs import file_util
import os, os.path as path, shutil

class step_install_install_files(step):
  'Install files to the stage dir.'

  def __init__(self):
    super(step_install_install_files, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    install_files   file_install_list
    '''
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    install_files = values.get('install_files')
      
    if not install_files:
      message = 'No install_files for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)
    
    check.check_recipe_install_file_list(install_files)
    
    for install_file in install_files:
      src = variable.substitute(install_file.filename, script.substitutions)
      if not path.isfile(src):
        return step_result(False, 'File not found: %s' % (src))
      dst = path.join(script.staged_files_dir, install_file.dst_filename)
      dst_dir = path.dirname(dst)
      mode = file_util.mode(src)
      self.blurb('Installing file %s in %s (%s)' % (src, dst_dir, mode))
      file_util.mkdir(path.dirname(dst))
      shutil.copy(src, dst)
      os.chmod(dst, mode)
      
    return step_result(True, None)

  def sources_keys(self):
    return [ 'install_files' ]
