#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import dir_util, file_util
from rebuild.dependency import dependency_resolver
from .caca_pkg_config_file import caca_pkg_config_file
from collections import namedtuple

class caca_pkg_config(object):

  def __init__(self, pc_path):
    self.files = self._scan_path(pc_path)
    
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
    for name, pc_file in self.files.items():
      pass
    return dep_map
  
  _list_all_item = namedtuple('_list_all_item', 'name,description')
  def list_all(self):
    'List all modules available.'
    result = []
    for name, pc_file in self.files.items():
      result.append(self._list_all_item(name, pc_file.resolved_properties.find_key('Description').value))
    return sorted(result, cmp = lambda a, b: cmp(a.name.lower(), b.name.lower()))

  def list_all_names(self):
    mods = self.list_all()
    return [ mod.name for mod in mods ]

  def module_version(self, module_name):
    return self.module_property(module_name, caca_pkg_config_file.PROPERTY_VERSION)
    
  def module_cflags(self, module_name):
    return self.module_property(module_name, caca_pkg_config_file.PROPERTY_CFLAGS)
    
  def module_requires(self, module_name):
    return self.module_property(module_name, caca_pkg_config_file.PROPERTY_REQUIRES)

  def module_property(self, module_name, property_name):
    pc_file = self.files.get(module_name, None)
    if not pc_file:
      raise ValueError('Invalid module: %s' % (module_name))
    return pc_file.get_property(property_name)
    
  def module_exists(self, name):
    'Return True if module exists.'
    return self.files.get(name, None) != None
