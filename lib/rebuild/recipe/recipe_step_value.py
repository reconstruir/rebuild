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

class recipe_step_value(namedtuple('recipe_step_value', 'mask,key,value')):

  def __new__(clazz, mask, key, value):
    return clazz.__bases__[0].__new__(clazz, mask, key, value)

  @classmethod
  def parse(clazz, text, argspec):
    check_type.check_string(text, 'text')
    check_type.check_step_argspec(argspec, 'argspec')
    text = recipe_parser_util.strip_comment(text)
    key, delimiter, value = text.partition(':')
    key = key.strip()
    if not key:
      raise ValueError('Invalid step value key: \"%s\"' % (text))
    if not delimiter:
      return clazz(None, key, None)
    value = value.strip() or None
    if not value:
      return clazz(None, key, value)
    value = clazz._parse_value(value, argspec)
    return clazz(None, key, value)

  def __str__(self):
    return self.to_string(indent = 2)
  
  def to_string(self, depth = 0, indent = 2):
    if self.mask:
      return self._to_string_with_mask(depth, indent)
    else:
      return self._to_string_no_mask(depth, indent)
  
  def _to_string_no_mask(self, depth, indent):
    buf = StringIO()
    buf.write(self.key)
    buf.write(':')
    buf.write(' ')
    self._write_value_to_buf(buf)
    return buf.getvalue()
      
  def _to_string_with_mask(self, depth, indent):
    spaces = indent * ' '
    buf = StringIO()
    buf.write(self.key)
    buf.write('\n')
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
  def _parse_value(clazz, value, argspec):
    if argspec == step_argspec.BOOL:
      return bool_util.parse_bool(value)
    elif argspec == step_argspec.INT:
      return int(value)
    elif argspec == step_argspec.KEY_VALUES:
      return key_value_list.parse(value, options = key_value_list.KEEP_QUOTES)
    elif argspec == step_argspec.STRING_LIST:
      return string_list_parser.parse_to_list(value, options = string_list_parser.KEEP_QUOTES)
    elif argspec == step_argspec.STRING:
      return value
    assert False
    
  @classmethod
  def parse_mask(clazz, text):
    mask, delimiter, _ = text.partition(':')
    if delimiter == ':' and mask:
      return mask
    return None
  
  @classmethod
  def parse_mask_and_value(clazz, key, text, argspec):
    mask, delimiter, value = text.partition(':')
    value = clazz._parse_value(value.strip(), argspec)
    return clazz(mask, key, value)

  def mask_matches(self, system):
    return build_system.mask_matches(self.mask or 'all', system)
  
check_type.register_class(recipe_step_value)
