#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check_type
from bes.system import compat
from rebuild.base import build_system

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

  def resolve(self, system):
    if not self._values:
      raise IndexError('list is empty')
    first_value = self._values[0].value
    if compat.is_int(first_value):
      return self._resolve_int(system)
    elif compat.is_string(first_value):
      return self._resolve_string(system)
    elif isinstance(first_value, bool):
      return self._resolve_bool(system)
    elif isinstance(first_value, key_value_list):
      return self._resolve_key_values(system)
    elif string_list.is_string_list(first_value):
      return self._resolve_string_list(system)
    else:
      assert False

  def _resolve_int(self, system):
    result = None
    for value in self._values:
      if build_system.mask_matches(value.system_mask, system):
        result = value.value
    return result
