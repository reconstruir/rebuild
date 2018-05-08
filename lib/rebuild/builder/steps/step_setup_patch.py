#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.step import step, step_result
from rebuild.tools import patch
from bes.common import variable

class step_setup_patch(step):
  'patch.'

  DEFAULT_PATCH_STRIP_DEPTH = 1

  def __init__(self):
    super(step_setup_patch, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    patches            file_list  
    patch_strip_depth  int        1
    patch_program      string     patch
    patch_dir          dir        ${REBUILD_SOURCE_UNPACKED_DIR}
    '''
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    patches = [ f.filename for f in values.get('patches') or [] ]
    patch_strip_depth = values.get('patch_strip_depth')
    patch_program = values.get('patch_program') or 'patch'
    patch_dir = values.get('patch_dir')
    patch_dir = variable.substitute(patch_dir.filename, script.substitutions)
    if not patches:
      message = 'No patches for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    for p in patches:
      self.blurb('Patching with %s at %s' % (p, path.relpath(patch_dir)))

    exit_code, msg = patch.patch(patches,
                                 patch_dir,
                                 strip = patch_strip_depth,
                                 backup = True,
                                 posix = True,
                                 program = patch_program)
    return step_result(exit_code == 0, msg)

  def sources_keys(self):
    return [ 'patches' ]
