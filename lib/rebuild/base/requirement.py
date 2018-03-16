#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check
from collections import namedtuple
from bes.compat import StringIO

from .requirement_hardness import requirement_hardness

class requirement(namedtuple('requirement', 'name,operator,version,system_mask,hardness')):

  def __new__(clazz, name, operator, version, system_mask = None, hardness = None):
    assert name
    assert name == str(name)
    name = str(name)
    if operator:
      assert operator == str(operator)
      operator = str(operator)
    if version:
      assert version == str(version)
      version = str(version)
    if system_mask:
      assert system_mask == str(system_mask)
      system_mask = str(system_mask)
    if hardness:
      hardness = requirement_hardness(hardness)
      check.check_requirement_hardness(hardness)
    return clazz.__bases__[0].__new__(clazz, name, operator, version, system_mask, hardness)

  def __str__(self):
    buf = StringIO()
    if self.hardness:
      buf.write(str(self.hardness))
      buf.write(' ')
    buf.write(self.name)
    if self.system_mask and self.system_mask != 'all':
      buf.write('(')
      buf.write(self.system_mask)
      buf.write(')')
    if self.operator:
      buf.write(' ')
      buf.write(self.operator)
      buf.write(' ')
      buf.write(self.version)
    return buf.getvalue()

  def to_string_colon_format(self):
    req_no_system_mask = requirement(self.name, self.operator, self.version, None)
    return '%s: %s' % (self.system_mask or 'all', str(req_no_system_mask))

  def clone_replace_hardness(self, hardness):
    l = list(self)
    l[4] = hardness
    return self.__class__(*l)

  def hardness_matches(self, hardness):
    'Return True if hardness matches.'
    hardness = requirement_hardness(hardness)
    if not self.hardness:
      return hardness == requirement_hardness.DEFAULT
    return self.hardness == hardness
  
check.register_class(requirement)
