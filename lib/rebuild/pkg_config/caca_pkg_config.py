#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
#from bes.common import string_util
#from bes.system import log, os_env_var, host
from bes.fs import dir_util, file_util #file_find, file_match, 
#from rebuild import build_blurb, build_arch, System

from .caca_pkg_config_file import caca_pkg_config_file
from collections import namedtuple

class caca_pkg_config(object):

  @classmethod
  def scan_dir(clazz, d):
    'Scan a directory for .pc files.'
    if not path.isdir(d):
      return []
    return [ f for f in dir_util.list(d) if caca_pkg_config_file.is_pc_file(f) ]

  @classmethod
  def scan(clazz, pc_path):
    'Scan all dirs in pc_path for .pc files.'
    result = {}
    for d in pc_path:
      files = clazz.scan_dir(d)
      for filename in files:
        name = file_util.remove_extension(path.basename(filename))
        pc_file = caca_pkg_config_file.parse_file(filename)
        if name in result:
          raise RuntimeError('Duplicate pc file: %s' % (filename))
        result[name] = pc_file
    return result
  
  _list_all_item = namedtuple('_list_all_item', 'name,description')
  @classmethod
  def list_all(clazz, pc_path):
    'List all modules available.'
    files = clazz.scan(pc_path)
    result = []
    for name, pc_file in files.items():
      result.append(clazz._list_all_item(name, pc_file.properties.find_key('Description').value))
    return sorted(result, cmp = lambda a, b: cmp(a.name.lower(), b.name.lower()))

  @classmethod
  def list_all_names(clazz, pc_path):
    mods = clazz.list_all(pc_path)
    return [ mod.name for mod in mods ]
  
