#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum import enum

class step_argspec(enum):
  BOOL = 1
  INT = 2
  KEY_VALUES = 3
#  MASKED_FILE_LIST = 4
  STRING_LIST = 4
  STRING = 5
    
  DEFAULT = STRING

class step_arg_interpret(enum):
  NONE = 1
  DIR = 2
  FILE = 3
  FILE_LIST = 4
  DEFAULT = NONE
