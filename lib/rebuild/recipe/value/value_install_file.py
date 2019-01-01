#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.common import algorithm, check, string_util
from bes.compat import StringIO
from bes.dependency import dependency_provider
from bes.fs import file_find

from .value_base import value_base
from .value_list_base import value_list_base

_install_file = namedtuple('_install_file', 'filename, dst_filename')
class value_install_file(value_base):

  def __init__(self, origin = None, value = None, properties = None):
    super(value_install_file, self).__init__(origin, properties = properties)
    if value:
      assert isinstance(value, _install_file)
    self.value = value

  def __hash__(self):
    return hash(self.value)
    
  def __eq__(self, other):
    return self.value == other.value

  @property
  def filename(self):
    return self.substitute(self.value.filename)
  
  @property
  def dst_filename(self):
    return self.substitute(self.value.dst_filename)
  
  #@abstractmethod
  def value_to_string(self, quote, include_properties = True):
    buf = StringIO()
    buf.write(path.basename(self.value.filename))
    buf.write(' ')
    buf.write(self.value.dst_filename)
    self._append_properties_string(buf, include_properties)
    return buf.getvalue()

  @classmethod
  #@abstractmethod
  def default_value(clazz, class_name):
    'Return the default value to use for this class.'
    return value_install_file_list()

  #@abstractmethod
  def sources(self, recipe_env):
    'Return a list of sources this value provides or None if no sources.'
    if path.isdir(self.filename):
      return file_find.find(self.filename, relative = False)
    else:
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
    value = _install_file(filename, dst_filename)
    return clazz(origin = origin, value = value, properties = properties)

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, class_name):
    check.check_value_install_file_seq(values)
    result_values = []
    for value in values:
      check.check_value_install_file(value)
      result_values.append(value)
    result = value_install_file_list(value = result_values)
    result.remove_dups()
    return result
  
check.register_class(value_install_file, include_seq = True)

class value_install_file_list(value_list_base):

  __value_type__ = value_install_file
  
  def __init__(self, origin = None, value = None):
    super(value_install_file_list, self).__init__(origin = origin, value = value)

check.register_class(value_install_file_list, include_seq = False)
