#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util
from bes.compat import StringIO
from .value_base import value_base
from .value_list_base import value_list_base

class value_file(value_base):

  def __init__(self, env = None, filename = '', properties = None):
    'Class to manage a recipe file.'
    super(value_file, self).__init__(env, properties = properties)
    check.check_string(filename)
    self.filename = filename

  def __eq__(self, other):
    return self.filename == other.filename
    
  #@abstractmethod
  def value_to_string(self, quote):
    buf = StringIO()
    buf.write(path.basename(self.filename))
    ps = self.properties_to_string()
    if ps:
      buf.write(' ')
      buf.write(ps)
    return buf.getvalue()

  @classmethod
  #@abstractmethod
  def default_value(clazz, arg_type):
    'Return the default value to use for this class.'
    return None
    return value_file_list()

  #@abstractmethod
  def sources(self):
    'Return a list of sources this caca provides or None if no sources.'
    return [ self.filename ]

  #@abstractmethod
  def substitutions_changed(self):
    self.filename = self.substitute(self.filename)
  
  @classmethod
  #@abstractmethod
  def parse(clazz, env, recipe_filename, value):
    base = path.dirname(recipe_filename)
    filename, _, rest = string_util.partition_by_white_space(value)
    filename_abs = path.abspath(path.join(base, filename))
    if not path.isfile(filename_abs):
      raise RuntimeError('file not found: %s' % (filename_abs))
    properties = clazz.parse_properties(rest)
    return value_file(env = env, filename = filename_abs, properties = properties)

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, arg_type):
    check.check_value_file_seq(values)
    env = None
    result_values = []
    for value in values:
      check.check_value_file(value)
      if not env:
        env = value.env
      result_values.append(value)
    result = value_file_list(env = env, values = result_values)
    result.remove_dups()
    return result
  
check.register_class(value_file, include_seq = True)

class value_file_list(value_list_base):

  __value_type__ = value_file
  
  def __init__(self, env = None, values = None):
    super(value_file_list, self).__init__(env = env, values = values)

check.register_class(value_file_list, include_seq = False)
