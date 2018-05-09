#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import bool_util, check
from bes.key_value import key_value
from rebuild.recipe.value import value_type, value_hook
from bes.text import comments, string_list

from .value import value_bool
from .value import value_file
from .value import value_file_list
from .value import value_git_address
from .value import value_install_file
from .value import value_int
from .value import value_key_values
from .value import value_source_dir
from .value import value_source_tarball
from .value import value_string

class recipe_parser_util(object):

  @classmethod
  def parse_key(clazz, text):
    'Parse only the key'
    check.check_string(text)
    key, _, _ = comments.strip_line(text).partition(':')
    return key.strip()

  @classmethod
  def parse_key_and_value(clazz, env, recipe_filename, text, arg_type):
    check.check_recipe_load_env(env)
    check.check_string(recipe_filename)
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
    value = clazz.parse_value(env, recipe_filename, value, arg_type)
    return key_value(key, value)

  @classmethod
  def parse_value(clazz, env, recipe_filename, value, arg_type):
    check.check_recipe_load_env(env)
    check.check_string(recipe_filename)
    check.check_string(value)
    check.check_value_type(arg_type)
    if arg_type == value_type.BOOL:
      return value_bool.parse(env, recipe_filename, value)
    elif arg_type == value_type.INT:
      return value_int.parse(env, recipe_filename, value)
    elif arg_type == value_type.KEY_VALUES:
      return value_key_values.parse(env, recipe_filename, value)
    elif arg_type == value_type.STRING_LIST:
      return clazz._parse_string_list(value)
    elif arg_type == value_type.STRING:
      return value_string.parse(env, recipe_filename, value)
    elif arg_type == value_type.HOOK_LIST:
      return value_hook.parse(env, recipe_filename, value)
    elif arg_type == value_type.FILE_LIST:
      return value_file_list.parse(env, recipe_filename, value)
    elif arg_type == value_type.FILE:
      return value_file.parse(env, recipe_filename, value)
    elif arg_type == value_type.DIR:
      return clazz._parse_dir(env, value, path.dirname(recipe_filename))
    elif arg_type == value_type.INSTALL_FILE:
      return value_install_file.parse(env, recipe_filename, value)
    elif arg_type == value_type.GIT_ADDRESS:
      return value_git_address.parse(env, recipe_filename, value)
    elif arg_type == value_type.SOURCE_TARBALL:
      return value_source_tarball.parse(env, recipe_filename, value)
    elif arg_type == value_type.SOURCE_DIR:
      return value_source_dir.parse(env, recipe_filename, value)
    raise ValueError('unknown arg_type: %s' % (str(arg_type)))

  @classmethod
  def value_default(clazz, arg_type):
    if arg_type == value_type.BOOL:
      return value_bool.default_value(arg_type)
    elif arg_type == value_type.INT:
      return value_int.default_value(arg_type)
    elif arg_type == value_type.KEY_VALUES:
      return value_key_values.default_value(arg_type)
    elif arg_type == value_type.STRING_LIST:
      return string_list()
    elif arg_type == value_type.STRING:
      return value_string.default_value(arg_type)
    elif arg_type == value_type.HOOK_LIST:
      return value_hook.default_value(arg_type)
    elif arg_type == value_type.FILE_LIST:
      return value_file_list.default_value(arg_type)
    elif arg_type == value_type.FILE:
      return value_file.default_value(arg_type)
    elif arg_type == value_type.DIR:
      return None
    elif arg_type == value_type.INSTALL_FILE:
      return value_install_file.default_value(arg_type)
    elif arg_type == value_type.GIT_ADDRESS:
      return value_git_address.default_value(arg_type)
    elif arg_type == value_type.SOURCE_TARBALL:
      return value_source_tarball.default_value(arg_type)
    elif arg_type == value_type.SOURCE_DIR:
      return value_source_dir.default_value(arg_type)
    raise ValueError('unknown arg_type: %s' % (str(arg_type)))

  @classmethod
  def _parse_string_list(clazz, value):
    if not value:
      return []
    return string_list.parse(value, options = string_list.KEEP_QUOTES)

  @classmethod
  def _parse_dir(clazz, env, value, base):
    if value.startswith('$'):
      filename_abs = value
    else:
      filename_abs = path.join(base, value)
#    if not path.isdir(filename_abs):
#      raise RuntimeError('dir not found: %s' % (filename_abs))
    return value_file(env = env, filename = filename_abs)
  
