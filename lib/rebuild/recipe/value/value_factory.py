#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check

from .value_registry import value_registry

class value_factory(object):

  @classmethod
  def create_with_class_name(clazz, origin, text, value_class_name):
    check.check_value_origin(origin)
    check.check_string(text)
    check.check_string(value_class_name)
    value_class = clazz.get_class(value_class_name)
    return value_class.parse(origin, text)
  
  @classmethod
  def get_class(clazz, value_class_name):
    check.check_string(value_class_name)
    value_class = value_registry.get(value_class_name)
    if not value_class:
      raise TypeError('unknown value_class_name \"%s\"' % (value_class_name))
    return value_class
