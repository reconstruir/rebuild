#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.common.type_checked_list import type_checked_list
from bes.compat.StringIO import StringIO
from rebuild.base import build_system

from .value_factory import value_factory

class masked_value_list(object):

  def __init__(self, values = None):
    self._values = []
    for value in values or []:
      check.check_masked_value(value)
      self._values.append(value)

  def __iter__(self):
    return iter(self._values)

  def __getitem__(self, i):
    return self._values[i]
  
  def __setitem__(self, i, value):
    check.check_masked_value(value)
    self._values[i] = value

  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self._values == other._values
    elif isinstance(other, list):
      return self._values == other
    else:
      raise TypeError('other should be of masked_value_list type instead of %s' % (type(other)))
    
  def __str__(self):
    buf = StringIO()
    for value in self._values:
      buf.write(str(value))
      buf.write(';')
    return buf.getvalue()
    
  def append(self, value):
    check.check_masked_value(value)
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

  def resolve(self, system, class_name):
    if not self._values:
      return None
    
    values = self._resolve_values_by_mask(system)
      
    if not values:
      return None

    if not check.is_value_base(values[0]):
      raise TypeError('value should be subclass of value_base: %s - %s' % (str(values[0]), type(values[0])))

    value_class = value_factory.get_class(class_name)
    
    return value_class.resolve(values, class_name)

  def _resolve_values_by_mask(self, system):
    result = []
    for i, value in enumerate(self._values):
      if value.mask_matches(system):
        result.append(value.value)
    return result

check.register_class(masked_value_list, include_seq = False)
