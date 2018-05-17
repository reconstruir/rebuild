#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, type_checked_list
from bes.compat import StringIO
from bes.text import string_list

from .value_base import value_base

class value_list_base(type_checked_list, value_base):

  def __init__(self, env = None, origin = None, values = None, properties = None):
    type_checked_list.__init__(self, values = values)
    value_base.__init__(self, env, origin, properties = properties)

  #@abstractmethod
  def value_to_string(self, quote, include_properties = True):
    buf = StringIO()
    ps = None
    for i, value in enumerate(self):
      if i != 0:
        buf.write(' ')
      buf.write(value.value_to_string(quote, include_properties = False))
      if ps is None:
        ps = value.properties_to_string()
    if include_properties and ps:
      buf.write(' ')
      buf.write(ps)
    return buf.getvalue()
    
  #@abstractmethod
  def substitutions_changed(self):
    for value in self:
      value.substitutions = self.substitutions
    
  @classmethod
  #@abstractmethod
  def parse(clazz, env, origin, text):
    strings = string_list.parse(text, options = string_list.KEEP_QUOTES)
    string_values, properties_text = clazz._split_values_and_properties(strings)
    values = []
    for string_value in string_values:
      value_text = string_value + ' ' + properties_text
      value = clazz.value_type().parse(env, origin, value_text)
      values.append(value)
    return clazz(env = env, origin = origin, values = values)

  @classmethod
  #@abstractmethod
  def default_value(clazz, class_name):
    'Return the default value to use for this class.'
    return clazz()

  #@abstractmethod
  def sources(self):
    result = []
    for value in self:
      result.extend(value.sources())
    return result

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, class_name):
    'Resolve a list of list values by flattening it down to a single list.'
    if not check.is_seq(values, clazz):
      raise TypeError('%s: should be a sequence of %s instead of %s - %s' % (values[0].origin, clazz, str(values), type(values)))
    value_type = clazz.value_type()
    result = clazz()
    for value in values:
      check.check(value, clazz)
      result.extend(value._values)
    result.remove_dups()
    return result

  @classmethod
  def _split_values_and_properties(clazz, l):
    values = []
    properties = []
    for v in l:
      if '=' in v:
        properties.append(v)
      else:
        values.append(v)
    return ( values, ' '.join(properties) )
  
check.register_class(value_list_base, include_seq = False)
