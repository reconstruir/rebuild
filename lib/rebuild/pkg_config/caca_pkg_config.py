#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
#from bes.common import algorithm, object_util, Shell, string_util
#from bes.system import log, os_env_var, host
from bes.fs import dir_util #file_find, file_match, file_util
#from rebuild import build_blurb, build_arch, System

from .pkg_config_file import pkg_config_file
from collections import namedtuple

class caca_pkg_config(object):

  @classmethod
  def scan_dir(clazz, d):
    'Scan a directory for .pc files.'
    if not path.isdir(d):
      return []
    return [ f for f in dir_util.list(d) if pkg_config_file.is_pc_file(f) ]

  @classmethod
  def scan(clazz, pc_path):
    'Scan all dirs in pc_path for .pc files.'
    result = {}
    for d in pc_path:
      files = clazz.scan_dir(d)
      for filename in files:
        pc_file = pkg_config_file()
        pc_file.parse_file(filename)
        name = pc_file.variables['Name']
        if name in result:
          raise RuntimeError('Duplicate pc file: %s' % (filename))
        result[name] = pc_file
    return result
  
  _list_item = namedtuple('_list_item', 'name,description')
  @classmethod
  def list_all(clazz, pc_path):
    'List all modules available.'
    possible_files = dir_util.list(d)
    return [ f for f in possible_files if pkg_config_file.is_pc_file(f) ]
  
