#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from bes.key_value import key_value_list
from .value_base import value_base

class value_key_values(value_base):

  def __init__(self, origin = None, value = None):
    super(value_key_values, self).__init__(origin)
    value = value or key_value_list()
    check.check_key_value_list(value)
    self.value = value

  def __eq__(self, other):
    return self.value == other.value
    
  def __iter__(self):
    return iter(self.value)
    
  #@abstractmethod
  def value_to_string(self, quote, include_properties = True):
    return self.value.to_string(delimiter = '=', value_delimiter = ' ', quote = quote)

  #@abstractmethod
  def sources(self, recipe_env):
    'Return a list of sources this caca provides or None if no sources.'
    return []

  #@abstractmethod
  def substitutions_changed(self):
    self.value.substitute_variables(self.substitutions)
  
  @classmethod
  #@abstractmethod
  def parse(clazz, origin, value, node):
    #assert False
    if origin:
      check.check_value_origin(origin)
    check.check_node(node)
    values = key_value_list.parse(value, options = key_value_list.KEEP_QUOTES)
    return clazz(origin = origin, value = values)

  @classmethod
  #@abstractmethod
  def _parse_plain_string(clazz, origin, s):
    'Parse just a string.'
    return key_value_list.parse(s, options = key_value_list.KEEP_QUOTES)
  
  @classmethod
  #@abstractmethod
  def xnew_parse(clazz, origin, node):
    'Parse a value.'
    return clazz._new_parse_simple(value_key_values, origin, node)
  
  @classmethod
  #@abstractmethod
  def default_value(clazz, class_name):
    return key_value_list()

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, class_name):
    'Resolve a list of values if this type into a nice dictionary.'
    result = key_value_list()
    seen = {}
    for value in values:
      check.check_value_key_values(value)
      check.check_key_value_list(value.value)
      for next_kv in value.value:
        check.check_key_value(next_kv)
        i = len(result)
        seen_i = seen.get(next_kv.key, None)
        if seen_i is not None:
          result[seen_i] = next_kv
        else:
          result.append(next_kv)
          seen[next_kv.key] = i
    return result
  
check.register_class(value_key_values, include_seq = False)
