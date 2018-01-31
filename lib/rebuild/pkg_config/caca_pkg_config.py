#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import algorithm, check, object_util
from bes.fs import dir_util, file_util
from rebuild.dependency import dependency_resolver
from .caca_pkg_config_file import caca_pkg_config_file
from collections import namedtuple

class caca_pkg_config(object):

  def __init__(self, pc_path):
    self.files = self._scan_path(pc_path)
    self.dep_map = self._make_dep_map(self.files)
    #print('DEP_MAP:')
    #self._print_dep_map(self.dep_map)
    
  @classmethod
  def _scan_dir(clazz, d):
    'Scan a directory for .pc files.'
    if not path.isdir(d):
      return []
    return [ f for f in dir_util.list(d) if caca_pkg_config_file.is_pc_file(f) ]

  @classmethod
  def _scan_path(clazz, pc_path):
    'Scan all dirs in pc_path for .pc files.'
    result = {}
    for d in pc_path:
      files = clazz._scan_dir(d)
      for filename in files:
        name = file_util.remove_extension(path.basename(filename))
        pc_file = caca_pkg_config_file.parse_file(filename)
        if name in result:
          raise RuntimeError('Duplicate pc file: %s' % (filename))
        result[name] = pc_file
    return result

  @classmethod
  def _make_dep_map(clazz, files):
    'Scan a directory for .pc files.'
    dep_map = {}
    for name, pc_file in files.items():
      p = set()
      for req in pc_file.requires:
        p.add(req.name)
      dep_map[name] = p
    return dep_map
  
  @classmethod
  def _print_dep_map(clazz, dep_map):
    for name, deps in sorted(dep_map.items()):
      print('%s: %s' % (name, ' '.join(sorted(deps))))
  
  _list_all_item = namedtuple('_list_all_item', 'name,description')
  def list_all(self):
    'List all modules available.'
    result = []
    for name, pc_file in self.files.items():
      desc = pc_file.resolved_properties.find_key('Description').value
      prop_name = pc_file.resolved_properties.find_key('Name').value
      result.append(self._list_all_item(name, '%s - %s' % (prop_name, desc)))
    return sorted(result, cmp = lambda a, b: cmp(a.name.lower(), b.name.lower()))

  def list_all_names(self):
    mods = self.list_all()
    return [ mod.name for mod in mods ]

  def module_version(self, module_name):
    return self._get_pc_file(module_name).version
    
  def cflags(self, modules):
    modules = object_util.listify(modules)
    check.check_string_seq(modules)
    cflags = []
    reqs = self.module_requires(module_name)
    req_names = [ req.name for req in reqs ]
    order = dependency_resolver.resolve_deps(self.dep_map, req_names)
    for mod in reqs:
      cflags.extend(self._single_module_cflags(mod.name))
    cflags.extend(self._single_module_cflags(module_name))
    return cflags
    
  def requires(self, modules, resolved = False):
    modules = object_util.listify(modules)
    check.check_string_seq(modules)
    #if not resolved:
    #return self._get_pc_file(module_name).requires

  def _requires_no_resolve(self, modules):
    modules = object_util.listify(modules)
    check.check_string_seq(modules)
    reqs = []
    for name in modules:
      reqs.extend(self._get_pc_file(module_name).requires)
    return algorithm.unique(reqs)

  def _resolve_requires(self, modules):
    modules = object_util.listify(modules)
    check.check_string_seq(modules)
    immediate_reqs = self.module_requires(module_name)
    immediate_req_names = [ req.name for req in reqs ]
    order = dependency_resolver.resolve_deps(self.dep_map, req_names)
    for mod in reqs:
      cflags.extend(self._single_module_cflags(mod.name))
    cflags.extend(self._single_module_cflags(module_name))
    return cflags
    
  
  def module_exists(self, name):
    'Return True if module exists.'
    return self.files.get(name, None) != None

  def _single_module_cflags(self, module_name):
    return self._get_pc_file(module_name).cflags

  def _get_pc_file(self, module_name):
    pc_file = self.files.get(module_name, None)
    if not pc_file:
      raise ValueError('Invalid module: %s' % (module_name))
    return pc_file
