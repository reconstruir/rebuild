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
    
  def execute(self, script, env, args):
    if self._recipe:
      values = self.recipe.resolve_values(env.config.build_target.system)
      pc_files = [ f.filename for f in values.get('pc_files') or [] ]
      pc_file_variables = values.get('pc_file_variables')
    else:
      pc_files = args.get('pc_files', None)
      pc_file_variables = self.args_get_key_value_list(args, 'pc_file_variables')

    if not pc_files:
      message = 'No .pc files for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    replacements = {}
    replacements.update(script.substitutions)
    if pc_file_variables:
      pc_file_variables.unquote_strings()
      replacements.update(pc_file_variables.to_dict())
    for src_pc in pc_files:
      dst_dir = path.join(script.stage_dir, 'lib/pkgconfig')
      dst_pc = path.join(dst_dir, path.basename(src_pc))
      file_replace.copy_with_substitute(src_pc, dst_pc, replacements, backup = False)

    return step_result(True, None)

#  def sources_keys(self):
#    return [ 'pc_files' ]

  @classmethod
  def parse_step_args(clazz, script, env, args):
    pc_file_variables_dict = clazz.resolve_step_args_key_values(script, args, 'pc_file_variables')
    pc_files_dict = clazz.resolve_step_args_files(script, args, 'pc_files')
    dict_util.del_keys(args, 'pc_file_variables', 'pc_files')
    args.update(pc_file_variables_dict)
    args.update(pc_files_dict)
    return args
