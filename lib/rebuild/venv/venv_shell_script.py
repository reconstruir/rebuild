#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from bes.common.string_util import string_util
from bes.fs.file_util import file_util

class venv_shell_script(object):

  def __init__(self, template, basename):
    self.template = template
    self.basename = basename
    if template.startswith('#!/'):
      self.mode = 0o755
    else:
      self.mode = 0o644
  
  def save(self, root_dir, variables, only_if_not_there = False):
    filename = path.join(root_dir, self.basename)
    variables = copy.deepcopy(variables)
    content = string_util.replace(self.template, variables)
    content = content.replace(path.expanduser('~'), '${HOME}')
    if self._content_changed(filename, content):
      if only_if_not_there and path.isfile(filename):
        return False
      file_util.save(filename, content = content, mode = self.mode)
      return True
    return False

  def _determine_mode(clazz, template):
    if template.starts_with('#!/'):
      return 0o755
    else:
      return 0o644
    
  def _content_changed(clazz, filename, content):
    if not path.isfile(filename):
      return True
    return file_util.read(filename) != content
