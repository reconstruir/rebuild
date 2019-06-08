#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path

from bes.common.dict_util import dict_util
from bes.common.object_util import object_util
from bes.common.string_util import string_util
from bes.common.variable import variable
from bes.fs.file_replace import file_replace
from rebuild.step.step import step
from rebuild.step.step_result import step_result

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
    pc_files = values.get('pc_files')
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
      dst_pc = path.join(dst_dir, path.basename(src_pc.filename))
      file_replace.copy_with_substitute(src_pc.filename, dst_pc, replacements, backup = False)
    return step_result(True, None)
