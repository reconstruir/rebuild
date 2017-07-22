#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bes.common import variable

class entry(object):
  'A single pkg-config .pc file entry.'

  VARIABLE = 'variable'
  EXPORT = 'export'
  
  COLON = ':'
  EQUAL = '='

  def __init__(self, type, name, value):
    self._type = type
    self.name = name
    self.value = value

  def __str__(self):
    if self._type == self.VARIABLE:
      return '%s%s%s' % (self.name, self.EQUAL, self.value)
    else:
      if self.value:
        return '%s%s %s' % (self.name, self.COLON, self.value)
      else:
        return '%s%s' % (self.name, self.COLON)

  def __repr__(self):
    return self.__str__()
  
  def __eq__(self, entry):
    return cmp(self.__dict__, entry.__dict__) == 0

  @classmethod
  def parse(clazz, s):
    'Parse a pkg-config .pc file entry.'
    delimiter = clazz.__first_delimiter(s)
    if not delimiter:
      raise RuntimeError('No valid delimiter (: or =) found in \"%s\"' % (s))
    if delimiter == clazz.COLON:
      return clazz.__parse_export(s)
    else:
      return clazz.__parse_variable(s)

  def is_variable(self):
    return self._type == self.VARIABLE

  def is_export(self):
    return self._type == self.EXPORT

  def replace(self, replacements):
    self.value = variable.substitute(self.value, replacements)

  @classmethod
  def __first_delimiter(clazz, s):
    'Return which delimiter comes first in s (either : or =).'
    colon_index = s.find(clazz.COLON)
    equal_index = s.find(clazz.EQUAL)
    colon_found = colon_index >= 0
    equal_found = equal_index >= 0
    if colon_found and equal_found:
      if colon_index < equal_index:
        return clazz.COLON
      else:
        return clazz.EQUAL
    elif colon_found:
      return clazz.COLON
    elif equal_found:
      return clazz.EQUAL
    else:
      return None

  @classmethod
  def __parse_variable(clazz, s):
    v = s.partition(clazz.EQUAL)
    assert v[1] == clazz.EQUAL
    return clazz(clazz.VARIABLE, v[0].strip(), v[2].strip())

  @classmethod
  def __parse_export(clazz, s):
    v = s.partition(clazz.COLON)
    assert v[1] == clazz.COLON
    return clazz(clazz.EXPORT, v[0].strip(), v[2].strip())
