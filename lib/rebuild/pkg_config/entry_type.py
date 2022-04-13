#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from enum import IntEnum

from bes.system.check import check

class entry_type(IntEnum):
  BLANK = 1
  COMMENT = 2
  PROPERTY = 3
  VARIABLE = 4

check.register_class(entry_type, include_seq = False)
  
