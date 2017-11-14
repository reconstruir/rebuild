#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum import enum

class step_argspec(enum):
  BOOL = 1
  INT = 2
  MASKED_KEY_VALUES = 3
  MASKED_FILE_LIST = 4
  MASKED_STRING_LIST = 5
  STRING = 6
    
  DEFAULT = STRING
