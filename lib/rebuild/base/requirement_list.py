#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from bes.compat import StringIO
#from .key_value_parser import key_value_parser
#from .key_value import key_value
from bes.common import check, type_checked_list
#from bes.text import string_lexer_options
from .requirement import requirement

class requirement_list(type_checked_list):

  def __init__(self, values = None):
    super(key_value_list, self).__init__(key_value, values = values)

  @classmethod
  def cast_entry(clazz, entry):
    if isinstance(entry, tuple):
      return requirement(*entry)
    return entry
  
  def to_string(self, delimiter = ' '):
    buf = StringIO()
    first = True
    for req in iter(self):
      if not first:
        buf.write(delimiter)
      first = False
      buf.write(str(req))
    return buf.getvalue()
    
  def __str__(self):
    return self.to_string()

#  @classmethod
#  def parse(clazz, text, options = 0):
#    check.check_string(text)

check.register_class(requirement_list, include_seq = False)
