#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.compat import StringIO
from bes.common import check
from rebuild.base import build_system
from rebuild.step import step_arg_type
from bes.key_value import key_value_list
from .recipe_value_list import recipe_value_list
from .recipe_parser_util import recipe_parser_util

class recipe_step(namedtuple('recipe_step', 'name,description,values')):

  def __new__(clazz, name, description, values):
    check.check_string(name, 'name')
    check.check_step_description(description, 'description')
    if not check.is_recipe_value_list(values):
      values = recipe_value_list(values)
    check.check_recipe_value_list(values, 'values')
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
    args_definition = self.description.step_class.args_definition()
    for name, argspec in args_definition.items():
      if name not in result:
        if argspec.default != None:
          result[name] = recipe_parser_util.parse_value(argspec.default, '<default>', argspec.atype)
        else:
          result[name] = None
    return result

check.register_class(recipe_step, include_seq = False)
