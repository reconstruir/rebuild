#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, variable
from bes.key_value import key_value
from collections import namedtuple
from .entry_type import entry_type

class caca_entry(namedtuple('caca_entry', 'line,etype,value')):
  'A single pkg-config .pc file entry.'

  COLON = ':'
  EQUAL = '='

  def __new__(clazz, line, etype, value):
    check.check_text_line(line)
    check.check_entry_type(etype)
    if value:
      check.check_key_value(value)
    return clazz.__bases__[0].__new__(clazz, line, etype, value)
  
  def __str__(self):
    return self.line.text

  def __repr__(self):
    return str(self)
  
  @classmethod
  def parse(clazz, line):
    'Parse a pkg-config .pc file entry.'
    check.check_text_line(line)
    delimiter = clazz._first_delimiter(line.text_no_comments)
    value = None
    etype = None
    if delimiter == clazz.COLON:
      value = clazz._parse_value(line, delimiter)
      etype = entry_type.PROPERTY
    elif delimiter == clazz.EQUAL:
      value = clazz._parse_value(line, delimiter)
      etype = entry_type.VARIABLE
    elif not line.text.strip():
      etype = entry_type.BLANK
    else:
      etype = entry_type.COMMENT
    assert etype != None
    return clazz(line, etype, value)

  @property
  def is_variable(self):
    return self.etype == entry_type.VARIABLE

  @property
  def is_property(self):
    return self.etype == entry_type.PROPERTY

#  def replace(self, replacements):
#    self.value = variable.substitute(self.value, replacements)

  @classmethod
  def _first_delimiter(clazz, s):
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
  def _parse_value(clazz, line, delimiter):
    v = line.text_no_comments.partition(delimiter)
    assert v[1] == delimiter
    return key_value(v[0].strip(), v[2].strip())
check.register_class(caca_entry, name = 'caca_pkg_config_entry')
