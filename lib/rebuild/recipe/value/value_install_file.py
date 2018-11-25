#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import algorithm, check, string_util
from bes.compat import StringIO
from bes.dependency import dependency_provider
from .value_base import value_base
from .value_list_base import value_list_base

class value_install_file(value_base):

  def __init__(self, origin = None, filename = '', dst_filename = '', properties = None):
    super(value_install_file, self).__init__(origin, properties = properties)
    self._filename = filename
    self._dst_filename = dst_filename

  def __eq__(self, other):
    return self._filename == other._filename and self._dst_filename == other._dst_filename

  @property
  def filename(self):
    return self.substitute(self._filename)
  
  @property
  def dst_filename(self):
    return self.substitute(self._dst_filename)
  
  #@abstractmethod
  def value_to_string(self, quote, include_properties = True):
    buf = StringIO()
    buf.write(path.basename(self._filename))
    buf.write(' ')
    buf.write(self._dst_filename)
    self._append_properties_string(buf, include_properties)
    return buf.getvalue()

  @classmethod
  #@abstractmethod
  def default_value(clazz, class_name):
    'Return the default value to use for this class.'
    return value_install_file_list()

  #@abstractmethod
  def sources(self, recipe_env):
    'Return a list of sources this caca provides or None if no sources.'
    return [ self.filename ]

  #@abstractmethod
  def substitutions_changed(self):
    pass

  @classmethod
  #@abstractmethod
  def parse(clazz, origin, text, node):
    if origin:
      check.check_value_origin(origin)
    check.check_node(node)
    parts = string_util.split_by_white_space(text)
    if len(parts) < 2:
      raise ValueError('%s: expected filename and dst_filename instead of: %s' % (origin, text))
    filename = parts[0]
    dst_filename = parts[1]
    rest = text.replace(filename, '')
    rest = rest.replace(dst_filename, '')
    properties = clazz.parse_properties(rest)
    return clazz(origin = origin, filename = filename, dst_filename = dst_filename, properties = properties)

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, class_name):
    check.check_value_install_file_seq(values)
    result_values = []
    for value in values:
      check.check_value_install_file(value)
      result_values.append(value)
    result = value_install_file_list(values = result_values)
    result.remove_dups()
    return result
  
check.register_class(value_install_file, include_seq = True)

class value_install_file_list(value_list_base):

  __value_type__ = value_install_file
  
  def __init__(self, origin = None, values = None):
    super(value_install_file_list, self).__init__(origin = origin, values = values)

check.register_class(value_install_file_list, include_seq = False)
