#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import Step, step_result
from rebuild import Patch

class step_setup_patch(Step):
  'Patch.'

  DEFAULT_PATCH_STRIP_DEPTH = 1

  def __init__(self):
    super(step_setup_patch, self).__init__()

  def execute(self, argument):
    patches = argument.args.get('patches', None)
    if not patches:
      message = 'No patches for %s' % (argument.env.script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    patch_strip_depth = argument.args.get('patch_strip_depth', self.DEFAULT_PATCH_STRIP_DEPTH)
    patch_program = argument.args.get('patch_program', None)
    
    for patch in patches:
      self.blurb('Patching with %s at %s' % (patch, argument.env.source_unpacked_dir))

    exit_code, msg = Patch.patch(patches,
                                 argument.env.source_unpacked_dir,
                                 strip = patch_strip_depth,
                                 backup = True,
                                 posix = True,
                                 program = patch_program)
    return step_result(exit_code == 0, msg)

  def sources_keys(self):
    return [ 'patches' ]

  @classmethod
  def parse_step_args(clazz, packager_env, args):
    return clazz.resolve_step_args_files(packager_env, args, 'patches')
