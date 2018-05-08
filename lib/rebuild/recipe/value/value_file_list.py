#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, type_checked_list
from bes.compat import StringIO
from bes.text import string_list

from .value_base import value_base
from .value_file import value_file

class value_file_list(type_checked_list, value_base):

  __value_type__ = value_file
  
  def __init__(self, env = None, values = None):
    type_checked_list.__init__(self, values = values)
    value_base.__init__(self, env)

  #@abstractmethod
  def value_to_string(self, quote):
    buf = StringIO()
    for i, value in enumerate(self):
      if i != 0:
        buf.write(' ')
      buf.write(value.value_to_string(quote))
    return buf.getvalue()
    
  #@abstractmethod
  def substitutions_changed(self):
    for value in self:
      value.substitutions = self.substitutions
    
  @classmethod
  #@abstractmethod
  def parse(clazz, env, recipe_filename, value):
    result = clazz()
    filenames = string_list.parse(value, options = string_list.KEEP_QUOTES)
    for filename in filenames:
      rf = value_file.parse(env, recipe_filename, filename)
      result.append(rf)
    return result

  #@abstractmethod
  def sources(self):
    result = []
    for value in iter(self):
      result.extend(value.sources())
    return result
  
check.register_class(value_file_list, include_seq = False)
