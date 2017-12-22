#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check_type, string_util
from collections import namedtuple
from .step_arg_type import step_arg_type

class step_arg_spec(namedtuple('step_arg_spec', 'name,atype,default,line_number')):
  
  def __new__(clazz, name, atype, default, line_number):
    check_type.check_string(name, 'name')
    check_type.check_step_arg_type(atype, 'atype')
    if default != None:
      check_type.check_string(default, 'default')
    check_type.check_int(line_number, 'line_number')
    return clazz.__bases__[0].__new__(clazz, name, atype, default, line_number)

  @classmethod
  def parse(clazz, text, line_number):
    if not text:
      return None
    parts = string_util.split_by_white_space(text, strip = True)
    if len(parts) < 2:
      raise RuntimeError('invalid arg spec: "%s"' % (text))
    name = parts[0]
    atype = parts[1].upper()
    if not step_arg_type.name_is_valid(atype):
      raise RuntimeError('invalid arg type: "%s"' % (atype))
    default = None
    if len(parts) > 2:
      default = ' '.join(parts[2:])
    return clazz(name, atype, default, line_number)