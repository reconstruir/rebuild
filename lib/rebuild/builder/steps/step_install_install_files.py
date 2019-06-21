#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step.step import step
from rebuild.step.step_result import step_result

from rebuild.recipe.recipe_parser_util import recipe_parser_util

from bes.common.check import check
from bes.common.object_util import object_util
from bes.variable.variable import variable
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
import os, os.path as path, shutil

class step_install_install_files(step):
  'Install files to the stage dir.'

  def __init__(self):
    super(step_install_install_files, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    install_files   install_file
    '''
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    install_files = values.get('install_files')
    if not install_files:
      message = 'No install_files for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)
    
    check.check_value_install_file_seq(install_files)

    for install_file in install_files:
      src = variable.substitute(install_file.filename, script.substitutions)
      dst = path.join(script.staged_files_dir, install_file.dst_filename)
      if path.isfile(src):
        property_mode = install_file.get_property('mode', None)
        if property_mode:
          mode = int(property_mode, 8)
        else:
          mode = None
        self._install_one('FILE', src, dst, mode)
      elif path.isdir(src):
        files = file_find.find(src, relative = True)
        for f in files:
          self._install_one('DIR', path.join(src, f), path.join(dst, f), None)
      else:
        msg = 'File or dir not found at %s: %s' % (str(install_file.origin), path.relpath(src))
        if not env.config.ignore_install_file_errors:
          return step_result(False, msg)
        else:
          self.blurb('WARNING: %s' % (msg))
    return step_result(True, None)

  def _install_one(self, label, src, dst, mode):
    mode = mode or file_util.mode(src)
    self.log_d('%s: src=%s' % (label, src))
    self.log_d('%s: dst=%s' % (label, dst))
    dst_dir = path.dirname(dst)
    self.blurb('Installing %s => %s (mode=%s)' % (path.relpath(src), path.relpath(dst_dir), mode))
    file_util.mkdir(dst_dir)
    shutil.copy(src, dst)
    os.chmod(dst, mode)
