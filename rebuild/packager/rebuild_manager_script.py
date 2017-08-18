#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import copy, os.path as path
from bes.common import string_util
from bes.fs import file_util

class rebuild_manager_script(object):

  DEFAULT_ROOT_DIR = path.expanduser('~/.rebuild')
  
  def __init__(self, template, basename):
    self.template = template
    self.basename = basename
    if template.startswith('#!/'):
      self.mode = 0755
    else:
      self.mode = 0644
  
  def save(self, root_dir, variables):
    filename = path.join(root_dir, self.basename)
    variables = copy.deepcopy(variables)
    content = string_util.replace(self.template, variables)
    content = content.replace(path.expanduser('~'), '${HOME}')
    if self._content_changed(filename, content):
      file_util.save(filename, content = content, mode = self.mode)
      return True
    return False

  def _determine_mode(clazz, template):
    if template.starts_with('#!/'):
      return 0755
    else:
      return 0644
    
  def _content_changed(clazz, filename, content):
    if not path.isfile(filename):
      return True
    return file_util.read(filename) != content
