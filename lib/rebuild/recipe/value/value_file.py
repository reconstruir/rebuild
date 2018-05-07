#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util, type_checked_list
from bes.compat import StringIO
from bes.key_value import key_value_list
from bes.text import string_list
from .value_base import value_base

class value_file(value_base):

  def __init__(self, env = None, filename = '', properties = None):
    'Class to manage a recipe file.'
    super(value_file, self).__init__(env, properties = properties)
    check.check_string(filename)
    self.filename = filename

  def __eq__(self, other):
    return self.filename == other.filename
    
  #@abstractmethod
  def value_to_string(self, quote):
    buf = StringIO()
    buf.write(path.basename(self.filename))
    ps = self.properties_to_string()
    if ps:
      buf.write(' ')
      buf.write(ps)
    return buf.getvalue()
    
  #@abstractmethod
  def sources(self):
    'Return a list of sources this caca provides or None if no sources.'
    return [ self.filename ]

  #@abstractmethod
  def substitutions_changed(self):
    self.filename = self.substitute(self.filename)
  
  @classmethod
  #@abstractmethod
  def parse(clazz, env, recipe_filename, value):
    base = path.dirname(recipe_filename)
    filename, _, rest = string_util.partition_by_white_space(value)
    filename_abs = path.join(base, filename)
    if not path.isfile(filename_abs):
      raise RuntimeError('file not found: %s' % (filename_abs))
    properties = key_value_list.parse(rest, options = key_value_list.KEEP_QUOTES)
    return value_file(env = env, filename = filename_abs, properties = properties)
  
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
  
check.register_class(value_file, include_seq = False)
check.register_class(value_file_list, include_seq = False)
