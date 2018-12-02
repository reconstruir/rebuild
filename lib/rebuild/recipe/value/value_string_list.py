#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from bes.text import string_list

from .value_base import value_base
from .value_type import value_type

class value_string_list(value_base):

  def __init__(self, origin = None, value = None):
    super(value_string_list, self).__init__(origin)
    values = value or string_list()
    if not check.is_string_list(values):
      values = string_list(values)
    check.check_string_list(values)
    self.value = values

  def __eq__(self, other):
#    if check.is_string_seq(other):
#      return self.value == other
    return self.value == other.value
    
  def __iter__(self):
    return iter(self.value)
    
  #@abstractmethod
  def value_to_string(self, quote, include_properties = True):
    return self.value.to_string(delimiter = ' ', quote = quote)

  #@abstractmethod
  def sources(self, recipe_env):
    'Return a list of sources this caca provides or None if no sources.'
    return []

  #@abstractmethod
  def substitutions_changed(self):
    self.value.substitute_variables(self.substitutions)
  
  @classmethod
  #@abstractmethod
  def parse(clazz, origin, text, node):
    #assert False
    if origin:
      check.check_value_origin(origin)
    check.check_node(node)
    if not text:
      values = string_list()
    else:
      values = string_list.parse(text, options = string_list.KEEP_QUOTES)
    return clazz(origin = origin, value = values)

  @classmethod
  #@abstractmethod
  def _parse_plain_string(clazz, origin, s):
    'Parse just a string.'
    return string_list.parse(s, options = string_list.KEEP_QUOTES)
  
  @classmethod
  #@abstractmethod
  def xnew_parse(clazz, origin, node):
    'Parse a value.'
    return clazz._new_parse_simple(value_string_list, origin, node)

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
      result.extend(value.value)
    result.remove_dups()
    return result
  
check.register_class(value_string_list, include_seq = False)
