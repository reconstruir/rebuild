#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.system import execute
from bes.common.check import check
from bes.common.string_util import string_util
from bes.compat import StringIO
from bes.archive import archiver
from bes.fs import file_util, tar_util

from .value_base import value_base

class value_source_dir(value_base):

  def __init__(self, origin = None, value = None, properties = None):
    super(value_source_dir, self).__init__(origin, properties = properties)
    check.check_string(value)
    value = value or ''
    self.value = path.expanduser(value)
    self._tarball = None
    self._resolved_value = None
    
  def __eq__(self, other):
    return self.value == other.value
    
  #@abstractmethod
  def value_to_string(self, quote, include_properties = True):
    buf = StringIO()
    buf.write(self.value)
    self._append_properties_string(buf, include_properties)
    return buf.getvalue()

  #@abstractmethod
  def sources(self, recipe_env, variables):
    'Return a list of sources this caca provides or None if no sources.'
    return [ recipe_env.source_dir_zipballs.get_tarball(self._resolved_value) ]

  #@abstractmethod
  def substitutions_changed(self):
    assert self.substitutions
    self._resolved_value = self.substitute(self.value)
    
  @classmethod
  #@abstractmethod
  def parse(clazz, origin, text, node):
    if origin:
      check.check_value_origin(origin)
    check.check_node(node)
    parts = string_util.split_by_white_space(text)
    if len(parts) < 1:
      raise ValueError('%s: expected filename instead of: %s' % (origin, text))
    value = parts[0]
    rest = string_util.replace(text, { value: '' })
    properties = clazz.parse_properties(rest)
    return clazz(origin = origin, value = value, properties = properties)
  
  @classmethod
  #@abstractmethod
  def default_value(clazz, class_name):
    return None

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, class_name):
    # FIXME
    return values[-1]
  
  def tarball(self):
    assert self._tarball
    return self._tarball

  def update(self, recipe_env):
    assert self._resolved_value
    self._tarball = recipe_env.source_dir_zipballs.get_tarball(self._resolved_value)
  
check.register_class(value_source_dir, include_seq = False)
