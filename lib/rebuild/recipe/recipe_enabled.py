#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.system.check import check

from .recipe_error import recipe_error

class recipe_enabled(namedtuple('recipe_enabled', 'origin, expression')):

  def __new__(clazz, origin, expression):
    check.check_value_origin(origin)
    check.check_string(expression)
    return clazz.__bases__[0].__new__(clazz, origin, expression)

  def parse_expression(self, build_target):
    check.check_build_target(build_target)
    try:
      return build_target.parse_expression(self.expression)
    except Exception as ex:
      raise recipe_error(str(ex), self.origin.filename, self.origin.line_number)

check.register_class(recipe_enabled, include_seq = False)
  
