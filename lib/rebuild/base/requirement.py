#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check
from collections import namedtuple
from bes.compat import StringIO

class requirement(namedtuple('requirement', 'name,operator,version,system_mask')):

  def __new__(clazz, name, operator, version, system_mask = None):
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
    return clazz.__bases__[0].__new__(clazz, name, operator, version, system_mask)

  def __str__(self):
    buf = StringIO()
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

check.register_class(requirement)
