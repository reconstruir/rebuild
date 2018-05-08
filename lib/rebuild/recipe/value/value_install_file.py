#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import algorithm, check, string_util
from bes.compat import StringIO
from bes.dependency import dependency_provider
from .value_base import value_base

class value_install_file(value_base):

  def __init__(self, env = None, filename = '', dst_filename = '', properties = None):
    super(value_install_file, self).__init__(env, properties = properties)
    self.filename = filename
    self.dst_filename = dst_filename

  def __eq__(self, other):
    return self.filename == other.filename and self.dst_filename == other.dst_filename
    
  #@abstractmethod
  def value_to_string(self, quote):
    buf = StringIO()
    buf.write(path.basename(self.filename))
    buf.write(' ')
    buf.write(self.dst_filename)
    ps = self.properties_to_string()
    if ps:
      buf.write(' ')
      buf.write(ps)
    return buf.getvalue()

  @classmethod
  #@abstractmethod
  def default_value(clazz):
    'Return the default value to use for this class.'
    return []

  #@abstractmethod
  def sources(self):
    'Return a list of sources this caca provides or None if no sources.'
    return [ self.filename ]

  #@abstractmethod
  def substitutions_changed(self):
    self.filename = self.substitute(self.filename)
    self.dst_filename = self.substitute(self.dst_filename)

  @classmethod
  #@abstractmethod
  def parse(clazz, env, recipe_filename, text):
    parts = string_util.split_by_white_space(text)
    if len(parts) < 2:
      raise ValueError('expected filename and dst_filename instead of: %s' % (text))
    filename = parts[0]
    dst_filename = parts[1]
    rest = text.replace(filename, '')
    rest = rest.replace(dst_filename, '')
    properties = clazz.parse_properties(rest)
    return clazz(env = env, filename = filename, dst_filename = dst_filename, properties = properties)

  @classmethod
  #@abstractmethod
  def resolve(clazz, values):
    check.check_value_install_file_seq(values)
    result = []
    for value in values:
      check.check_value_install_file(value)
      result.append(value)
    return algorithm.unique(result)
  
check.register_class(value_install_file) #, include_seq = False)
