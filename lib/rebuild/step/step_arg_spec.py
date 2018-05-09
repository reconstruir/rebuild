#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, string_util
from bes.text import comments
from collections import namedtuple
from rebuild.recipe.value import value_type

class step_arg_spec(namedtuple('step_arg_spec', 'name, atype, default, line_number')):
  
  def __new__(clazz, name, atype, default, line_number):
    check.check_string(name)
    check.check_value_type(atype)
    if check.is_string(atype):
      atype = value_type.name_to_value(atype)
    if default != None:
      check.check_string(default)
    check.check_int(line_number)
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
    if not value_type.name_is_valid(atype):
      raise RuntimeError('invalid arg type "%s"' % (atype))
    default = None
    if len(parts) > 2:
      default = ' '.join(parts[2:])
    return clazz(name, atype, default, line_number)

  @classmethod
  def parse_many(clazz, text):
    result = {}
    text = comments.strip_multi_line(text, strip_head = True, strip_tail = True, remove_empties = False)
    lines = text.split('\n')
    for i, line in enumerate(lines):
      if line:
        spec = clazz.parse(line, i + 1)
        if spec.name in result:
          raise ValueError('duplicate arg spec: %s' % (spec.name))
        result[spec.name] = spec
    return result
  
