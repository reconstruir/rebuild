#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# FIXME: maintain integrity of original pc whitespace and comments

import copy, glob, os.path as path
from bes.common.algorithm import algorithm
from bes.common.string_util import string_util
from bes.key_value.key_value import key_value
from bes.fs.dir_util import dir_util
from bes.fs.file_util import file_util
from .entry import entry
from bes.build.requirement import requirement
from bes.build.requirement_list import requirement_list

class pkg_config_file(object):

  def __init__(self):
    self.__reset()

  def __reset(self):
    self.variables = []
    self.exports = []

  def parse_file(self, filename):
    self.__reset()
    try:
      return self.parse_string(file_util.read(filename).decode('utf-8'))
    except:
      print("failed loading %s" % (filename))
      raise

  def write_file(self, filename, backup = True):
    new_content = str(self)
    if path.exists(filename):
      old_content = file_util.read(filename)
      if new_content == old_content:
        return False
    if backup:
      file_util.backup(filename)
    file_util.save(filename, new_content)
    return True

  def parse_string(self, s):
    self.__reset()
    lines = [ s.strip() for s in s.split('\n') ]
    lines = [ line for line in lines if self.__line_is_valid(line) ]
    
    entries = [ entry.parse(line) for line in lines ]
    for e in entries:
      if e.is_variable():
        self.variables.append(e)
      else:
        self.exports.append(e)

  def __eq__(self, cf):
    return self.__dict__ == cf.__dict__

  def __str__(self):
    variables_lines = [ str(variable) for variable in self.variables ]
    exports_lines = [ str(export) for export in self.exports ]
    return '\n'.join(variables_lines) + '\n\n' + '\n'.join(exports_lines)

  @classmethod
  def __line_is_valid(clazz, line):
    if not line:
      return False
    if line.startswith('#'):
      return False
    return True

  def deep_copy(self):
    result = pkg_config_file()
    result.variables = copy.deepcopy(self.variables)
    result.exports = copy.deepcopy(self.exports)
    return result

  def variables_as_dict(self):
    result = {}
    for variable in self.variables:
      result[variable.name] = variable.value
    return result

#  def set_variable(self, name, value):
#    for variable in self.variables:
#      if variable.name == name:
#        variable.value = value

#  def set_variables(self, variables):
#    check.check_key_value_list(variables)
#    for kv in variables:
#      self.set_variable(kv.key, kv.value)

  def set_export(self, name, value):
    assert False
    for export in self.exports:
      if export.name == name:
        export.value = value

  def resolve(self):
    'Resolve all variables.'
    for variable in self.variables:
      variable.replace(self.variables_as_dict())
    variable_dict = self.variables_as_dict()
    for export in self.exports:
      export.replace(variable_dict)

#  def replace(self, replacements):
#    assert False
#    assert isinstance(replacements, dict)
#    for variable in self.variables:
#      variable.replace(replacements)
#    for export in self.exports:
#      export.replace(replacements)

  def cleanup_duplicate_exports(self):
    'Cleanup duplicate flags in exports.'
    for export in self.exports:
      if export.name.lower().startswith('requires'):
        export.value = self.__dedup_requirements(export.value)
      else:
        export.value = self.__unduplicate_flags(export.value)

  @classmethod
  def __dedup_requirements(clazz, value):
    reqs = requirement_list.parse(value)
    reqs.remove_dups()
    return reqs.to_string()

  def __parse_requirements(self):
    buf = StringIO()
    buf.write(self.label)
    buf.write(': ')
    buf.write(' '.join([ str(req) for req in self.requirements ]))
    return buf.getvalue()

  def __unduplicate_flags(clazz, flags):
    'Unduplicate flags.'
    v = string_util.split_by_white_space(flags)
    unique_v = algorithm.unique(v)
    return ' '.join(unique_v)

  @classmethod
  def rewrite_cleanup(clazz, src_pc, dst_pc, backup = True):
    cf = pkg_config_file()
    cf.parse_file(src_pc)
    cf.cleanup_duplicate_exports()
    return cf.write_file(dst_pc, backup = backup)

  @classmethod
  def is_pc_file(clazz, f):
    'Return True of f is a pkg-config pc file.'
    return f.lower().endswith('.pc')
