#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from bes.key_value import key_value_list
from .value_base import value_base

class value_key_values(value_base):

  def __init__(self, env = None, origin = None, values = None):
    super(value_key_values, self).__init__(env, origin)
    values = values or key_value_list()
    check.check_key_value_list(values)
    self.values = values

  def __eq__(self, other):
    return self.values == other.values
    
  def __iter__(self):
    return iter(self.values)
    
  #@abstractmethod
  def value_to_string(self, quote):
    return self.values.to_string(delimiter = '=', value_delimiter = ' ', quote = quote)

  #@abstractmethod
  def sources(self):
    'Return a list of sources this caca provides or None if no sources.'
    return []

  #@abstractmethod
  def substitutions_changed(self):
    self.values.substitute_variables(self.substitutions)
  
  @classmethod
  #@abstractmethod
  def parse(clazz, env, origin, value):
    values = key_value_list.parse(value, options = key_value_list.KEEP_QUOTES)
    return clazz(env, origin = origin, values = values)
  
  @classmethod
  #@abstractmethod
  def default_value(clazz, arg_type):
    return key_value_list()

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, arg_type):
    'Resolve a list of values if this type into a nice dictionary.'
    result = key_value_list()
    seen = {}
    for value in values:
      check.check_value_key_values(value)
      check.check_key_value_list(value.values)
      for next_kv in value.values:
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
