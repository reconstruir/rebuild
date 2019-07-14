#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import os.path as path

from bes.compat.StringIO import StringIO
from bes.common.check import check
from bes.common.node import node
from bes.key_value.key_value_list import key_value_list
from bes.system.log import log

from rebuild.recipe.recipe_error import recipe_error
from rebuild.recipe.recipe_util import recipe_util

from .ingest_entry_list import ingest_entry_list

class ingest_file(namedtuple('ingest_file', 'format_version, filename, description, variables, entries')):

  FORMAT_VERSION = 1
  MAGIC = '!rebuild.ingest!'
  
  def __new__(clazz, format_version, filename, description, variables, entries):
    check.check_int(format_version)
    if format_version != clazz.FORMAT_VERSION:
      raise recipe_error('Invalid ingest_file format_version {}'.format(format_version), filename, 1)
    check.check_string(filename)
    check.check_string(description, allow_none = True)
    check.check_key_value_list(variables, allow_none = True)
    check.check_ingest_entry_list(entries, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, format_version, filename, description, variables, entries)

  def __str__(self):
    return self.to_string().strip() + '\n'

  def to_string(self, depth = 0, indent = 2):
    buf = StringIO()
    buf.write(self.MAGIC + '\n')
    buf.write('\n')
    if self.description:
      n = recipe_util.description_to_node(self.description)
      buf.write(str(n))
      buf.write('\n')
    if self.variables:
      n = self._variables_to_node(self.variables)
      buf.write(str(n))
      buf.write('\n')
    if self.entries:
      first = True
      for entry in self.entries:
        n = entry.to_node()
        if not first:
          buf.write('\n')
        first = False
        buf.write(str(n))
    buf.write('\n')
    return buf.getvalue()
  

#  def resolve_recipes(self, system):
#    if not self.recipes:
#      return string_list()
#    return sorted(self.recipes.resolve(system, 'string_list'))
  
  @classmethod
  def is_ingest_file(clazz, filename):
    'Return True if filename is a valid rebuild.ingest file.'
    return recipe_util.file_starts_with_magic(filename, clazz.MAGIC)

  @classmethod
  def _variables_to_node(clazz, variables):
    check.check_key_value_list(variables)
    result = node('variables')
    for kv in variables:
      result.add_child(kv.to_string(quote_value = True))
    return result
  
check.register_class(ingest_file, include_seq = False)
