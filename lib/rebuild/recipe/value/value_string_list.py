#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from bes.text import string_list

from .value_base import value_base
from .value_type import value_type

class value_string_list(value_base):

  def __init__(self, origin = None, values = None):
    super(value_string_list, self).__init__(origin)
    values = values or string_list()
    if not check.is_string_list(values):
      values = string_list(values)
    check.check_string_list(values)
    self.values = values

  def __eq__(self, other):
    if check.is_string_seq(other):
      return self.values == other
    return self.values == other.values
    
  def __iter__(self):
    return iter(self.values)
    
  #@abstractmethod
  def value_to_string(self, quote, include_properties = True):
    return self.values.to_string(delimiter = ' ', quote = quote)

  #@abstractmethod
  def sources(self, recipe_env):
    'Return a list of sources this caca provides or None if no sources.'
    return []

  #@abstractmethod
  def substitutions_changed(self):
    self.values.substitute_variables(self.substitutions)
  
  @classmethod
  #@abstractmethod
  def parse(clazz, origin, text, node):
    if origin:
      check.check_value_origin(origin)
    check.check_node(node)
    if not text:
      values = string_list()
    else:
      values = string_list.parse(text, options = string_list.KEEP_QUOTES)
    return clazz(origin = origin, values = values)
  
  @classmethod
  #@abstractmethod
  def default_value(clazz, class_name):
    return string_list()

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, class_name):
    'Resolve a list of values if this type into a nice dictionary.'
    if class_name != value_type.STRING_LIST:
      values_string = [ str(x) for x in values ]
      print('WARNING: %s: class_name should be %s instead of %s for %s' % (values[0].origin, value_type.value_to_name(value_type.STRING_LIST),
                                                                         value_type.value_to_name(class_name), values_string))
      assert False
      return clazz.default_value(class_name)
      #raise TypeError('class_name should be %s instead of %d' % (value_type.STRING_LIST, class_name))
    result = string_list()
    for value in values:
      check.check_value_string_list(value)
      result.extend(value.values)
    result.remove_dups()
    return result
  
check.register_class(value_string_list, include_seq = False)
