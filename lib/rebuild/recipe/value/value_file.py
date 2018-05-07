#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util, type_checked_list
from bes.compat import StringIO
from bes.key_value import key_value_list
from bes.dependency import dependency_provider
from bes.text import string_list

class value_file(dependency_provider):

  def __init__(self, filename, properties = None):
    'Class to manage a recipe file.'
    check.check_string(filename)
    properties = properties or key_value_list()
    check.check_key_value_list(properties)
    self.filename = filename
    self.properties = properties

  def __str__(self):
    return self.value_to_string()
    
  def value_to_string(self):
    buf = StringIO()
    buf.write(path.basename(self.filename))
    if self.properties:
      buf.write(' ')
      buf.write(self.properties.to_string(value_delimiter = ' ', quote = True))
    return buf.getvalue()
    
  def provided(self):
    'Return a list of dependencies provided by this provider.'
    return [ self.filename ]

  @classmethod
  def parse(clazz, value, value_filename):
    base = path.dirname(value_filename)
    filename, _, rest = string_util.partition_by_white_space(value)
    filename_abs = path.join(base, filename)
    if not path.isfile(filename_abs):
      raise RuntimeError('file not found: %s' % (filename_abs))
    properties = key_value_list.parse(rest, options = key_value_list.KEEP_QUOTES)
    return value_file(filename_abs, properties)
  
class value_file_list(type_checked_list, dependency_provider):

  def __init__(self, values = None):
    super(value_file_list, self).__init__(value_file, values = values)

  def __str__(self):
    return ' '.join([ h.value_to_string() for h in iter(self) ])

  @classmethod
  def parse(clazz, value, value_filename):
    result = clazz()
    filenames = string_list.parse(value, options = string_list.KEEP_QUOTES)
    for filename in filenames:
      rf = value_file.parse(filename, value_filename)
      result.append(value_file.parse(filename, value_filename))
    return result

  def provided(self):
    'Return a list of dependencies provided by this provider.'
    result = []
    for value in iter(self):
      result.extend(value.provided())
    return result
  
check.register_class(value_file, include_seq = False)
check.register_class(value_file_list, include_seq = False)
