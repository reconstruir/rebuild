#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import bool_util, check_type
from rebuild.step_manager import step_argspec

class recipe_step_value_key(namedtuple('recipe_step_value_key', 'key,value')):

  def __new__(clazz, key, value):
    return clazz.__bases__[0].__new__(clazz, key, value)

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
      return clazz(key, None)
    value = value.strip() or None
    if not value:
      return clazz(key, value)
    value = clazz._parse_value(value, argspec)
    return clazz(key, value)
  
  @classmethod
  def _parse_value(clazz, value, argspec):
    if argspec == step_argspec.BOOL:
      return bool_util.parse_bool(value)
    elif argspec == step_argspec.INT:
      return int(value)
    elif argspec == step_argspec.MASKED_KEY_VALUES:
      assert False
    elif argspec == step_argspec.MASKED_STRING_LIST:
      assert False
    elif argspec == step_argspec.STRING:
      return value
    assert False
    
  @classmethod
  def _strip_comment(clazz, s):
    i = s.find('#')
    if i >= 0:
      return s[0:i]
    return s
