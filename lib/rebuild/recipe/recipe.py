#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.compat import StringIO

class recipe(namedtuple('recipe', 'filename,enabled,properties,requirements,build_requirements,descriptor,instructions,steps')):

  def __new__(clazz, filename, enabled, properties, requirements, build_requirements,
              descriptor, instructions, steps):
    return clazz.__bases__[0].__new__(clazz, filename, enabled, properties, requirements,
                                      build_requirements, descriptor, instructions, steps)

  def __str__(self):
    return self.to_string(depth = 0, indent = 2)
  
  def to_string(self, depth = 0, indent = 2):
    spaces = depth * indent * ' '
    buf = StringIO()
    buf.write('enabled=')
    buf.write(self.enabled)
    buf.write('\n')
    buf.write('\nproperties\n')
    buf.write(self._properties_to_string(self.properties, depth = depth + 1, indent = indent))
    buf.write('\n')
    buf.write('\nrequirements\n')
    buf.write(self._requirements_to_string(self.requirements, depth = depth + 1, indent = indent))
    buf.write('\n')
    buf.write('\nbuild_requirements\n')
    buf.write(self._requirements_to_string(self.build_requirements, depth = depth + 1, indent = indent))
    buf.write('\n')
    return buf.getvalue()

  @classmethod
  def _properties_to_string(clazz, properties, depth = 0, indent = 2):
    spaces = depth * indent * ' '
    buf = StringIO()
    for key, value in sorted(properties.items()):
      buf.write(spaces)
      buf.write(key)
      buf.write('=')
      buf.write(value)
      buf.write('\n')
    return buf.getvalue().rstrip()

  @classmethod
  def _requirements_to_string(clazz, requirements, depth = 0, indent = 2):
    spaces = depth * indent * ' '
    buf = StringIO()
    for req in requirements:
      buf.write(spaces)
      buf.write(req.to_string_colon_format())
      buf.write('\n')
    return buf.getvalue().rstrip()
  
