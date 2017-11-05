#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import step, step_result
from rebuild import Patch

class step_setup_patch(step):
  'Patch.'

  DEFAULT_PATCH_STRIP_DEPTH = 1

  def __init__(self):
    super(step_setup_patch, self).__init__()

  def execute(self, script, env, args):
    patches = args.get('patches', None)
    if not patches:
      message = 'No patches for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    patch_strip_depth = args.get('patch_strip_depth', self.DEFAULT_PATCH_STRIP_DEPTH)
    patch_program = args.get('patch_program', None)
    
    for patch in patches:
      self.blurb('Patching with %s at %s' % (patch, script.source_unpacked_dir))

    exit_code, msg = Patch.patch(patches,
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
