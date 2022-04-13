#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.common.node import node
from bes.text.string_list import string_list
from bes.text.white_space import white_space
from collections import namedtuple

class instruction(namedtuple('instruction', 'name,flags,requires')):

  def __new__(clazz, name, flags, requires):
    flags = flags or {}
    requires = requires or set()
    check.check_string(name)
    check.check_dict(flags, key_type = check.STRING_TYPES, value_type = string_list)
    check.check_set(requires, entry_type = check.STRING_TYPES)
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
