#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.compat.StringIO import StringIO
from bes.common.check import check
from bes.common.string_util import string_util
from bes.common.type_checked_list import type_checked_list
from bes.version.software_version import software_version

class recipe_data_entry(namedtuple('recipe_data_entry', 'mask, name, version, value')):
  
  def __new__(clazz, mask, name, version, value):
    check.check_string(mask)
    check.check_string(name)
    check.check_string(version)
    check.check_string(value)
    return clazz.__bases__[0].__new__(clazz, mask, name, version, value)

  def __str__(self):
    return '{}: {} {} {}'.format(self.mask, self.name, self.version, self.value)

  @classmethod
  def parse(clazz, text):
    check.check_string(text)
    parts = string_util.split_by_white_space(text, strip = True)
    if len(parts) != 4:
      raise ValueError('invalid recipe data entry: "{}"'.format(text))
    return recipe_data_entry(string_util.remove_tail(parts[0], ':'), parts[1], parts[2], parts[3])
  
check.register_class(recipe_data_entry, include_seq = False)

class recipe_data_entry_list(type_checked_list):

  __value_type__ = recipe_data_entry
  
  def __init__(self, values = None):
    super(recipe_data_entry_list, self).__init__(values = values)
    
  def to_string(self, delimiter = '\n'):
    buf = StringIO()
    first = True
    longest_name = self._longest_name()
    longest_version = self._longest_version()
    for v in self._values:
      if not first:
        buf.write(delimiter)
      first = False
      buf.write(v.mask)
      buf.write(': ')
      buf.write(string_util.justify(v.name, string_util.JUSTIFY_LEFT, longest_name))
      buf.write(' ')
      buf.write(string_util.justify(v.version, string_util.JUSTIFY_LEFT, longest_version))
      buf.write(' ')
      buf.write(v.value)
    return buf.getvalue()
    
  def _longest_name(self):
    return max([ len(v.name) for v in self ])
    
  def _longest_version(self):
    return max([ len(v.version) for v in self ])
    
  def __str__(self):
    return self.to_string()

  def sort_by_version(self):
    self.sort(key = lambda entry: software_version.parse_version(entry.version).parts)
  
  def find_by_version(self, version):
    return filter(lambda entry: entry.version == version, self._values)
  
check.register_class(recipe_data_entry_list, include_seq = False)
