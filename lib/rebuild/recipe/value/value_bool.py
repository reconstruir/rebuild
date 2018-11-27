#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import bool_util, check

from .value_base import value_base
from .value_type import value_type
from .value_parsing import value_parsing
from .value_origin import value_origin

class value_bool(value_base):

  def __init__(self, origin = None, value = False):
    super(value_bool, self).__init__(origin)
    check.check_bool(value)
    self.value = value

  def __eq__(self, other):
    if check.is_bool(other):
      return self.value == other
    return self.value == other.value

#  def __bool__(self):
#    return self.value
#  
#  __nonzero__ = __bool__
    
  #@abstractmethod
  def value_to_string(self, quote, include_properties = True):
    return str(self.value)

  #@abstractmethod
  def sources(self, recipe_env):
    'Return a list of sources this caca provides or None if no sources.'
    return []

  #@abstractmethod
  def substitutions_changed(self):
    pass
  
  @classmethod
  #@abstractmethod
  def parse(clazz, origin, text, node):
    if origin:
      check.check_value_origin(origin)
    check.check_node(node)
    value = bool_util.parse_bool(text)
    return clazz(origin = origin, value = value)

  @classmethod
  #@abstractmethod
  def new_parse(clazz, origin, node):
    'Parse a value.'
    result = []
    text = node.data.text_no_comments
    if ':' in text:
      pv = value_parsing.parse_key_value(origin, text)
      pv = clazz._parsed_value_to_bool_value(pv)
      key = pv.key
      result.append(pv)
    else:
      key = text.strip()
    for child in node.children:
      child_origin = value_origin(origin.filename, child.data.line_number, child.data.text)
      child_text = child.data.text_no_comments
      cpv = value_parsing.parse_mask_and_value(child_origin, key, child_text)
      cpv = clazz._parsed_value_to_bool_value(cpv)
      result.append(cpv)
    return result
  
  @classmethod
  #@abstractmethod
  def default_value(clazz, class_name):
    return False

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, class_name):
    'Resolve a list of values if this type into a nice dictionary.'
    assert class_name == value_type.BOOL
    return values[-1].value

  @classmethod
  def _parsed_value_to_bool_value(clazz, pv):
    'Parse a value.'
    value = bool_util.parse_bool(pv.value or 'False')
    return value_parsing.parsed_value(pv.mask, pv.key, value)
  
check.register_class(value_bool, include_seq = True)
