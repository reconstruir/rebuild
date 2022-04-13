#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.system.check import check
from bes.common.variable import variable
from bes.system.user import user

class variable_manager(object):

  def __init__(self):
    self.variables = {}
    self._add_system_variables()

  def __str__(self):
    return str(self.variables)

  def add_variable(self, key, value):
    check.check_string(key)
    check.check_string(value)
    self.variables[key] = value
    
  def add_variables(self, variables):
    if check.is_key_value_list(variables):
      for kv in variables:
        self.variables[kv.key] = kv.value
    elif check.is_dict(variables):
      for key, value in variables.items():
        self.variables[key] = value
    else:
      raise ValueError('Unknown variables type: %s' % (type(variables)))
      
  def substitute(self, text, word_boundary = True):
    check.check_string(text)
    return variable.substitute(text, self.variables)

  def _add_system_variables(self):
    self.variables['HOME'] = path.expanduser('~')
    self.variables['USER'] = user.USERNAME
  
check.register_class(variable_manager, include_seq = False)
