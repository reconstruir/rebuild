#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import check_type
from bes.compat import StringIO
from .masked_value_list import masked_value_list

class recipe_value(namedtuple('recipe_value', 'key,values')):

  def __new__(clazz, key, values):
    check_type.check_string(key, 'key')
    if not isinstance(values, masked_value_list):
      values = masked_value_list(values)
    check_type.check_masked_value_list(values, 'values')
    return clazz.__bases__[0].__new__(clazz, key, values)

  def __str__(self):
    return self.to_string(depth = 0, indent = 2)
  
  def to_string(self, depth = 0, indent = 2):
    if not self.values:
      return self._to_string_empty(depth, indent)
    elif len(self.values) == 1 and self.values[0].mask == None:
      return self._to_string_one_line(depth, indent)
    else:
      return self._to_string_multi_line(depth, indent)

  def _to_string_empty(self, depth, indent):
    assert len(self.values) == 0
    spaces = depth * indent * ' '
    buf = StringIO()
    buf.write(spaces)
    buf.write(self.key)
    buf.write(':')
    return buf.getvalue()
    
  def _to_string_one_line(self, depth, indent):
    assert len(self.values) == 1
    assert self.values[0].mask == None
    spaces = depth * indent * ' '
    buf = StringIO()
    buf.write(spaces)
    buf.write(self.key)
    buf.write(':')
    buf.write(' ')
    buf.write(self.values[0].value_to_string())
    return buf.getvalue()
      
  def _to_string_multi_line(self, depth, indent):
    assert len(self.values) > 0
    spaces = depth * indent * ' '
    buf = StringIO()
    buf.write(spaces)
    buf.write(self.key)
    buf.write('\n')
    for value in self.values:
      buf.write(spaces)
      buf.write(indent * ' ')
      buf.write(str(value))
      buf.write('\n')
    return buf.getvalue().strip()

  def resolve(self, system):
    return self.values.resolve(system)
  
check_type.register_class(recipe_value, include_seq = False)
