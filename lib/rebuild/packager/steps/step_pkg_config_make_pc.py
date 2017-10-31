#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path

from bes.common import object_util, variable
from bes.fs import file_replace
from rebuild.step_manager import Step, step_result
from rebuild.pkg_config import pkg_config_file

# FIXME: unify the replacements here with those in Step

class step_pkg_config_make_pc(Step):
  'Synthesize a .pc file for a package.'

  def __init__(self):
    super(step_pkg_config_make_pc, self).__init__()

  def execute(self, script, env, args):
    pc_files = args.get('pc_files', [])
    if not pc_files:
      message = 'No .pc files for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    replacements = {
      'REBUILD_PACKAGE_NAME': script.descriptor.name,
      'REBUILD_PACKAGE_DESCRIPTION': script.descriptor.name,
      'REBUILD_PACKAGE_VERSION': str(script.descriptor.version),
    }

    pc_file_variables = args.get('pc_file_variables', {})
    replacements.update(pc_file_variables)
    for src_pc in pc_files:
      dst_dir = path.join( script.stage_dir, 'lib/pkgconfig')
      dst_pc = path.join(dst_dir, path.basename(src_pc))
      file_replace.copy_with_substitute(src_pc, dst_pc, replacements, backup = False)

    return step_result(True, None)

  def sources_keys(self):
    return [ 'pc_files' ]

  @classmethod
  def parse_step_args(clazz, script, env, args):
    return clazz.resolve_step_args_files(script, args, 'pc_files')
