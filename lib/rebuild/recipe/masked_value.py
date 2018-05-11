#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import check
from bes.compat import StringIO
from rebuild.base import build_system
from .recipe_parser_util import recipe_parser_util

from .value import value_bool
from .value import value_int
from .value import value_key_values
from .value import value_string
from .value import value_string_list

class masked_value(namedtuple('masked_value', 'mask, value')):

  def __new__(clazz, mask, value, origin = None):
    if not check.is_value_base(value):
      if check.is_bool(value):
        value = value_bool(env = None, origin = origin, value = value)
      elif check.is_int(value):
        value = value_int(env = None, origin = origin, value = value)
      elif check.is_string(value):
        value = value_string(env = None, origin = origin, value = value)
      elif check.is_string_list(value) or check.is_string_seq(value):
        value = value_string_list(env = None, origin = origin, values = value)
      elif check.is_key_value_list(value):
        value = value_key_values(env = None, origin = origin, values = value)

    if not check.is_value_base(value):
      raise TypeError('value should be subclass of value_base: %s - %s' % (str(value), type(value)))

    if origin:
      check.check_value_origin(origin)
    return clazz.__bases__[0].__new__(clazz, mask, value)

  def __str__(self):
    return self.to_string(depth = 0, indent = 2)
  
  def to_string(self, depth = 0, indent = 2, quote = True):
    if self.mask:
      return self._to_string_with_mask(depth, indent, quote)
    else:
      return self._to_string_no_mask(depth, indent, quote)

  def value_to_string(self, quote = True):
    return self.value.value_to_string(quote)
      
  def _to_string_no_mask(self, depth, indent, quote):
    spaces = depth * indent * ' '
    buf = StringIO()
    buf.write(spaces)
    buf.write(self.value_to_string(quote = quote))
    return buf.getvalue()
      
  def _to_string_with_mask(self, depth, indent, quote):
    spaces = depth * indent * ' '
    buf = StringIO()
    buf.write(spaces)
    buf.write(self.mask)
    buf.write(': ')
    buf.write(self.value_to_string(quote = quote))
    return buf.getvalue()

  @classmethod
  def parse_mask_and_value(clazz, env, origin, text, class_name):
    check.check_value_origin(origin)
    check.check_string(text)
    check.check_string(class_name)
    mask, delimiter, value = text.partition(':')
    value = recipe_parser_util.make_value(env, origin, value.strip(), class_name)
    return clazz(mask, value, origin)

  def mask_matches(self, system):
    return build_system.mask_matches(self.mask or 'all', system)
  
check.register_class(masked_value, include_seq = False)
