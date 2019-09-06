#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import os
from bes.common.check import check
from bes.common.variable import variable

from .credentials import credentials
from .credentials_source import credentials_source

class credentials_source_env(credentials_source):

  def __init__(self, values):
    check.check_dict(values)
    self._values = values
  
  #@abstractmethod
  def is_valid(self):
    for key, value in self._values.items():
      found_vars = variable.find_variables(value)
      for v in found_vars:
        if not v in os.environ:
          return False
    return True

  #@abstractmethod
  def credentials(self):
    c = credentials('<env>')
    for key, value in self._values.items():
      setattr(c, key, value)
    return c
