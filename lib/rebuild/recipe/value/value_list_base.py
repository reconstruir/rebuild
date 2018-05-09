#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, type_checked_list
from bes.compat import StringIO
from bes.text import string_list

from .value_base import value_base

class value_list_base(type_checked_list, value_base):

  def __init__(self, env = None, origin = None, values = None):
    type_checked_list.__init__(self, values = values)
    value_base.__init__(self, env, origin)

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
  def parse(clazz, env, origin, text):
    result = clazz(env = env, origin = origin)
    values = string_list.parse(text, options = string_list.KEEP_QUOTES)
    for value in values:
      rf = clazz.value_type().parse(env, origin, value)
      result.append(rf)
    return result

  @classmethod
  #@abstractmethod
  def default_value(clazz, arg_type):
    'Return the default value to use for this class.'
    return []

  #@abstractmethod
  def sources(self):
    result = []
    for value in self:
      result.extend(value.sources())
    return result

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, arg_type):
    'Resolve a list of list values by flattening it down to a single list.'
    check.check_seq(values, clazz)
    value_type = clazz.value_type()
    result = clazz()
    for value in values:
      check.check(value, clazz)
      result.extend(value._values)
    result.remove_dups()
    return result
  
check.register_class(value_list_base, include_seq = False)
