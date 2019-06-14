#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.fs.file_copy import file_copy
from rebuild.step.step import step

class step_install_rebuild_files(step):
  'Install rebuild files in the root of the build_dir.'

  def __init__(self):
    super(step_install_rebuild_files, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    skip_install_rebuild_files   bool    False
    '''
  
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    if values.get('skip_install_rebuild_files'):
      return self.result(True, 'skipping install_rebuild_files because skip_install_rebuild_files is True.')
    rebuild_dir = path.join(script.build_dir, 'rebuild')
    if not path.isdir(rebuild_dir):
      message = 'No rebuild files for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return self.result(True, message)
    dest_dir = path.join(script.staged_files_dir, 'share', 'rebuild')
    file_copy.copy_tree(rebuild_dir, dest_dir)
    return self.result(True)
