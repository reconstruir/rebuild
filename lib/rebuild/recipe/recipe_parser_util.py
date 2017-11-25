#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import bool_util, check_type, string_list
from bes.key_value import key_value, key_value_list
from rebuild.step_manager import step_argspec
from bes.text import string_list_parser

class recipe_parser_util(object):

  @classmethod
  def strip_comment(clazz, s):
    i = s.find('#')
    if i >= 0:
      return s[0:i]
    return s

  @classmethod
  def parse_key(clazz, text):
    'Parse only the key'
    check_type.check_string(text, 'text')
    key, _, _ = clazz.strip_comment(text).partition(':')
    return key.strip()

  @classmethod
  def parse_key_and_value(clazz, text, argspec):
    check_type.check_string(text, 'text')
    check_type.check_step_argspec(argspec, 'argspec')
    text = recipe_parser_util.strip_comment(text)
    key, delimiter, value = text.partition(':')
    key = key.strip()
    if not key:
      raise ValueError('Invalid step value key: \"%s\"' % (text))
    if not delimiter:
      return key_value(key, None)
    value = value.strip() or None
    if not value:
      return key_value(key, value)
    value = clazz.parse_value(value, argspec)
    return key_value(key, value)

  @classmethod
  def parse_value(clazz, value, argspec):
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
