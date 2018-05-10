#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check

from .value_registry import value_registry
from .value_type import value_type

class value_factory(object):

  @classmethod
  def create_with_class_name(clazz, env, origin, text, value_class_name):
    check.check_recipe_load_env(env)
    check.check_value_origin(origin)
    check.check_string(text)
    check.check_string(value_class_name)
    value_class = clazz.get_class(value_class_name)
    return value_class.parse(env, origin, text)
  
  @classmethod
  def create_with_value_type(clazz, env, origin, text, vtype):
    check.check_value_type(vtype)
    value_class_name = value_type.value_to_name(vtype).lower()
    return clazz.create_with_class_name(env, origin, text, value_class_name)

  @classmethod
  def get_class(clazz, value_class_name):
    check.check_string(value_class_name)
    value_class = value_registry.get(value_class_name)
    if not value_class:
      raise TypeError('%s: unknown value class \"%s\"' % (origin, value_class_name))
    return value_class
