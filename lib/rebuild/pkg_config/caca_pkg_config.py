#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#import os.path as path
#from bes.common import algorithm, object_util, Shell, string_util
#from bes.system import log, os_env_var, host
from bes.fs import dir_util #file_find, file_match, file_util
#from rebuild import build_blurb, build_arch, System

from .pkg_config_file import pkg_config_file

class caca_pkg_config(object):

  @classmethod
  def scan_dir(clazz, d):
    'Scan a directory for .pc files.'
    possible_files = dir_util.list(d, relative = True)
    return [ f for f in possible_files if pkg_config_file.is_pc_file(f) ]
