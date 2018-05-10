#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum import enum

class value_type(enum):
  BOOL = 1
  DIR = 2
  FILE = 3
  INSTALL_FILE = 4
  FILE_LIST = 5
  HOOK_LIST = 6
  INT = 7
  KEY_VALUES = 8
  STRING = 9
  STRING_LIST = 10
  GIT_ADDRESS = 11
  SOURCE_TARBALL = 12
  SOURCE_DIR = 13
    
  DEFAULT = STRING
