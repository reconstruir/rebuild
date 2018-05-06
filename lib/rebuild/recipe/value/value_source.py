#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util
from bes.compat import StringIO
from bes.key_value import key_value_list
from .value_base import value_base

class value_source(value_base):

  def __init__(self, env = None, filename = '', properties = None):
    super(value_source, self).__init__(env)
    check.check_string(filename)
    self.filename = filename
    properties = properties or key_value_list()
    check.check_key_value_list(properties)
    self.properties = properties

  def __str__(self):
    return self.value_to_string()
    
  def __eq__(self, other):
    return self.filename == other.filename
    
  def value_to_string(self):
    buf = StringIO()
    buf.write(self.filename)
    if self.properties:
      buf.write(' ')
      buf.write(self.properties.to_string(value_delimiter = ' ', quote = True))
    return buf.getvalue()

  #@abstractmethod
  def sources(self):
    'Return a list of sources this caca provides or None if no sources.'
    return [ self.env.source_finder.find_tarball(self.filename) ]

  @classmethod
  #@abstractmethod
  def parse(clazz, env, value_filename, value):
    parts = string_util.split_by_white_space(value)
    if len(parts) < 1:
      raise ValueError('expected filename instead of: %s' % (value))
    filename = parts[0]
    rest = value.replace(filename, '')
    properties = key_value_list.parse(rest, options = key_value_list.KEEP_QUOTES)
    return clazz(env, filename = filename, properties = properties)
  
  @classmethod
  #@abstractmethod
  def default_value(clazz):
    return None

check.register_class(value_source, include_seq = False)
