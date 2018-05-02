#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import check
from bes.text import string_list
from bes.compat import StringIO
from bes.key_value import key_value, key_value_list
from rebuild.base import build_system
from rebuild.value import value_type
from .recipe_parser_util import recipe_parser_util

class masked_value(namedtuple('masked_value', 'mask,value')):

  def __new__(clazz, mask, value):
    if (not check.is_string(value) and not check.is_string_list(value)) and check.is_string_seq(value):
      value = string_list(value)
    if not clazz.value_type_is_valid(value):
      raise TypeError('invalid value type: %s - %s' % (str(value), type(value)))
    return clazz.__bases__[0].__new__(clazz, mask, value)

  def __str__(self):
    return self.to_string(depth = 0, indent = 2)
  
  def to_string(self, depth = 0, indent = 2, quote = True):
    if self.mask:
      return self._to_string_with_mask(depth, indent, quote)
    else:
      return self._to_string_no_mask(depth, indent, quote)

  def value_to_string(self, quote = True):
    if check.is_int(self.value):
      return str(self.value)
    elif check.is_string(self.value):
      return self.value
    elif check.is_bool(self.value):
      return str(self.value)
    elif check.is_key_value_list(self.value):
      return self.value.to_string(delimiter = '=', value_delimiter = ' ', quote = quote)
    elif check.is_string_list(self.value):
      return self.value.to_string(delimiter = ' ', quote = quote)
    elif check.is_hook_list(self.value):
      return str(self.value)
    elif check.is_recipe_install_file_list(self.value):
      return ' '.join([ h.value_to_string() for h in self.value ])
    elif check.is_recipe_file_list(self.value):
      return str(self.value)
    elif check.is_recipe_file(self.value):
      return str(self.value)
    elif check.is_git_address(self.value):
      return str(self.value)
    else:
      assert False

  _VALUE_TYPE_CHECKERS = [
    check.is_int,
    check.is_string,
    check.is_bool,
    check.is_key_value_list,
    check.is_string_list,
    check.is_hook_list,
    check.is_recipe_file,
    check.is_recipe_file_list,
    check.is_recipe_install_file_list,
    check.is_recipe_install_file_list,
    check.is_git_address,
  ]
      
  @classmethod
  def value_type_is_valid(clazz, v):
    for checker in clazz._VALUE_TYPE_CHECKERS:
      if checker(v):
        return True
    return False
    
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
  def parse_mask_and_value(clazz, env, recipe_filename, text, argspec):
    mask, delimiter, value = text.partition(':')
    value = recipe_parser_util.parse_value(env, recipe_filename, value.strip(), argspec)
    return clazz(mask, value)

  def mask_matches(self, system):
    return build_system.mask_matches(self.mask or 'all', system)
  
check.register_class(masked_value, include_seq = False)
