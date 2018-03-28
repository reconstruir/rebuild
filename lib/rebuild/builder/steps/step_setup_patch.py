#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import step, step_result
from rebuild.tools import patch

class step_setup_patch(step):
  'patch.'

  DEFAULT_PATCH_STRIP_DEPTH = 1

  def __init__(self):
    super(step_setup_patch, self).__init__()

  @classmethod
  def define_args(clazz):
    return 'patches file_list'
    
  def execute(self, script, env, args):
    if self._recipe:
      values = self.recipe.resolve_values(env.config.build_target.system)
      patches = [ f.filename for f in values.get('patches') or [] ]
    else:
      patches = args.get('patches', None)

    if not patches:
      message = 'No patches for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    patch_strip_depth = args.get('patch_strip_depth', self.DEFAULT_PATCH_STRIP_DEPTH)
    patch_program = args.get('patch_program', None)
    
    for p in patches:
      self.blurb('Patching with %s at %s' % (p, script.source_unpacked_dir))

    exit_code, msg = patch.patch(patches,
                                 script.source_unpacked_dir,
                                 strip = patch_strip_depth,
                                 backup = True,
                                 posix = True,
                                 program = patch_program)
    return step_result(exit_code == 0, msg)

  def sources_keys(self):
    return [ 'patches' ]

  @classmethod
  def parse_step_args(clazz, script, env, args):
    return clazz.resolve_step_args_files(script, args, 'patches')
