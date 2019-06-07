#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum.enum import enum

class requirement_hardness(enum):
  # Requirement needed at runtime.  For example a dynamically linked library.
  RUN = 1

  # Requirement is tool needed at build time.  For example a compiler.
  TOOL = 2

  # Requirement needed only at build time.  For example a statically linked library.
  BUILD = 3
    
  # Requirement needed only for testing.
  TEST = 4
    
  DEFAULT = RUN
