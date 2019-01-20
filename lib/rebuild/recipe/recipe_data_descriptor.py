#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import check, string_util

from .recipe_error import recipe_error

class recipe_data_descriptor(namedtuple('recipe_data_descriptor', 'name, version, origin')):

  def __new__(clazz, name, version, origin = None):
    check.check_string(name)
    check.check_string(version)
    check.check_value_origin(origin, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, name, version, origin)

  def __hash__(self):
    return hash( ( self.name, self.version ) )
  
  def __str__(self):
    return '@DATA:{name}:{version}'.format(name = self.name, version = self.version)
  
  @classmethod
  def parse(clazz, text, origin = None):
    check.check_string(text)
    if not text.startswith('@DATA:'):
      raise ValueError('recipe_data_descriptor should start with @DATA: "%s"' % (text))
    s = string_util.remove_head(text, '@DATA:')
    parts = s.split(':')
    if len(parts) != 2:
      raise ValueError('recipe_data_descriptor should have 2 parts: "%s"' % (text))
    return recipe_data_descriptor(parts[0], parts[1], origin)

check.register_class(recipe_data_descriptor, include_seq = False)
  
