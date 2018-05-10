#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check
from bes.compat import StringIO
from .recipe_value import recipe_value

class recipe_value_list(object):

  def __init__(self, values = None):
    self._values = []
    for value in values or []:
      check.check_recipe_value(value)
      self._values.append(value)

  def __iter__(self):
    return iter(self._values)

  def __getitem__(self, i):
    return self._values[i]
  
  def __setitem__(self, i, value):
    check.check_recipe_value(value)
    self._values[i] = value

  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self._values == other._values
    elif isinstance(other, list):
      return self._values == other
    else:
      raise TypeError('other should be of recipe_value_list or list type instead of %s' % (type(other)))
    
  def __str__(self):
    buf = StringIO()
    for value in self._values:
      buf.write(str(value))
      buf.write(';')
    return buf.getvalue()
    
  def append(self, value):
    check.check_recipe_value(value)
    self._values.append(value)

  def extend(self, values):
    for value in values:
      self.append(value)

  def __len__(self):
    return len(self._values)

  def resolve(self, system, args_definition):
    result = {}
    for value in self._values:
      assert value.key in args_definition
      result[value.key] = value.resolve(system, args_definition[value.key].class_name)
    return result
  
check.register_class(recipe_value_list, include_seq = False)
