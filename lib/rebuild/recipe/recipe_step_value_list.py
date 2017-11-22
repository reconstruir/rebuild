#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check_type

class recipe_step_value_list(object):

  def __init__(self):
    self._values = []

  def __iter__(self):
    return iter(self._values)

  def __getitem__(self, i):
    return self._values[i]
  
  def __setitem__(self, i, value):
    check_type.check_recipe_step_value(value, 'value')
    self._values[i] = value

  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self._values == other._values
    elif isinstance(other, list):
      return self._values == other
    else:
      raise TypeError('other should be of recipe_step_value_list type instead of %s' % (type(other)))
    
  def append(self, value):
    check_type.check_recipe_step_value(value, 'value')
    if self._values:
      expected_type = type(self._values[-1])
      actual_type = type(value)
      if expected_type != actual_type:
        raise TypeError('value should be of type %s instead of %s' % (expected_type, actual_type))
    self._values.append(value)

  def extend(self, values):
    for value in values:
      self.append(value)

  def __len__(self):
    return len(self._values)
