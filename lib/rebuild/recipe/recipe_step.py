#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.compat import StringIO
from bes.common import check
from bes.key_value import key_value_list
from .recipe_value_list import recipe_value_list
from .recipe_parser_util import recipe_parser_util

from .value import value_origin
from .value import value_type

class recipe_step(namedtuple('recipe_step', 'name,description,values')):

  def __new__(clazz, name, description, values):
    check.check_string(name)
    check.check_step_description(description)
    if not check.is_recipe_value_list(values):
      values = recipe_value_list(values)
    check.check_recipe_value_list(values)
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

  def resolve_values(self, substitutions, env):
    check.check_dict(substitutions)
    check.check_recipe_load_env(env)
    args_definition = self.description.step_class.args_definition()
    result = {}
    for value in self.values:
      assert value.key in args_definition
      class_name = args_definition[value.key].class_name
      result.update({ value.key: value.resolve(env.build_target.system, class_name) })
      
    for name, arg_def in args_definition.items():
      if name not in result:
        if arg_def.default is not None:
          origin = value_origin('<default>', arg_def.line_number, arg_def.default)
          value = recipe_parser_util.parse_value(env, origin, arg_def.default, arg_def.class_name)
          check.check_value_base(value)
          result[name] = value.resolve([ value ], arg_def.class_name)
        else:
          result[name] = recipe_parser_util.value_default(arg_def.class_name)
          
    for key, value in result.items():
      if check.is_value_base(value):
        value.substitutions = substitutions
          
    return result

check.register_class(recipe_step, include_seq = False)
