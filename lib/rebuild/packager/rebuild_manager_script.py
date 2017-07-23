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
    if template.starts_with('#!/'):
      self.mode = 0755
    else:
      self.mode = 0644
  
  def save(self, root_dir, variables, mode):
    filename = path.join(root_dir, self.basename)
    variables = copy.deepcopy(variables)
    variables[path.expanduser('~/')] = '~/'
    content = string_util.replace(self.template, variables)
    if self._content_changed(filename, content):
      file_util.save(filename, content = content, mode = self.mode)

  def _determine_mode(clazz, template):
    if template.starts_with('#!/'):
      return 0755
    else:
      return 0644
    
  def _content_changed(clazz, filename, content):
    return path.isfile(filename) and file_util.read(filename) != content
