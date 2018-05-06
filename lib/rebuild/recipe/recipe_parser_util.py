#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import bool_util, check, object_util, string_util
from bes.key_value import key_value, key_value_list
from rebuild.recipe.value import value_type, hook_list
from bes.text import comments, string_list
from .value_file import value_file, value_file_list
from .recipe_install_file import recipe_install_file, recipe_install_file_list

from .value import value_git_address
from .value import value_source_tarball

class recipe_parser_util(object):

  @classmethod
  def parse_key(clazz, text):
    'Parse only the key'
    check.check_string(text)
    key, _, _ = comments.strip_line(text).partition(':')
    return key.strip()

  @classmethod
  def parse_key_and_value(clazz, env, value_filename, text, arg_type):
    check.check_recipe_load_env(env)
    check.check_string(value_filename)
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
    value = clazz.parse_value(env, value_filename, value, arg_type)
    return key_value(key, value)

  @classmethod
  def parse_value(clazz, env, value_filename, value, arg_type):
    check.check_recipe_load_env(env)
    check.check_string(value_filename)
    check.check_string(value)
    check.check_value_type(arg_type)
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
      return hook_list.parse(value)
    elif arg_type == value_type.FILE_LIST:
      return value_file_list.parse(value, value_filename)
    elif arg_type == value_type.FILE:
      return value_file.parse(value, value_filename)
    elif arg_type == value_type.DIR:
      return clazz._parse_dir(value, path.dirname(value_filename))
    elif arg_type == value_type.FILE_INSTALL_LIST:
      if value_filename:
        base = path.dirname(value_filename)
      else:
        base = None
      return clazz._parse_file_install_list(value, base)
    elif arg_type == value_type.GIT_ADDRESS:
      return value_git_address.parse(env, value_filename, value)
    elif arg_type == value_type.SOURCE_TARBALL:
      return value_source_tarball.parse(env, value_filename, value)
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
      return hook_list()
    elif arg_type == value_type.FILE_LIST:
      return value_file_list()
    elif arg_type == value_type.FILE:
      return None
    elif arg_type == value_type.DIR:
      return None
    elif arg_type == value_type.FILE_INSTALL_LIST:
      return recipe_install_file_list()
    elif arg_type == value_type.GIT_ADDRESS:
      return value_git_address.default_value()
    elif arg_type == value_type.SOURCE_TARBALL:
      return value_source_tarball.default_value()
    raise ValueError('unknown arg_type: %s' % (str(arg_type)))

  @classmethod
  def _parse_string_list(clazz, value):
    if not value:
      return []
    return string_list.parse(value, options = string_list.KEEP_QUOTES)

  @classmethod
  def _parse_dir(clazz, value, base):
    if value.startswith('$'):
      filename_abs = value
    else:
      filename_abs = path.join(base, value)
#    if not path.isdir(filename_abs):
#      raise RuntimeError('dir not found: %s' % (filename_abs))
    return value_file(filename_abs)

  @classmethod
  def _parse_file_install_list(clazz, value, base):
    result = recipe_install_file_list()
    data = clazz._parse_string_list(value)
    if (len(data) % 2) != 0:
      raise RuntimeError('invalid non even list: %s' % (data))
    for filename, dst_filename in object_util.chunks(data, 2):
      if False: #base:
        filename_abs = path.abspath(path.join(base, filename))
      else:
        filename_abs = filename
#      if not path.isfile(filename_abs):
#        raise RuntimeError('not found: %s' % (filename_abs))
      result.append(recipe_install_file(filename_abs, dst_filename))
    return result
  
