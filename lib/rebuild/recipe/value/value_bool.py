#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common.bool_util import bool_util
from bes.common.check import check

from .value_base import value_base
from .value_type import value_type

class value_bool(value_base):

  def __init__(self, origin = None, value = False):
    super(value_bool, self).__init__(origin)
    check.check_bool(value)
    self.value = value

  def __eq__(self, other):
    if check.is_bool(other):
      return self.value == other
    return self.value == other.value
  
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

  @classmethod
  #@abstractmethod
  def _parse_plain_string(clazz, origin, s):
    'Parse just a string.'
    result = bool_util.parse_bool(s or False)
    return result
  
  @classmethod
  #@abstractmethod
  def new_parse(clazz, origin, node):
    'Parse a value.'
    clazz.log_d('new_parse: origin=%s' % (str(origin)))
    result = clazz._new_parse_simple(value_bool, origin, node)
    clazz.log_d('new_parse: result=%s' % (result))
    return result
  
  @classmethod
  #@abstractmethod
  def default_value(clazz, class_name):
    return False

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, class_name):
    'Resolve a list of values if this type into a nice dictionary.'
    clazz.log_d('resolve: values=%s; class_name=%s' % (values, class_name))
    assert class_name == value_type.BOOL
    result = values[-1].value
    clazz.log_d('resolve: result=%s' % (result))
    return result

check.register_class(value_bool, include_seq = True)
