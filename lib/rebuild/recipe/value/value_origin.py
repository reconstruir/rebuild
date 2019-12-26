#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple
from bes.common.check import check

class value_origin(namedtuple('value_origin', 'filename, line_number, text, recipe_text')):
  'Class to keep track of the origin of a value.  Mostly useful for error reporting.'
  
  def __new__(clazz, filename, line_number, text, recipe_text = ''):
    filename = path.relpath(filename)
    check.check_string(filename)
    check.check_int(line_number)
    check.check_string(text)
    check.check_string(recipe_text)
    return clazz.__bases__[0].__new__(clazz, filename, line_number, text, recipe_text)

  def __str__(self):
    return '%s:%s' % (self.filename, self.line_number)
  
  def __repr__(self):
    return str(self)

  @classmethod
  def get_origin(clazz, obj):
    origin = getattr(obj, '_origin', None)
    if not origin:
      raise ValueError('origin not set: {}'.format(str(obj)))
    return origin

  @classmethod
  def set_origin(clazz, obj, origin):
    check.check_value_origin(origin)
    setattr(obj, '_origin', origin)
  
check.register_class(value_origin)
