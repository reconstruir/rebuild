#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import bool_util, check_type
from bes.key_value import key_value
from bes.text import string_list_parser
from rebuild.step_manager import step_argspec

class recipe_step_value(namedtuple('recipe_step_value', 'system_mask,key,value')):

  def __new__(clazz, system_mask, key, value):
    return clazz.__bases__[0].__new__(clazz, system_mask, key, value)

  @classmethod
  def parse(clazz, text, argspec):
    check_type.check_string(text, 'text')
    check_type.check_step_argspec(argspec, 'argspec')
    text = clazz._strip_comment(text)
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
  
  @classmethod
  def _parse_value(clazz, value, argspec):
    if argspec == step_argspec.BOOL:
      return bool_util.parse_bool(value)
    elif argspec == step_argspec.INT:
      return int(value)
    elif argspec == step_argspec.KEY_VALUES:
      assert False
    elif argspec == step_argspec.STRING_LIST:
      return string_list_parser.parse_to_list(value, options = string_list_parser.KEEP_QUOTES)
    elif argspec == step_argspec.STRING:
      return value
    assert False
    
  @classmethod
  def _strip_comment(clazz, s):
    i = s.find('#')
    if i >= 0:
      return s[0:i]
    return s

  @classmethod
  def parse_key(clazz, text):
    'Parse only the key'
    check_type.check_string(text, 'text')
    key, _, _ = clazz._strip_comment(text).partition(':')
    return key.strip()

  @classmethod
  def parse_system_mask(clazz, text):
    system_mask, delimiter, _ = text.partition(':')
    if delimiter == ':' and system_mask:
      return system_mask
    return None
check_type.register_class(recipe_step_value)
