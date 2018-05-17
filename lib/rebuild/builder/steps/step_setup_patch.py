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
    patch_program      string     patch
    patch_dir          dir        ${REBUILD_SOURCE_UNPACKED_DIR}
    '''
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    patches = values.get('patches')
    if not patches:
      message = 'No patches for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)
    patch_program = values.get('patch_program')
    patch_dir = values.get('patch_dir')

    for p in patches:
      props = p.properties_dict
      strip = int(props.get('strip', self.DEFAULT_PATCH_STRIP_DEPTH))
      self.blurb('Applying patch %s (strip=%d) in dir %s' % (path.relpath(p.filename),
                                                             strip,
                                                             path.relpath(patch_dir.filename)))
      exit_code, msg = patch.patch(p.filename,
                                   patch_dir.filename,
                                   strip = strip,
                                   backup = True,
                                   posix = True,
                                   program = patch_program)
    return step_result(exit_code == 0, msg)
