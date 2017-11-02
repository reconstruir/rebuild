#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path

from bes.common import object_util, variable
from bes.fs import file_replace
from rebuild.step_manager import Step, step_result
from rebuild.pkg_config import pkg_config_file

# FIXME: unify the replacements here with those in Step

class step_install_env_files(Step):
  'Install any env files this package might require.'

  def __init__(self):
    super(step_install_env_files, self).__init__()

  def execute(self, script, env, args):
    env_files = args.get('env_files', [])
    if not env_files:
      message = 'No env files for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    replacements = {
      'REBUILD_PACKAGE_NAME': script.descriptor.name,
      'REBUILD_PACKAGE_DESCRIPTION': script.descriptor.name,
      'REBUILD_PACKAGE_VERSION': str(script.descriptor.version),
    }

    env_file_variables = args.get('env_file_variables', {})
    replacements.update(env_file_variables)
    for env_file in env_files:
      dst_file = path.join(script.env_dir, path.basename(env_file))
      file_replace.copy_with_substitute(env_file, dst_file, replacements, backup = False)

    return step_result(True, None)

  def sources_keys(self):
    return [ 'env_files' ]

  @classmethod
  def parse_step_args(clazz, script, env, args):
    return clazz.resolve_step_args_files(script, args, 'env_files')
