#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path

from bes.common import dict_util, object_util, string_util, variable
from bes.fs import file_replace
from rebuild.step import step, step_result

# FIXME: unify the replacements here with those in step

class step_pkg_config_make_pc(step):
  'Synthesize a .pc file for a package.'

  def __init__(self):
    super(step_pkg_config_make_pc, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    pc_files           file_list  
    pc_file_variables  key_values
    '''
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    pc_files = [ f.filename for f in values.get('pc_files') or [] ]
    pc_file_variables = values.get('pc_file_variables')
    
    if not pc_files:
      message = 'No .pc files for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    replacements = {}
    replacements.update(script.substitutions)
    if pc_file_variables:
      pc_file_variables = pc_file_variables[:]
      pc_file_variables.unquote_strings()
      replacements.update(pc_file_variables.to_dict())
    for src_pc in pc_files:
      dst_dir = path.join(script.staged_files_dir, 'lib/pkgconfig')
      dst_pc = path.join(dst_dir, path.basename(src_pc))
      file_replace.copy_with_substitute(src_pc, dst_pc, replacements, backup = False)
    return step_result(True, None)
