#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import check_type

class recipe_value(namedtuple('recipe_value', 'key,values')):

  def __new__(clazz, key, values):
    check_type.check_string(key, 'values')
    check_type.check_masked_value_list(values, 'values')
    return clazz.__bases__[0].__new__(clazz, key, value)

  def __str__(self):
    return self.to_string(depth = 0, indent = 0)
  
  def to_string(self, depth = 0, indent = 0):
    spaces = indent * ' '
    buf = StringIO()
    buf.write(spaces)
    buf.write(self.key)
    buf.write(':')
    buf.write(' ')
    for value in self.values:
      buf.write(value.to_string())
    return buf.getvalue()
      
check_type.register_class(recipe_value)
