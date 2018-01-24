#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum import enum

class entry_type(enum):
  BLANK = 1
  COMMENT = 2
  PROPERTY = 3
  VARIABLE = 4
