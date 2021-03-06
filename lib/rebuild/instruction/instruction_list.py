#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, re, glob, os.path as path
from bes.fs import file_util
from bes.common import algorithm, check, dict_util, string_util, type_checked_list
from bes.text import string_list_parser
from bes.compat import StringIO
from .instruction_list_parser import instruction_list_parser
from .instruction import instruction
from bes.dependency import dependency_resolver

class instruction_list(type_checked_list):

  __value_type__ = instruction
  
  def __init__(self, values = None):
    super(instruction_list, self).__init__(values = values)

  def __contains__(self, v):
    if check.is_string(v):
      return self.contains_name(v)
    return super(instruction, self).__contains__(v)
  
  def contains_name(self, name):
    for v in self._values:
      if v.name == name:
        return True
    return False

  def __str__(self):
    buf = StringIO()
    for inst in self._values:
      buf.write(inst.to_string(depth = 2))
      buf.write('\n\n')
    return buf.getvalue().strip()

  '''
  def update(self, what):
    check.check(what, ( instruction, instruction_list ), 'what')
    if isinstance(what, instruction):
      self[what.name] = what
    elif isinstance(what, instruction_list):
      for inst in what:
        self[inst.name] = inst
  '''
  
  def values(self):
    'Return all instructions as a list ordered by name.'
    return sorted(self._values(), key = lambda inst: inst.name)
    
  @classmethod
  def parse(clazz, text):
    return clazz(instruction_list_parser.parse(text))

  def save(self, where):
    for inst in iter(self):
      filename = '%s.rci' % (inst.name)
      filepath = path.join(where, filename)
      if path.exists(filepath):
        return False, 'Instruction already exists: %s' % (filepath)
      file_util.save(filepath, content = str(inst), mode = 0o644)
    return True, None

  @classmethod
  def load_dir(clazz, where):
    result = instruction_list()
    pattern = '%s/*.rci' % (where)
    files = sorted(glob.glob('%s/*.rci' % (where)))
    seen_file = {}
    for f in files:
      instructions = clazz.load_file(f)
      for instruction in instructions:
        if instruction.name in seen_file:
          raise RuntimeError('duplicate instruction \"%s\": %s %s' % (instruction.name, f, seen_file[instruction.name]))
        result[instruction.name] = instruction
        seen_file[instruction.name] = f
    return result

  @classmethod
  def load_file(clazz, filename):
    return clazz.parse(file_util.read(filename, codec = 'utf-8'))

  def dependencies(self, target):
    check.check_string(target)
    dependency_map = self._dependency_map()
    if not target in dependency_map:
      raise KeyError('target not found: \"%s\"' % (target))
    resolved_names = dependency_resolver.resolve_deps(dependency_map, target)
    resolved_map = dict_util.filter_with_keys(dependency_map, resolved_names)
    build_order = dependency_resolver.build_order_flat(resolved_map)
    build_order.remove(target)
    return build_order
  
  def _dependency_map(self):
    result = {}
    for instruction in iter(self):
      result[instruction.name] = instruction.requires
    return result

  def flags(self, names):
    result = {}
    for name in names:
      if not name in self:
        raise KeyError('not found: \"%s\"' % (name))
      instruction = self[name]
      self._append_flag_values(result, instruction)
    for k, v in result.items():
      result[k] = ' '.join(algorithm.unique(self._flatten_flags_list(v)))
    return result

  @classmethod
  def _append_flag_values(clazz, d, instruction):
    for flag_key, flag_value in instruction.flags.items():
      if not flag_key in d:
        d[flag_key] = []
      d[flag_key].append(flag_value)

  @classmethod
  def _flatten_flags_list(clazz, l):
    result = []
    for x in l:
      parsed = string_list_parser.parse(x, options = string_list_parser.KEEP_QUOTES)
      result.extend(parsed)
    return result
  
    '''
    spaces_escaped = [ string_util.escape_spaces(x) for x in l ]
    all_flat = ' '.join(spaces_escaped)
    print "ALL_FLAT: _%s_" % (all_flat)
    all_flat = string_util.escape_quotes(all_flat)
    parsed = string_list_parser.parse(all_flat)
    for p in parsed:
      print "PARSED: _%s_" % (p)
    parsed = algorithm.unique(parsed)
    parsed_flat =  ' '.join(parsed)
    return string_util.escape_quotes(parsed_flat)
    '''
