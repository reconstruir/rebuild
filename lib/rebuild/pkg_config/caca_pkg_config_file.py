#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# FIXME: maintain integrity of original pc whitespace and comments

#import copy, glob, os.path as path
from bes.common.check import check
from bes.common.variable import variable
from bes.common.string_util import string_util
from bes.text import text_line_parser, string_list_parser
from bes.key_value import key_value, key_value_list
from bes.fs import file_util
#from .entry import entry
from rebuild.base import requirement, requirement_list
from .caca_entry import caca_entry

from collections import namedtuple

class caca_pkg_config_file(namedtuple('caca_pkg_config_file', 'filename,entries,variables,properties,resolved_variables,resolved_properties')):

  PROPERTY_CFLAGS = 'Cflags'
  PROPERTY_DESCRIPTION = 'Description'
  PROPERTY_LIBS = 'Libs'
  PROPERTY_NAME = 'Name'
  PROPERTY_REQUIRES = 'Requires'
  PROPERTY_VERSION = 'Version'
  
  def __new__(clazz, filename, entries, variables, properties):
    check.check_string(filename)
    check.check_caca_pkg_config_entry_seq(entries)
    check.check_key_value_list(variables)
    check.check_key_value_list(properties)
    resolved_variables = variables[:]
    resolved_variables.substitute_variables(variables.to_dict())
    resolved_properties = properties[:]
    resolved_properties.substitute_variables(resolved_variables.to_dict())

    raw_reqs = resolved_properties.find_by_key(clazz.PROPERTY_REQUIRES)
    if raw_reqs:
      reqs = clazz._parse_requirements(raw_reqs.value)
      resolved_properties.replace(clazz.PROPERTY_REQUIRES, key_value(clazz.PROPERTY_REQUIRES, reqs))
    else:
      resolved_properties.append(key_value(clazz.PROPERTY_REQUIRES, []))
    
    return clazz.__bases__[0].__new__(clazz, filename, entries, variables, properties, resolved_variables, resolved_properties)
  
  def write_file(self, filename, backup = True):
    new_content = str(self)
    if path.exists(filename):
      old_content = file_util.read(filename, codec = 'utf-8')
      if new_content == old_content:
        return False
    if backup:
      file_util.backup(filename)
    file_util.save(filename, new_content)
    return True

  @classmethod
  def parse_text(clazz, filename, text):
    ll = text_line_parser(text)
    entries = [ caca_entry.parse(line) for line in ll ]
    variables = key_value_list([ entry.value for entry in entries if entry.is_variable ])
    properties = key_value_list([ entry.value for entry in entries if entry.is_property ])
    return clazz(filename, entries, variables, properties)

  @classmethod
  def parse_file(clazz, filename):
    text = file_util.read(filename).decode('utf-8')
    return clazz.parse_text(filename, text)

  @classmethod
  def _parse_requirements(clazz, text):
    'Parse the "Requires" property of a pc file.'
    ll = text_line_parser(text, delimiter = ',').texts(strip_head = True, strip_tail = True)
    result = []
    for s in ll:
      result.extend(requirement_list.parse(s))
    return result
    
#  def __str__(self):
#    variables_lines = [ str(variable) for variable in self.variables ]
#    properties_lines = [ str(export) for export in self.properties ]
#    return '\n'.join(variables_lines) + '\n\n' + '\n'.join(properties_lines)

#  @classmethod
#  def __line_is_valid(clazz, line):
#    if not line:
#      return False
#    if line.startswith('#'):
#      return False
#    return True

#  def deep_copy(self):
#    result = caca_pkg_config_file()
#    result.variables = copy.deepcopy(self.variables)
#    result.properties = copy.deepcopy(self.properties)
#    return result

#  def variables_as_dict(self):
#    result = {}
#    for variable in self.variables:
#      result[variable.name] = variable.value
#    return result

#  def set_variable(self, name, value):
#    for variable in self.variables:
#      if variable.name == name:
#        variable.value = value

#  def set_variables(self, variables):
#    check.check_key_value_list(variables)
#    for kv in variables:
#      self.set_variable(kv.key, kv.value)

#  def set_export(self, name, value):
#    for export in self.properties:
#      if export.name == name:
#        export.value = value

#  def resolve(self):
#    'Resolve all variables.'
#    for variable in self.variables:
#      variable.replace(self.variables_as_dict())
#    variable_dict = self.variables_as_dict()
#    for export in self.properties:
#      export.replace(variable_dict)

#  def replace(self, replacements):
#    assert False
#    assert isinstance(replacements, dict)
#    for variable in self.variables:
#      variable.replace(replacements)
#    for export in self.properties:
#      export.replace(replacements)

#  def cleanup_duplicate_properties(self):
#    'Cleanup duplicate flags in properties.'
#    for export in self.properties:
#      if export.name.lower().startswith('requires'):
#        export.value = self.__dedup_requirements(export.value)
#      else:
#        export.value = self.__unduplicate_flags(export.value)
#
#  @classmethod
#  def __dedup_requirements(clazz, value):
#    reqs = requirement_list.parse(value)
#    return requirement.requirement_list_to_string(reqs)
#
#  def __parse_requirements(self):
#    buf = StringIO()
#    buf.write(self.label)
#    buf.write(': ')
#    buf.write(' '.join([ str(req) for req in self.requirements ]))
#    return buf.getvalue()
#
#        
#  def __unduplicate_flags(clazz, flags):
#    'Unduplicate flags.'
#    v = string_util.split_by_white_space(flags)
#    unique_v = algorithm.unique(v)
#    return ' '.join(unique_v)
#
#  @classmethod
#  def rewrite_cleanup(clazz, src_pc, dst_pc):
#    cf = caca_pkg_config_file()
#    cf.parse_file(src_pc)
#    cf.cleanup_duplicate_properties()
#    return cf.write_file(dst_pc)
#
  @classmethod
  def is_pc_file(clazz, f):
    'Return True of f is a pkg-config pc file.'
    return f.lower().endswith('.pc')

  @property
  def version(self):
    return self.get_property(self.PROPERTY_VERSION)

  @property
  def cflags(self):
    cflags = self.get_property(self.PROPERTY_CFLAGS) or ''
    return string_list_parser.parse_to_list(cflags, options = string_list_parser.KEEP_QUOTES)

  @property
  def requires(self):
    return self.get_property(self.PROPERTY_REQUIRES)

  def get_property(self, name):
    prop = self.resolved_properties.find_by_key(name)
    if prop:
      return prop.value
    return None

  PC_FILE_TEMPLATE = '''prefix=@PREFIX@
exec_prefix=${prefix}
libdir=${exec_prefix}/lib
sharedlibdir=${libdir}
includedir=${prefix}/include

Name: @NAME@
Description: @DESCRIPTION@
Version: @VERSION@

Requires: @REQUIRES@
Libs: @LIBS@
Cflags: @CFLAGS@
'''
  
  @classmethod
  def make_pc_file_content(clazz, prefix, name, description, version, requires, libs, cflags):
    'Make a testing .pc file.'
    replacements = {
      '@PREFIX@': prefix,
      '@NAME@': name,
      '@DESCRIPTION@': description,
      '@VERSION@': version,
      '@REQUIRES@': requires,
      '@LIBS@': libs,
      '@CFLAGS@': cflags,
    }
    return string_util.replace(clazz.PC_FILE_TEMPLATE, replacements)
