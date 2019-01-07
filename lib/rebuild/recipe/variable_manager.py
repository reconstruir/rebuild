#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, variable

class variable_manager(object):

  def __init__(self):
    self.variables = {}

  def add_variables(self, kvl):
    check.check_key_value_list(kvl)
    for kv in kvl:
      self.variables[kv.key] = kv.value
      
  def substitute(self, text, word_boundary = True):
    check.check_string(text)
    return variable.substitute(text, self.variables, word_boundary = word_boundary)
  
check.register_class(variable_manager, include_seq = False)
