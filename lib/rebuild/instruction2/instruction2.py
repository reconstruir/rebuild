#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, node
from bes.text import white_space
from collections import namedtuple

class instruction2(namedtuple('instruction2', 'name,flags,requires')):

  def __new__(clazz, name, flags, requires):
    flags = flags or {}
    requires = requires or set()
    check.check_string(name, 'name')
    check.check_dict(flags, 'flags', key_type = check.STRING_TYPES, value_type = check.STRING_TYPES)
    check.check_set(requires, 'requires', entry_type = check.STRING_TYPES)
    return clazz.__bases__[0].__new__(clazz, name, flags, requires)

  def __str__(self):
    return self.to_string()

  def to_string(self, depth = 0, indent = 2):
    s = self._to_node().to_string(depth = depth, indent = indent).strip()
    return white_space.shorten_multi_line_spaces(s)
  
  def _to_node(self):
    'A convenient way to make a recipe string is to build a graph first.'
    root = node(self.name)
    for key, value in sorted(self.flags.items()):
      root.add_child(key).add_child(value)
    requires_node = root.add_child('requires')
    for req in sorted(self.requires):
      requires_node.add_child(req)
    return root
  
'''
import re
from bes.common import algorithm, dict_util, object_util, string_util
from bes.system import compat
from bes.compat import StringIO

class instruction2(object):

  def __init__(self, name, flags, requires):
    if not string_util.is_string(name):
      raise RuntimeError('name should be a string: %s' % (name))
    self.name = name
    if not isinstance(flags, dict):
      raise RuntimeError('flags should be a dict: %s' % (flags))
    if not dict_util.is_homogeneous(flags, compat.STRING_TYPES, compat.STRING_TYPES):
      raise RuntimeError('invalid flags.  all keys and values should be strings: %s' % (flags))
    self.flags = flags
    if not isinstance(requires, set):
      raise RuntimeError('requires should be a set: %s' % (requires))
    self.requires = requires

  def __str__(self):
    buf = StringIO()
    buf.write('name: ')
    buf.write(self.name)
    buf.write('\n')
    for key in sorted(self.flags.keys()):
      buf.write(key)
      buf.write(': ')
      buf.write(self.flags[key])
      buf.write('\n')
    buf.write('requires: ')
    buf.write(' '.join(self.requires))
    return buf.getvalue()

  def __eq__(self, other):
    return self.__dict__ == other.__dict__
'''
