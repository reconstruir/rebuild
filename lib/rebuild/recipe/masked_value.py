#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.system import compat
from bes.common import bool_util, check_type, string_list, string_util
from bes.compat import StringIO
from bes.key_value import key_value, key_value_list
from bes.text import string_list_parser
from rebuild.base import build_system
from rebuild.step_manager import step_argspec
from .recipe_parser_util import recipe_parser_util

class masked_value(namedtuple('masked_value', 'mask,value')):

  def __new__(clazz, mask, value):
    return clazz.__bases__[0].__new__(clazz, mask, value)

  def __str__(self):
    return self.to_string(indent = 0)
  
  def to_string(self, depth = 0, indent = 0):
    if self.mask:
      return self._to_string_with_mask(depth, indent)
    else:
      return self._to_string_no_mask(depth, indent)
  
  def _to_string_no_mask(self, depth, indent):
    spaces = indent * ' '
    buf = StringIO()
    buf.write(spaces)
    self._write_value_to_buf(buf)
    return buf.getvalue()
      
  def _to_string_with_mask(self, depth, indent):
    spaces = indent * ' '
    buf = StringIO()
    buf.write(spaces)
    buf.write(self.mask)
    buf.write(': ')
    self._write_value_to_buf(buf)
    return buf.getvalue()
      
  def _write_value_to_buf(self, buf):
    if compat.is_int(self.value):
      buf.write(str(self.value))
    elif compat.is_string(self.value):
      buf.write(self.value)
    elif isinstance(self.value, bool):
      buf.write(str(self.value))
    elif isinstance(self.value, key_value_list):
      buf.write(self.value.to_string(delimiter = '=', value_delimiter = ' ', quote = True))
    elif string_list.is_string_list(self.value):
      buf.write(string_list.to_string(self.value, delimiter = ' ', quote = True))
    else:
      assert False
    
  @classmethod
  def parse_mask_and_value(clazz, text, argspec):
    mask, delimiter, value = text.partition(':')
    value = recipe_parser_util.parse_value(value.strip(), argspec)
    return clazz(mask, value)

  def mask_matches(self, system):
    return build_system.mask_matches(self.mask or 'all', system)
  
check_type.register_class(masked_value)
