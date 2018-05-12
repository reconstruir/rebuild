#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util
from bes.compat import StringIO

from .value_base import value_base
from .value_type import value_type
from .value_list_base import value_list_base

class value_file(value_base):

  def __init__(self, env = None, origin = None, filename = '', properties = None):
    'Class to manage a recipe file.'
    super(value_file, self).__init__(env, origin, properties = properties)
    check.check_string(filename)
    self._filename = filename

  @property
  def filename(self):
    return self.substitute(self._filename)
    
  def __eq__(self, other):
    return self._filename == other._filename
    
  #@abstractmethod
  def value_to_string(self, quote):
    buf = StringIO()
    buf.write(path.basename(self._filename))
    ps = self.properties_to_string()
    if ps:
      buf.write(' ')
      buf.write(ps)
    return buf.getvalue()

  @classmethod
  #@abstractmethod
  def default_value(clazz, class_name):
    'Return the default value to use for this class.'
    if class_name == value_type.FILE:
      return None
    elif class_name == value_type.FILE_LIST:
      return value_file_list()
    else:
      raise ValueError('Invalid value_type: %s' % (class_name))

  #@abstractmethod
  def sources(self):
    'Return a list of sources this caca provides or None if no sources.'
    return [ self.filename ]

  #@abstractmethod
  def substitutions_changed(self):
    pass
  
  @classmethod
  #@abstractmethod
  def parse(clazz, env, origin, value):
    base = path.dirname(origin.filename)
    filename, _, rest = string_util.partition_by_white_space(value)
    if filename.startswith('$'):
      filename_abs = filename
    else:
      filename_abs = path.abspath(path.join(base, filename))
      if not path.isfile(filename_abs):
        raise RuntimeError('%s: file not found: %s' % (origin, filename_abs))
    properties = clazz.parse_properties(rest)
    return value_file(env = env, origin = origin, filename = filename_abs, properties = properties)

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, class_name):
    check.check_value_file_seq(values)
    if class_name == value_type.FILE:
      return clazz._resolve_file(values)
    elif class_name == value_type.DIR:
      return clazz._resolve_file(values)
    elif class_name == value_type.FILE_LIST:
      return clazz._resolve_file_list(values)
    else:
      raise ValueError('Invalid value_type: %s' % (class_name))
  
  @classmethod
  def _resolve_file_list(clazz, values):
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
  
  @classmethod
  def _resolve_file(clazz, values):
    if not values:
      return None
    return values[-1]
  
check.register_class(value_file, include_seq = True)

class value_file_list(value_list_base):

  __value_type__ = value_file
  
  def __init__(self, env = None, origin = None, values = None):
    super(value_file_list, self).__init__(env = env, origin = origin, values = values)

check.register_class(value_file_list, include_seq = False)
