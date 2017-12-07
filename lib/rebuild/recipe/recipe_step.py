#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.compat import StringIO
from bes.common import check_type
from .recipe_value_list import recipe_value_list

class recipe_step(namedtuple('recipe_step', 'name,description,values')):

  def __new__(clazz, name, description, values):
    check_type.check_string(name, 'name')
    check_type.check_step_description(description, 'description')
    if not check_type.is_recipe_value_list(values):
      values = recipe_value_list(values)
    check_type.check_recipe_value_list(values, 'values')
    return clazz.__bases__[0].__new__(clazz, name, description, values)

  def __str__(self):
    return self.to_string(depth = 0, indent = 2)

  def to_string(self, depth, indent):
    spaces = depth * indent * ' '
    buf = StringIO()
    buf.write(spaces)
    buf.write(self.name)
    buf.write('\n')
    for value in self.values:
      buf.write(spaces)
      buf.write(indent * ' ')
      buf.write(value.to_string(depth = depth + 1))
      buf.write('\n')
    return buf.getvalue().strip()

  def resolve_values(self, system):
    result = {}
    for value in self.values:
      print('CACA value: %s' % (str(value)))
      resolved = value.resolve(system)
      print('CACA resolved: %s' % (resolved))
      result.update(value.resolve(system))
    return result
  
check_type.register_class(recipe_step, include_seq = False)
