#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import bool_util, check, object_util
from bes.key_value import key_value, key_value_list
from rebuild.step import hook_registry
from rebuild.value import value_type
from bes.text import comments, string_list
from .recipe_file import recipe_file
from .recipe_install_file import recipe_install_file

class recipe_parser_util(object):

  @classmethod
  def parse_key(clazz, text):
    'Parse only the key'
    check.check_string(text)
    key, _, _ = comments.strip_line(text).partition(':')
    return key.strip()

  @classmethod
  def parse_key_and_value(clazz, text, filename, arg_type):
    check.check_string(text)
    check.check_value_type(arg_type)
    text = comments.strip_line(text)
    key, delimiter, value = text.partition(':')
    key = key.strip()
    if not key:
      raise ValueError('Invalid step value key: \"%s\"' % (text))
    if not delimiter:
      return key_value(key, None)
    value = value.strip() or None
    if not value:
      return key_value(key, value)
    value = clazz.parse_value(value, filename, arg_type)
    return key_value(key, value)

  @classmethod
  def parse_value(clazz, value, filename, arg_type):
    if arg_type == value_type.BOOL:
      return bool_util.parse_bool(value)
    elif arg_type == value_type.INT:
      return int(value)
    elif arg_type == value_type.KEY_VALUES:
      return key_value_list.parse(value, options = key_value_list.KEEP_QUOTES)
    elif arg_type == value_type.STRING_LIST:
      return clazz._parse_string_list(value)
    elif arg_type == value_type.STRING:
      return value
    elif arg_type == value_type.HOOK_LIST:
      return clazz._parse_hook_list(value)
    elif arg_type == value_type.FILE_LIST:
      return clazz._parse_file_list(value, path.dirname(filename))
    elif arg_type == value_type.FILE_INSTALL_LIST:
      if filename:
        base = path.dirname(filename)
      else:
        base = None
      return clazz._parse_file_install_list(value, base)
    raise ValueError('unknown arg_type: %s' % (str(arg_type)))

  @classmethod
  def value_default(clazz, arg_type):
    if arg_type == value_type.BOOL:
      return False
    elif arg_type == value_type.INT:
      return None
    elif arg_type == value_type.KEY_VALUES:
      return key_value_list()
    elif arg_type == value_type.STRING_LIST:
      return string_list()
    elif arg_type == value_type.STRING:
      return None
    elif arg_type == value_type.HOOK_LIST:
      return []
    elif arg_type == value_type.FILE_LIST:
      return []
    elif arg_type == value_type.FILE_INSTALL_LIST:
      return []
    raise ValueError('unknown arg_type: %s' % (str(arg_type)))

  @classmethod
  def _parse_string_list(clazz, value):
    if not value:
      return []
    return string_list.parse(value, options = string_list.KEEP_QUOTES)

  @classmethod
  def _parse_hook_list(clazz, value):
    hooks = []
    names = clazz._parse_string_list(value)
    for name in names:
      hook_class = hook_registry.get(name)
      if not hook_class:
        raise RuntimeError('hook class not found: %s' % (name))
      hook = hook_class()
      hooks.append(hook)
    return hooks

  @classmethod
  def _parse_file_list(clazz, value, base):
    files = []
    filenames = clazz._parse_string_list(value)
    for filename in filenames:
      filename_abs = path.join(base, filename)
      if not path.isfile(filename_abs):
        raise RuntimeError('not found: %s' % (filename_abs))
      files.append(recipe_file(filename_abs))
    return files

  @classmethod
  def _parse_file_install_list(clazz, value, base):
    result = []
    data = clazz._parse_string_list(value)
    if (len(data) % 2) != 0:
      raise RuntimeError('invalid non even list: %s' % (data))
    for filename, dst_filename in object_util.chunks(data, 2):
      if base:
        filename_abs = path.abspath(path.join(base, filename))
      else:
        filename_abs = filename
#      if not path.isfile(filename_abs):
#        raise RuntimeError('not found: %s' % (filename_abs))
      result.append(recipe_install_file(filename_abs, dst_filename))
    return result
  
