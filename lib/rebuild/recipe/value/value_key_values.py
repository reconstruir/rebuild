#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from bes.key_value import key_value_list
from .value_base import value_base

class value_key_values(value_base):

  def __init__(self, env = None, values = None):
    super(value_key_values, self).__init__(env)
    values = values or key_value_list()
    check.check_key_value_list(values)
    self.values = values

  def __str__(self):
    return self.value_to_string()
    
  def __eq__(self, other):
    return self.values == other.values
    
  def value_to_string(self):
    return str(self.values)

  #@abstractmethod
  def sources(self):
    'Return a list of sources this caca provides or None if no sources.'
    return []

  #@abstractmethod
  def substitutions_changed(self):
    self.values.substitute_variables(self.substitutions)
  
  @classmethod
  #@abstractmethod
  def parse(clazz, env, value_filename, value):
    values = key_value_list.parse(value, options = key_value_list.KEEP_QUOTES)
    return clazz(env, values = values)
  
  @classmethod
  #@abstractmethod
  def default_value(clazz):
    return key_value_list()

check.register_class(value_key_values, include_seq = False)
