#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from collections import namedtuple
#
#from bes.compat import StringIO
#from bes.key_value import key_value_parser
#from bes.system import log
#from bes.text import tree_text_parser
#
#from rebuild.base import build_version, masked_config, requirement
#from rebuild.package_manager import package_descriptor
#from rebuild.step_manager import step_description
#

from collections import namedtuple
from bes.common import check_type

class recipe_step_value_key(namedtuple('recipe_step_value_key', 'key,value')):

  def __new__(clazz, key, value):
    return clazz.__bases__[0].__new__(clazz, key, value)

  @classmethod
  def parse(clazz, text):
    check_type.check_string(text, 'text')
    left, delimiter, right = text.partition(':')
    left = left.strip()
    if not left:
      raise ValueError('Invalid step value key: \"%s\"' % (text))
    if not delimiter:
      return clazz(left, None)
    right = right.strip() or None
    return clazz(left, right)
