#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.fs import tar_util
from rebuild.step import step

class step_install_rebuild_files(step):
  'Install rebuild files in the root of the build_dir.'

  def __init__(self):
    super(step_install_rebuild_files, self).__init__()

  @classmethod
  def define_args(clazz):
    return ''
  
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    rebuild_dir = path.join(script.build_dir, 'rebuild')
    if not path.isdir(rebuild_dir):
      message = 'No rebuild files for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return self.result(True, message)
    dest_dir = path.join(script.staged_files_dir, 'share', 'rebuild')
    tar_util.copy_tree_with_tar(rebuild_dir, dest_dir)
    return self.result(True)
