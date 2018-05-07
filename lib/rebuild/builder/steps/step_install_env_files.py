#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path

from bes.common import object_util, variable
from bes.fs import file_replace
from rebuild.step import step, step_result

# FIXME: unify the replacements here with those in step

class step_install_env_files(step):
  'Install any env files this package might require.'

  def __init__(self):
    super(step_install_env_files, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    env_files   file_list
    '''
    
  def execute(self, script, env, args):
    values = self.values
    env_files = values.get('env_files')
    if env_files:
      env_files = [ f.filename for f in env_files ]

    if not env_files:
      message = 'No env files for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    replacements = {
      'REBUILD_PACKAGE_NAME': script.descriptor.name,
      'REBUILD_PACKAGE_DESCRIPTION': script.descriptor.name,
      'REBUILD_PACKAGE_FULL_VERSION': str(script.descriptor.version),
    }

    for env_file in env_files:
      dst_file = path.join(script.stagged_env_dir, path.basename(env_file))
      file_replace.copy_with_substitute(env_file, dst_file, replacements, backup = False)

    return step_result(True, None)

  def sources_keys(self):
    return [ 'env_files' ]
