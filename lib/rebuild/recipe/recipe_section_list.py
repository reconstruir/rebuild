#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, re, glob, os.path as path
from bes.fs import file_util
from bes.common import algorithm, dict_util, string_util, string_list_parser
from bes.compat import StringIO
from recipe_section_list_parser import recipe_section_list_parser
from recipe_section import recipe_section
from rebuild.dependency import dependency_resolver

class recipe_section_list(object):

  def __init__(self):
    self._recipe_sections = {}
    
  def __str__(self):
    buf = StringIO()
    for recipe_section in iter(self):
      buf.write(recipe_section)
      buf.write('\n\n')
    return buf.getvalue()

  def __eq__(self, other):
    return self._recipe_sections == other._recipe_sections

  def __len__(self):
    return len(self._recipe_sections)

  def __iter__(self):
    return iter(self.values())

  def __getitem__(self, name):
    return self._recipe_sections[name]
  
  def __setitem__(self, name, recipe_section):
    if name in self._recipe_sections:
      raise RuntimeError('duplicate recipe_section \"%s\"' % (name))
    self._recipe_sections[name] = recipe_section

  def __contains__(self, name):
    return name in self._recipe_sections
    
  def __add__(self, other):
    result = recipe_section_list()
    result._recipe_sections = copy.deepcopy(self._recipe_sections)
    result.update(other)
    return result
    
  def update(self, what):
    if isinstance(what, recipe_section):
      self[what.name] = what
    elif isinstance(what, recipe_section_list):
      for inst in what:
        self[inst.name] = inst
    else:
      raise TypeError('what should be of either recipe_section or recipe_section_list type instead of %s' % (type(what)))

  def values(self):
    'Return all recipe_sections as a list ordered by name.'
    return sorted(self._recipe_sections.values(), key = lambda x: x.name)
    
  @classmethod
  def parse(clazz, text):
    result = clazz()
    for recipe_section in recipe_section_list_parser.parse(text):
      result[recipe_section.name] = recipe_section
    return result

  def save(self, where):
    for recipe_section in iter(self):
      filename = '%s.rci' % (recipe_section.name)
      filepath = path.join(where, filename)
      if path.exists(filepath):
        return False, 'Recipe_Section already exists: %s' % (filepath)
      file_util.save(filepath, content = str(recipe_section), mode = 0644)
    return True, None

  @classmethod
  def load_dir(clazz, where):
    result = recipe_section_list()
    pattern = '%s/*.rci' % (where)
    files = sorted(glob.glob('%s/*.rci' % (where)))
    seen_file = {}
    for f in files:
      recipe_sections = clazz.load_file(f)
      for recipe_section in recipe_sections:
        if recipe_section.name in seen_file:
          raise RuntimeError('duplicate recipe_section \"%s\": %s %s' % (recipe_section.name, f, seen_file[recipe_section.name]))
        result[recipe_section.name] = recipe_section
        seen_file[recipe_section.name] = f
    return result

  @classmethod
  def load_file(clazz, filename):
    return clazz.parse(file_util.read(filename))

  def dependencies(self, target):
    if not string_util.is_string(target):
      raise TypeError('target should be a string: \"%s\"' % (target))
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
    for recipe_section in iter(self):
      result[recipe_section.name] = recipe_section.requires
    return result

  def flags(self, names):
    result = {}
    for name in names:
      if not name in self:
        raise KeyError('not found: \"%s\"' % (name))
      recipe_section = self[name]
      self._append_flag_values(result, recipe_section)
    for k, v in result.items():
      result[k] = ' '.join(algorithm.unique(self._flatten_flags_list(v)))
    return result

  @classmethod
  def _append_flag_values(clazz, d, recipe_section):
    for flag_key, flag_value in recipe_section.flags.items():
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
