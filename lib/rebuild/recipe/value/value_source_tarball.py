#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, cached_property, string_util
from bes.compat import StringIO
from .value_base import value_base

class value_source_tarball(value_base):

  def __init__(self, origin = None, filename = '', properties = None):
    super(value_source_tarball, self).__init__(origin, properties = properties)
    check.check_string(filename)
    self.filename = filename

  def __eq__(self, other):
    return self.filename == other.filename
    
  #@abstractmethod
  def value_to_string(self, quote, include_properties = True):
    buf = StringIO()
    buf.write(self.filename)
    self._append_properties_string(buf, include_properties)
    return buf.getvalue()

  #@abstractmethod
  def sources(self, recipe_env):
    'Return a list of sources this caca provides or None if no sources.'
    return [ recipe_env.source_finder.find_tarball(self.filename) ]

  #@abstractmethod
  def substitutions_changed(self):
    self.filename = self.substitute(self.filename)
  
  @classmethod
  #@abstractmethod
  def parse(clazz, origin, text, node):
    if origin:
      check.check_value_origin(origin)
    check.check_node(node)
    parts = string_util.split_by_white_space(text)
    if len(parts) < 1:
      raise ValueError('%s: expected filename instead of: %s' % (origin, text))
    filename = parts[0]
    rest = string_util.replace(text, { filename: '' })
    properties = clazz.parse_properties(rest)
    return clazz(origin = origin, filename = filename, properties = properties)
  
  @classmethod
  #@abstractmethod
  def default_value(clazz, class_name):
    return None

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, class_name):
    # FIXME
    return values[-1]
  
check.register_class(value_source_tarball, include_seq = False)
