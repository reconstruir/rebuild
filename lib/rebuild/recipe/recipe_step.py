#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.compat import StringIO
from bes.common import check_type
from .recipe_value_list import recipe_value_list
from rebuild.base import build_system
from rebuild.step import step_arg_type
from bes.key_value import key_value_list

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
    assert build_system.system_is_valid(system)
    result = {}
    for value in self.values:
      result.update({ value.key: value.resolve(system) })
    return result
    for name, argspec in self.description.argspec.items():
      if name not in result:
        result[name] = self._DEFAULT_VALUES[argspec]
    return result

  _DEFAULT_VALUES = {
    step_arg_type.BOOL: False,
    step_arg_type.INT: 0,
    step_arg_type.KEY_VALUES: key_value_list(),
    step_arg_type.STRING_LIST: [],
    step_arg_type.STRING: None,
    step_arg_type.HOOK_LIST: [],
    step_arg_type.FILE_LIST: [],
  }
  
check_type.register_class(recipe_step, include_seq = False)
