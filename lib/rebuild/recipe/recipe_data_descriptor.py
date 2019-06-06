#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from collections import namedtuple
from bes.common.check import check
from bes.common.string_util import string_util

from .recipe_error import recipe_error

class recipe_data_descriptor(namedtuple('recipe_data_descriptor', 'name, version, origin')):

  RE_PATTERN = '@\{DATA:(.+?):(.+?)\}'
  RE_PATTERN_EXACT = '^{pattern}$'.format(pattern = RE_PATTERN)
  
  def __new__(clazz, name, version, origin = None):
    check.check_string(name)
    check.check_string(version)
    check.check_value_origin(origin, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, name, version, origin)

  def __hash__(self):
    return hash( ( self.name, self.version ) )
  
  def __str__(self):
    return '@{{DATA:{name}:{version}}}'.format(name = self.name, version = self.version)

  @classmethod
  def is_data_descriptor(clazz, text):
    return re.match(clazz.RE_PATTERN_EXACT, text) != None
  
  @classmethod
  def parse(clazz, text, origin = None):
    check.check_string(text)
    found = re.findall(clazz.RE_PATTERN_EXACT, text)
    if not found or len(found) != 1:
      raise ValueError('Not a valid data descriptor: "%s"' % (text))
    return recipe_data_descriptor(found[0][0], found[0][1], origin)

  @classmethod
  def find(self, text, origin = None):
    result = []
    for found in re.findall(recipe_data_descriptor.RE_PATTERN, text):
      result.append(recipe_data_descriptor(found[0], found[1], origin))
    return result
  
check.register_class(recipe_data_descriptor, include_seq = False)
