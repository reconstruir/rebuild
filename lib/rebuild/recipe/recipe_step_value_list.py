#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check_type

class recipe_step_value_list(object):

  def __init__(self):
    self._values = []

  def append(self, value):
    check_type.check_recipe_step_value(value, 'value')
    if self._values:
      expected_type = type(self._values[-1])
      actual_type = type(value)
      if expected_type != actual_type:
        raise TypeError('value should be of type %s instead of %s' % (expected_type, actual_type))
    self._values.append(value)

  def __len__(self):
    return len(self._values)
