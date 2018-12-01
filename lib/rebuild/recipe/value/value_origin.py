#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import check

class value_origin(namedtuple('value_origin', 'filename, line_number, text, recipe_text')):
  'Class to keep track of the origin of a value.  Mostly useful for error reporting.'
  
  def __new__(clazz, filename, line_number, text, recipe_text = ''):
    check.check_string(filename)
    check.check_int(line_number)
    check.check_string(text)
    check.check_string(recipe_text)
    return clazz.__bases__[0].__new__(clazz, filename, line_number, text, recipe_text)

  def __str__(self):
    return '%s:%s' % (self.filename, self.line_number)
  
  def __repr__(self):
    return str(self)

check.register_class(value_origin)
