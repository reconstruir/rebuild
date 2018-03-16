#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum import enum
#from bes.common import string_util
#from bes.text import comments
#from collections import namedtuple

class requirement_hardness(enum):
  # Requirement needed at runtime.
  RUN = 1

  # Requirement is tool needed at build time.
  TOOL = 2

  # Requirement is library needed at build time.
  BUILD = 3
    
  DEFAULT = RUN

  '''
  @classmethod
  def parse(clazz, text):
    result = []
    text = comments.strip_multi_line(text, strip_head = True, strip_tail = True, remove_empties = False)
    lines = text.split('\n')
    for i, line in enumerate(lines):
      next_parsed_line = clazz._parse_line(line, i + 1)
      if next_parsed_line:
        result.append(next_parsed_line)
    return result

  _parsed_line = namedtuple('_parsed_line', 'name,argspec,default,line_number')
      
  @classmethod
  def _parse_line(clazz, line, line_number):
    if not line:
      return None
    parts = string_util.split_by_white_space(line, strip = True)
    if len(parts) < 2:
      raise RuntimeError('invalid argspec - "%s"' % (line))
    name = parts[0]
    argspec = parts[1]
    if not clazz.name_is_valid(argspec.upper()):
      raise RuntimeError('invalid argspec %s -  "%s"' % (argspec, line))
    default = None
    if len(parts) > 2:
      default = ' '.join(parts[2:])
    return clazz._parsed_line(name, argspec, default, line_number)
'''
  
