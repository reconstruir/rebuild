#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import check
from bes.compat import StringIO
from rebuild.base import build_system

from .value_parsing import value_parsing

class masked_value(namedtuple('masked_value', 'mask, value')):

  def __new__(clazz, mask, value, origin = None):
    check.check_value_base(value)
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
    return self.value.value_to_string(quote = quote)
      
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
    buf.write(value_parsing.MASK_DELIMITER)
    buf.write(' ')
    buf.write(self.value_to_string(quote = quote))
    return buf.getvalue()

  def mask_matches(self, system):
    return build_system.mask_matches(self.mask or 'all', system)
  
check.register_class(masked_value, include_seq = False)
