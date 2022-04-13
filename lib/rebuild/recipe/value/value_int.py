#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.system.check import check

from .value_base import value_base
from .value_type import value_type
from .value_parsing import value_parsing

class value_int(value_base):

  def __init__(self, origin = None, value = None):
    super(value_int, self).__init__(origin)
    if value is not None:
      check.check_int(value)
    self.value = value

  def __eq__(self, other):
    if check.is_int(other):
      return self.value == other
    return self.value == other.value

#  def __int__(self):
#    return self.value
  
  #@abstractmethod
  def value_to_string(self, quote, include_properties = True):
    return str(self.value)

  #@abstractmethod
  def sources(self, recipe_env, variables):
    'Return a list of sources this caca provides or None if no sources.'
    return []

  #@abstractmethod
  def substitutions_changed(self):
    pass
  
  @classmethod
  #@abstractmethod
  def parse(clazz, origin, text, node):
    assert False
    if origin:
      check.check_value_origin(origin)
    check.check_node(node)
    value = int(text)
    return clazz(origin = origin, value = value)

  @classmethod
  #@abstractmethod
  def _parse_plain_string(clazz, origin, s):
    'Parse just a string.'
    try:
      return int(s)
    except Exception as ex:
      value_parsing.raise_error(origin, 'Not a valid int: \"%s\"' % (s))
      
  @classmethod
  #@abstractmethod
  def new_parse(clazz, origin, node):
    'Parse a value.'
    return clazz._new_parse_simple(value_int, origin, node)
  
  @classmethod
  #@abstractmethod
  def default_value(clazz, class_name):
    return None

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, class_name):
    'Resolve a list of values if this type into a nice dictionary.'
    assert class_name == value_type.INT
    return values[-1].value
  
check.register_class(value_int, include_seq = True)
