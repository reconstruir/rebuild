#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from bes.text import string_list

from .value_base import value_base
from .value_type import value_type

class value_string_list(value_base):

  def __init__(self, env = None, values = None):
    super(value_string_list, self).__init__(env)
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
  def value_to_string(self, quote):
    return self.values.to_string(delimiter = ' ', quote = quote)

  #@abstractmethod
  def sources(self):
    'Return a list of sources this caca provides or None if no sources.'
    return []

  #@abstractmethod
  def substitutions_changed(self):
    self.values.substitute_variables(self.substitutions)
  
  @classmethod
  #@abstractmethod
  def parse(clazz, env, recipe_filename, text):
    if not text:
      values = string_list()
    else:
      values = string_list.parse(text, options = string_list.KEEP_QUOTES)
    return clazz(env, values = values)
  
  @classmethod
  #@abstractmethod
  def default_value(clazz, arg_type):
    return string_list()

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, arg_type):
    'Resolve a list of values if this type into a nice dictionary.'
    if arg_type != value_type.STRING_LIST:
      values_string = [ str(x) for x in values ]
      print('FUCK: arg_type should be %s instead of %d for %s' % (value_type.STRING_LIST, arg_type, values_string))
      return clazz.default_value(arg_type)
      #raise TypeError('arg_type should be %s instead of %d' % (value_type.STRING_LIST, arg_type))
    result = string_list()
    for value in values:
      check.check_value_string_list(value)
      result.extend(value.values)
    result.remove_dups()
    return result
  
check.register_class(value_string_list, include_seq = False)