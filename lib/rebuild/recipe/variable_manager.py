#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.common import check, variable
from bes.system import user

class variable_manager(object):

  def __init__(self):
    self.variables = {}

  def add_variable(self, key, value):
    check.check_string(key)
    check.check_string(value)
    self.variables[key] = value
    
  def add_variables(self, kvl):
    check.check_key_value_list(kvl)
    self._add_system_variables()
    for kv in kvl:
      self.variables[kv.key] = kv.value
      
  def substitute(self, text, word_boundary = True):
    check.check_string(text)
    return variable.substitute(text, self.variables, word_boundary = word_boundary, patterns = variable.BRACKET)

  def _add_system_variables(self):
    self.variables['HOME'] = path.expanduser('~')
    self.variables['USER'] = user.USERNAME
  
check.register_class(variable_manager, include_seq = False)
